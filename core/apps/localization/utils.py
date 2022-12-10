import gettext

from core.apps.localization.services import LocalizationService
from core.common.config import config


def translate(message: str) -> str:
    language = LocalizationService.translate_language
    return gettext.translation(
        'base', localedir=config.LOCALE_DIR, languages=[language],
    ).gettext(message)
