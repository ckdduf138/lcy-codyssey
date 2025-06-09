# javis.py

import os
import wave
import datetime
import pyaudio


def create_records_directory():
    if not os.path.exists('records'):
        os.makedirs('records')


def generate_filename():
    now = datetime.datetime.now()
    timestamp = now.strftime('%Y%m%d-%H%M%S')
    return f'records/{timestamp}.wav'


def record_audio(duration=5, channels=1, rate=44100, chunk=1024):
    audio = pyaudio.PyAudio()

    stream = audio.open(format=pyaudio.paInt16,
                        channels=channels,
                        rate=rate,
                        input=True,
                        frames_per_buffer=chunk)

    print('녹음 시작...')
    frames = []

    for _ in range(0, int(rate / chunk * duration)):
        data = stream.read(chunk)
        frames.append(data)

    print('녹음 종료.')

    stream.stop_stream()
    stream.close()
    audio.terminate()

    create_records_directory()
    filename = generate_filename()

    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(rate)
        wf.writeframes(b''.join(frames))

    print(f'파일 저장 완료: {filename}')


if __name__ == '__main__':
    record_audio()
