def write_error_log(message: str, fileName: str):
    try:
        with open(f'{fileName}.log', 'a', encoding='utf-8') as file:
            file.write(f'{message}\n')
            print(f'{fileName}.log 파일을 저장했습니다.')
    except Exception as e:
        print(f'로그를 기록할 수 없습니다: {e}')

def read_file(fileName: str):
    try:
        with open(fileName, 'r', encoding='utf-8') as file:
            content = file.read()
            return content
    except FileNotFoundError:
        error_message = f'{fileName} 파일을 찾을 수 없습니다.'
        print(error_message)
        write_error_log(error_message, 'file_error')
    except PermissionError:
        error_message = f'{fileName} 파일에 접근할 권한이 없습니다.'
        print(error_message)
        write_error_log(error_message, 'file_error')
    except Exception as e:
        error_message = f'알 수 없는 오류 발생: {e}'
        print(error_message)
        write_error_log(error_message, 'file_error')

def convert_to_list(content: str) -> list:
    lines = content.strip().split('\n')
    data = [line.split(',') for line in lines]
    
    return data

def save_json_sections(fileName: str, content: dict):
    try:
        with open(f'{fileName}.json', 'r', encoding='utf-8'):
            choice = input(f'{fileName} 파일이 이미 존재합니다. 덮어쓸까요? (y/n): ').strip().lower()
            if choice != 'y':
                print('저장을 취소했습니다.')
                return
    except FileNotFoundError:
        print(f'파일을 찾을 수 없습니다: {fileName}')
        pass

    try:
        json_content = '{\n'
        for key, value in content.items():
            key = str(key).replace('\'', '\\\'')
            if isinstance(value, list):
                value = '[' + ', '.join([f'\'{str(item).replace('\'', '\\\'')}\'' for item in value]) + ']'
            else:
                value = f'\'{str(value).replace('\'', '\\\'')}\''
            json_content += f'    '{key}': {value},\n'

        json_content = json_content.rstrip(',\n') + '\n}'
        
        with open(f'{fileName}.json', 'w', encoding='utf-8') as file:
            file.write(json_content)
        
        print(f'{fileName} 파일을 저장했습니다.')
    except Exception as e:
        print(f'파일 저장 중 오류가 발생했습니다: {e}')

def search_for_key_value(content: dict):
    search_string = input('검색할 문자열을 입력하세요: ').strip()

    found = False
    for key, value in content.items():
        if search_string.lower() in str(key).lower() or any(search_string.lower() in str(v).lower() for v in value):
            print(f'찾은 항목: {key}: {value}')
            found = True

    if not found:
        print(f''{search_string}'에 해당하는 항목을 찾을 수 없습니다.')

file_content = read_file('mission_computer_main.log')

if file_content:
    # mission_computer_main.log 내용 출력
    print(file_content)

    # 콤마를 기준으로 날짜 및 시간과 로그 내용을 분류해서 Python의 리스트(List) 객체로 전환한다. 
    list_file_content = convert_to_list(file_content)

    # 전환된 리스트 객체를 화면에 출력한다. 
    print(list_file_content)

    # 리스트 객체를 시간의 역순으로 정렬(sort)한다. 
    sorted_list_file_content = sorted(list_file_content, key=lambda x: x[0], reverse=True)

    # 리스트 객체를 사전(Dict) 객체로 전환한다. 
    sorted_dict_file_content = {row[0]: row[1:] for row in sorted(sorted_list_file_content, key=lambda x: x[0], reverse=True)}

    print(sorted_dict_file_content)

    # 사전 객체로 전환된 내용을 mission_computer_main.json 파일로 저장하는데 파일 포멧은 JSON(JavaScript Ontation)으로 저장한다. 
    save_json_sections('mission_computer_main', sorted_dict_file_content)

    # 사전 객체로 전환된 내용에서 특정 문자열 (예를 들어 Oxygen)을 입력하면 해당 내용을 출력하는 코드를 추가한다. 
    search_for_key_value(sorted_dict_file_content)