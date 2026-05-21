"""
WDanbooru_Grabber — ComfyUI Custom Node
Fetches ALL posts for an artist from e621, Gelbooru, or Konachan
and writes them as a prompt dataset text file to the ComfyUI output folder.

Each post becomes one line (or block) of tags formatted as a positive prompt,
separated by a blank line — ready for use as a training dataset or prompt library.
"""

import os
import re
import time
import requests
import folder_paths
import logging

log = logging.getLogger("Winnougan")
NODE_NAME = "WDanbooru Grabber"

DEFAULT_QUALITY = "masterpiece, best quality, score_7"

# ── URL / tag parsing ─────────────────────────────────────────────────────────

def _parse_artist_url(raw: str) -> tuple[str, str]:
    """
    Parse a booru artist URL or plain tag and return (site, artist_tag).
    
    Accepted formats:
      https://e621.net/posts?tags=whisperfoot           → ("e621", "whisperfoot")
      https://e621.net/posts?tags=whisperfoot+rating:s   → ("e621", "whisperfoot rating:s")
      https://gelbooru.com/index.php?...&tags=artist:foo → ("gelbooru", "foo")
      https://konachan.net/post?tags=whisperfoot         → ("konachan.net", "whisperfoot")
      https://konachan.com/post?tags=whisperfoot         → ("konachan.com", "whisperfoot")
      whisperfoot                                         → guessed from context
    """
    raw = raw.strip()

    # e621
    if "e621.net" in raw:
        m = re.search(r"[?&]tags=([^&]+)", raw)
        tag = m.group(1).replace("+", " ").replace("%20", " ").strip() if m else raw
        # Strip artist: prefix if present
        tag = re.sub(r"\bartist:", "", tag).strip()
        return ("e621", tag)

    # Gelbooru
    if "gelbooru.com" in raw:
        m = re.search(r"[?&]tags=([^&]+)", raw)
        tag = m.group(1).replace("+", " ").replace("%20", " ").strip() if m else raw
        tag = re.sub(r"\bartist:", "", tag).strip()
        return ("gelbooru", tag)

    # Danbooru
    if "danbooru.donmai.us" in raw:
        m = re.search(r"[?&]tags=([^&]+)", raw)
        tag = m.group(1).replace("+", " ").replace("%20", " ").strip() if m else raw
        tag = re.sub(r"\bartist:", "", tag).strip()
        return ("danbooru", tag)

    # Konachan
    if "konachan.com" in raw:
        m = re.search(r"[?&]tags=([^&]+)", raw)
        tag = m.group(1).replace("+", " ").replace("%20", " ").strip() if m else raw
        return ("konachan.com", tag)
    if "konachan.net" in raw:
        m = re.search(r"[?&]tags=([^&]+)", raw)
        tag = m.group(1).replace("+", " ").replace("%20", " ").strip() if m else raw
        return ("konachan.net", tag)

    # Yande.re
    if "yande.re" in raw:
        m = re.search(r"[?&]tags=([^&]+)", raw)
        tag = m.group(1).replace("+", " ").replace("%20", " ").strip() if m else raw
        return ("yande.re", tag)

    # Safebooru
    if "safebooru.org" in raw:
        m = re.search(r"[?&]tags=([^&]+)", raw)
        tag = m.group(1).replace("+", " ").replace("%20", " ").strip() if m else raw
        return ("safebooru", tag)

    # Rule34.xxx
    if "rule34.xxx" in raw:
        m = re.search(r"[?&]tags=([^&]+)", raw)
        tag = m.group(1).replace("+", " ").replace("%20", " ").strip() if m else raw
        return ("rule34", tag)

    # Lolibooru
    if "lolibooru.moe" in raw:
        m = re.search(r"[?&]tags=([^&]+)", raw)
        tag = m.group(1).replace("+", " ").replace("%20", " ").strip() if m else raw
        return ("lolibooru", tag)

    # Hypnohub
    if "hypnohub.net" in raw:
        m = re.search(r"[?&]tags=([^&]+)", raw)
        tag = m.group(1).replace("+", " ").replace("%20", " ").strip() if m else raw
        return ("hypnohub", tag)

    # ATFBooru
    if "allthefallen.moe" in raw:
        m = re.search(r"[?&]tags=([^&]+)", raw)
        tag = m.group(1).replace("+", " ").replace("%20", " ").strip() if m else raw
        return ("atfbooru", tag)

    # Xbooru
    if "xbooru.com" in raw:
        m = re.search(r"[?&]tags=([^&]+)", raw)
        tag = m.group(1).replace("+", " ").replace("%20", " ").strip() if m else raw
        return ("xbooru", tag)

    # Plain tag — can't auto-detect site
    raise ValueError(
        f"Cannot determine site from '{raw}'.\n"
        "Paste the full artist page URL from any supported booru.\n"
        "Supported: e621, Danbooru, Gelbooru, Konachan, Yande.re, Safebooru,\n"
        "           Rule34.xxx, Lolibooru, Hypnohub, ATFBooru, Xbooru\n"
        "Example: https://e621.net/posts?tags=whisperfoot"
    )

