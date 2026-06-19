from flask import Flask, render_template, request
from gpiozero import DigitalInputDevice, OutputDevice, LED
import requests
import time
import threading

# ========== 설정 (본인 값으로 수정) ==========
API_KEY = "여기에_OpenWeatherMap_API_키_입력"
CITY = "Seoul"
LAT, LON = 37.5665, 126.9780
PM25_THRESHOLD = 36
CHECK_INTERVAL = 300   # 날씨 확인 주기 (초)

# ========== 핀 설정 ==========
gas = DigitalInputDevice(17)
buzzer = OutputDevice(18)
led_green = LED(16)
led_blue = LED(20)
led_red = LED(21)

app = Flask(__name__)

# 웹페이지에 보여줄 현재 상태 (전역 변수)
state = {
    "gas_detected": False,
    "weather_bad": False,
    "pm25": 0,
    "condition": "-",
    "muted": False,        # 사용자가 끄기 버튼 눌렀는지 여부
}


def check_weather_bad():
    """미세먼지 나쁨 또는 비/눈 오면 True 반환, state에도 값 저장"""
    try:
        air_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={LAT}&lon={LON}&appid={API_KEY}"
        air_res = requests.get(air_url, timeout=5).json()
        pm25 = air_res['list'][0]['components']['pm2_5']

        weather_url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"
        weather_res = requests.get(weather_url, timeout=5).json()
        condition = weather_res['weather'][0]['main']

        state["pm25"] = round(pm25, 1)
        state["condition"] = condition

        if pm25 >= PM25_THRESHOLD:
            return True
        if condition in ['Rain', 'Snow']:
            return True
        return False

    except Exception as e:
        print("날씨 API 오류:", e)
        return False


def sensor_loop():
    """백그라운드에서 계속 센서 확인하는 함수 (Flask와 동시에 실행됨)"""
    led_blue.on()   # 정상 작동중 표시등, 항상 켜짐
    last_check = 0

    while True:
        gas_now = (gas.value == 0)
        prev_gas = state["gas_detected"]
        state["gas_detected"] = gas_now

        # 가스 상태가 "새로" 감지된 순간이면 음소거 해제
        if gas_now and not prev_gas:
            state["muted"] = False

        if time.time() - last_check > CHECK_INTERVAL:
            new_weather_bad = check_weather_bad()
            if new_weather_bad and not state["weather_bad"]:
                state["muted"] = False   # 날씨도 새로 나빠지면 음소거 해제
            state["weather_bad"] = new_weather_bad
            last_check = time.time()

        if gas_now:
            led_red.on()
            led_green.off()
            buzzer.off() if state["muted"] else buzzer.on()

        elif state["weather_bad"]:
            led_red.off()
            led_green.on()
            buzzer.off() if state["muted"] else buzzer.on()

        else:
            led_red.off()
            led_green.off()
            buzzer.off()
            state["muted"] = False   # 평상시로 돌아오면 음소거 초기화

        time.sleep(1)


# ========== Flask 라우트 ==========
@app.route('/')
def home():
    return render_template("index.html", state=state)


@app.route('/mute', methods=['POST'])
def mute():
    state["muted"] = True
    buzzer.off()
    return home()


if __name__ == "__main__":
    t = threading.Thread(target=sensor_loop, daemon=True)
    t.start()
    app.run(host="0.0.0.0", port=80)
