#-------------------------------------------------------------------------------
# Name:        SilentMapConverter
# Purpose:     Convert arma 2 mission files into an sqf script files
#
# Author:      SilentSpike
#
# Created:     17/10/2014
# Copyright:   (c) SilentSpike 2014
# Licence:     GNU GPL v3.0
#-------------------------------------------------------------------------------
versionNum = "2.0.0"

#Import needed libraries
import os, re, sys

#Path to .sqm files required for reading
#Mission files should be in same directroy as script
if hasattr(sys, 'frozen'):
    scriptDirectory = os.path.dirname(os.path.realpath(sys.argv[0])) #For compilation - sys.frozen only exists in the .exe
else:
    scriptDirectory = os.path.dirname(os.path.realpath(__file__)) #For testing in script form
sqmFiles = []
for fileName in os.listdir(scriptDirectory):
    if fileName[len(fileName)-4:] == ".sqm":
        sqmFiles.append(fileName)
scriptDirectory += "\\"

for fileName in sqmFiles:
    missionPath = scriptDirectory + fileName
    #Make sure the file exists before opening to avoid errors
    if os.path.isfile(missionPath):
        # Initialise the output string with file header
        outputString = "// Created by SMC v{0}\nprivate [\"_currentGroup\",\"_currentUnit\",\"_currentWaypoint\"];\n\n".format(versionNum)

        #Open the file this way so that it closes automatically when done
        with open(missionPath) as missionFile:
            # Extract the top-level sections of mission.sqm, returns an iterator of match objects
            mainSections = re.finditer(r"^\tclass\s(Groups|Vehicles|Markers|Sensors).+?^\t};",missionFile.read(),re.I|re.M|re.S)

        # Convert interator into list for ease of use
        mainSections = list(mainSections)

        for currentSection in mainSections:
            outputString += currentSection.group(0) + "\n"

        #The written file should be created/overwritten in the same directory
        outputPath = scriptDirectory + fileName[:len(fileName)-1] + "f"
        with open(outputPath, 'w') as outputFile:
            outputFile.write(outputString)