Silent Map Converter
========================

## Overview
A program used to convert SQM files into SQF files for ARMA 2/3 (particularly useful for headless client missions).

This was my first programming project which I used in order to get comfortable with Python and various programming concepts.

As such, the program isn't a full blown SQM parser or anything particularly sophisticated. It simply uses regular expressions to find and extract the information it needs based on the standardised output of the ARMA mission editor.

Please note that if you have python installed then you can just run the script file itself. It behaves exactly the same as the executable.

## How to use
1. Place SMC in the same directory as the SQM file(s) to be converted.
2. Run SMC.
3. SQF file(s) with the same respective name(s) will be created in the directory.
4. Open the file(s) to check that there were no errors in conversion (SMC will create error messages with the prefix `// Error:`).

The output SQF will be structured like so:

- Markers
- Vehicles/Objects
- Units
- Waypoints
- Sensors

## Using SMC for a headless client
1. Create a mission as normal.
2. Make a copy of the mission and open it in the editor.
3. Delete everything you don't want to be created on the headless client (in general: anything that isn't AI).
4. Save this version of the mission and then convert the SQM file using SMC.
5. Remove everything that you want on the headless client from the original mission file (so that it isn't duplicated).
6. *Optional*: Store the headless client SQM file in the mission folder in case you need it again.
7. Set your mission up to execute the output SQF file on the headless client.

## Functionality
SMC will ignore player units, units that belong to sideLogic (including modules) and anything marked with `!SMC` (see list below for details).

Below is a list of supported and unsupported SQM values. Keep this information in mind when designing your mission.

- Units/Vehicles/Objects
  - [x] Description (used solely for `!SMC`)
  - [x] Condition of presence
  - [x] Probability of presence
  - [x] Name (only available on the machine that runs the code, use publicVariable in unit's initialization field if required elsewhere)
  - [x] Position
  - [x] Placement radius
  - [x] Special
  - [x] Synchronization
  - [x] Direction
  - [x] Elevation (A3 feature)
  - [x] Skill
  - [x] Rank
  - [x] Lock
  - [x] Fuel
  - [x] Ammo
  - [x] Health
  - [x] Initialization field (executed inline directly after unit is created)
- Waypoints
  - [x] Description (used solely for `!SMC`)
  - [x] Position
  - [x] Height
  - [x] Placement radius
  - [x] Synchronization
  - [ ] Unit attachment (waypoints can't be attached to units created via script)
  - [x] Static attachment
  - [x] Building position
  - [x] Type
  - [x] Condition
  - [x] On Activation
  - [x] Completion radius
  - [x] Timeout
  - [x] Combat mode
  - [x] Behaviour
  - [x] Speed
  - [x] Formation
  - [x] Name (A3 feature - not the same as a variable name)
  - [x] Visibility
  - [x] Script (and arguments)
- Markers
  - [x] Name
  - [x] Position
  - [x] Alpha
  - [x] Shape
  - [x] Type
  - [x] Angle
  - [x] Size
  - [x] Brush
  - [x] Colour
  - [x] Text (can use `!SMC` here, otherwise treated as expected)
- Sensors
  - [x] Text (used solely for `!SMC`)
  - [x] Name
  - [x] Position
  - [x] Synchronization
  - [x] Type
  - [x] Timeout
  - [x] Countdown
  - [x] Size
  - [x] Angle
  - [x] Shape
  - [x] Condition
  - [x] On Activation
  - [x] On Deactivation
  - [x] Activation
  - [x] Once/Repeatedly
  - [x] Present/Detected By
  
## Footnotes
* Originally written for the unit I play with. Come join us at http://www.reddit.com/r/clearbackblast
* Bohemia Interactive forum thread: http://forums.bistudio.com/showthread.php?189056-Silent-Map-Converter