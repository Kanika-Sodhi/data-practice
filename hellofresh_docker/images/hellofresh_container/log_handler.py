import logging
from logging.handlers import TimedRotatingFileHandler


def initialize_logger():
    logging.basicConfig(format ='%(asctime)s:%(levelname)s:%(name)s:%(message)s',
                        filename='../../logs/etl_pipeline.log', encoding='utf-8', level=logging.INFO)