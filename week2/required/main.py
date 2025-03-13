def save_error_log(content: str):
    lines = content.strip().split('\n')
    data = [line.split(',') for line in lines[1:]]

    for row in data:
        if row[1] == 'ERROR':
            write_error_log(','.join(row), 'error') 

def write_error_log(message: str, fileName: str):
    try:
        with open(f'{fileName}.log', 'a', encoding='utf-8') as file:
            file.write(f'{message}\n')
            print(f'{fileName}.log 파일을 저장했습니다.')
    except Exception as e:
        print(f'로그를 기록할 수 없습니다: {e}')

def save_markdown_sections(fileName: str, content: str):
    try:
        with open(fileName, 'r', encoding='utf-8'):
            choice = input(f'{fileName} 파일이 이미 존재합니다. 덮어쓸까요? (y/n): ').strip().lower()
            if choice != 'y':
                print('저장을 취소했습니다.')
                return
    except FileNotFoundError:
        print(f'파일을 찾을 수 없습니다: {fileName}')
        pass

    with open(fileName, 'w', encoding='utf-8') as file:
        file.write(content)
    print(f'{fileName} 파일을 저장했습니다.')

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

def convert_to_markdown(content: str) -> str:
    lines = content.strip().split('\n')
    headers = lines[0].split(',')
    data = [line.split(',') for line in lines[1:]]

    markdown_table = '| ' + ' | '.join(headers) + ' |\n'
    markdown_table += '|-' + '-|-'.join(['-' * len(header) for header in headers]) + '-|\n'

    for row in data:
        markdown_table += '| ' + ' | '.join(row) + ' |\n'

    return markdown_table

def sort_file_content_by_timestamp(file_content: str) -> str:
    lines = file_content.strip().split('\n')
    headers = lines[0]
    data = [line for line in lines[1:] if line.strip()]

    data.sort(key = lambda x: x.split(',')[0], reverse = True)

    sorted_content = '\n'.join([headers] + data)
    return sorted_content

file_content = read_file('mission_computer_main.log')

if file_content:
    # 출력 결과를 시간의 역순으로 정렬해서 출력한다. 
    sorted_file_content = sort_file_content_by_timestamp(file_content)

    # mission_computer_main.log 내용 출력
    print(sorted_file_content)

    # 출력 결과 중 문제가 되는 부분만 따로 파일로 저장한다. 
    save_error_log(file_content)

    # mission_computer_main.log 내용 사고의 원인을 분석하고 정리
    convert_content = convert_to_markdown(file_content)

    # log_analysis 작성
    save_markdown_sections('log_analysis', convert_content)
