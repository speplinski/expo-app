from dataclasses import dataclass, field

from config.modules_configs.depth_config import DepthConfig
from config.modules_configs.display_config import DisplayConfig
from config.modules_configs.runtime_config import RuntimeConfig
from config.modules_configs.sequence_config import SequenceConfig
from config.modules_configs.spade_config import SpadeConfig
from config.modules_configs.timing_config import TimingConfig


@dataclass
class IntegratedConfig:
    runtime: RuntimeConfig = field(default_factory=RuntimeConfig)

    depth: DepthConfig = field(default_factory=DepthConfig)

    display: DisplayConfig = field(default_factory=DisplayConfig)

    sequence: SequenceConfig = field(default_factory=SequenceConfig)
    timing: TimingConfig = field(default_factory=TimingConfig)

    spade: SpadeConfig = field(default_factory=SpadeConfig)
