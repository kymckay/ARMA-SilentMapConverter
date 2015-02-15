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
import os, re, sys, time

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

reGroupTop = re.compile(r"^\t{3}class\s(Vehicles|Waypoints).+?^\t{3}\};",re.I|re.M|re.S)
reGroupSub = re.compile(r"^\t{4}class\sItem(\d+).+?^\t{4}\};",re.I|re.M|re.S)

#Define common function for reporting malformed sqm file
def malformed(reason):
    return "// Error: SQM file is malformed, {0}".format(reason)

#Returns first group of match if match made, otherwise default value
def matchValue(valueType,value,item,default):
    #Numerical config values
    if valueType == 0:
        match = re.search(value + r"=(\d+(\.\d+)?);",item,re.I)
    #String config entries
    elif valueType == 1:
        match = re.search(value + r"=\"(.+)\";",item,re.I)
    #Array config entries
    elif valueType == 2:
        match = re.search(value + r"\[\]=\{(.+)\};",item,re.I)
    else:
        return default

    if match:
        return match.group(1)
    else:
        return default

#Store created sync IDs
def syncList(syncID):
    if not hasattr(syncList, "idList"):
        syncList.idList = []  # it doesn't exist yet, so initialize it
    if syncID:
        syncList.idList.append(syncID)
    return syncList.idList

