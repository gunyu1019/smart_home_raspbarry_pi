import adafruit_dht
import RPi.GPIO as gpio
from flask import Blueprint
from flask import jsonify
from flask import make_response
from flask import request as req

from config.config import get_config

parser = get_config()


class AirCondition(Blueprint):
    def __init__(self):
        super(AirCondition, self).__init__(
            name="air_condition",
            import_name="air_condition",
                url_prefix="/air_condition"
        )
        self.power_status = 0

        self.add_url_rule("/power", "get_power", view_func=self.get_air_condition_power)
        self.add_url_rule("/power/set", "set_power", view_func=self.set_air_condition_power)
        self.add_url_rule("/status", "air_status", view_func=self.get_air_status)

        self.dht_pin = parser.getint('port', 'DHT_pin')
        self.relay_pin = parser.getint('port', 'relay_pin')
        self.dht_sensor = adafruit_dht.DHT11(self.dht_pin)

        gpio.setup(self.relay_pin, gpio.OUT)

    def get_air_condition_power(self):
        return make_response(jsonify(self.power_status), 200)

    @property
    def humidity(self):
        return self.dht_sensor.humidity

    @property
    def temperature(self):
        return self.dht_sensor.temperature

    def get_air_status(self):
        try:
            temp, humid = self.temperature, self.humidity
        except RuntimeError:
            return make_response(jsonify({
                "success": False,
                "message": "DHT sensor not found",
                "code": 1
            }), 500)
        return make_response(jsonify({
            "humidity": humid,
            "temperature": temp
        }), 200)

    def control_relay(self, value):
        gpio.output(self.relay_pin, int(value))

    def set_air_condition_power(self):
        status = int(req.args.get('status', not self.get_air_condition_power()))
        self.power_status = status
        self.control_relay(self.power_status)
        return make_response("OK", 200)


def setup(app):
    app.register_blueprint(AirCondition())
