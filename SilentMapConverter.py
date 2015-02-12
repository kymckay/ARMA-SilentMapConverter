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

#Define side dictionary used to translate config to code
sideDict = {
    "EAST": "east",
    "WEST": "west",
    "GUER": "independent",
    "CIV": "civilian",
    "LOGIC": "sideLogic"
}

#Compile commonly used regex objects
reTopLevel = re.compile(r"^\tclass\s(Groups|Vehicles|Markers|Sensors).+?^\t\};",re.I|re.M|re.S)
reSubLevel = re.compile(r"^\t\tclass\sItem(\d+).+?^\t\t\};",re.I|re.M|re.S)

reGroupSide = re.compile(r"^\t{3}side=\"(.+)\";",re.I|re.M)
reGroupTop = re.compile(r"^\t{3}class\s(Vehicles|Waypoints).+?^\t{3}\};",re.I|re.M|re.S)
reGroupSub = re.compile(r"^\t{4}class\sItem(\d+).+?^\t{4}\};",re.I|re.M|re.S)

#Define common function for reporting malformed sqm file
def malformed(reason):
    return "// Error: SQM file is malformed, {0}\n".format(reason)

#Define processing functions for later (they all take a list of match objects)
def procGroups(groupsList):
    returnString = ""
    for group in groupsList:
        #Extract index of the group
        groupIndex = group.group(1)

        #Extract and verify group side
        groupSide = reGroupSide.search(group.group(0)).group(1)
        if groupSide in sideDict:
            groupSide = sideDict[groupSide]
        else:
            return malformed("group {0} uses unknown side {1}".format(groupIndex,groupSide))

        #Extract the units and waypoints subclasses of the group
        groupSections = list(reGroupTop.finditer(group.group(0)))
        if groupSections:
            groupUnits = []
            groupWaypoints = []
            for section in groupSections:
                if section.group(1) == "Vehicles":
                    groupUnits = list(reGroupSub.finditer(section.group(0)))
                elif section.group(1) == "Waypoints":
                    groupWaypoints = list(reGroupSub.finditer(section.group(0)))
        else:
            return malformed("group {0} has no subclasses".format(groupIndex))

        #Process the units of the group, verify that it has any
        if groupUnits:
            returnString += "_group{0} = createGroup {1}\n".format(groupIndex,groupSide)
            #for unit in groupUnits:

        else:
            return malformed("group {0} has no units".format(groupIndex))

        #Process the waypoints of the group
        '''if groupWaypoints:
            for unit in groupUnits:
                unitPos ='''

    return returnString

def procVehicles(vehiclesList):
    returnString = ""
    return returnString

def procMarkers(markersList):
    returnString = ""
    return returnString

def procTriggers(triggersList):
    returnString = ""
    return returnString
#-------------------------------------------------------------------------------
#Main

#Retrieve directory the program is ran in
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

for fileName in sqmFiles:
    missionPath = scriptDirectory + "\\" + fileName
    #Make sure the file exists before opening to avoid errors
    if os.path.isfile(missionPath):
        # Initialise the output code with file header
        outputCode = "// Created by SMC v{0}\n\n".format(versionNum)

        #Open the file this way so that it closes automatically when done
        with open(missionPath) as missionFile:
            fileContents = missionFile.read()
            mainSections = []
            #Verify that the number of braces match
            if len(re.findall(r"{",fileContents)) == len(re.findall(r"}",fileContents)):
                # Extract the top-level sections of mission.sqm, returns an iterator of match objects so cast to list
                mainSections = list(reTopLevel.finditer(fileContents))
            else:
                outputCode += malformed("number of opening and closing braces isn't equal")
            #Clear file contents variable (unrequired from here)
            fileContents = None

        groupsCode = "// ---Groups---\n"
        vehiclesCode = "// ---Vehicles---\n"
        markersCode = "// ---Markers---\n"
        triggersCode = "// ---Triggers---\n"
        if mainSections:
            for currentSection in mainSections:
                #All sections use the same classname system
                sectionList = list(reSubLevel.finditer(currentSection.group(0)))
                if currentSection.group(1) == "Groups":
                    groupsCode += procGroups(sectionList)
                elif currentSection.group(1) == "Vehicles":
                    vehiclesCode += procVehicles(sectionList)
                elif currentSection.group(1) == "Markers":
                    markersCode += procMarkers(sectionList)
                elif currentSection.group(1) == "Sensors":
                    triggersCode += procTriggers(sectionList)
        else:
            outputCode += malformed("doesn't contain any data to convert")

        #Combine sqf code from each section in specific desirable order
        outputCode += markersCode + vehiclesCode + groupsCode + triggersCode

        #The written file should be created/overwritten in the same directory
        outputPath = scriptDirectory + "\\" + fileName[:len(fileName)-1] + "f"
        with open(outputPath, 'w') as outputFile:
            outputFile.write(outputCode)