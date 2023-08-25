import RPi.GPIO as GPIO
import time
import adafruit_dht
from picamera import PiCamera

# GPIO 핀 설정
servo_pin = 18
dht_pin = 3
vibration_pin = 23
relay_pin = 14

# DHT22 센서 설정
dht_sensor = adafruit_dht.DHT22(dht_pin)

# 카메라 초기화
camera = PiCamera()

# GPIO 설정 초기화
def initialize_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(servo_pin, GPIO.OUT)
    GPIO.setup(vibration_pin, GPIO.IN)
    GPIO.setup(relay_pin, GPIO.OUT)

# 서보 모터 초기화 및 제어 함수
def initialize_servo():
    pwm = GPIO.PWM(servo_pin, 50)  # 50Hz PWM 주파수
    pwm.start(0)  # PWM 듀티 사이클을 0으로 초기화
    return pwm

def set_servo_angle(pwm, angle):
    duty = angle / 18 + 2
    GPIO.output(servo_pin, True)
    pwm.ChangeDutyCycle(duty)
    time.sleep(1)
    GPIO.output(servo_pin, False)
    pwm.ChangeDutyCycle(0)

# 진동 센서 읽기 함수
def read_vibration_sensor():
    vibration_value = GPIO.input(vibration_pin)
    return vibration_value

# 릴레이 제어 함수
def control_relay(value):
    GPIO.output(relay_pin, value)

# 메인 함수
def main():
    try:
        initialize_gpio()
        pwm = initialize_servo()

        while True:
            vibration_value = read_vibration_sensor()
            if vibration_value:
                print("Vibration detected!")
            else:
                print("No vibration")

            control_relay(not vibration_value)

            set_servo_angle(pwm, 0)  # 0도로 초기 위치
            time.sleep(1)
            set_servo_angle(pwm, 180)  # 180도 회전
            time.sleep(3)  # 3초간 유지
            set_servo_angle(pwm, 0)  # 다시 0도로 회전
            time.sleep(1)

            try:
                humidity = dht_sensor.humidity
                temperature = dht_sensor.temperature
                print(f"Temperature: {temperature:.2f}°C, Humidity: {humidity:.2f}%")
            except RuntimeError as e:
                print("Failed to retrieve data from DHT sensor:", str(e))

            camera.start_recording('video.h264')
            time.sleep(5)  # 5초간 녹화
            camera.stop_recording()

    except KeyboardInterrupt:
        pass

    finally:
        pwm.stop()
        GPIO.cleanup()
        camera.close()

if __name__ == "__main__":
    main()