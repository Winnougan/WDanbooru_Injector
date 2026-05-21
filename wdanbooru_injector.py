"""
WDanbooru_Injector — ComfyUI Custom Node
Fetches tags from Gelbooru by post ID or URL and injects them into a positive
prompt formatted for Anima and other Danbooru-trained models.

Source: Gelbooru (gelbooru.com) — free account API credentials required.
Get them at: gelbooru.com → My Account → Options → API key
"""

import re
import requests

# ──────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────

GELBOORU_API     = "https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1&id={}"
E621_API         = "https://e621.net/posts/{}.json"
KONACHAN_NET_API = "https://konachan.net/post.json?tags=id:{}"   # SFW
KONACHAN_COM_API = "https://konachan.com/post.json?tags=id:{}"   # NSFW
DANBOORU_API     = "https://danbooru.donmai.us/posts/{}.json"
YANDERE_API      = "https://yande.re/post.json?tags=id:{}"
LOLIBOORU_API    = "https://lolibooru.moe/post.json?tags=id:{}"

DEFAULT_QUALITY  = "masterpiece, best quality, score_7"
DEFAULT_NEGATIVE = "worst quality, low quality, score_1, score_2, score_3, artist name"

_CREDS_HINT = (
    "Gelbooru requires API credentials for all requests (free account is fine). "
    "Fill in 'gelbooru_user_id' and 'gelbooru_api_key' in the node. "
    "Get them at: gelbooru.com → My Account → Options → API key."
)

_E621_CREDS_HINT = (
    "e621 requires a User-Agent with your e621 username for API access. "
    "Fill in 'e621_username' in the node. "
    "An API key is optional but recommended for higher rate limits — "
    "get it at: e621.net → Account → Manage API Access."
)


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def _fmt_tags(raw: str) -> list[str]:
    """Split a tag string and convert underscores to spaces (Anima requirement)."""
    return [t.replace("_", " ").strip() for t in raw.split() if t.strip()]


def _artist_prefix(tags: list[str]) -> list[str]:
    """Prefix every artist tag with @ as required by Anima."""
    return [f"@{t}" if not t.startswith("@") else t for t in tags]


def _build_prompt_sections(
    quality: str,
    count_tag: str,
    character_tags: list[str],
    copyright_tags: list[str],
    artist_tags: list[str],
    general_tags: list[str],
    year_tag: str,
    safety_tag: str,
) -> str:
    """
    Assemble tags in Anima's recommended order:
    [quality] [year] [safety] [count] [character] [copyright] [artist] [general]
    """
    parts = []
    if quality:
        parts.append(quality.strip().rstrip(","))
    if year_tag and year_tag != "none":
        parts.append(f"year {year_tag}")
    if safety_tag and safety_tag != "none":
        parts.append(safety_tag)
    if count_tag.strip():
        parts.append(count_tag.strip())
    parts.extend(character_tags)
    parts.extend(copyright_tags)
    parts.extend(_artist_prefix(artist_tags))
    parts.extend(general_tags)
    return ", ".join(p for p in parts if p)


def _clean_creds(user_id: str, api_key: str) -> tuple[str, str]:
    """Strip accidental & and key= prefixes from pasted credential strings."""
    uid = user_id.strip().lstrip("&").split("=")[-1].strip()
    key = api_key.strip().rstrip("&").split("=")[-1].strip()
    return uid, key


def _parse_post_id_e621(raw: str) -> int:
    """Accept plain int or https://e621.net/posts/1234567 URL."""
    raw = raw.strip()
    m = re.search(r"e621\.net/posts/(\d+)", raw)
    if m:
        return int(m.group(1))
    if raw.isdigit():
        return int(raw)
    raise ValueError(
        f"Cannot parse e621 post ID from '{raw}'.\n"
        "Accepted: plain ID (4218495) or URL (https://e621.net/posts/4218495)"
    )


