import random

# 더미 센서에 해당하는 클래스를 생성한다. 클래스의 이름은 DummySensor로 정의한다. 
class DummySensor:
    # DummySensor의 멤버로 env_values라는 사전 객체를 추가한다. 
    def __init__(self):
        self.env_values = {
            'mars_base_internal_temperature': 0,
            'mars_base_external_temperature': 0,
            'mars_base_internal_humidity': 0,
            'mars_base_external_illuminance': 0,
            'mars_base_internal_co2': 0.0,
            'mars_base_internal_oxygen': 0.0,
        }
    
    # DummySensor 클래스에 set_env() 메소드를 추가한다
    def set_env(self):
        self.env_values['mars_base_internal_temperature'] = random.randint(18, 30)
        self.env_values['mars_base_external_temperature'] = random.randint(0, 21)
        self.env_values['mars_base_internal_humidity'] = random.randint(50, 60)
        self.env_values['mars_base_external_illuminance'] = random.randint(500, 715)
        self.env_values['mars_base_internal_co2'] = round(random.uniform(0.02, 0.1), 3)
        self.env_values['mars_base_internal_oxygen'] = round(random.uniform(4.0, 7.0), 2)
    
    # DummySensor 클래스는 get_env() 메소드를 추가하는데 get_env() 메소드는 env_values를 return 한다. 
    def get_env(self):
        try:
            log_entry = self.generate_log_entry()
            with open('mars_mission_log.txt', 'a', encoding='utf-8') as log_file:
                log_file.write(log_entry + '\n')

        except FileNotFoundError:
            error_message = f'{log_file} 파일을 찾을 수 없습니다.'
            print(error_message)
        except PermissionError:
            error_message = f'{log_file} 파일에 접근할 권한이 없습니다.'
            print(error_message)    
        except Exception as e:
            error_message = f'알 수 없는 오류 발생: {e}'
            print(error_message)
        
        return self.env_values
    
    # 파일에 log를 남기는 부분을 get_env()에 추가 한다.
    def generate_log_entry(self):
        timestamp = self.get_current_time()

        log_format = (
            f'{timestamp}, '
            f'내부 온도: {self.env_values['mars_base_internal_temperature']}°C, '
            f'외부 온도: {self.env_values['mars_base_external_temperature']}°C, '
            f'내부 습도: {self.env_values['mars_base_internal_humidity']}%, '
            f'외부 광량: {self.env_values['mars_base_external_illuminance']} W/m², '
            f'내부 CO2: {self.env_values['mars_base_internal_co2']}%, '
            f'내부 O2: {self.env_values['mars_base_internal_oxygen']}%'
        )
        return log_format

    def get_current_time(self):
        return '2025-03-31 20:37:10'

# DummySensor 클래스를 ds라는 이름으로 인스턴스(Instance)로 만든다. 
ds = DummySensor()

# 인스턴스화 한 DummySensor 클래스에서 set_env()와 get_env()를 차례로 호출해서 값을 확인한다. 
ds.set_env()
env_data = ds.get_env()

print(env_data)