from config.modules_configs.sequence_config import SequenceConfig
from sequences_manager.sequence_generator.random_paths_generator.random_sequence_generator import \
    RandomSequenceGenerator

if __name__ == "__main__":
    generator = RandomSequenceGenerator(SequenceConfig())

    generator.next_sequence()

    print(f'Generation attempts: {generator.current_path_data['attempts']}')

    print('Tags path:')
    print(generator.current_path_data['tags_sequence'])
    print('->')
    print(generator.current_path_data['combined_tags_sequence'])
    print('')
    print('Path:')
    print(' -> '.join(generator.current_path_data['path']))
    print('')
    print('Path details')
    for node in generator.current_path_data['path']:
        tags = generator.get_scenery_tags(node)
        print(f'{node:>4}: {tags}')