def _parse_post_id_konachan(raw: str) -> int:
    """Accept plain int or https://konachan.net/post/show/402821 URL."""
    raw = raw.strip()
    m = re.search(r"konachan\.(?:net|com)/post/show/(\d+)", raw)
    if m:
        return int(m.group(1))
    if raw.isdigit():
        return int(raw)
    raise ValueError(
        f"Cannot parse Konachan post ID from '{raw}'.\n"
        "Accepted: plain ID (402821) or URL (https://konachan.net/post/show/402821)"
    )


def _parse_post_id(raw: str) -> int:
    """
    Accept a plain integer string OR a full Gelbooru post URL and return
    the numeric post ID.

    Accepted formats:
      "12345678"
      "https://gelbooru.com/index.php?page=post&s=view&id=12345678"

    NOT accepted (direct image URLs — no post ID embedded):
      "https://img2.gelbooru.com/images/.../abc123.jpg"
    """
    raw = raw.strip()

    # Catch Gelbooru CDN / image URLs (img2.gelbooru.com etc.)
    if re.search(r"img\d+\.gelbooru\.com", raw):
        raise ValueError(
            "That looks like a Gelbooru image URL (img*.gelbooru.com/\u2026). "
            "It does not contain a post ID.\n\n"
            "How to get the correct URL or ID:\n"
            "  1. Open the image post on Gelbooru in your browser.\n"
            "  2. Copy the address bar URL \u2014 it will look like:\n"
            "     https://gelbooru.com/index.php?page=post&s=view&id=12345678\n"
            "  3. Paste that URL (or just the numeric ID) into the post_id field."
        )

    # Gelbooru post page URL: ?id=<id> or &id=<id>
    m = re.search(r"[?&]id=(\d+)", raw)
    if m:
        return int(m.group(1))

    # Plain integer
    if raw.isdigit():
        return int(raw)

    raise ValueError(
        f"WDanbooru_Injector: cannot parse a post ID from '{raw}'.\n\n"
        "Accepted inputs:\n"
        "  \u2022 A plain post ID number:   12345678\n"
        "  \u2022 A Gelbooru post page URL: "
        "https://gelbooru.com/index.php?page=post&s=view&id=12345678\n\n"
        "Do NOT paste direct image URLs \u2014 those don't contain post IDs."
    )


# ──────────────────────────────────────────────
# Fetch
# ──────────────────────────────────────────────

def _fetch_gelbooru(post_id: int, user_id: str, api_key: str) -> dict:
    """Fetch post metadata from Gelbooru. Credentials are required for all requests."""
    uid, key = _clean_creds(user_id, api_key)

    if not uid or not key:
        raise ValueError(f"Gelbooru post {post_id}: credentials missing. " + _CREDS_HINT)

    url  = GELBOORU_API.format(post_id) + f"&user_id={uid}&api_key={key}"
    resp = requests.get(url, timeout=10)

    if resp.status_code == 401:
        raise ValueError(
            f"Gelbooru rejected credentials for post {post_id} (401). "
            "Double-check your user_id and api_key. " + _CREDS_HINT
        )
    if resp.status_code == 403:
        raise ValueError(
            f"Gelbooru access forbidden for post {post_id} (403). "
            "Your account may not have permission to view this post."
        )
    if resp.status_code == 404:
        raise ValueError(f"Gelbooru post {post_id} not found (404). Check the ID.")

    resp.raise_for_status()

    if "html" in resp.headers.get("Content-Type", ""):
        raise ValueError(
            f"Gelbooru returned HTML instead of JSON for post {post_id}. "
            "Your credentials may be invalid, or the post is unavailable."
        )

    data = resp.json()

    if isinstance(data, list):
        posts = data
    elif isinstance(data, dict):
        posts = data.get("post", [])
        if isinstance(posts, dict):
            posts = [posts]
    else:
        posts = []

    if not posts:
        raise ValueError(
            f"Gelbooru: no post found for ID {post_id}. "
            "The post may have been deleted, or the ID is wrong."
        )
    return posts[0]


