from dataclasses import dataclass


@dataclass
class SequenceConfig:
    use_static_paths = True

    images_path: str = "data/landscapes"

    sequence_mapping_path: str = "data/sequence_config/sequence_mapping.json"
    mak_mapping_path: str = "data/sequence_config/mask_mapping.json"

    static_paths_path: str = "data/sequence_config/static_paths.json"

    sequence_nodes_tags: str = "data/sequence_config/sequence_nodes_tags.json"
    sequence_transitions_graph: str = "data/sequence_config/sequence_transitions_graph.json"
    tags_weights: str = "data/sequence_config/tags_weights.json"
