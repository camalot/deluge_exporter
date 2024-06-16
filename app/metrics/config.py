import os
import codecs
import inspect
import json
import traceback
import yaml

from libs import utils
from libs.logger import Log
from libs.enums.loglevel import LogLevel
from libs.settings import Settings

class DelugeMetricsConfig:
    def __init__(self, file: str):
        _method = inspect.stack()[0][3]
        self._class = self.__class__.__name__
        self._module = os.path.basename(__file__)[:-3]
        self.settings = Settings()
        log_level = LogLevel[self.settings.log_level.upper()]
        if not log_level:
            log_level = LogLevel.DEBUG
        self.log = Log(log_level)

        # set defaults for config from environment variables if they exist
        self.metrics = {
            "port": int(utils.dict_get(os.environ, "DE_METRICS_PORT", "9354")),
            "pollingInterval": int(utils.dict_get(os.environ, "DE_CONFIG_METRICS_POLLING_INTERVAL", "60")),
        }
        
        deluge_config_path = utils.dict_get(os.environ, "DE_DELUGE_CONFIG_PATH", "/config")
        deluge_rpc_port = None
        deluge_rpc_user = None
        deluge_rpc_password = None

        with open(os.path.join(deluge_config_path, 'core.conf')) as f:
            while f.read(1) != '}':
                pass
            deluge_rpc_port = json.load(f)['daemon_port']
            with open(os.path.join(deluge_config_path, 'auth')) as f:
                deluge_rpc_user, deluge_rpc_password = f.readline().strip().split(':')[:2]

        self.deluge = {
            "host": utils.dict_get(os.environ, "DE_DELUGE_HOST", "localhost"),
            "configPath": deluge_config_path,
            "rpcPort": int(utils.dict_get(os.environ, "DE_DELUGE_RPC_PORT", deluge_rpc_port)),
            "rpcUser": deluge_rpc_user,
            "rpcPassword": deluge_rpc_password,
        }

        # load config from file
        try:
            # check if file exists
            if os.path.exists(file):
                self.log.debug(f"{self._module}.{self._class}.{_method}", f"Loading config from {file}")
                with codecs.open(file, encoding="utf-8-sig", mode="r") as f:
                    settings = yaml.safe_load(f)
                    self.__dict__.update(settings)
        except yaml.YAMLError as exc:
            self.log.error(f"{self._module}.{self._class}.{_method}", str(exc), traceback.format_exc())
