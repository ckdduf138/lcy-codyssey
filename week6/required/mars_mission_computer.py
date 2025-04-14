import subprocess
import platform
import json

class MissionComputer:
    
    def __init__(self):
        self.os_name = self.get_os_name()
        self.os_version = self.get_os_version()
        self.cpu_type = self.get_cpu_type()
        self.cpu_cores = self.get_cpu_cores()
        self.memory_size = self.get_memory_size()
        self.info_settings, self.load_settings = self.load_settings()

    def is_unix_like(self):
       return platform.system() == "Linux"
    
    def is_windows(self):
        return platform.system() == "Windows"
    
    # bonus: 1. setting.txt 파일을 만들어서 출력되는 정보의 항목을 셋팅 할 수 있도록 코드를 수정한다.
    def load_settings(self):
        # 텍스트 파일에서 설정을 읽어옵니다.
        info_settings = []
        load_settings = []
        
        try:
            with open("setting.txt", "r") as f:
                section = None
                for line in f:
                    line = line.strip()
                    # [info] 또는 [load] 구분
                    if line.startswith("[info]"):
                        section = "info"
                    elif line.startswith("[load]"):
                        section = "load"
                    elif line:
                        if section == "info":
                            info_settings.append(line)
                        elif section == "load":
                            load_settings.append(line)
        except FileNotFoundError:
            print("setting.txt 파일이 없습니다.")
        
        return info_settings, load_settings

    def get_os_name(self):
        return platform.system() 
    
    def get_os_version(self):
        return platform.version()  # 운영 체제 버전
    
    def get_cpu_type(self):
        return platform.processor()  # CPU 정보

    def get_cpu_cores(self):
        # platform 모듈에서 CPU 코어 수를 제공하지 않으므로, os나 subprocess를 사용해 CPU 코어 수를 얻는 방법이 필요할 수 있습니다.
        return platform.machine()  # 예시로 머신 아키텍처 (x86_64 등) 반환
    
    def get_memory_size(self):
        if self.is_windows():
            try:
                output = subprocess.getoutput("wmic computersystem get TotalPhysicalMemory")
                lines = output.strip().splitlines()
                # 숫자만 추출
                for line in lines:
                    line = line.strip()
                    if line.isdigit():
                        mem_bytes = int(line)
                        mem_gb = round(mem_bytes / (1024 ** 3), 2)
                        return f"{mem_gb} GB"
            except Exception as e:
                print(f"Error retrieving memory size: {e}")
            return "Unable to retrieve memory size."
        
        elif self.is_unix_like():
            try:
                output = subprocess.getoutput("free -b | grep Mem | awk '{ print $2 }'")
                if output.strip().isdigit():
                    mem_bytes = int(output.strip())
                    mem_gb = round(mem_bytes / (1024 ** 3), 2)
                    return f"{mem_gb} GB"
            except Exception:
                pass
            return "Unable to retrieve memory size."

        return "Unable to retrieve memory size."

    # 1. 파이썬 코드를 사용해서 다음과 같은 미션 컴퓨터의 정보를 알아보는 메소드를 get_mission_computer_info()
    #    라는 이름으로 만들고 문제 7에서 완성한 MissionComputer 클래스에 추가한다. 
    def get_mission_computer_info(self):
        info = {}
        
        if 'OS' in self.info_settings:
            info['OS'] = self.os_name
        if 'OS Version' in self.info_settings:
            info['OS Version'] = self.os_version
        if 'CPU Type' in self.info_settings:
            info['CPU Type'] = self.cpu_type
        if 'CPU Cores' in self.info_settings:
            info['CPU Cores'] = self.cpu_cores
        if 'Memory Size' in self.info_settings:
            info['Memory Size'] = self.memory_size
        
        return json.dumps(info, indent=4)
    
    # 3. 미션 컴퓨터의 부하를 가져오는 코드를 get_mission_computer_load() 메소드로 만들고 MissionComputer 클래스에 추가한다.
    # 4. get_mission_computer_load() 메소드의 경우 다음과 같은 정보들을 가져 올 수 있게한다.
    def get_mission_computer_load(self):
        cpu_usage = "Unable to retrieve CPU usage."
        memory_usage = "Unable to retrieve memory usage."

        if self.is_windows():
            cpu_usage = get_cpu_usage_windows()
            memory_usage = get_memory_usage_windows()

        load_info = {}
        if 'CPU Usage' in self.load_settings:
            load_info['CPU Usage'] = cpu_usage
        if 'Memory Usage' in self.load_settings:
            load_info['Memory Usage'] = memory_usage

        return json.dumps(load_info, indent=4)

def get_memory_usage_windows():
    try:
        # PowerShell을 통해 전체 사용률 % 계산
        command = [
            "powershell",
            "-Command",
            "(Get-CimInstance Win32_OperatingSystem | "
            "Select-Object @{Name='MemoryUsed';Expression={($_.TotalVisibleMemorySize - $_.FreePhysicalMemory) * 100 / $_.TotalVisibleMemorySize}}).MemoryUsed"
        ]
        output = subprocess.check_output(command, universal_newlines=True)
        lines = output.strip().split('\n')
        if lines:
            return f"{float(lines[-1].strip()):.2f}%"
        else:
            return "Unable to retrieve memory usage."
    except Exception as e:
        return "Unable to retrieve memory usage."

def get_cpu_usage_windows():
    try:
        output = subprocess.check_output(["wmic", "cpu", "get", "loadpercentage"], universal_newlines=True)
        lines = output.strip().splitlines()
        usage_values = [line.strip() for line in lines[1:] if line.strip().isdigit()]
        if usage_values:
            avg = sum(int(val) for val in usage_values) / len(usage_values)
            return f"{round(avg)}%"
        else:
            return "Unable to retrieve CPU usage."
    except Exception as e:
        return "Unable to retrieve CPU usage."


if __name__ == '__main__':
    # 7. MissionComputer 클래스를 runComputer 라는 이름으로 인스턴스화 한다.  
    runComputer = MissionComputer()

    # 2. get_mission_computer_info()에 가져온 시스템 정보를 JSON 형식으로 출력하는 코드를 포함한다
    print(runComputer.get_mission_computer_info())

    # 5. get_mission_computer_load()에 해당 결과를 JSON 형식으로 출력하는 코드를 추가한다. 
    print(runComputer.get_mission_computer_load())

# 6. get_mission_computer_info(), get_mission_computer_load()를 호출해서 출력이 잘되는지 확인한다. 
# 7. runComputer 인스턴스의 get_mission_computer_info(), get_mission_computer_load()
#    메소드를 호출해서 시스템 정보에 대한 값을 출력 할 수 있도록 한다.
# 8. 최종적으로 결과를 mars_mission_computer.py 에 저장한다. 