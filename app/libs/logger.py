import sys
import typing

from libs.enums.loglevel import LogLevel
# from libs.mongodb.logs import LogsDatabase
from libs.colors import Colors


class Log:
    def __init__(self, minimumLogLevel: LogLevel = LogLevel.DEBUG):
        # self.logs_db = LogsDatabase()
        self.minimum_log_level = minimumLogLevel

    def __write(
        self,
        level: LogLevel,
        method: str,
        message: str,
        stackTrace: typing.Optional[str] = None,
        file: typing.IO = sys.stdout,
    ):
        color = Colors.get_color(level)
        m_level = Colors.colorize(color, f"[{level.name}]", bold=True)
        m_method = Colors.colorize(Colors.HEADER, f"[{method}]", bold=False)
        m_message = f"{Colors.colorize(color, message)}"
        str_out = f"{m_level} {m_method} {m_message}"
        print(str_out, file=file)
        if stackTrace:
            print(Colors.colorize(color, stackTrace), file=file)

        # if level >= self.minimum_log_level:
        #     self.logs_db.insert_log(guildId=guildId, level=level, method=method, message=message, stackTrace=stackTrace)

    def debug(self, method: str, message: str, stackTrace: typing.Optional[str] = None):
        self.__write(
            level=LogLevel.DEBUG,
            method=method,
            message=message,
            stackTrace=stackTrace,
            file=sys.stdout,
        )

    def info(self, method: str, message: str, stackTrace: typing.Optional[str] = None):
        self.__write(
            level=LogLevel.INFO,
            method=method,
            message=message,
            stackTrace=stackTrace,
            file=sys.stdout,
        )

    def warn(self, method: str, message: str, stackTrace: typing.Optional[str] = None):
        self.__write(
            level=LogLevel.WARNING,
            method=method,
            message=message,
            stackTrace=stackTrace,
            file=sys.stdout,
        )

    def error(self, method: str, message: str, stackTrace: typing.Optional[str] = None):
        self.__write(
            level=LogLevel.ERROR,
            method=method,
            message=message,
            stackTrace=stackTrace,
            file=sys.stderr,
        )

    def fatal(self, method: str, message: str, stackTrace: typing.Optional[str] = None):
        self.__write(
            level=LogLevel.FATAL,
            method=method,
            message=message,
            stackTrace=stackTrace,
            file=sys.stderr,
        )
