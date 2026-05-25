# 🌸 WDanbooru Injector — ComfyUI Booru Tag Nodes

<img width="2400" height="1792" alt="full_body,_she&#39;s_holding_a_202605211210 (1)" src="https://github.com/user-attachments/assets/5d8d896f-fde7-4746-954c-6b7c6ce7292b" />

> Fetch booru tags directly inside ComfyUI and inject them into your prompts — by **Lord Winnougan**  
> 🎨 Anima · Danbooru-trained models · AI Art Workflows

---

## 📦 Included Nodes

| Node | Description |
|---|---|
| **🌸 WDanbooru Injector** | Fetch tags from any supported booru by post ID or URL and inject them into your positive prompt |
| **🌸 WDanbooru Negative Preset** | Pre-built negative prompt presets tuned for Anima and Danbooru-trained models |
| **🌸 W-Booru Grabber** | Bulk-fetch an entire artist's tag library from any supported booru and save it as a dataset `.txt` file |

---

## 🚀 Installation

### Option 1 — ComfyUI Manager (Recommended)
Search for **`WDanbooru_Injector`** in ComfyUI Manager and install directly.

### Option 2 — Manual Install

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/Winnougan/WDanbooru_Injector.git
```

Restart ComfyUI. All nodes appear under the **WDanbooru** category.

### Dependencies

```bash
pip install requests
```

---

## 🖥️ Requirements

- [ComfyUI](https://github.com/comfyanonymous/ComfyUI)
- Python 3.10+
- A Gelbooru free account (for Injector and Grabber on Gelbooru posts)
- e621/Danbooru credentials are optional but recommended

---

## 🔑 API Credentials

### Gelbooru (required for all Gelbooru requests)
1. Create a free account at [gelbooru.com](https://gelbooru.com)
2. Go to **My Account → Options → API key**
3. Copy your **User ID** and **API Key**
4. Paste them into the node's `gelbooru_user_id` and `gelbooru_api_key` fields

> **Tip:** Credentials look like `user_id=123456&api_key=abc123...` — the node accepts the raw string or just the values after the `=` sign.

### e621 (optional)
- Add your **username** to the node for polite API access (e621 policy encourages this)
- Add both username **and** API key for higher rate limits
- Get your API key at: e621.net → Account → Manage API Access
- Anonymous access works for public posts but is rate-limited

### Danbooru (optional)
- Username + API key for higher rate limits
- Public posts work without credentials

### All other sites (Konachan, Yande.re, Safebooru, Rule34, etc.)
- No credentials required

---

## 📖 Node Reference & Tutorial

---

### 🌸 WDanbooru Injector

Fetches tags from a booru post and injects them into your positive prompt, formatted correctly for Anima and Danbooru-trained models. Supports 13 sources.

**Supported Sources:**
`gelbooru` · `e621` · `danbooru` · `konachan.net` · `konachan.com` · `yande.re` · `lolibooru` · `safebooru` · `rule34` · `hypnohub` · `atfbooru` · `xbooru` · `manual`

**Required Inputs:**

| Input | Description |
|---|---|
| `source` | Select which booru to fetch from |
| `post_id` | The post ID (plain number) or full post page URL. See format notes below. |
| `inject_mode` | `prepend` — tags go before your prompt. `append` — after. `replace` — replaces your prompt entirely. |
| `quality_prefix` | Prepended quality tags. Default: `masterpiece, best quality, score_7` |
| `safety_tag` | Manually set the rating tag: `safe`, `sensitive`, `questionable`, `explicit`, or `none` |
| `year_tag` | Optionally add a year tag (e.g. `2024`). Use `none` to skip. |
| `include_artist` | Toggle artist tags on/off |
| `include_character` | Toggle character tags on/off |
| `include_copyright` | Toggle copyright/series tags on/off |
| `include_general` | Toggle general descriptive tags on/off |
| `max_general_tags` | Cap the number of general tags (default 40) |

**Optional Inputs:**

| Input | Description |
|---|---|
| `positive_prompt` | Your existing prompt to inject into. Wire from a text node. |
| `manual_tags` | Paste tags manually when source is set to `manual` |
| `count_tag` | Add a character count tag (e.g. `1girl`, `2boys`) |
| `gelbooru_user_id` / `gelbooru_api_key` | Gelbooru API credentials |
| `e621_username` / `e621_api_key` | e621 credentials |
| `danbooru_username` / `danbooru_api_key` | Danbooru credentials |
| `extra_tags` | Additional tags to always append, comma-separated |

**Outputs:**

| Output | Description |
|---|---|
| `positive_prompt` | Your full injected prompt, ready to wire to your encoder |
| `injected_tags_only` | Just the fetched tags, without your base prompt — useful for debugging |

#### Post ID Format Guide

| Source | Accepted formats |
|---|---|
| Gelbooru | `12345678` or `https://gelbooru.com/index.php?page=post&s=view&id=12345678` |
| e621 | `4218495` or `https://e621.net/posts/4218495` |
| Danbooru | `12345` or `https://danbooru.donmai.us/posts/12345` |
| Konachan | `402821` or `https://konachan.net/post/show/402821` |
| Yande.re | `123456` or `https://yande.re/post/show/123456` |
| Others | Plain post ID number |

