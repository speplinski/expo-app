from sequences_manager.sequence_generator.random_paths_generator.config import SEQUENCE_CONFIG
from sequences_manager.sequence_generator.random_paths_generator.random_sequence_generator import \
    RandomSequenceGenerator

if __name__ == "__main__":
    generator = RandomSequenceGenerator()

    generator.next_sequence()

    print('Tags path:')
    print(generator.current_path_data['tags_sequence'])
    print('->')
    print(generator.current_path_data['combined_tags_sequence'])
    print('')
    print('Path:')
    print(' -> '.join([str(i) for i in generator.current_path_data['path']]))
    print('')
    print('Path details')
    for node in generator.current_path_data['path']:
        tags = SEQUENCE_CONFIG['sceneries_tags'][str(node)]
        print(f'{node:4}: {tags}')