#Define processing functions for later (they all take a list of match objects)
def procGroups(groupsList):
    returnCode = "// --Groups--\n"
    unitCode = "// -Units-\n"
    wpCode = "// -Waypoints-\n"
    for group in groupsList:
        #Extract index of the group
        groupIndex = group.group(1)
        group = group.group(0)

        #Extract and verify group side
        groupSide = matchValue(1,"side",group,"")
        if groupSide:
            if groupSide in sideDict:
                groupSide = sideDict[groupSide]
            else:
                return malformed("group {0} uses unknown side {1}".format(groupIndex,groupSide))
        else:
            return malformed("group {0} has no assigned side".format(groupIndex,groupSide))

        #Extract the units and waypoints subclasses of the group
        groupSections = list(reGroupTop.finditer(group))
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

        #Process the units of the group if applicable
        if groupUnits and (groupSide != "sideLogic"):
            unitCode += "_group{0} = createGroup {1};\n".format(groupIndex,groupSide)
            for unit in groupUnits:
                unitIndex = unit.group(1)
                unit = unit.group(0)

                unitPlayer = matchValue(1,"player",unit,"")
                unitDesc = matchValue(1,"description",unit,"")
                #Player and marked units should be skipped
                if not (unitPlayer or (unitDesc == "!SMC")):
                    #Required unit values
                    unitID = matchValue(0,"id",unit,"")
                    unitType = matchValue(1,"vehicle",unit,"")
                    unitPos = matchValue(2,"position",unit,"")

                    #Optional unit values
                    unitAmmo = matchValue(0,"ammo",unit,"")
                    unitCond = matchValue(1,"presenceCondition",unit,"")
                    unitChance = matchValue(0,"presence",unit,"")
                    unitDir = matchValue(0,"azimut",unit,"")
                    unitFuel = matchValue(0,"fuel",unit,"")
                    unitHP = matchValue(0,"health",unit,"")
                    unitInit = matchValue(1,"init",unit,"")
                    unitLock = matchValue(1,"lock",unit,"")
                    unitName = matchValue(1,"text",unit,"")
                    unitOff = matchValue(0,"offsetY",unit,"")
                    unitRadius = matchValue(0,"placement",unit,"0")
                    unitRank = matchValue(1,"rank",unit,"")
                    unitSkill = matchValue(0,"skill",unit,"0.60000002")
                    unitSpecial = matchValue(1,"special",unit,"FORM")
                    unitSyncID = matchValue(0,"syncId",unit,"")
                    unitSyncs = matchValue(2,"synchronizations",unit,"")


                    #Unit must have an ID number (to generate variable)
                    if unitID:
                        if unitName:
                            unitVariable = unitName
                        else:
                            unitVariable = "_unit{0}".format(unitID)
                    else:
                        return malformed("unit {0} in group {1} has no id number".format(unitIndex,groupIndex))

                    #Build the unit presence condition
                    if unitCond and unitChance:
                        #Only useful to 2 DP
                        unitChance = str(round(float(unitChance),2))
                        #Strings all the way down
                        unitCond = unitCond.replace("\"\"","\"")
                        unitCode += "if (({0}) && (random 1 < {1})) then {{\n".format(unitCond,unitChance)
                    elif unitCond:
                        unitCond = unitCond.replace("\"\"","\"")
                        unitCode += "if ({0}) then {{\n".format(unitCond)
                    elif unitChance:
                        unitChance = str(round(float(unitChance),2))
                        unitCode += "if (random 1 < {0}) then {{\n".format(unitChance)

                    #Create the unit
                    if unitType:
                        if unitPos:
                            #Z and Y coordinates flipped in SQM, split string
                            unitPos = unitPos.split(",")
                            if len(unitPos) == 3:
                                unitPos.append(unitPos.pop(1))
                            else:
                                return malformed("unit {0} in group {1} has invalid position coordinates".format(unitIndex,groupIndex))

                            #Join list back into position string
                            unitPos = ",".join(unitPos)

                            unitCode += "\t{0} = _group{1} createUnit [\"{2}\",[{3}],[],{4},\"{5}\"];\n".format(unitVariable,groupIndex,unitType,unitPos,unitRadius,unitSpecial)
                            #Vehicles can't be created as units, use BIS func for backwards compatibility
                            unitCode += "\tif (isNull {0}) then {{{0} = createVehicle [\"{1}\",[{2}],[],{3},\"{4}\"]; [{0},_group{5}] call BIS_fnc_spawnCrew;}};\n".format(unitVariable,unitType,unitPos,unitRadius,unitSpecial,groupIndex)
                        else:
                            return malformed("unit {0} in group {1} has no position".format(unitIndex,groupIndex))
                    else:
                        return malformed("unit {0} in group {1} has no classname".format(unitIndex,groupIndex))

                    #Set and broadcast unit name
                    if unitName:
                        unitCode += "\t\t{0} setVehicleVarName \"{1}\";\n".format(unitVariable,unitName)

                    #Unit syncID (assign standardised var for synchronization)
                    if unitSyncID:
                        unitCode += "\t\tSMC_sync{0} = {1};\n".format(unitSyncID,unitVariable)
                        #Store syncID if created (can check that it exists)
                        syncList(unitSyncID)

                        #Syncronize unit, only possible with syncID
                        if unitSyncs:
                            unitSyncs = unitSyncs.split(",")
                            validSyncs = []
                            #Build list of IDs that have been created earlier
                            for sync in unitSyncs:
                                if sync in syncList(""):
                                    sync = "SMC_sync{0}".format(sync)
                                    validSyncs.append(sync)
                            if validSyncs:
                                validSyncs = ",".join(validSyncs)
                                unitCode += "\t\t{0} synchronizeObjectsAdd [{1}]\n".format(unitVariable,validSyncs)

                    #Unit heading
                    if unitDir:
                        unitCode += "\t\t{0} setDir {1};\n".format(unitVariable,unitDir)

                    #Unit elevation offset (Arma 3)
                    if unitOff:
                        unitPos = unitPos.split(",")
                        unitPos.pop(2)
                        unitPos.append(unitOff)
                        unitPos = ",".join(unitPos)
                        unitCode += "\t\t{0} setPosATL [{1}];\n".format(unitVariable,unitPos)

                    #Unit skill
                    if unitSkill:
                        if unitSkill != "0.60000002":
                            unitCode += "\t\t{0} setSkill {1};\n".format(unitVariable,unitSkill)

                    #Unit rank
                    if unitRank:
                        unitRank = unitRank.upper()
                        unitCode += "\t\t{0} setRank \"{1}\";\n".format(unitVariable,unitRank)

                    #Unit lock
                    if unitLock:
                        unitLock = unitLock.upper()
                        unitCode += "\t\t{0} setVehicleLock \"{1}\";\n".format(unitVariable,unitLock)

                    #Unit fuel
                    if unitFuel:
                        unitCode += "\t\t{0} setFuel {1};\n".format(unitVariable,unitFuel)
                    #Unit ammo
                    if unitAmmo:
                        unitCode += "\t\t{0} setVehicleAmmo {1};\n".format(unitVariable,unitAmmo)
                    #Unit health
                    if unitHP:
                        unitHP = 1 - float(unitHP)
                        unitCode += "\t\t{0} setDamage {1};\n".format(unitVariable,unitHP)

                    #Run init lines inline
                    if unitInit:
                        #Strings all the way down
                        unitInit = unitInit.replace("\"\"","\"")
                        unitInit = unitInit.replace("this",unitVariable)
                        if unitInit[len(unitInit) - 1] != ";":
                            unitInit = unitInit + ";"
                        unitCode += "\t\t{0}\n".format(unitInit)

                    #Must close condition block if present
                    if unitCond or unitChance:
                        unitCode += "};\n"

            #Process the waypoints of the group (only if units exist)
            if groupWaypoints:
                for wp in groupWaypoints:
                    wpIndex = wp.group(1)
                    wp = wp.group(0)

                    wpDesc = matchValue(1,"description",wp,"")
                    if wpDesc != "!SMC":
                        #Required waypoint values
                        wpPos = matchValue(2,"position",wp,"")

                        #Optional waypoint values
                        wpName = matchValue(1,"name",wp,"")
                        wpRadius = matchValue(0,"placement",wp,"0")
                        wpType = matchValue(1,"type",wp,"")

                        #Waypoint variable
                        wpVariable = "_wp{0}{1}".format(groupIndex,wpIndex)

                        #Create the waypoint
                        if wpPos:
                            #Z and Y coordinates flipped in SQM, split string
                            wpPos = wpPos.split(",")
                            if len(wpPos) == 3:
                                wpPos.append(wpPos.pop(1))
                            else:
                                return malformed("waypoint {0} in group {1} has invalid position coordinates".format(wpIndex,groupIndex))

                            #Join list back into position string
                            wpPos = ",".join(wpPos)

                            wpCode += "\t{0} = _group{1} addWaypoint [[{2}],{3}];\n".format(wpVariable,groupIndex,wpPos,wpRadius)
                        else:
                            return malformed("waypoint {0} in group {1} has no position".format(wpIndex,groupIndex))

                        #Waypoint name
                        if wpName:
                            wpCode += "\t\t{0} setWaypointName \"{1}\";\n".format(wpVariable,wpName)

    #Create all units then all waypoints
    returnCode += unitCode + wpCode
    return returnCode

