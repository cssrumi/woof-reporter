from sound_detector import SoundDetector
import logging


logger = logging.getLogger('woof_reporter')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('app.log')
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)


def main():
    try:
        logger.info('App started')
        sd = SoundDetector(min_record_time=5)
        sd.run()
    except KeyboardInterrupt:
        logger.info('App stopped')


if __name__ == '__main__':
    main()
