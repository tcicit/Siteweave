import gettext
import os
from typing import Optional

from core import I18N_DOMAIN

# Centralized i18n helper for the application.
# Call init() early in the application (e.g. app startup) to load translations.

_current_gettext = gettext.gettext

def init(app_root: Optional[str] = None, locale: Optional[str] = None, domain: str = I18N_DOMAIN, locales_dir: str = 'locales'):

    """Initialize translations.

    - app_root: base path to look for the `locales` directory (defaults to cwd)
    - locale: specific locale name (e.g. 'de') or None to use system default
    - domain: gettext domain (default I18N_DOMAIN)
    - locales_dir: relative directory name for locale files
    """
    global _current_gettext
    try:
        base = app_root or os.getcwd()
        locales_path = os.path.join(base, locales_dir)
        if locale:
            trans = gettext.translation(domain, localedir=locales_path, languages=[locale], fallback=True)
        else:
            trans = gettext.translation(domain, localedir=locales_path, fallback=True)
        _current_gettext = trans.gettext
        # also install to builtins for third-party code that expects _()
        trans.install()
    except Exception:
        _current_gettext = gettext.gettext


def _(msg: str) -> str:
    """Return translated string using the currently installed translation."""
    return _current_gettext(msg)
