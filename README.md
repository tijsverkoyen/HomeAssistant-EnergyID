# Home Assistant EnergyID Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

Integrate [EnergyID](https://www.energyid.eu/) into you Home Assistant.

## Installation
At this point the integration is not part of the default HACS repositories, so
you will need to add this repository as a custom repository in HACS.

When this is done, just install the repository.

The configuration happens in the configuration flow when you add the integration.


## Sensors
For each meter in EnergyID there will be a sensor for the:

* latest/current reading
* previous reading

These will be updated every 15 minutes.


## Services
### set_meter_reading
This services allows you to add a meter reading from within Home Assistant.