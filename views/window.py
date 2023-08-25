import time

import RPi.GPIO as gpio
from flask import Blueprint
from flask import make_response

from config.config import get_config

parser = get_config()


class Window(Blueprint):
    def __init__(self):
        super(Window, self).__init__(
            name="window",
            import_name="window",
            url_prefix="/window"
        )
        self.pwm = None

        self.add_url_rule("/open", "open_window", view_func=self.window_open)
        self.add_url_rule("/close", "close_window", view_func=self.window_close)

        self.servo_pin = parser.getint('port', 'servo_pin')

        gpio.setup(self.servo_pin, gpio.OUT)
        self.initialize_servo()

    def initialize_servo(self):
        pwm = self.pwm = gpio.PWM(self.servo_pin, 50)  # 50Hz PWM 주파수
        pwm.start(0)  # PWM 듀티 사이클을 0으로 초기화
        return pwm

    def set_servo_angle(self, angle):
        duty = angle / 18 + 2
        gpio.output(self.servo_pin, True)
        self.pwm.ChangeDutyCycle(duty)
        time.sleep(1)
        gpio.output(self.servo_pin, False)

    def window_control_base(self, status: bool):
        angle = 330 if status else 0
        self.set_servo_angle(angle)

    def window_open(self):
        self.window_control_base(True)
        return make_response("OK", 200)

    def window_close(self):
        self.window_control_base(False)
        return make_response("OK", 200)


def setup(app):
    app.register_blueprint(Window())
