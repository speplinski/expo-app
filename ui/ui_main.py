from __future__ import annotations

import asyncio
import logging
import threading
from typing import cast

import cv2
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Footer, Sparkline, Static, Digits

import numpy as np
import numpy.typing as npt

from config.integrated_config import IntegratedConfig
from ui.detections_display import DetectionsDisplay
from ui.display.images_interpolator import ImagesInterpolator
from ui.display.window_display import WindowDisplay
from ui.log_screen import LogPanel
from ui.numbers_row import NumbersRow
from ui.sequences_tree import SequencesTree

FIELD_SIZE = 2

class ExpoApp(App):
    CSS_PATH = 'expo_app.tcss'

    BINDINGS = [
        ('l', 'show_log', 'toggle log')
    ]

    def __init__(self, config: IntegratedConfig, cleanup, debug_mode=False):
        super().__init__()

        self.config = config

        self.debug_mode = debug_mode

        self._cleanup = cleanup

        self._app_logger = logging.getLogger()
        self._app_logger.info(f"UI running on thread: {threading.current_thread().name}")

        self.detections = None
        self.columns_display = None
        self.counters_display = None
        self.epoch_display = None
        self.sequences_tree = None
        self._sequences_tree_updates_buffer = []
        self.playback_statistics_static = None

        self._images_interpolator = ImagesInterpolator(config.timing.target_interpolation_frames)
        self._window_display = WindowDisplay(config.display, config.spade.output_resolution, self)
        self._window_display_task = None

    def compose(self) -> ComposeResult:
        with Horizontal():
            with Vertical(id="detections_panel"):
                with Container(classes="detections_data distances"):
                    yield DetectionsDisplay(self.config, FIELD_SIZE, id="distances")

                with Container(classes="detections_data counters_list"):
                    yield Sparkline([], id="columns_counters")

                    yield NumbersRow(id="base_counters")
                    yield NumbersRow(id="aggregate_counters")
                    yield NumbersRow(id="final_counter")

                with Container(classes="detections_data"):
                    yield Digits('-', id="epoch")

            with Vertical(id="sequences_info"):
                yield SequencesTree("Sequences", id="sequences_info_tree")

                with Container(classes="statistics_container"):
                    yield Static(self._window_display.stats.format_stats(), id="playback_statistics")

        yield Footer()

    def on_mount(self) -> None:
        self.theme = "monokai"

        self.detections: DetectionsDisplay = cast(DetectionsDisplay, self.query_one("#distances"))
        self.detections.styles.width = self.config.depth.depth_grid_display_segments_count.horizontal * FIELD_SIZE * 2
        self.detections.styles.height = self.config.depth.depth_grid_display_segments_count.vertical * FIELD_SIZE * 2

        counters_width = self.config.depth.counters_count * FIELD_SIZE * 2

        self.columns_display: Sparkline = cast(Sparkline, self.query_one("#columns_counters"))
        self.columns_display.styles.width = counters_width

        self.base_counters_display: NumbersRow = cast(NumbersRow, self.query_one("#base_counters"))
        self.base_counters_display.styles.width = counters_width
        self.aggregate_counters_display: NumbersRow = cast(NumbersRow, self.query_one("#aggregate_counters"))
        self.aggregate_counters_display.styles.width = counters_width
        self.final_counter_display: NumbersRow = cast(NumbersRow, self.query_one("#final_counter"))
        self.final_counter_display.styles.width = counters_width

        self.epoch_display = self.query_one("#epoch")

        self.sequences_tree: SequencesTree = cast(SequencesTree, self.query_one("#sequences_info_tree"))

        self.playback_statistics_static: Static = cast(Static, self.query_one("#playback_statistics"))

        while len(self._sequences_tree_updates_buffer) > 0:
            self.sequences_tree.update_sequence(self._sequences_tree_updates_buffer.pop(0))

        self._window_display_task = asyncio.create_task(self._window_display_refresh_process())

    def on_unmount(self):
        self._window_display_task.cancel()

    def update_window_image(self, image: npt.NDArray[np.uint8]):
        self._images_interpolator.update_image(image)

    async def _window_display_refresh_process(self) -> None:
        target_frame_time = 1.0 / self.config.timing.target_interpolation_frames

        while True:
            frame_start = asyncio.get_event_loop().time()

            image = self._images_interpolator.get_intermediate_image()

            if image is not None:
                self._window_display.process_frame(image)

            self.playback_statistics_static.update(self._window_display.stats.format_stats())

            elapsed = asyncio.get_event_loop().time() - frame_start
            sleep_time = max(0.001, target_frame_time - elapsed)

            await asyncio.sleep(sleep_time)

    def action_show_log(self):
        self.push_screen(LogPanel())

    def update_sequence_display(self, sequence_info):
        self._app_logger.info(f"updating: {sequence_info['sequence_name']} (satus: {sequence_info['status'].name})")

        if self.sequences_tree is None:
            self._sequences_tree_updates_buffer.append(sequence_info)
            return

        self.call_from_thread(self.sequences_tree.update_sequence, sequence_info)

    def select_sequence(self, sequence_name):
        self.call_from_thread(self.sequences_tree.select_sequence, sequence_name)

    def update_detections(self, data):
        self.call_from_thread(self._update_detections_display, data)

    def _update_detections_display(self, data):
        self.detections.detection_data = data['distances'].tolist()
        self.detections.mutate_reactive(DetectionsDisplay.detection_data)

        self.columns_display.data = data['columns'].tolist()

    def update_counters(self, values):
        self.call_from_thread(self._update_counters, values)

    def _update_counters(self, values):
        base_values_count = len(values) - 4
        self.base_counters_display.numbers = values[:base_values_count].tolist()
        self.final_counter_display.numbers = [values[base_values_count]]  # Global
        self.aggregate_counters_display.numbers = values[base_values_count+1:].tolist()  # Left, Center, Right

    def update_epoch(self, epoch):
        self.call_from_thread(self._update_epoch, epoch)

    def _update_epoch(self, epoch):
        self.epoch_display.update(f'{epoch}')

    def action_help_quit(self):
        if self.debug_mode:
            self.action_quit()

        cv2.destroyAllWindows()

        super().action_help_quit()

    def action_quit(self) -> None:
        self._window_display_task.cancel()
        self._window_display.cleanup()
        self._cleanup()
        self.exit()
