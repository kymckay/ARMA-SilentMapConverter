#-------------------------------------------------------------------------------
# Name:        SilentMapConverter
# Purpose:     Converts arma mission files into sqf script files.
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

#Define functions for later
def procGroups(groupsList):
    returnString = "// ---Groups---\n"
    return returnString

def procVehicles(vehiclesList):
    returnString = "// ---Vehicles---\n"
    return returnString

def procMarkers(markersList):
    returnString = "// ---Markers---\n"
    return returnString

def procTriggers(triggersList):
    returnString = "// ---Triggers---\n"
    return returnString
#-------------------------------------------------------------------------------
#Main

#Retrieve directory program is ran in
if hasattr(sys, 'frozen'):
    #For use as an executable - sys.frozen only exists in the .exe
    scriptDirectory = os.path.dirname(os.path.realpath(sys.argv[0]))
else:
    #For use in script form
    scriptDirectory = os.path.dirname(os.path.realpath(__file__))

#Produce an array of sqm files in the directory
sqmFiles = []
for fileName in os.listdir(scriptDirectory):
    if fileName[len(fileName)-4:] == ".sqm":
        sqmFiles.append(fileName)
scriptDirectory += "\\"

for fileName in sqmFiles:
    missionPath = scriptDirectory + fileName
    #Make sure the file exists before opening to avoid errors
    if os.path.isfile(missionPath):
        # Initialise the output code with file header
        outputCode = "// Created by SMC v{0}\nprivate [\"_currentGroup\",\"_currentUnit\",\"_currentWaypoint\"];\n\n".format(versionNum)

        #Open the file this way so that it closes automatically when done
        with open(missionPath) as missionFile:
            # Extract the top-level sections of mission.sqm, returns an iterator of match objects so cast to list
            mainSections = list(re.finditer(r"^\tclass\s(Groups|Vehicles|Markers|Sensors).+?^\t};",missionFile.read(),re.I|re.M|re.S))

        for currentSection in mainSections:
            sectionList = list(re.finditer(r"^\t\tclass\sItem(\d+).+?^\t\t};",currentSection.group(0),re.I|re.M|re.S))
            if currentSection.group(1) == "Groups":
                groupsCode = procGroups(sectionList)
            elif currentSection.group(1) == "Vehicles":
                vehiclesCode = procVehicles(sectionList)
            elif currentSection.group(1) == "Markers":
                markersCode = procMarkers(sectionList)
            elif currentSection.group(1) == "Sensors":
                triggersCode = procTriggers(sectionList)

        #Combine sqf code from each section in specific desirable order
        outputCode += markersCode + vehiclesCode + groupsCode + triggersCode

        #The written file should be created/overwritten in the same directory
        outputPath = scriptDirectory + fileName[:len(fileName)-1] + "f"
        with open(outputPath, 'w') as outputFile:
            outputFile.write(outputCode)