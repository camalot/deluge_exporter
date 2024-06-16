import glob
import inspect
import json
import os
import sys
import traceback
import typing

from . import utils
from libs.enums.loglevel import LogLevel


class Settings:
    APP_VERSION = "1.0.0-snapshot"

    def __init__(self):
        self._module = os.path.basename(__file__)[:-3]
        self._class = self.__class__.__name__

        self.name = None
        self.version = None

        self.log_level = utils.dict_get(os.environ, 'DE_LOG_LEVEL', default_value = 'DEBUG')

    def to_dict(self):
        return self.__dict__

    def get(self, name, default_value=None) -> typing.Any:
        return utils.dict_get(self.to_dict(), name, default_value)
