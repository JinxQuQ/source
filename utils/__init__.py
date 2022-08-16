from utils.other_tools.models import Config
from utils.read_files_tools.yaml_control import GetYamlData
from common.setting import ConfigHandler

_data = GetYamlData(ConfigHandler.config_path).get_yaml_data()
config = Config(**_data)


_cache_config = {}


class CacheHandler:
    @staticmethod
    def get_cache(cache_data):
        return _cache_config[cache_data]

    @staticmethod
    def update_cache(*, cache_name, value):
        _cache_config[cache_name] = value


if __name__ == '__main__':
    CacheHandler.update_cache(cache_name="yushaoqi", value="1233")
    print(_cache_config)