def _fetch_e621(post_id: int, username: str, api_key: str) -> dict:
    """
    Fetch post metadata from e621.
    - No credentials needed for public posts (rate limited to 2 req/s).
    - Username in User-Agent is polite but not required.
    - Both username AND api_key together enable authenticated access.
    Returns a normalised dict with separate tag-category lists.
    """
    u = username.strip()
    k = api_key.strip()

    # Build User-Agent — include username if provided (e621 policy encourages it)
    ua = f"WDanbooru_Injector/2.0 (by {u})" if u else "WDanbooru_Injector/2.0 (ComfyUI custom node)"
    headers = {"User-Agent": ua}

    # Only send auth params when BOTH are present — sending login without
    # a valid api_key causes e621 to reject with 401
    params = {}
    if u and k:
        params["login"]   = u
        params["api_key"] = k

    url  = E621_API.format(post_id)
    resp = requests.get(url, headers=headers, params=params, timeout=10)

    if resp.status_code == 401:
        raise ValueError(
            f"e621 rejected credentials for post {post_id} (401). "
            "Make sure both e621_username AND e621_api_key are correct, "
            "or leave both empty to use unauthenticated access. "
            + _E621_CREDS_HINT
        )
    if resp.status_code == 404:
        raise ValueError(f"e621 post {post_id} not found (404).")
    if resp.status_code == 403:
        raise ValueError(f"e621 post {post_id} forbidden (403). The post may be deleted or require login.")
    resp.raise_for_status()

    data = resp.json()
    post = data.get("post", {})
    if not post:
        raise ValueError(f"e621: no post data for ID {post_id}.")

    tags = post.get("tags", {})
    return {
        "_source":    "e621",
        "rating":     post.get("rating", "s"),
        "artist":     tags.get("artist",    []),
        "character":  tags.get("character", []),
        "copyright":  tags.get("copyright", []),
        "species":    tags.get("species",   []),   # e621-specific
        "general":    tags.get("general",   []),
        "meta":       tags.get("meta",      []),
    }


def _fetch_konachan(post_id: int, site: str = "net") -> dict:
    """
    Fetch post metadata from Konachan (net=SFW, com=NSFW).
    No credentials required. Returns a Gelbooru-style flat tag string.
    """
    api = KONACHAN_NET_API if site == "net" else KONACHAN_COM_API
    url  = api.format(post_id)
    resp = requests.get(
        url,
        headers={"User-Agent": "WDanbooru_Injector/2.0 (ComfyUI custom node)"},
        timeout=10,
    )

    if resp.status_code == 404:
        raise ValueError(f"Konachan post {post_id} not found (404).")
    if resp.status_code == 403:
        raise ValueError(f"Konachan returned 403 for post {post_id}. The post may be restricted.")
    resp.raise_for_status()

    data = resp.json()
    if not data:
        raise ValueError(f"Konachan: no post found for ID {post_id}.")

    post = data[0]
    return {
        "_source": f"konachan.{site}",
        "tags":    post.get("tags", ""),
        "rating":  post.get("rating", "s"),
        "author":  post.get("author", ""),
    }