def _fmt(tag: str) -> str:
    return tag.replace("_", " ").strip()


# ── Fetchers ──────────────────────────────────────────────────────────────────

def _fetch_e621_all(artist_tag: str, username: str, api_key: str,
                    max_posts: int, delay: float) -> list[dict]:
    """Fetch all posts for an artist from e621, paginated."""
    u = username.strip()
    k = api_key.strip()
    ua = f"WBooru-Grabber/2.0 (by {u})" if u else "WBooru-Grabber/2.0 (ComfyUI custom node)"
    params_auth = {}
    if u and k:
        params_auth = {"login": u, "api_key": k}

    posts = []
    page  = 1
    limit = 320

    while True:
        params = {"tags": artist_tag, "limit": limit, "page": page, **params_auth}
        resp   = requests.get(
            "https://e621.net/posts.json",
            headers={"User-Agent": ua},
            params=params,
            timeout=15,
        )
        if resp.status_code == 401:
            raise ValueError(
                "e621 rejected credentials (401). "
                "Leave both fields empty for anonymous access, or fill in both username AND api_key."
            )
        resp.raise_for_status()
        batch = resp.json().get("posts", [])
        if not batch:
            break

        posts.extend(batch)
        log.info(f"[{NODE_NAME}] e621 page {page}: {len(batch)} posts (total so far: {len(posts)})")

        if max_posts > 0 and len(posts) >= max_posts:
            posts = posts[:max_posts]
            break
        if len(batch) < limit:
            break

        page += 1
        time.sleep(delay)

    return posts


def _fetch_gelbooru_all(artist_tag: str, user_id: str, api_key: str,
                         max_posts: int, delay: float) -> list[dict]:
    """Fetch all posts for an artist from Gelbooru, paginated."""
    uid, key = user_id.strip(), api_key.strip()
    if not uid or not key:
        raise ValueError(
            "Gelbooru requires API credentials. "
            "Fill in gelbooru_user_id and gelbooru_api_key."
        )
    uid = uid.split("=")[-1].strip()
    key = key.split("=")[-1].strip()

    posts = []
    pid   = 0
    limit = 100

    while True:
        url = (
            f"https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1"
            f"&limit={limit}&pid={pid}&tags={requests.utils.quote(artist_tag)}"
            f"&user_id={uid}&api_key={key}"
        )
        resp = requests.get(url, timeout=15)
        if resp.status_code == 401:
            raise ValueError("Gelbooru rejected credentials (401).")
        resp.raise_for_status()

        data  = resp.json()
        batch = data.get("post", [])
        if isinstance(batch, dict):
            batch = [batch]
        if not batch:
            break

        posts.extend(batch)
        log.info(f"[{NODE_NAME}] Gelbooru pid={pid}: {len(batch)} posts (total: {len(posts)})")

        if max_posts > 0 and len(posts) >= max_posts:
            posts = posts[:max_posts]
            break
        if len(batch) < limit:
            break

        pid += 1
        time.sleep(delay)

    return posts


