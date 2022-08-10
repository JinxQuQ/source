

from utils.other_tools.models import Config
from utils.read_files_tools.yaml_control import GetYamlData
from common.setting import ConfigHandler

_data = GetYamlData(ConfigHandler.config_path).get_yaml_data()
config = Config(**_data)