def _fetch_danbooru(post_id: int, username: str, api_key: str) -> dict:
    """Fetch post metadata from Danbooru. Free account credentials recommended."""
    u, k = username.strip(), api_key.strip()
    ua = f"WDanbooru_Injector/2.0 (by {u})" if u else "WDanbooru_Injector/2.0 (ComfyUI custom node)"
    params = {}
    if u and k:
        params["login"]   = u
        params["api_key"] = k
    resp = requests.get(
        DANBOORU_API.format(post_id),
        headers={"User-Agent": ua},
        params=params,
        timeout=10,
    )
    if resp.status_code == 401:
        raise ValueError(f"Danbooru rejected credentials for post {post_id} (401).")
    if resp.status_code == 404:
        raise ValueError(f"Danbooru post {post_id} not found (404).")
    resp.raise_for_status()
    post = resp.json()
    if not post:
        raise ValueError(f"Danbooru: no data for post {post_id}.")
    raw    = post.get("tag_string", "")
    artist = post.get("tag_string_artist", "")
    char   = post.get("tag_string_character", "")
    copy_  = post.get("tag_string_copyright", "")
    skip   = set(artist.split()) | set(char.split()) | set(copy_.split())
    gen    = [t for t in raw.split() if t not in skip]
    return {
        "_source":   "danbooru",
        "rating":    post.get("rating", "s"),
        "artist":    artist.split(),
        "character": char.split(),
        "copyright": copy_.split(),
        "general":   gen,
        "meta":      [],
        "species":   [],
    }


def _fetch_dapi_by_id(post_id: int, base_url: str, site_label: str) -> dict:
    """Generic fetch-by-ID for dapi-compatible sites (Safebooru, Rule34, Hypnohub, ATFBooru, Xbooru)."""
    url  = f"{base_url}?page=dapi&s=post&q=index&json=1&id={post_id}"
    resp = requests.get(
        url,
        headers={"User-Agent": "WDanbooru_Injector/2.0 (ComfyUI custom node)"},
        timeout=10,
    )
    if resp.status_code == 404:
        raise ValueError(f"{site_label} post {post_id} not found (404).")
    resp.raise_for_status()
    data  = resp.json()
    posts = data if isinstance(data, list) else data.get("post", [])
    if isinstance(posts, dict):
        posts = [posts]
    if not posts:
        raise ValueError(f"{site_label}: no post found for ID {post_id}.")
    post = posts[0]
    return {
        "_source": site_label.lower(),
        "tags":    post.get("tags", ""),
        "rating":  post.get("rating", "s"),
        "author":  post.get("owner", ""),
    }


def _fetch_moebooru_by_id(post_id: int, domain: str, site_label: str) -> dict:
    """Generic fetch-by-ID for moebooru-style sites (Yande.re, Lolibooru)."""
    url  = f"https://{domain}/post.json?tags=id:{post_id}"
    resp = requests.get(
        url,
        headers={"User-Agent": "WDanbooru_Injector/2.0 (ComfyUI custom node)"},
        timeout=10,
    )
    if resp.status_code == 404:
        raise ValueError(f"{site_label} post {post_id} not found (404).")
    resp.raise_for_status()
    data = resp.json()
    if not data:
        raise ValueError(f"{site_label}: no post found for ID {post_id}.")
    post = data[0]
    return {
        "_source": site_label.lower(),
        "tags":    post.get("tags", ""),
        "rating":  post.get("rating", "s"),
        "author":  post.get("author", ""),
    }



# ──────────────────────────────────────────────