> ⚠️ **Don't paste direct image URLs** (e.g. `img2.gelbooru.com/images/...`). Those don't contain post IDs. Open the post page in your browser and copy the URL from the address bar.

#### Tag Order (Anima format)
The injector builds prompts in Anima's recommended tag order:
```
[quality] [year] [safety] [count] [character] [copyright] [@artist] [general]
```
Artist tags are automatically prefixed with `@` as required by Anima.

---

### 🌸 WDanbooru Negative Preset

Pre-built negative prompt presets tuned for Anima and other Danbooru-trained models. Saves you from maintaining the same negative string across every workflow.

**Inputs:**

| Input | Description |
|---|---|
| `preset` | Select a preset from the list below |
| `extra_negative` *(optional)* | Additional negative terms to append to the preset |

**Presets:**

| Preset | Best for |
|---|---|
| `anima_default` | General use — quality tags + artist name suppression |
| `anima_detailed` | Adds anatomy and artifact suppression. Good all-rounder. |
| `anima_portrait` | Close-up / portrait generations — suppresses wide shots and face duplication |
| `anima_multi_character` | Multiple characters — suppresses body fusion and clone artifacts |
| `anima_sfw_strict` | Borderline source posts — aggressively suppresses NSFW content |
| `quality_only` | Minimal — just `worst quality, low quality` |
| `empty` | Blank — only your `extra_negative` text is used |

**Output:** `negative_prompt` STRING — wire directly to your CLIP encoder's negative input.

---

### 🌸 W-Booru Grabber

Bulk-fetches ALL posts for an artist from any supported booru and saves them as a prompt dataset `.txt` file in your ComfyUI output folder. One line (or block) per post, formatted as a positive prompt — ready to use as a training dataset or prompt library.

**Supported Sources:** e621 · Gelbooru · Danbooru · Konachan · Yande.re · Safebooru · Rule34.xxx · Lolibooru · Hypnohub · ATFBooru · Xbooru

**Required Inputs:**

| Input | Description |
|---|---|
| `artist_url` | Paste the full artist page URL from any supported booru. e.g. `https://e621.net/posts?tags=whisperfoot` |
| `output_filename` | Name for the output `.txt` file (no extension needed) |
| `quality_prefix` | Quality tags prepended to every prompt line |
| `include_rating` | Include post safety rating (`safe`/`questionable`/`explicit`) in each prompt |
| `max_general_tags` | Max general/descriptive tags per post (default 60) |
| `max_posts` | Max posts to fetch. `0` = fetch all (can be slow for prolific artists) |
| `separator` | How to separate prompts: `blank line`, `---`, `===`, or `single line` |
| `request_delay` | Seconds between API pages (default 0.6). Increase to 1.0+ if you get rate-limited. |

**Optional Inputs:** `gelbooru_user_id`, `gelbooru_api_key`, `e621_username`, `e621_api_key`, `danbooru_username`, `danbooru_api_key`

**Outputs:**

| Output | Description |
|---|---|
| `output_path` | Full path to the saved `.txt` file |
| `status` | Summary: post count, artist name, site, and filename |
| `post_count` | Number of prompts written (INT) |

**Output file location:** `ComfyUI/output/<your_filename>.txt`

> **Tip:** Use `max_posts = 100` for a quick test run before fetching an entire artist's gallery. Set `request_delay` to `1.0` or higher for large artists to avoid rate limiting.

---

## 🔗 Example Workflow

```
WDanbooru Injector
    ← source: gelbooru
    ← post_id: 12345678
    ← gelbooru_user_id / gelbooru_api_key
    ← inject_mode: prepend
    ← positive_prompt (from your text node)
    ↓ positive_prompt (injected)

WDanbooru Negative Preset
    ← preset: anima_detailed
    ↓ negative_prompt

CLIP Text Encoder (positive) ← positive_prompt
CLIP Text Encoder (negative) ← negative_prompt

KSampler / Sampler
```

---

## ❤️ Support

If these nodes save you time, consider supporting on Patreon — exclusive workflows, nodes, and LLM setups drop there first.

[![Support on Patreon](https://img.shields.io/badge/Patreon-Support%20Winnougan-F96854?style=for-the-badge&logo=patreon&logoColor=white)](https://www.patreon.com/c/u5867556)
[![Support on Ko-fi](https://img.shields.io/badge/Ko--fi-Support%20Winnougan-FF5E5B?style=for-the-badge&logo=kofi&logoColor=white)](https://ko-fi.com/Winnougan)
---

## 📄 License

Apache 2.0 — use it, build on it, don't be lame about it.
