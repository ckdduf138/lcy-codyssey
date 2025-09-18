import os
import csv
import speech_recognition as sr


class JavisSTTProcessor:
    def __init__(self, directory='/Users/heesup9683/Desktop/Codyssey/ia-codyssey/week13/records'):
        self.directory = directory
        self.recognizer = sr.Recognizer()

        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

    def list_audio_files(self):
        return [f for f in os.listdir(self.directory) if f.endswith('.wav')]

    def convert_audio_to_text(self, filename):
        filepath = os.path.join(self.directory, filename)
        with sr.AudioFile(filepath) as source:
            audio = self.recognizer.record(source)

        try:
            return self.recognizer.recognize_google(audio, language='ko-KR')
        except sr.UnknownValueError:
            return '[인식 실패]'
        except sr.RequestError:
            return '[요청 실패]'

    def save_text_to_csv(self, filename, text):
        csv_filename = filename.replace('.wav', '.csv')
        csv_path = os.path.join(self.directory, csv_filename)

        with open(csv_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Time', 'Recognized Text'])
            writer.writerow(['전체', text])

        print(f'✅ CSV 저장 완료: {csv_path}')

    def process_all_files(self):
        files = self.list_audio_files()
        if not files:
            print('⚠️ WAV 파일이 없습니다.')
            return

        for filename in files:
            print(f'🎧 처리 중: {filename}')
            text = self.convert_audio_to_text(filename)
            print(f'📝 인식 결과: {text}')
            self.save_text_to_csv(filename, text)

    def search_keyword(self, keyword):
        csv_files = [f for f in os.listdir(self.directory) if f.endswith('.csv')]
        if not csv_files:
            print('⚠️ CSV 파일이 없습니다.')
            return

        print(f'🔍 키워드 "{keyword}" 검색 결과:')
        found = False
        for f in csv_files:
            with open(os.path.join(self.directory, f), mode='r', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader)  # skip header
                for row in reader:
                    if keyword in row[1]:
                        print(f'📄 {f}: {row[1]}')
                        found = True

        if not found:
            print('❌ 결과 없음.')


if __name__ == '__main__':
    processor = JavisSTTProcessor()

    keyword = input('🔍 검색할 키워드를 입력하세요: ')
    processor.search_keyword(keyword)
