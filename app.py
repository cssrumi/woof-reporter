from sound_detector import SoundDetector


def main():
    sd = SoundDetector(min_record_time=30)
    sd.run()


if __name__ == '__main__':
    main()
