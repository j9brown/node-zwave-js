# Poppy Enclosure Surrogate

Allows [Poppy](https://github.com/j9brown/poppy) to integrate with
[OctoDash](https://unchartedbull.github.io/OctoDash/) as a replacement for the
[Enclosure](https://plugins.octoprint.org/plugins/enclosure/) plug-in (which is no longer supported).

OctoDash relies on the Enclosure plug-in to get the current temperature
of the printing enclosure and to control the LEDs. OctoDash currently doesn't
support using Poppy instead of Enclosure so the Poppy Enclosure Surrogate plug-in
bridges the gap by emulating the Enclosure plug-in's API.

This plug-in requires the Poppy plug-in into be installed. It is incompatible with
the Enclosure plug-in so uninstall the Enclosure plug-in prior to installing this one.

## Setup

Install via the bundled [Plugin Manager](https://docs.octoprint.org/en/master/bundledplugins/pluginmanager.html)
or manually using this URL:

    https://github.com/j9brown/poppy-enclosure-surrogate/archive/master.zip

## Configuration

After installing this plug-in, configure OctoDash as follows to complete the integration.

1. Set the OctoDash `Ambient Sensor ID` parameter to `1` to display the enclosure temperature in the OctoDash user interface.

1. Create OctoDash actions to control the enclosure's lights from the OctoDash user interface using the following OctoDash command syntax.

   * Turn off the lights: `[!NEOPIXEL]2,0,0,0`
   * Set brightness to low: `[!NEOPIXEL]2,1,0,0`
   * Set brightness to medium: `[!NEOPIXEL]2,2,0,0`
   * Set brightness to high: `[!NEOPIXEL]2,3,0,0`
