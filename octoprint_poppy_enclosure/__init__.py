# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin
from flask import make_response, Response
import json

_INPUT_ID_FAN_EXTERNAL_TEMPERATURE = 1
_OUTPUT_ID_LIGHTS = 2

class PoppyEnclosureSurrogatePlugin(
    octoprint.plugin.StartupPlugin,
    octoprint.plugin.BlueprintPlugin
):

    def __init__(self):
        self._poppy = {}

    def _get_input(self, identifier):
        self._logger.debug("get input %s", identifier)
        if identifier == _INPUT_ID_FAN_EXTERNAL_TEMPERATURE:
            if "get_fan_external_temperature" in self._poppy:
                return {
                    "index_id": identifier,
                    "temp_sensor_temp": self._poppy["get_fan_external_temperature"](),
                    "temp_sensor_humidity": 0,
                    "use_fahrenheit": False
                }
        return None

    def _set_output(self, identifier, value):
        self._logger.debug("set output %s, value %s", identifier, value)
        if identifier == _OUTPUT_ID_LIGHTS:
            self._logger.info("set lights %s", value)
            return True
        return False

    # ~~ Blueprintplugin mixin

    @octoprint.plugin.BlueprintPlugin.route("/inputs/<int:identifier>", methods=["GET"])
    def get_input_status(self, identifier):
        result = self._get_input(identifier)
        if result:
            return Response(json.dumps(result), mimetype='application/json')
        return make_response('', 404)

    @octoprint.plugin.BlueprintPlugin.route("/outputs/<int:identifier>", methods=["PATCH"])
    def set_output_status(self, identifier):
        return self._set_output_attrib(identifier, "status")

    @octoprint.plugin.BlueprintPlugin.route("/pwm/<int:identifier>", methods=["PATCH"])
    def set_output_pwm(self, identifier):
        return self._set_output_attrib(identifier, "duty_cycle")
    
    def _set_output_attrib(self, identifier, attrib):
        self._logger.info("YYY")
        if "application/json" not in request.headers["Content-Type"]:
            return make_response("expected json", 400)

        try:
            data = request.json
        except BadRequest:
            return make_response("malformed request", 400)

        if attrib not in data:
            return make_response("missing attribute in body", 406)

        value = 0
        try:
            value = int(data[attrib])
        except:
            return make_response("malformed attribute in body", 406)

        if self._set_output(identifier, value):
            return make_response('', 204)
        return make_response('', 404)

    ##~~ StartupPlugin mixin

    def on_startup(self, host, port):
        helpers = self._plugin_manager.get_helpers("poppy", "get_fan_external_temperature")
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
