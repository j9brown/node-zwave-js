# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin
from flask import request, make_response, Response
import json

_ID_CHAMBER_TEMPERATURE = 1
_ID_CHAMBER_LIGHTING = 2

class PoppyEnclosureSurrogatePlugin(
    octoprint.plugin.StartupPlugin,
    octoprint.plugin.BlueprintPlugin
):

    def __init__(self):
        self._poppy = {}

    # Get input property.
    def _get_input(self, identifier):
        self._logger.debug("get input %s", identifier)
        if identifier == _ID_CHAMBER_TEMPERATURE:
            if "get_chamber_temperature" in self._poppy:
                return {
                    "index_id": identifier,
                    "temp_sensor_temp": self._poppy["get_chamber_temperature"](),
                    "temp_sensor_humidity": 0,
                    "use_fahrenheit": False
                }
        return None

    # Set an output with a boolean state.
    def _set_output_state(self, identifier, state):
        self._logger.debug("set output %s, state %s", identifier, state)

        # Fallback to output with floating-point duty cycle, if any.
        return self._set_output_level(identifier, float(state))

    # Set an output with a floating-point level between 0.0 and 1.0.
    def _set_output_level(self, identifier, level):
        self._logger.debug("set output %s, level %s", identifier, level)

        # No outputs yet, OctoDash v2.2.0 doesn't support sending this action.
        return False

    # Set an LED with RGB tuple components between 0 and 255.
    def _set_led_color(self, identifier, color):
        self._logger.debug("set led %s, color %s", identifier, color)
        if identifier == _ID_CHAMBER_LIGHTING:
            if "set_chamber_light_mode" in self._poppy:
                # Using red channel to set the mode
                self._poppy["set_chamber_light_mode"](color[0])
                return True
        return False

    # ~~ BlueprintPlugin mixin

    @octoprint.plugin.BlueprintPlugin.route("/inputs/<int:identifier>", methods=["GET"])
    def handle_input_request(self, identifier):
        result = self._get_input(identifier)
        if result:
            return Response(json.dumps(result), mimetype='application/json')
        return make_response('', 404)

    @octoprint.plugin.BlueprintPlugin.route("/outputs/<int:identifier>", methods=["PATCH"])
    def handle_output_request(self, identifier):
        state = self._parse_json_request(lambda x: bool(x["status"]))
        if not state:
            return make_response("malformed request", 400)
        if self._set_output_state(identifier, state):
            return make_response('', 204)
        return make_response('', 404)

    @octoprint.plugin.BlueprintPlugin.route("/pwm/<int:identifier>", methods=["PATCH"])
    def handle_pwm_request(self, identifier):
        level = self._parse_json_request(lambda x: float(x["duty_cycle"]))
        if not level:
            return make_response("malformed request", 400)
        if self._set_output_level(identifier, level):
            return make_response('', 204)
        return make_response('', 404)

    @octoprint.plugin.BlueprintPlugin.route("/neopixel/<int:identifier>", methods=["PATCH"])
    def handle_neopixel_request(self, identifier):
        color = self._parse_json_request(lambda x: (int(x["red"]), int(x["green"]), int(x["blue"])))
        if not color:
            return make_response("malformed request", 400)
        if self._set_led_color(identifier, color):
            return make_response('', 204)
        return make_response('', 404)

    def _parse_json_request(self, fn):
        if "application/json" not in request.headers["Content-Type"]:
            return None
        try:
            return fn(request.json)
        except:
            return None

    ##~~ StartupPlugin mixin

    def on_startup(self, host, port):
        helpers = self._plugin_manager.get_helpers("poppy",
                "get_chamber_temperature", "set_chamber_light_mode")
        if helpers:
            self._poppy = helpers
        else:
            self._logger.warning("This plug-in requires the poppy plug-in to be installed")

    ##~~ Softwareupdate hook

    def get_update_information(self):
        # Define the configuration for your plugin to use with the Software Update
        # Plugin here. See https://docs.octoprint.org/en/master/bundledplugins/softwareupdate.html
        # for details.
        return {
            "enclosure": {
                "displayName": "Poppy Enclosure Surrogate",
                "displayVersion": self._plugin_version,

                # version check: github repository
                "type": "github_release",
                "user": "j9brown",
                "repo": "poppy-enclosure-surrogate",
                "current": self._plugin_version,

                # update method: pip
                "pip": "https://github.com/j9brown/poppy-enclosure-surrogate/archive/{target_version}.zip",
            }
        }


__plugin_pythoncompat__ = ">=3,<4" # only python 3

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = PoppyEnclosureSurrogatePlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }
