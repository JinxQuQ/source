import os
from common.setting import ConfigHandler
from utils.otherUtils.get_os_sep import get_os_sep
from utils.otherUtils.get_conf_data import get_mirror_url
from utils.logUtils.logControl import INFO
os.system("pip3 install chardet")
import chardet


__all__ = [
    "os",
    "ConfigHandler",
    "get_os_sep",
    "get_mirror_url",
    "INFO",
    "chardet"
]