def _fetch_danbooru_all(artist_tag: str, username: str, api_key: str,
                         max_posts: int, delay: float) -> list[dict]:
    """Fetch all posts for an artist from Danbooru, paginated."""
    u, k = username.strip(), api_key.strip()
    posts = []
    page  = 1
    limit = 200

    while True:
        params = {"tags": artist_tag, "limit": limit, "page": page}
        if u and k:
            params["login"]   = u
            params["api_key"] = k
        resp = requests.get(
            "https://danbooru.donmai.us/posts.json",
            headers={"User-Agent": "WBooru-Grabber/2.0 (ComfyUI custom node)"},
            params=params, timeout=15,
        )
        if resp.status_code == 401:
            raise ValueError("Danbooru rejected credentials (401). Check username and API key.")
        resp.raise_for_status()
        batch = resp.json()
        if not isinstance(batch, list) or not batch:
            break
        posts.extend(batch)
        log.info(f"[{NODE_NAME}] Danbooru page {page}: {len(batch)} posts (total: {len(posts)})")
        if max_posts > 0 and len(posts) >= max_posts:
            posts = posts[:max_posts]; break
        if len(batch) < limit:
            break
        page += 1
        time.sleep(delay)
    return posts


def _fetch_dapi_all(artist_tag: str, base_url: str, site_label: str,
                     max_posts: int, delay: float) -> list[dict]:
    """Generic paginated fetch for Danbooru-compatible dapi sites
    (Safebooru, Rule34, Hypnohub, ATFBooru, Xbooru, etc.)."""
    posts = []
    pid   = 0
    limit = 100

    while True:
        params = {
            "page": "dapi", "s": "post", "q": "index", "json": "1",
            "tags": artist_tag, "pid": pid, "limit": limit,
        }
        resp = requests.get(
            base_url,
            headers={"User-Agent": "WBooru-Grabber/2.0 (ComfyUI custom node)"},
            params=params, timeout=15,
        )
        resp.raise_for_status()
        data  = resp.json()
        batch = data if isinstance(data, list) else data.get("post", [])
        if isinstance(batch, dict):
            batch = [batch]
        if not batch:
            break
        posts.extend(batch)
        log.info(f"[{NODE_NAME}] {site_label} pid={pid}: {len(batch)} posts (total: {len(posts)})")
        if max_posts > 0 and len(posts) >= max_posts:
            posts = posts[:max_posts]; break
        if len(batch) < limit:
            break
        pid += 1
        time.sleep(delay)
    return posts


def _fetch_moebooru_all(artist_tag: str, domain: str, site_label: str,
                         max_posts: int, delay: float) -> list[dict]:
    """Generic paginated fetch for moebooru-style sites (Yande.re, Lolibooru, Konachan)."""
    posts = []
    page  = 1
    limit = 100

    while True:
        url  = f"https://{domain}/post.json"
        resp = requests.get(
            url,
            headers={"User-Agent": "WBooru-Grabber/2.0 (ComfyUI custom node)"},
            params={"tags": artist_tag, "page": page, "limit": limit},
            timeout=15,
        )
        resp.raise_for_status()
        batch = resp.json()
        if not isinstance(batch, list) or not batch:
            break
        posts.extend(batch)
        log.info(f"[{NODE_NAME}] {site_label} page {page}: {len(batch)} posts (total: {len(posts)})")
        if max_posts > 0 and len(posts) >= max_posts:
            posts = posts[:max_posts]; break
        if len(batch) < limit:
            break
        page += 1
        time.sleep(delay)
    return posts


