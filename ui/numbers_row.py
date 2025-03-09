from textual.containers import Horizontal
from textual.reactive import reactive
from textual.widgets import Static


class NumbersRow(Static):
    numbers = reactive(None)

    def compose(self):
        yield Horizontal(id="number-row")

    def watch_numbers(self, numbers: list):
        if numbers is None:
            return

        row = self.query_one("#number-row")
        row.remove_children()

        for number in numbers:
            row.mount(Static(f'{number}', classes="number-cell"))