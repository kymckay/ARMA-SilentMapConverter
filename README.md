SilentMapConverter
========================

***Overview***  
A program used to convert .sqm files into .sqf files for Arma (useful for headless client missions). This was my first programming project which I used in order to get comfortable with Python and various programming concepts.

***What it does***  
When the program is ran, all .sqm files in the same directory will be converted. The output .sqf files will be created in the same directory with the same names respectively.
Works with both Arma 2 and 3.

***How it works***  
Under the hood I'm simply using regex to find and extract the needed details for each sqf scripting command. The hardest part of approaching this project was figuring out how best to read and process the file.