class WDanbooru_Injector:
    """
    Fetches Gelbooru tags for a post and injects them at the top of a positive
    prompt, formatted for Anima and other Danbooru-trained models.
    """

    CATEGORY = "WDanbooru"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "source": ([
                    "gelbooru", "e621", "danbooru",
                    "konachan.net", "konachan.com",
                    "yande.re", "lolibooru",
                    "safebooru", "rule34", "hypnohub", "atfbooru", "xbooru",
                    "manual",
                ], {"default": "gelbooru"}),
                "post_id": ("STRING", {
                    "default": "",
                    "multiline": False,
                }),
                "inject_mode": (["prepend", "append", "replace"], {"default": "prepend"}),
                "quality_prefix": ("STRING", {
                    "default": DEFAULT_QUALITY,
                    "multiline": False,
                }),
                "safety_tag": (
                    ["safe", "sensitive", "questionable", "explicit", "none"],
                    {"default": "safe"},
                ),
                "year_tag": (
                    ["none", "2020", "2021", "2022", "2023", "2024", "2025"],
                    {"default": "none"},
                ),
                "include_artist":    ("BOOLEAN", {"default": True}),
                "include_character": ("BOOLEAN", {"default": True}),
                "include_copyright": ("BOOLEAN", {"default": True}),
                "include_general":   ("BOOLEAN", {"default": True}),
                "max_general_tags":  ("INT", {
                    "default": 40,
                    "min": 1,
                    "max": 200,
                    "step": 1,
                }),
            },
            "optional": {
                "positive_prompt": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "forceInput": True,
                }),
                "manual_tags": ("STRING", {
                    "default": "",
                    "multiline": True,
                }),
                "count_tag":        ("STRING", {"default": ""}),
                "gelbooru_user_id": ("STRING", {"default": ""}),
                "gelbooru_api_key": ("STRING", {"default": ""}),
                "e621_username":    ("STRING", {"default": "", "tooltip": "Your e621 username. Required for API access (e621 policy)."}),
                "e621_api_key":     ("STRING", {"default": "", "tooltip": "Optional e621 API key for higher rate limits. Get at e621.net → Account → Manage API Access."}),
                "danbooru_username": ("STRING", {"default": "", "tooltip": "Your Danbooru username. Optional for public posts."}),
                "danbooru_api_key":  ("STRING", {"default": "", "tooltip": "Optional Danbooru API key."}),
                "extra_tags":       ("STRING", {"default": "", "multiline": False}),
            },
        }

    RETURN_TYPES  = ("STRING", "STRING")
    RETURN_NAMES  = ("positive_prompt", "injected_tags_only")
    FUNCTION      = "inject"
    OUTPUT_NODE   = False

    def inject(
        self,
        source,
        post_id,
        inject_mode,
        quality_prefix,
        safety_tag,
        year_tag,
        include_artist,
        include_character,
        include_copyright,
        include_general,
        max_general_tags,
        positive_prompt="",
        manual_tags="",
        count_tag="",
        gelbooru_user_id="",
        gelbooru_api_key="",
        e621_username="",
        e621_api_key="",
        danbooru_username="",
        danbooru_api_key="",
        extra_tags="",
    ):
        artist_tags    = []
        character_tags = []
        copyright_tags = []
        general_tags   = []

        # ── 1. Resolve tags ───────────────────────────────────────────────────

        if source == "manual":
            raw = re.split(r"[,\n]+", manual_tags)
            general_tags = [t.strip().replace("_", " ") for t in raw if t.strip()]

        elif source == "gelbooru":
            if not post_id.strip():
                return (positive_prompt.strip(), "")
            pid  = _parse_post_id(post_id)
            data = _fetch_gelbooru(pid, gelbooru_user_id, gelbooru_api_key)
            general_tags = _fmt_tags(data.get("tags", ""))

        elif source == "e621":
            if not post_id.strip():
                return (positive_prompt.strip(), "")
            pid  = _parse_post_id_e621(post_id)
            data = _fetch_e621(pid, e621_username, e621_api_key)
            artist_tags    = [t.replace("_", " ") for t in data.get("artist",    [])]
            character_tags = [t.replace("_", " ") for t in data.get("character", [])]
            copyright_tags = [t.replace("_", " ") for t in data.get("copyright", [])]
            general_tags   = [t.replace("_", " ") for t in
                               data.get("species", []) + data.get("general", []) + data.get("meta", [])]

        elif source == "danbooru":
            if not post_id.strip():
                return (positive_prompt.strip(), "")
            # Danbooru post IDs: plain int or https://danbooru.donmai.us/posts/12345
            raw_id = post_id.strip()
            m = re.search(r"donmai\.us/posts/(\d+)", raw_id)
            pid = int(m.group(1)) if m else int(raw_id) if raw_id.isdigit() else None
            if pid is None:
                return (positive_prompt.strip(), f"Cannot parse Danbooru post ID from '{raw_id}'.")
            data = _fetch_danbooru(pid, danbooru_username, danbooru_api_key)
            artist_tags    = [t.replace("_", " ") for t in data.get("artist",    [])]
            character_tags = [t.replace("_", " ") for t in data.get("character", [])]
            copyright_tags = [t.replace("_", " ") for t in data.get("copyright", [])]
            general_tags   = [t.replace("_", " ") for t in data.get("general", []) + data.get("species", []) + data.get("meta", [])]

        elif source in ("konachan.net", "konachan.com"):
            if not post_id.strip():
                return (positive_prompt.strip(), "")
            site = "net" if source == "konachan.net" else "com"
            pid  = _parse_post_id_konachan(post_id)
            data = _fetch_konachan(pid, site)
            general_tags = _fmt_tags(data.get("tags", ""))
            if include_artist and data.get("author"):
                artist_tags = [data["author"].replace("_", " ")]

        elif source == "yande.re":
            if not post_id.strip():
                return (positive_prompt.strip(), "")
            raw_id = post_id.strip()
            m = re.search(r"yande\.re/post/show/(\d+)", raw_id)
            pid = int(m.group(1)) if m else int(raw_id) if raw_id.isdigit() else None
            if pid is None:
                return (positive_prompt.strip(), f"Cannot parse Yande.re post ID from '{raw_id}'.")
            data = _fetch_moebooru_by_id(pid, "yande.re", "Yande.re")
            general_tags = _fmt_tags(data.get("tags", ""))
            if data.get("author"):
                artist_tags = [data["author"].replace("_", " ")]

        elif source == "lolibooru":
            if not post_id.strip():
                return (positive_prompt.strip(), "")
            raw_id = post_id.strip()
            m = re.search(r"lolibooru\.moe/post/show/(\d+)", raw_id)
            pid = int(m.group(1)) if m else int(raw_id) if raw_id.isdigit() else None
            if pid is None:
                return (positive_prompt.strip(), f"Cannot parse Lolibooru post ID from '{raw_id}'.")
            data = _fetch_moebooru_by_id(pid, "lolibooru.moe", "Lolibooru")
            general_tags = _fmt_tags(data.get("tags", ""))
            if data.get("author"):
                artist_tags = [data["author"].replace("_", " ")]

        elif source in ("safebooru", "rule34", "hypnohub", "atfbooru", "xbooru"):
            if not post_id.strip():
                return (positive_prompt.strip(), "")
            _DAPI_MAP = {
                "safebooru": ("https://safebooru.org/index.php",          "Safebooru"),
                "rule34":    ("https://api.rule34.xxx/index.php",         "Rule34.xxx"),
                "hypnohub":  ("https://hypnohub.net/index.php",           "Hypnohub"),
                "atfbooru":  ("https://booru.allthefallen.moe/index.php", "ATFBooru"),
                "xbooru":    ("https://xbooru.com/index.php",             "Xbooru"),
            }
            base_url, label = _DAPI_MAP[source]
            raw_id = post_id.strip()
            m = re.search(r"[?&]id=(\d+)", raw_id)
            pid = int(m.group(1)) if m else int(raw_id) if raw_id.isdigit() else None
            if pid is None:
                return (positive_prompt.strip(), f"Cannot parse {label} post ID from '{raw_id}'.")
            data = _fetch_dapi_by_id(pid, base_url, label)
            general_tags = _fmt_tags(data.get("tags", ""))

        # ── 2. Apply toggles ──────────────────────────────────────────────────

        if not include_artist:    artist_tags    = []
        if not include_character: character_tags = []
        if not include_copyright: copyright_tags = []
        if not include_general:   general_tags   = []
        else:                     general_tags   = general_tags[:max_general_tags]

        # ── 3. Extra user tags ────────────────────────────────────────────────

        if extra_tags.strip():
            extras = [
                t.strip().replace("_", " ")
                for t in re.split(r"[,\n]+", extra_tags) if t.strip()
            ]
            general_tags.extend(extras)

        # ── 4. Build injected block ───────────────────────────────────────────

        injected = _build_prompt_sections(
            quality        = quality_prefix,
            count_tag      = count_tag,
            character_tags = character_tags,
            copyright_tags = copyright_tags,
            artist_tags    = artist_tags,
            general_tags   = general_tags,
            year_tag       = year_tag,
            safety_tag     = safety_tag,
        )

        # ── 5. Combine with existing prompt ──────────────────────────────────

        base = positive_prompt.strip()
        if inject_mode == "prepend":
            combined = (injected + ", " + base) if base else injected
        elif inject_mode == "append":
            combined = (base + ", " + injected) if base else injected
        else:  # replace
            combined = injected

        return (combined, injected)


