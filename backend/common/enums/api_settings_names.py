from enum import Enum
from typing import Final

class ApiSettingsNamesEnum(Enum):
    api_version = 'app_version'
    db_version = 'db_version'
    webapp_main_color = 'webapp_main_color'
    index_page = 'index_page'
    gvdbs_def_retr_params = 'gvdbs_def_retr_params'
    # Feature 199: 'TRUE' hides the Retrieval Parameters control on the Queries page
    suppress_retrieval_parameters = 'suppress_retrieval_parameters'
    # Chat: how many earlier turns are resent to the LLM (a window, not a cap). Default 6.
    chat_history_turns = 'chat_history_turns'
    # free-form long string reserved for future use
    future = 'future'


API_SETTINGS_NAMES_LIST: Final = [x.value for x in ApiSettingsNamesEnum]
