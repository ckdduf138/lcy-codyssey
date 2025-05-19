import zipfile
import time

def unlock_zip():
    zip_path = 'emergency_storage_key.zip'

    # 'mars06' 문자가 앞쪽에 오도록 문자열 우선순위 조정
    custom_priority = 'mars06'
    others = ''.join(c for c in 'abcdefghijklmnopqrstuvwxyz0123456789' if c not in custom_priority)
    characters = custom_priority + others  # 최종 문자집합: m, a, r, s, 0, 6, ..., 나머지

    password_length = 6
    attempts = 0
    start_time = time.time()

    try:
        with zipfile.ZipFile(zip_path) as zf:
            total = len(characters) ** password_length

            for i in range(total):
                password = ''
                index = i
                for _ in range(password_length):
                    password = characters[index % len(characters)] + password
                    index = index // len(characters)

                attempts += 1
                try:
                    zf.extractall(pwd=password.encode('utf-8'))
                    elapsed = time.time() - start_time
                    print('✅ Success! Password:', password)
                    print('🔁 Total attempts:', attempts)
                    print('⏱️ Elapsed time: {:.2f} seconds'.format(elapsed))
                    with open('password.txt', 'w') as f:
                        f.write(password)
                    return password
                except:
                    if attempts % 100000 == 0:
                        print('Attempts:', attempts, 'Elapsed time: {:.2f} seconds'.format(time.time() - start_time))
                    continue
    except FileNotFoundError:
        print('Error: FileNotFoundError.')
    except zipfile.BadZipFile:
        print('Error: BadZipFile.')

    return None

if __name__ == '__main__':
    unlock_zip()