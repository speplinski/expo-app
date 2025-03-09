import logging

from rich.logging import RichHandler
from textual.widget import Widget
from textual.widgets import RichLog

class LoggingConsole(RichLog):
    file = False
    console: Widget

    def print(self, content):
        self.write(content)

rich_log_handler = RichHandler(
    console=LoggingConsole(max_lines=80),  # type: ignore
    rich_tracebacks=True,
)

def build_app_logger(log_file, log_level):
    logger = logging.getLogger()

    logger.setLevel(log_level)

    logger.addHandler(rich_log_handler)
    _add_file_handler(logger, log_file)


def _add_file_handler(logger, log_file):
    file_handler = logging.FileHandler(log_file)

    file_formatter = logging.Formatter('%(asctime)s\t%(levelname)s\t%(message)s')
    file_handler.setFormatter(file_formatter)

    logger.addHandler(file_handler)