def _fetch_konachan_all(artist_tag: str, site: str,
                         max_posts: int, delay: float) -> list[dict]:
    """Kept for back-compat — delegates to _fetch_moebooru_all."""
    domain = "konachan.net" if site == "konachan.net" else "konachan.com"
    return _fetch_moebooru_all(artist_tag, domain, site, max_posts, delay)


# ── Tag formatting ────────────────────────────────────────────────────────────

RATING_MAP = {
    "s": "safe",
    "q": "questionable",
    "e": "explicit",
    "g": "safe",       # e621 uses g for general/safe
}

def _build_prompt_from_e621(post: dict, quality: str, include_rating: bool,
                              max_general: int) -> str:
    tags   = post.get("tags", {})
    artist = [_fmt(t) for t in tags.get("artist", [])]
    char   = [_fmt(t) for t in tags.get("character", [])]
    copy_  = [_fmt(t) for t in tags.get("copyright", [])]
    species= [_fmt(t) for t in tags.get("species", [])]
    gen    = [_fmt(t) for t in tags.get("general", [])]
    meta   = [_fmt(t) for t in tags.get("meta", [])]
    rating = RATING_MAP.get(post.get("rating", "s"), "safe")

    parts = []
    if quality:
        parts.append(quality.strip().rstrip(","))
    if include_rating:
        parts.append(rating)
    parts.extend(char)
    parts.extend(copy_)
    parts.extend([f"@{a}" for a in artist])
    # species + general + meta combined, capped
    combined = species + gen + meta
    parts.extend(combined[:max_general])
    return ", ".join(p for p in parts if p)


def _build_prompt_from_danbooru(post: dict, quality: str, include_rating: bool,
                                  max_general: int) -> str:
    raw    = post.get("tag_string", "")
    tags   = [_fmt(t) for t in raw.split() if t]
    rating = RATING_MAP.get(post.get("rating", "s"), "safe")
    # Danbooru has separate tag_string_artist etc.
    artist_raw = post.get("tag_string_artist", "")
    char_raw   = post.get("tag_string_character", "")
    artists    = [_fmt(t) for t in artist_raw.split() if t]
    chars      = [_fmt(t) for t in char_raw.split() if t]
    # General = everything minus artist / character / copyright
    skip = set(artist_raw.split()) | set(char_raw.split()) | set(post.get("tag_string_copyright","").split())
    gen  = [_fmt(t) for t in raw.split() if t and t not in skip]

    parts = []
    if quality:
        parts.append(quality.strip().rstrip(","))
    if include_rating:
        parts.append(rating)
    parts.extend(chars)
    parts.extend([f"@{a}" for a in artists])
    parts.extend(gen[:max_general])
    return ", ".join(p for p in parts if p)


def _build_prompt_from_flat(post: dict, quality: str, include_rating: bool,
                              max_general: int) -> str:
    """Works for any site that returns tags as a space-separated string field."""
    raw    = post.get("tags", "")
    tags   = [_fmt(t) for t in (raw if isinstance(raw, list) else raw.split()) if t]
    rating = RATING_MAP.get(post.get("rating", "s"), "safe")

    parts = []
    if quality:
        parts.append(quality.strip().rstrip(","))
    if include_rating:
        parts.append(rating)
    parts.extend(tags[:max_general])
    return ", ".join(p for p in parts if p)



def _build_prompt_from_gelbooru(post: dict, quality: str, include_rating: bool,
                                  max_general: int) -> str:
    """Kept for back-compat — delegates to _build_prompt_from_flat."""
    return _build_prompt_from_flat(post, quality, include_rating, max_general)


def _build_prompt_from_konachan(post: dict, quality: str, include_rating: bool,
                                  max_general: int) -> str:
    tags   = [_fmt(t) for t in post.get("tags", "").split() if t]
    author = post.get("author", "")
    rating = RATING_MAP.get(post.get("rating", "s"), "safe")

    parts = []
    if quality:
        parts.append(quality.strip().rstrip(","))
    if include_rating:
        parts.append(rating)
    if author:
        parts.append(f"@{_fmt(author)}")
    parts.extend(tags[:max_general])
    return ", ".join(p for p in parts if p)


