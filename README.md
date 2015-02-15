SilentMapConverter
========================

# Overview
A program used to convert SQM files into SQF files for Arma (particularly useful for headless client missions). This was my first programming project which I used in order to get comfortable with Python and various programming concepts.

# How to use
When SMC is ran, all SQM files in the same directory will be converted. The output SQF files will be created in the same directory with the same names respectively.
Works with both Arma 2 and 3 standard SQM files.

# Functionality
SMC will ignore player units, units that belong to sideLogic (including modules) and anything with the description "!SMC".

Below is a list of supported and unsupported SQM values. Keep this information in mind when designing your mission.

## Units/Objects

- [x] Name (Won't be available on all machines, use publicVariable in unit's initialization field to achieve this)
- [x] Position
- [x] Direction
- [x] Elevation (Arma 3)
- [x] Placement radius
- [x] Condition of presence
- [x] Probability of presence
- [x] Initialization field (Executed after unit is created)
- [x] Rank
- [x] Skill
- [x] Health
- [x] Ammo
- [x] Fuel

## Waypoints

- [x] Name (Arma 3)
- [x] Position
- [x] Placement radius
- [ ] Unit attachment (Can't be done due to engine limitation)

## Markers

- [ ] N/A

## Triggers

- [ ] N/A