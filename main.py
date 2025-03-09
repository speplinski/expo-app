import logging

from config.args_parser import parse_arguments_and_init_config
from logger.build_logger import build_app_logger
from scheduler.main_pipeline import MainPipeline
from ui.ui_main import ExpoApp


if __name__ == "__main__":
    config = parse_arguments_and_init_config()

    build_app_logger(config.runtime.log_file, config.runtime.log_level)

    logger = logging.getLogger()
    logger.info('Application started')

    pipeline = MainPipeline(config)

    def cleanup():
        pipeline.cleanup()

        logger.info('Application stopped')
        for handler in logger.handlers:
            handler.flush()
            handler.close()

    app = ExpoApp(
        config,
        cleanup,
        debug_mode=True
    )

    pipeline.run_pipeline(app)

    app.run()
