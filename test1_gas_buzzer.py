from gpiozero import DigitalInputDevice, OutputDevice
import time

bz = OutputDevice(18)              # 부저 - GPIO 18
gas = DigitalInputDevice(17)       # 가스센서 - GPIO 17

print("테스트 시작! 라이터(불 붙이지 말고 가스만)나 알코올 솜을 센서에 가까이 대보세요.")
print("Ctrl+C로 종료")

try:
    while True:
        if gas.value == 0:             # LOW = 가스 감지됨
            print("🔥 가스 감지됨!")
            bz.on()
        else:
            print("정상")
            bz.off()
        time.sleep(0.3)

except KeyboardInterrupt:
    pass

bz.off()
print("종료")
