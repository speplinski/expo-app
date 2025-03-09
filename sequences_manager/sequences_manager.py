import json
import logging
import random
import threading
from enum import Enum
from multiprocessing import cpu_count

import numpy as np
import numpy.typing as npt
from reactivex import create, from_, Observable, of
from reactivex.scheduler import ThreadPoolScheduler
import reactivex.operators as ops

from config.integrated_config import IntegratedConfig
from sequences_manager.sequence import Sequence


class SequenceStatus(Enum):
    LOADING = 1
    READY = 2

class SequencesManager:
    def __init__(self, config: IntegratedConfig):
        self.config = config
        self.logger = logging.getLogger()

        self.logger.info(f'Sequence manager initialized on thread {threading.current_thread().name}')

        self._sequences: list[Sequence] = []
        self._current_sequence = None

    def load_masks_data(self) -> Observable:
        def sequence_loader_observable(observer, _):
            try:
                with open(self.config.sequence.config_path) as f:
                    sequences_config = json.load(f)
            except FileNotFoundError as e:
                observer.on_error(e)
                return

            self._sequences = []

            loading_scheduler = ThreadPoolScheduler(cpu_count())

            return from_(sequences_config.items()).pipe(
                ops.map(lambda item: { 'sequence_name': item[0], 'sequence_config': item[1] }),
                ops.do_action(lambda sequence_info: observer.on_next({
                    **sequence_info,
                    'status': SequenceStatus.LOADING
                })),
                ops.map(lambda sequence_info: {
                    'sequence_info': sequence_info,
                    'sequence': Sequence(
                        sequence_info['sequence_name'],
                        sequence_info['sequence_config'],
                        self.config.display.model_resolution
                    )
                }),
                ops.do_action(lambda sequence_data: self._sequences.append(sequence_data['sequence'])),
                ops.flat_map( # ensures concurrency
                    lambda sequence_data: of(sequence_data).pipe(
                        ops.observe_on(loading_scheduler),
                        ops.do_action(lambda sequence_data: sequence_data['sequence'].load_data(self.config.sequence.images_path)),
                        ops.do_action(lambda sequence_data: observer.on_next({
                            **sequence_data['sequence_info'],
                            'status': SequenceStatus.READY
                        }))
                    )
                )
            ).subscribe(
                on_error=observer.on_error,
                on_completed=observer.on_completed
            )

        return create(sequence_loader_observable)

    def get_sequence_image(self, counters: npt.NDArray[np.uint8]) -> npt.NDArray[np.uint8]:
        if self._current_sequence is None:
            self.switch_sequence()

        return self._sequences[self._current_sequence].build_image(counters)


    def switch_sequence(self):
        assert len(self._sequences) > 0, 'no sequences available'

        if self._current_sequence is None:
            self._current_sequence = 0
        else:
            self._current_sequence = (self._current_sequence + 1) % len(self._sequences)

    def get_current_sequence_name(self):
        return self._sequences[self._current_sequence].name







