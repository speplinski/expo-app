import logging
import threading

import numpy as np

from reactivex import Subject
from reactivex.scheduler import NewThreadScheduler, EventLoopScheduler

from reactivex import operators as ops

from config.integrated_config import IntegratedConfig
from movement_detector.movement_detector import build_detection_counters_stream, build_detection_counters_updates_stream
from sequences_manager.sequences_manager import SequencesManager
from spade.spade_adapter import SpadeAdapter
from ui.ui_main import ExpoApp


class MainPipeline:
    def __init__(self, config: IntegratedConfig):
        self.config = config

        self.logger = logging.getLogger()

        self.sequence_switcher = Subject()
        self.current_frame_subject: Subject = Subject()

        self.image_generation_scheduler = EventLoopScheduler()
        self.detections_scheduler = NewThreadScheduler()
        self.counters_processing_scheduler = EventLoopScheduler()
        self.transition_scheduler = EventLoopScheduler()

        self.sequences_manager: SequencesManager | None = None
        self.spade_adapter: SpadeAdapter | None = None

        self._continuous_stream_connection = None
        self._subscription = None

    def run_pipeline(self, app: ExpoApp):
        sequence_switch_epoch = self.config.timing.sequence_switch_epoch
        counters_count = self.config.depth.counters_count + 4 # 3 additional sides counters and 1 global
        max_counter_value = self.config.timing.max_counter_value
        test_animation_mode = self.config.runtime.test_animation_mode

        def build_image_generation_objects(_, __):
            self.spade_adapter = SpadeAdapter(self.config.spade)

            self.sequences_manager = SequencesManager(self.config)
            self.sequences_manager.load_masks_data().subscribe(
                on_next=app.update_sequence_display,
                on_error=lambda error: self.logger.exception(error),
                on_completed=lambda: self.sequence_switcher.on_next('start')
            )

            self.current_frame_subject.pipe(
                ops.observe_on(self.transition_scheduler),
                ops.start_with(self.spade_adapter.get_empty_frame()),
                ops.do_action(app.update_window_image)
            ).subscribe()

        self.image_generation_scheduler.schedule(build_image_generation_objects)

        detections_stream = build_detection_counters_stream(self.config)

        counters_sequence = self.sequence_switcher.pipe(
            ops.observe_on(self.counters_processing_scheduler),
            ops.do_action(lambda x: self.logger.info(f"Loop trigger: {x}")),
            ops.do_action(lambda _: self.logger.info(f"Counters stream working on thread: {threading.current_thread().name}")),
            ops.do_action(lambda _: self.sequences_manager.switch_sequence()),
            ops.do_action(lambda _: app.select_sequence(self.sequences_manager.get_current_sequence_name())),
            ops.flat_map_latest(
                lambda _: build_detection_counters_updates_stream(
                    detections_stream.pipe(
                        ops.do_action(lambda detections: app.update_detections(detections)),
                    ),
                    self.config
                ).pipe(
                    ops.do_action(lambda state: app.update_epoch(state['epoch'])),
                    ops.take_while(lambda state: state['epoch'] < sequence_switch_epoch),
                    ops.map(lambda state: state['counters_updates']),
                    ops.map(self._extend_counters_updates),
                    ops.map(lambda counters_updates: counters_updates if not test_animation_mode else np.ones(counters_count)),
                    ops.scan(
                        lambda counters, counters_updates: np.minimum(counters + counters_updates, np.full(counters_count, max_counter_value)),
                        np.zeros(counters_count)
                    ),
                    ops.map(lambda counters: np.concatenate([counters[:-4], [np.maximum.reduce(counters[-3:])], counters[-3:]])),
                    ops.map(lambda counters: counters.astype(int)),
                    ops.distinct(lambda counters: tuple(counters)),
                    ops.do_action(app.update_counters),
                    ops.take_while(lambda counters: max(counters) < max_counter_value),
                    ops.finally_action(lambda: self.sequence_switcher.on_next('next_sequence')),
                    ops.observe_on(self.image_generation_scheduler),
                    ops.map(self.sequences_manager.get_sequence_image),
                    ops.map_indexed(lambda image, index: (image, index)),
                    ops.filter(lambda indexed_image: indexed_image[1] % 2 == 0),
                    ops.map(lambda indexed_image: indexed_image[0]),
                    ops.map(self.spade_adapter.process_mask),
                    ops.do_action(self.current_frame_subject.on_next)
                )
            )
        )

        self._continuous_stream_connection = detections_stream.connect(self.detections_scheduler)

        self._subscription = counters_sequence.subscribe(
            on_error=lambda err: self.logger.exception(err),
            on_completed=lambda: self.logger.info("Pipeline closed")
        )

    def _extend_counters_updates(self, counters_updates):
        assert len(counters_updates) % 3 == 0, "counters count has to be a multiple of 3"

        group_size = len(counters_updates) // 3
        result_size = len(counters_updates) + 3 + 1

        result = np.zeros(result_size, dtype=counters_updates.dtype)

        result[:len(counters_updates)] = counters_updates

        left_max = np.max(counters_updates[0:group_size])
        center_max = np.max(counters_updates[group_size:group_size * 2])
        right_max = np.max(counters_updates[group_size * 2:group_size * 3])

        # @NOTE: Sprawdzić przypadek gdy DepthConfig.mirror_mode = False
        # Pytanie: Jak wpłynie to na relację Left <> Right?
        # Kontekst: 
        #   - Gdy mirror_mode jest wyłączony, może wystąpić asymetria w mapowaniu
        #   - Należy pamiętać o weryfikacji obu kierunków konwersji

        start_idx = len(counters_updates)
        result[start_idx] = max(left_max, center_max, right_max)  # Global
        result[start_idx + 1] = left_max  # Left
        result[start_idx + 2] = center_max  # Center
        result[start_idx + 3] = right_max  # Right

        return result


    def cleanup(self):
        self.logger.info('Cleaning up streams...')

        self._continuous_stream_connection.dispose()
        self._subscription.dispose()

        self.spade_adapter.model = None

        self.logger.info('DONE')
