def caesar_cipher_decode(target_text):
    results = []
    for shift in range(26):
        decoded = ''
        for char in target_text:
            if 'a' <= char <= 'z':
                decoded += chr((ord(char) - ord('a') - shift) % 26 + ord('a'))
            elif 'A' <= char <= 'Z':
                decoded += chr((ord(char) - ord('A') - shift) % 26 + ord('A'))
            else:
                decoded += char
        results.append((shift, decoded))
    return results

def contains_dictionary_word(text, dictionary):
    for word in dictionary:
        if word.lower() in text.lower():
            return True
    return False

def main():
    try:
        with open('password.txt', 'r') as f:
            encrypted_text = f.read().strip()
    except FileNotFoundError:
        print('❌ password.txt 파일이 존재하지 않습니다.')
        return

    print('🔍 Caesar Cipher 해독 시도 중...\n')

    results = caesar_cipher_decode(encrypted_text)

    # 보너스: 간단한 단어 사전
    dictionary = ['open', 'door', 'mars', 'code', 'unlock', 'success', 'hello']

    auto_found = False
    for shift, decoded in results:
        print(f'[Shift {shift:2}] {decoded}')
        if contains_dictionary_word(decoded, dictionary):
            print(f'\n✅ 단어 사전에서 발견됨! 자동 저장 (Shift {shift}) → result.txt\n')
            try:
                with open('result.txt', 'w') as result_file:
                    result_file.write(decoded)
                auto_found = True
                break
            except:
                print('❌ result.txt 저장 실패')
                return

    if not auto_found:
        try:
            shift_input = int(input('\n몇 번째 Shift가 정답인가요? 번호 입력: '))
            if 0 <= shift_input < 26:
                final_text = results[shift_input][1]
                with open('result.txt', 'w') as result_file:
                    result_file.write(final_text)
                print(f'\n✅ Shift {shift_input} 결과가 result.txt에 저장되었습니다.')
            else:
                print('❌ 잘못된 번호입니다. 0~25 사이로 입력하세요.')
        except ValueError:
            print('❌ 숫자로만 입력해주세요.')

if __name__ == '__main__':
    main()
