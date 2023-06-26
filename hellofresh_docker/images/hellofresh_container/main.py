#!/usr/bin/env python



import logging

from images.hellofresh_container.log_handler import initialize_logger

from images.hellofresh_container.pipeline import Pipeline



logger = logging.getLogger("main")



if __name__ == '__main__':

    initialize_logger()

    logger.info('Recipe Application started')

    pipeline = Pipeline("Change the way people eat")

    pipeline.run_pipeline()

    logger.info('Pipeline executed')

