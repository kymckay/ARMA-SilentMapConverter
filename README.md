Arma2-SilentMapConverter
========================

***Overview***  
A program used to convert .sqm files into .sqf files for Arma 2 (useful for headless client setups). This is my first programming project which I hope to use in order to get comfortable with Python and various concepts.

***What it does***  
When the program is ran, all .sqm files in the same directory will be read. The output .sqf files will be created in the same directory with the same names respectively.

***How it works***  
Under the hood I'm simply using regex to find and extract the needed details for each sqf scripting command. The hardest part of approaching this project is figuring out how best to read and process the file. Currently I am reading it line-by-line and creating each innermost class one at a time for processing.
