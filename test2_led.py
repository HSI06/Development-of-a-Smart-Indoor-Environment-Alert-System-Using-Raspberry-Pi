from gpiozero import LED
import time

led_green = LED(16)
led_blue = LED(20)
led_red = LED(21)

print("LED 테스트 시작! 초록 -> 파랑 -> 빨강 순서로 2초씩 켜질거에요")

try:
    print("초록 LED ON")
    led_green.on()
    time.sleep(2)
    led_green.off()

    print("파랑 LED ON")
    led_blue.on()
    time.sleep(2)
    led_blue.off()

    print("빨강 LED ON")
    led_red.on()
    time.sleep(2)
    led_red.off()

    print("테스트 완료!")

except KeyboardInterrupt:
    pass

led_green.off()
led_blue.off()
led_red.off()
