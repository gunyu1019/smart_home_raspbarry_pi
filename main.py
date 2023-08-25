import RPi.GPIO as gpio
import importlib.util
import logging
import os
import sys

from flask import Flask
from directory import directory


if __name__ == "__main__":
    app = Flask(__name__)
    environment = app.config.get("ENV")
    app.config['JSON_AS_ASCII'] = False
    log = logging.getLogger("app.create_app")

    gpio.setmode(gpio.BCM)

    views = [
        "views." + file[:-3] for file in os.listdir(
            os.path.join(directory, "views")
        ) if file.endswith(".py")
    ]
    for view in views:
        spec = importlib.util.find_spec(view)
        if spec is None:
            log.error("Extension Not Found: {0}".format(view))
            continue

        lib = importlib.util.module_from_spec(spec)
        sys.modules[view] = lib
        try:
            spec.loader.exec_module(lib)  # type: ignore
        except Exception as e:
            log.error("Extension Failed: {0} ({1})".format(view, e.__class__.__name__))
            del sys.modules[view]
            continue

        try:
            setup = getattr(lib, 'setup')
        except AttributeError:
            log.error("No Entry Point Error: {0}".format(view))
            del sys.modules[view]
            continue

        try:
            setup(app)
        except Exception as e:
            log.error("Extension Failed: {0} ({1})".format(view, e.__class__.__name__))
            del sys.modules[view]
            continue

    app.run(host='0.0.0.0', port=8000)
