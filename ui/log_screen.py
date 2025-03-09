from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import ModalScreen

from logger.build_logger import rich_log_handler


class LogPanel(ModalScreen):
    BINDINGS = [
        ('l', 'app.pop_screen()', 'toggle log')
    ]

    def compose(self) -> ComposeResult:
        with Container(classes="log_modal"):
            yield rich_log_handler.console