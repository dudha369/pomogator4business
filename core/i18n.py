from core.locales.en import EN
from core.locales.ru import RU
from core.locales.uk import UK

LOCALES = {"ru": RU, "en": EN, "uk": UK}
DEFAULT_LOCALE = "ru"
LANGUAGE_NAMES = {"ru": "Русский", "en": "English", "uk": "Українська"}


def t(key, locale=DEFAULT_LOCALE, **kwargs):
    strings = LOCALES.get(locale, LOCALES[DEFAULT_LOCALE])
    template = strings.get(key) or LOCALES[DEFAULT_LOCALE].get(key) or key

    if not kwargs:
        return template

    try:
        return template.format(**kwargs)
    except (KeyError, IndexError):
        return template
