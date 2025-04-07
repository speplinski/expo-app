from rich.segment import Segment
from rich.style import Style
from textual.color import Color
from textual.reactive import reactive
from textual.strip import Strip
from textual.widget import Widget

from config.integrated_config import IntegratedConfig
from config.modules_configs.depth_config import DistanceThresholdInM


class DetectionsDisplay(Widget):
    detection_data = reactive(None)

    def __init__(self, config: IntegratedConfig, field_size: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = config
        self.field_size = field_size

    def render_line(self, y: int) -> Strip:
        row_index = y // self.field_size

        if self.detection_data is None or row_index >= len(self.detection_data):
            return Strip.blank(self.size.width)

        segments = [
            Segment(" " * self.field_size * 2, Style.parse(f'on {self._get_field_colour_string(field)}'))
            for field in self.detection_data[row_index]
        ]

        return Strip(segments, len(self.detection_data[row_index]) * self.field_size * 2)

    def _get_field_colour_string(self, field):
        if field == 0:
            return 'black'

        default_distance_thresholds = DistanceThresholdInM()
        min_height = default_distance_thresholds.min
        max_height = default_distance_thresholds.max

        if field < min_height:
            return '#fff5eb'

        elif field > max_height:
            return '#ca0020'

        start_color = Color.parse('#f7fbff')
        end_color = Color.parse('#08306b')

        normalized = (field - min_height) / (max_height - min_height)
        color = Color.blend(start_color, end_color, normalized)

        return color.hex