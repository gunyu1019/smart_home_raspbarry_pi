import RPi.GPIO as gpio
from flask import Blueprint
from flask import jsonify
from flask import make_response
from flask import request as req

from config.config import get_config

parser = get_config()


class Light(Blueprint):
    def __init__(self):
        super(Light, self).__init__(
            name="light",
            import_name="light",
            url_prefix="/light"
        )
        self.power_status = 0

        self.add_url_rule("/power", "get_power", view_func=self.get_led_power)
        self.add_url_rule("/power/set", "set_power", view_func=self.set_led_power)

        self.led_pin = parser.getint('port', 'led_pin')

        gpio.setup(self.led_pin, gpio.OUT)

    def get_led_power(self):
        return make_response(jsonify(self.power_status), 200)

    def control_relay(self, value):
        gpio.output(self.led_pin, int(value))

    def set_led_power(self):
        status = int(req.args.get('status', not self.get_led_power()))
        self.power_status = status
        self.control_relay(self.power_status)
        return make_response("OK", 200)


def setup(app):
    app.register_blueprint(Light())
