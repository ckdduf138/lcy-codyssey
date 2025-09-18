import struct

# CSV 파일 읽기 함수
def read_csv_file(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        return [line.strip().split(',') for line in lines]  # 쉼표로 분리
    except FileNotFoundError:
        print(f'Error: {filename} 파일을 찾을 수 없습니다.')
        return []
    except Exception as e:
        print(f'Error: {e}')
        return []

# 데이터를 정렬하고 필터링하는 함수
def process_inventory(data):
    if not data:
        return []
    
    header = data[0]  # 헤더 저장
    inventory = data[1:]  # 실제 데이터

    # 인화성 기준으로 내림차순 정렬
    try:
        inventory.sort(key=lambda x: float(x[4]), reverse=True)  # 인화성 지수 (5번째 열) 기준으로 정렬
    except ValueError:
        print('Error: Flammability 값을 숫자로 변환할 수 없습니다.')
        return []

    return [header] + inventory  # 헤더 포함하여 반환

# 인화성 지수가 0.7 이상인 항목을 필터링하는 함수
def filter_dangerous_items(data, threshold=0.7):
    return [row for row in data[1:] if float(row[4]) >= threshold]  # 데이터의 2번째 행부터 필터링

# CSV 파일로 저장하는 함수
def save_to_csv(filename, data):
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            for row in data:
                line = ','.join(row) + '\n' 
                file.write(line)
        print(f'CSV 파일로 저장 완료: {filename}')
    except Exception as e:
        print(f'Error: {e}')

# 이진 파일로 저장
def save_to_binary(filename, data):

    # 각 리스트(행)를 쉼표로 구분하여 텍스트로 변환하고, 그 결과를 하나의 문자열로 결합
    text_data = '\n'.join([', '.join(row) for row in data])  # 각 행을 쉼표로 구분하고, 각 행을 줄바꿈으로 연결

    # 텍스트를 바이트로 변환
    encoded_data = text_data.encode()  # .encode()를 사용하여 문자열을 바이트로 변환

    try:
        with open(filename, 'wb') as file:
            
            file.write(encoded_data)
                
        print(f'\n이진 파일로 저장 완료: {filename}')
    except Exception as e:
        print(f'이진 파일로 저장 Error: {e}')

# 이진 파일에서 읽어오기
def read_from_binary(filename):
    try:
        # 바이너리 모드로 파일을 읽기
        with open(filename, 'rb') as file:
            encoded_data = file.read()  # 파일에서 바이트 데이터를 읽음

        # 바이트 데이터를 텍스트로 변환
        decoded_data = encoded_data.decode()  # .decode()를 사용하여 바이트 데이터를 문자열로 변환
        
        print(decoded_data)
        
    except FileNotFoundError:
        print(f'Error: {filename} 파일을 찾을 수 없습니다.')
    except Exception as e:
        print(f'이진 파일에서 읽어오기 Error: {e}')

if __name__ == '__main__':
    input_file = 'Mars_Base_Inventory_List.csv'
    danger_file = 'Mars_Base_Inventory_danger.csv'
    binary_file = 'Mars_Base_Inventory_List.bin'

    # CSV 파일 읽기
    # 'Mars_Base_Inventory_List.csv 내용을 읽어서 Python의 리스트(List) 객체로 변환한다.'
    csv_data = read_csv_file(input_file)

    # 'Mars_Base_Inventory_List.csv 의 내용을 읽어 들어서 출력한다.'
    print('Mars_Base_Inventory_List.csv 전체 출력')
    print(csv_data)

    processed_data = process_inventory(csv_data)

    if processed_data:
        # '배열 내용을 적제 화물 목록을 인화성이 높은 순으로 정렬한다.'
        dangerous_items = filter_dangerous_items(processed_data, 0.7)
        
        if dangerous_items:
            # 인화성 지수가 0.7 이상되는 목록을 뽑아서 별도로 출력한다.
            print('인화성 지수가 0.7 이상인 항목 ')
            for row in dangerous_items:
                print(f'물질: {row[0]}, 인화성 지수: {row[4]}')
            
            # '인화성 지수가 0.7 이상되는 목록을 CSV 포멧(Mars_Base_Inventory_danger.csv)으로 저장한다.'
            save_to_csv(danger_file, [csv_data[0]] + dangerous_items)
            
            # 인화성 순서로 정렬된 배열의 내용을 이진 파일형태로 저장한다. 파일이름은 Mars_Base_Inventory_List.bin
            save_to_binary(binary_file, processed_data)

            # '저장된 Mars_Base_Inventory_List.bin 의 내용을 다시 읽어 들여서 화면에 내용을 출력한다.'
            print('\n이진 파일에서 데이터 다시 읽기 ')
            read_from_binary(binary_file)
        else:
            print('인화성 지수가 0.7 이상인 항목이 없습니다.')