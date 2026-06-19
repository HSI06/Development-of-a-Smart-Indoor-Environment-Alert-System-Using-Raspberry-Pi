from gpiozero import DigitalInputDevice, OutputDevice, LED
import requests
import time

# ========== 설정 (본인 값으로 수정) ==========
API_KEY = "여기에_OpenWeatherMap_API_키_입력"
CITY = "Seoul"
LAT, LON = 37.5665, 126.9780      # 서울 좌표 (미세먼지 조회용)
PM25_THRESHOLD = 36               # 미세먼지 "나쁨" 기준 (환경부 기준)

# ========== 핀 설정 ==========
gas = DigitalInputDevice(17)      # 가스센서 DOUT - GPIO17
buzzer = OutputDevice(18)         # 부저 - GPIO18 (3.3V!)
led_green = LED(16)               # 초록 LED - GPIO16 (창문 닫아라)
led_blue = LED(20)                # 파랑 LED - GPIO20 (시스템 정상 작동중)
led_red = LED(21)                 # 빨강 LED - GPIO21 (환기해라, 최우선)


def check_weather_bad():
    """미세먼지 나쁨 또는 비/눈 오면 True 반환"""
    try:
        # 1) 미세먼지(PM2.5) 확인
        air_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={LAT}&lon={LON}&appid={API_KEY}"
        air_res = requests.get(air_url, timeout=5).json()
        pm25 = air_res['list'][0]['components']['pm2_5']

        # 2) 비/눈 확인
        weather_url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"
        weather_res = requests.get(weather_url, timeout=5).json()
        condition = weather_res['weather'][0]['main']   # Rain, Snow, Clear, Clouds 등

        print(f"[날씨확인] 미세먼지: {pm25:.1f} / 날씨상태: {condition}")

        if pm25 >= PM25_THRESHOLD:
            return True
        if condition in ['Rain', 'Snow']:
            return True
        return False

    except Exception as e:
        print("날씨 API 오류:", e)
        return False   # 오류나면 일단 안전하게 "괜찮음" 처리


# ========== 메인 로직 ==========
led_blue.on()   # 시스템 켜지면 파랑 LED 항상 ON (정상 작동중 표시)

last_check_time = 0
weather_bad = False
CHECK_INTERVAL = 300   # 5분(300초)마다 날씨 API 확인 (너무 자주 부르면 API 낭비)

print("시스템 시작! Ctrl+C로 종료")

try:
    while True:
        gas_detected = (gas.value == 0)   # LOW면 가스 감지된 것

        # 날씨는 5분마다 한 번만 확인 (가스는 매번 즉시 확인)
        if time.time() - last_check_time > CHECK_INTERVAL:
            weather_bad = check_weather_bad()
            last_check_time = time.time()

        if gas_detected:
            # 가스 감지 - 최우선, 빨강+부저
            led_red.on()
            led_green.off()
            buzzer.on()
            print("🔴 가스 감지! 환기하세요 (창문 여세요)")

        elif weather_bad:
            # 미세먼지/비/눈 - 초록+부저
            led_red.off()
            led_green.on()
            buzzer.on()
            print("🟢 미세먼지 나쁨 또는 비/눈 - 창문 닫으세요")

        else:
            # 평상시
            led_red.off()
            led_green.off()
            buzzer.off()
            print("정상")

        time.sleep(1)

except KeyboardInterrupt:
    pass

# 종료시 전부 끄기
led_red.off()
led_green.off()
led_blue.off()
buzzer.off()
print("시스템 종료")
