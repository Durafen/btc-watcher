import configparser
import logging

config = configparser.ConfigParser()
config.read("config.txt")

DEBUG = int(config.get('debug', 'DEBUG'))

if DEBUG:
    logging.basicConfig(filename='btc_watcher.log', level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s %(name)s %(message)s')
    logger = logging.getLogger(__name__)


def output_error(err):
    if DEBUG:
        logger.error(err)


def output_debug(data):
    if DEBUG:
        logger.debug(data)

