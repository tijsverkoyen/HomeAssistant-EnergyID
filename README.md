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

### EnergyID Premium and Premium HR
The following will only be available for Premium and Premium HR users.

For each meter in EnergyID there will be a sensor for the:

* current month Peak Power Power (kW)
* last month Peak Power Power (kW)
* current month Peak Power Datetime 
* last month Peak Power Datetime 

## Services
### set_meter_reading
This services allows you to add a meter reading from within Home Assistant.


## FAQ
### Where can I find the Record ID?

* Log into [EnergyID](https://app.energyid.eu/)
* Select your Record
* You will end up on an URL like: `https://app.energyid.eu/record/EA-12345678/meters`
* The record ID is the part after `/record/` and before `/meters`, so in this example `EA-12345678`.