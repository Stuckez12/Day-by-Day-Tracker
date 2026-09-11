import logging


class LogFormat(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        level_prefix = f"{record.levelname}:"
        padded_prefix = level_prefix.ljust(9)
        message = record.getMessage()
        return f"{padded_prefix} {message}"


log_handler = logging.StreamHandler()
log_handler.setFormatter(LogFormat())