def procVehicles(vehiclesList):
    returnCode = "// --Vehicles--\n"

    for veh in vehiclesList:
        #Extract index of the vehicle
        vehIndex = veh.group(1)
        veh = veh.group(0)

        vehDesc = matchValue(1,"description",veh,"")
        if vehDesc != "!SMC":
            #Required vehicle values
            vehType = matchValue(1,"vehicle",veh,"")
            vehPos = matchValue(2,"position",veh,"")

            #Optional vehicle values
            vehAmmo = matchValue(0,"ammo",veh,"")
            vehCond = matchValue(1,"presenceCondition",veh,"")
            vehChance = matchValue(0,"presence",veh,"")
            vehDir = matchValue(0,"azimut",veh,"")
            vehFuel = matchValue(0,"fuel",veh,"")
            vehHP = matchValue(0,"health",veh,"")
            vehInit = matchValue(1,"init",veh,"")
            vehLock = matchValue(1,"lock",veh,"")
            vehName = matchValue(1,"text",veh,"")
            vehOff = matchValue(0,"offsetY",veh,"")
            vehRadius = matchValue(0,"placement",veh,"0")
            vehSpecial = matchValue(1,"special",veh,"FORM")

            #Vehicle variable
            if vehName:
                vehVariable = vehName
            else:
                vehVariable = "_veh{0}".format(vehIndex)

            #Build the vehicle presence condition
            if vehCond and vehChance:
                #Only useful to 2 DP
                vehChance = str(round(float(vehChance),2))
                #Strings all the way down
                vehCond = vehCond.replace("\"\"","\"")
                returnCode += "if (({0}) && (random 1 < {1})) then {{\n".format(vehCond,vehChance)
            elif vehCond:
                vehCond = vehCond.replace("\"\"","\"")
                returnCode += "if ({0}) then {{\n".format(vehCond)
            elif vehChance:
                vehChance = str(round(float(vehChance),2))
                returnCode += "if (random 1 < {0}) then {{\n".format(vehChance)

            #Create the vehicle
            if vehType:
                if vehPos:
                    #Z and Y coordinates flipped in SQM, split string
                    vehPos = vehPos.split(",")
                    if len(vehPos) == 3:
                        vehPos.append(vehPos.pop(1))
                    else:
                        return malformed("vehicle {0} has invalid position coordinates".format(vehIndex))

                    #Join list back into position string
                    vehPos = ",".join(vehPos)

                    returnCode += "\t{0} = createVehicle [\"{1}\",[{2}],[],{3},\"{4}\"];\n".format(vehVariable,vehType,vehPos,vehRadius,vehSpecial)
                else:
                    return malformed("vehicle {0} has no position".format(vehIndex))
            else:
                return malformed("vehicle {0} has no classname".format(vehIndex))

            #Set and broadcast vehicle name
            if vehName:
                returnCode += "\t\t{0} setVehicleVarName \"{1}\";\n".format(vehVariable,vehName)

            #Vehicle heading
            if vehDir:
                returnCode += "\t\t{0} setDir {1};\n".format(vehVariable,vehDir)

            #Vehicle elevation offset (Arma 3)
            if vehOff:
                vehPos = vehPos.split(",")
                vehPos.pop(2)
                vehPos.append(vehOff)
                vehPos = ",".join(vehPos)
                returnCode += "\t\t{0} setPosATL [{1}];\n".format(vehVariable,vehPos)

            #Vehicle lock
            if vehLock:
                vehLock = vehLock.upper()
                returnCode += "\t\t{0} setVehicleLock \"{1}\";\n".format(vehVariable,vehLock)

            #Vehicle fuel
            if vehFuel:
                returnCode += "\t\t{0} setFuel {1};\n".format(vehVariable,vehFuel)
            #Vehicle ammo
            if vehAmmo:
                returnCode += "\t\t{0} setVehicleAmmo {1};\n".format(vehVariable,vehAmmo)
            #Vehicle health
            if vehHP:
                vehHP = 1 - float(vehHP)
                returnCode += "\t\t{0} setDamage {1};\n".format(vehVariable,vehHP)

            #Run init lines inline
            if vehInit:
                #Strings all the way down
                vehInit = vehInit.replace("\"\"","\"")
                vehInit = vehInit.replace("this",vehVariable)
                if vehInit[len(vehInit) - 1] != ";":
                    vehInit = vehInit + ";"
                returnCode += "\t\t{0}\n".format(vehInit)

            #Must close condition block if present
            if vehCond or vehChance:
                returnCode += "};\n"

    return returnCode

def procMarkers(markersList):
    returnCode = "// --Markers--\n"
    return returnCode

def procTriggers(triggersList):
    returnCode = "// --Triggers--\n"
    return returnCode
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
        outputCode = "// Created by SMC v{0}\n".format(versionNum)
        outputCode += "// {0}\n\n".format(time.strftime("%c"))

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

        groupsCode = ""
        vehiclesCode = ""
        markersCode = ""
        triggersCode = ""
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

        #Verify that valid code was returned
        validCode = ""
        #If section was malformed then include error message at top
        for code in [markersCode,vehiclesCode,groupsCode,triggersCode]:
            if re.match(r"//\sError:",code,re.I):
                outputCode += code + "\n"
            else:
                validCode += code

        #Combine valid sqf code from each section with output code
        outputCode += validCode

        #The written file should be created/overwritten in the same directory
        outputPath = scriptDirectory + "\\" + fileName[:len(fileName)-1] + "f"
        with open(outputPath, 'w') as outputFile:
            outputFile.write(outputCode)