# ── Node ──────────────────────────────────────────────────────────────────────

class WDanbooru_Grabber:
    """
    Grabs all posts for an artist from e621, Gelbooru, or Konachan
    and saves them as a prompt dataset text file.
    """

    CATEGORY = "WDanbooru"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "artist_url": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "tooltip": (
                        "Paste the full artist page URL from any supported booru: "
                        "e621, Danbooru, Gelbooru, Konachan, Yande.re, Safebooru, "
                        "Rule34.xxx, Lolibooru, Hypnohub, ATFBooru, Xbooru. "
                        "e.g. https://e621.net/posts?tags=whisperfoot"
                    ),
                }),
                "output_filename": ("STRING", {
                    "default": "artist_dataset",
                    "multiline": False,
                    "tooltip": "Name for the output .txt file (no extension needed).",
                }),
                "quality_prefix": ("STRING", {
                    "default": DEFAULT_QUALITY,
                    "multiline": False,
                }),
                "include_rating": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Include the post's safety rating (safe/questionable/explicit) in each prompt.",
                }),
                "max_general_tags": ("INT", {
                    "default": 60, "min": 1, "max": 300, "step": 1,
                    "tooltip": "Max number of general/descriptive tags per post.",
                }),
                "max_posts": ("INT", {
                    "default": 0, "min": 0, "max": 10000, "step": 10,
                    "tooltip": "Max posts to fetch. 0 = fetch all (may be slow for prolific artists).",
                }),
                "separator": (["blank line", "---", "===", "single line"], {
                    "default": "blank line",
                    "tooltip": "How to separate prompts in the output file.",
                }),
                "request_delay": ("FLOAT", {
                    "default": 0.6, "min": 0.1, "max": 5.0, "step": 0.1,
                    "tooltip": "Seconds to wait between API pages. Increase if you get rate-limited.",
                }),
            },
            "optional": {
                "gelbooru_user_id": ("STRING", {"default": ""}),
                "gelbooru_api_key": ("STRING", {"default": ""}),
                "e621_username":    ("STRING", {"default": "",
                    "tooltip": "Your e621 username. Optional for public posts."}),
                "e621_api_key":     ("STRING", {"default": "",
                    "tooltip": "Your e621 API key. Optional, increases rate limits."}),
                "danbooru_username": ("STRING", {"default": "",
                    "tooltip": "Your Danbooru username. Optional for public posts."}),
                "danbooru_api_key":  ("STRING", {"default": "",
                    "tooltip": "Your Danbooru API key. Optional, increases rate limits."}),
            },
        }

    RETURN_TYPES  = ("STRING", "STRING", "INT")
    RETURN_NAMES  = ("output_path", "status", "post_count")
    FUNCTION      = "grab"
    OUTPUT_NODE   = True

    def grab(
        self,
        artist_url,
        output_filename,
        quality_prefix,
        include_rating,
        max_general_tags,
        max_posts,
        separator,
        request_delay,
        gelbooru_user_id="",
        gelbooru_api_key="",
        e621_username="",
        e621_api_key="",
        danbooru_username="",
        danbooru_api_key="",
    ):
        if not artist_url.strip():
            return ("", "Error: paste an artist URL first.", 0)

        # ── Parse URL ─────────────────────────────────────────────────────────
        try:
            site, artist_tag = _parse_artist_url(artist_url)
        except ValueError as e:
            return ("", str(e), 0)

        log.info(f"[{NODE_NAME}] Grabbing '{artist_tag}' from {site} …")

        # ── Fetch all posts ───────────────────────────────────────────────────
        _DAPI_SITES = {
            "safebooru": ("https://safebooru.org/index.php",          "Safebooru"),
            "rule34":    ("https://api.rule34.xxx/index.php",         "Rule34.xxx"),
            "hypnohub":  ("https://hypnohub.net/index.php",          "Hypnohub"),
            "atfbooru":  ("https://booru.allthefallen.moe/index.php", "ATFBooru"),
            "xbooru":    ("https://xbooru.com/index.php",             "Xbooru"),
        }
        _MOEBOORU_SITES = {
            "yande.re":    ("yande.re",    "Yande.re"),
            "lolibooru":   ("lolibooru.moe", "Lolibooru"),
            "konachan.net":("konachan.net","Konachan.net"),
            "konachan.com":("konachan.com","Konachan.com"),
        }

        try:
            if site == "e621":
                raw_posts = _fetch_e621_all(
                    artist_tag, e621_username, e621_api_key, max_posts, request_delay
                )
            elif site == "danbooru":
                raw_posts = _fetch_danbooru_all(
                    artist_tag, danbooru_username, danbooru_api_key, max_posts, request_delay
                )
            elif site == "gelbooru":
                raw_posts = _fetch_gelbooru_all(
                    artist_tag, gelbooru_user_id, gelbooru_api_key, max_posts, request_delay
                )
            elif site in _DAPI_SITES:
                base_url, label = _DAPI_SITES[site]
                raw_posts = _fetch_dapi_all(artist_tag, base_url, label, max_posts, request_delay)
            elif site in _MOEBOORU_SITES:
                domain, label = _MOEBOORU_SITES[site]
                raw_posts = _fetch_moebooru_all(artist_tag, domain, label, max_posts, request_delay)
            else:
                return ("", f"Unsupported site: {site}", 0)
        except Exception as e:
            return ("", f"Fetch error: {e}", 0)

        if not raw_posts:
            return ("", f"No posts found for '{artist_tag}' on {site}.", 0)

        # ── Build prompt lines ────────────────────────────────────────────────
        _FLAT_SITES = {"gelbooru", "safebooru", "rule34", "hypnohub", "atfbooru", "xbooru"}
        _MOEBOORU_LIKE = {"konachan.net", "konachan.com", "yande.re", "lolibooru"}

        prompts = []
        for post in raw_posts:
            try:
                if site == "e621":
                    line = _build_prompt_from_e621(post, quality_prefix, include_rating, max_general_tags)
                elif site == "danbooru":
                    line = _build_prompt_from_danbooru(post, quality_prefix, include_rating, max_general_tags)
                elif site in _FLAT_SITES:
                    line = _build_prompt_from_flat(post, quality_prefix, include_rating, max_general_tags)
                elif site in _MOEBOORU_LIKE:
                    line = _build_prompt_from_konachan(post, quality_prefix, include_rating, max_general_tags)
                else:
                    line = _build_prompt_from_flat(post, quality_prefix, include_rating, max_general_tags)
                if line.strip():
                    prompts.append(line)
            except Exception as e:
                log.warning(f"[{NODE_NAME}] Skipped post {post.get('id', '?')}: {e}")

        # ── Separator ─────────────────────────────────────────────────────────
        sep_map = {
            "blank line":  "\n\n",
            "---":         "\n---\n",
            "===":         "\n===\n",
            "single line": "\n",
        }
        sep = sep_map.get(separator, "\n\n")
        content = sep.join(prompts)

        # ── Write file ────────────────────────────────────────────────────────
        out_dir  = folder_paths.get_output_directory()
        filename = output_filename.strip().rstrip(".txt") + ".txt"
        # Sanitise filename
        filename = re.sub(r'[<>:"/\\|?*]', "_", filename)
        out_path = os.path.join(out_dir, filename)

        try:
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            return ("", f"Write error: {e}", 0)

        status = (
            f"✓ {len(prompts)} prompts from '{artist_tag}' ({site}) "
            f"→ {filename}"
        )
        log.info(f"[{NODE_NAME}] {status}")
        return (out_path, status, len(prompts))


NODE_CLASS_MAPPINGS = {
    "WDanbooru_Grabber": WDanbooru_Grabber,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "WDanbooru_Grabber": "🌸 W-Booru Grabber",
}
