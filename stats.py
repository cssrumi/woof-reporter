import logging
import os
from datetime import datetime, timedelta

module_logger = logging.getLogger('woof_reporter.stats')


def now():
    return datetime.now()


def format_dt(dt: datetime):
    new_format = '{0:%Y-%m-%d}'
    return new_format.format(dt)


def get_default_location():
    _REPORT_DIR = 'reports'
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), _REPORT_DIR)


def count(date: (datetime, str) = format_dt(now())):
    if isinstance(date, datetime):
        date = format_dt(date)
    location = get_default_location()
    longer_than_0_list = [file for file in os.listdir(location) if date in file and '0minutes' not in file]
    longer_than_0_count = len(longer_than_0_list)
    sum_of_woofing = 0
    for file in longer_than_0_list:
        f = str(file).replace('minutes.wav', '')
        i = max([i for i, c in enumerate(f) if c == '-'])
        minutes = int(f[i + 1:])
        sum_of_woofing += minutes
    statistics = 'Count: {}, Sum: {}'.format(longer_than_0_count, sum_of_woofing)
    module_logger.debug(statistics)
    return statistics


def stats():
    dt = datetime.now() - timedelta(days=1)
    module_logger.info(count(dt))


if __name__ == '__main__':
    stats()
