from textual.widgets import Tree

from sequences_manager.sequences_manager import SequenceStatus


class SequencesTree(Tree):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._node_map = {}

    def on_mount(self):
        self.root.expand()

    def update_sequence(self, sequence_info):
        sequence_name = sequence_info['sequence_name']
        sequence_state = sequence_info['status']

        sequence_node = self._node_map.get(sequence_name)

        if sequence_node is None:
            sequence_node = self.root.add(sequence_name, data=sequence_info)
            self._node_map[sequence_name] = sequence_node
        else:
            sequence_node.data = sequence_info

        if sequence_state == SequenceStatus.LOADING:
            sequence_node.label = f"{sequence_name} (loading)"
            sequence_node.allow_expand = False
        elif sequence_state == SequenceStatus.READY:
            sequence_node.label = sequence_name
            sequence_node.allow_expand = True

            static_masks_node = sequence_node.add('static_masks', data=sequence_info['sequence_config']['static_masks'])
            for layer_id, gray_value in sequence_info['sequence_config']['static_masks'].items():
                item_node = static_masks_node.add(f'{layer_id} (gray shade: {gray_value})', data=gray_value)
                item_node.allow_expand = False

            dynamic_masks_node = sequence_node.add('sequence_masks', data=sequence_info['sequence_config']['sequence_masks'])
            for layer_id, gray_value in sequence_info['sequence_config']['sequence_masks'].items():
                item_node = dynamic_masks_node.add(f'{layer_id} (gray shade: {gray_value})', data=gray_value)
                item_node.allow_expand = False

    def select_sequence(self, sequence_name):
        sequence_node = self._node_map[sequence_name]
        self.select_node(sequence_node)
        self.set_timer(0.001, lambda: sequence_node.collapse())