# ──────────────────────────────────────────────
# Node: WDanbooru_NegativePreset
# ──────────────────────────────────────────────

class WDanbooru_NegativePreset:
    """
    Outputs a recommended negative prompt for Anima / Danbooru-trained models,
    optionally merged with user-supplied extra negatives.
    """

    CATEGORY = "WDanbooru"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "preset": (
                    [
                        "anima_default",
                        "anima_detailed",
                        "anima_portrait",
                        "anima_multi_character",
                        "anima_sfw_strict",
                        "quality_only",
                        "empty",
                    ],
                    {"default": "anima_default"},
                ),
            },
            "optional": {
                "extra_negative": ("STRING", {"default": "", "multiline": True}),
            },
        }

    RETURN_TYPES  = ("STRING",)
    RETURN_NAMES  = ("negative_prompt",)
    FUNCTION      = "build"

    _PRESETS = {
        # Anima base — score tags do the heavy quality lifting
        "anima_default": DEFAULT_NEGATIVE,

        # Adds anatomy + artifact terms. Good all-rounder for most generations
        "anima_detailed": (
            "worst quality, low quality, score_1, score_2, score_3, artist name, "
            "bad anatomy, bad hands, extra fingers, missing fingers, fused fingers, "
            "extra limbs, watermark, signature, text"
        ),

        # Portrait / close-up — tightens framing, suppresses wide shots
        "anima_portrait": (
            "worst quality, low quality, score_1, score_2, score_3, artist name, "
            "bad anatomy, bad hands, extra fingers, missing fingers, fused fingers, "
            "cloned face, extra faces, blurry, motion blur, "
            "watermark, signature, text, "
            "full body, wide shot, dutch angle"
        ),

        # Multiple characters — suppresses body/face duplication artifacts
        "anima_multi_character": (
            "worst quality, low quality, score_1, score_2, score_3, artist name, "
            "bad anatomy, bad hands, extra fingers, missing fingers, fused fingers, "
            "extra limbs, extra faces, cloned face, fused bodies, "
            "watermark, signature, text"
        ),

        # SFW strict — use when source post has borderline or sensitive tags
        "anima_sfw_strict": (
            "worst quality, low quality, score_1, score_2, score_3, artist name, "
            "bad anatomy, bad hands, extra fingers, missing fingers, "
            "nude, nudity, explicit, nsfw, revealing, suggestive, "
            "watermark, signature, text"
        ),

        # Minimal
        "quality_only": "worst quality, low quality",

        # Blank slate — only your extra_negative text is used
        "empty": "",
    }

    def build(self, preset, extra_negative=""):
        base   = self._PRESETS.get(preset, "")
        extras = extra_negative.strip()
        if base and extras:
            return (base + ", " + extras,)
        return (base or extras,)


# ──────────────────────────────────────────────
# Registration
# ──────────────────────────────────────────────

NODE_CLASS_MAPPINGS = {
    "WDanbooru_Injector":       WDanbooru_Injector,
    "WDanbooru_NegativePreset": WDanbooru_NegativePreset,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "WDanbooru_Injector":       "🌸 WDanbooru Injector",
    "WDanbooru_NegativePreset": "🌸 WDanbooru Negative Preset",
}
