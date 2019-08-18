import datetime
import wave
import logging
from array import array

import pyaudio
import os

from sender import EmailSender
from stats import count

module_logger = logging.getLogger('woof_reporter.sound_detector')


class SoundDetector:
    DATE_TIME_FORMAT = '{0:%Y-%m-%d_%H:%M:%S}'
    _FORMAT = pyaudio.paInt16
    _CHANNELS = 2
    _RATE = 44100
    _CHUNK = 1024
    _REPORT_DIR = 'reports'
    _TEMPLATE = 'report_from_'

    def __init__(self, location=None, threshold=500, min_record_time=30):
        self.logger = logging.getLogger('woof_reporter.sound_detector.SoundDetector')
        self.location = location if location else self.get_default_location()
        self.threshold = threshold
        self._min_record_time = min_record_time
        self._audio = pyaudio.PyAudio()
        self._audio.get_default_input_device_info()
        self._stream = self._audio.open(
            format=self._FORMAT,
            channels=self._CHANNELS,
            rate=self._RATE,
            input=True,
            frames_per_buffer=self._CHUNK
        )
        self._frames = []
        self._record_start_dt = None
        self.sender = EmailSender()
        self.logger.debug('SoundDetector class initialized')

    @staticmethod
    def get_default_location():
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), __class__._REPORT_DIR)

    def _check_noise_lvl(self, data):
        vol = max(array('h', data))
        if vol >= self.threshold:
            return True
        else:
            return False

    def run(self):
        while True:
            try:
                data = self._stream.read(self._CHUNK, exception_on_overflow=False)
                if self._check_noise_lvl(data):
                    self._start_recording(data)
            except OSError as e:
                module_logger.exception(e)

    def _save(self):
        formatted = self.DATE_TIME_FORMAT.format(self._record_start_dt)
        record_time = datetime.datetime.now() - self._record_start_dt - datetime.timedelta(
            seconds=self._min_record_time
        )
        # Check if it was just a mistake
        if record_time > datetime.timedelta(seconds=2):
            minutes = int(record_time.seconds / 60)
            record_time = '-' + str(minutes) + 'minutes'
            filename = self._TEMPLATE + formatted + record_time + '.wav'
            full_path = os.path.join(self.location, filename)
            if not (os.path.exists(self.location) and os.path.isdir(self.location)):
                os.mkdir(self._REPORT_DIR)
                full_path = os.path.join(self._REPORT_DIR, filename)

            with wave.open(full_path, 'wb') as wav_file:
                wav_file.setnchannels(self._CHANNELS)
                wav_file.setsampwidth(self._audio.get_sample_size(self._FORMAT))
                wav_file.setframerate(self._RATE)
                wav_file.writeframes(b''.join(self._frames))
            self._frames = []
            return full_path, formatted, record_time.replace('-', '')
        else:
            self._frames = []
            return None, None, None

    def _start_recording(self, data):
        self.logger.info('Recording started!')
        self._frames.append(data)
        start = datetime.datetime.now()
        self._record_start_dt = start
        stop = start + datetime.timedelta(seconds=self._min_record_time)
        while datetime.datetime.now() < stop:
            data = self._stream.read(self._CHUNK)
            self._frames.append(data)
            if self._check_noise_lvl(data):
                stop = datetime.datetime.now() + datetime.timedelta(seconds=self._min_record_time)
        saved_file, date, record_time = self._save()
        if saved_file:
            self.logger.info('Recording finished! {}'.format(saved_file))
            subject = '[WOOF-REPORTER] {}-{}'.format(date, record_time)
            self.sender.send_message_with_attachments(subject, message=count(date), file_path=saved_file)
        else:
            self.logger.info('Record lasted less than 2 seconds...')
