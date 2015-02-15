SilentMapConverter
========================

## Overview
A program used to convert SQM files into SQF files for Arma (particularly useful for headless client missions).

This was my first programming project which I used in order to get comfortable with Python and various programming concepts.

## How to use
1. Place SMC in the same directory as the SQM file(s) to be converted.
2. Run SMC.
3. An SQF file with the same respective name will be created in the directory.
4. Open the file to check that there were no errors in conversion (SMC will create an error message at the top of the file).

The output SQF will be structured like so:

- Empty Vehicles/Objects
- Groups
  - Units
  - Waypoints
- Markers
- Triggers

## Functionality
SMC will ignore player units, units that belong to sideLogic (including modules) and anything with the description `!SMC`.

Below is a list of supported and unsupported SQM values. Keep this information in mind when designing your mission.
### Units/Objects

- [x] Name (Only available on the machine that runs the code, use publicVariable in unit's initialization field if required)
- [x] Position
- [x] Direction
- [x] Elevation (Arma 3 feature)
- [x] Placement radius
- [x] Condition of presence
- [x] Probability of presence
- [x] Initialization field (Executed after unit is created)
- [x] Rank
- [x] Skill
- [x] Health
- [x] Ammo
- [x] Fuel
- [x] Synchronized units

### Waypoints

- [x] Name (Arma 3 feature)
- [x] Position
- [x] Placement radius
- [ ] Unit attachment (Waypoints can't be attached to units created via script)

### Markers

- [ ] N/A

### Triggers

- [ ] N/A