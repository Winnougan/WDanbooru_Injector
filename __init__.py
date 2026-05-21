from .wdanbooru_injector import (
    NODE_CLASS_MAPPINGS as INJECTOR_MAPPINGS,
    NODE_DISPLAY_NAME_MAPPINGS as INJECTOR_DISPLAY,
)
from .wdanbooru_grabber import (
    NODE_CLASS_MAPPINGS as GRABBER_MAPPINGS,
    NODE_DISPLAY_NAME_MAPPINGS as GRABBER_DISPLAY,
)

NODE_CLASS_MAPPINGS = {**INJECTOR_MAPPINGS, **GRABBER_MAPPINGS}
NODE_DISPLAY_NAME_MAPPINGS = {**INJECTOR_DISPLAY, **GRABBER_DISPLAY}

def _print_banner():
    PATREON_URL = "https://www.patreon.com/c/u5867556"
    LINK  = f"\033]8;;{PATREON_URL}\033\\{PATREON_URL}\033]8;;\033\\"
    PURP  = "\033[38;2;192;132;252m"
    LPURP = "\033[38;2;233;213;255m"
    DIM   = "\033[38;2;109;40;217m"
    RESET = "\033[0m"
    BOLD  = "\033[1m"
    banner = (
        f"\n{PURP}{'='*62}{RESET}\n"
        f"{PURP}  \U0001f338\U0001f338\U0001f338  {BOLD}{LPURP}W - B O O R U   I N J E C T O R{RESET}{PURP}  \U0001f338\U0001f338\U0001f338{RESET}\n"
        f"{DIM}{'='*62}{RESET}\n"
        f"{PURP}  \U0001f4aa Created by Lord Winnougan{RESET}\n"
        f"{PURP}  \U0001f3a8 AI Art \u00b7 Tag Injection \u00b7 Booru Scraping{RESET}\n"
        f"{LPURP}  \u2b50 Support the creator on Patreon:{RESET}\n"
        f"{LPURP}  \U0001f449 {LINK}{RESET}\n"
        f"{DIM}{'-'*62}{RESET}\n"
        f"{PURP}  \u2728 Nodes loaded:{RESET}\n"
        f"{DIM}     W-Booru Injector \u00b7 W-Booru Negative Preset \u00b7 W-Booru Grabber\n"
        f"     Sources: Gelbooru \u00b7 e621 \u00b7 Konachan.net \u00b7 Konachan.com \u00b7 Manual{RESET}\n"
        f"{PURP}{'='*62}{RESET}\n"
    )
    try:
        print(banner)
    except UnicodeEncodeError:
        print("\n[W-Booru Injector] Loaded — https://www.patreon.com/c/u5867556\n")

_print_banner()

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
