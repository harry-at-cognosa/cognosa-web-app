from enum import Enum
from typing import Final

class ApiSettingsNamesEnum(Enum):
    api_version = 'app_version'
    db_version = 'db_version'
    webapp_main_color = 'webapp_main_color'


API_SETTINGS_NAMES_LIST: Final = [x.value for x in ApiSettingsNamesEnum]
