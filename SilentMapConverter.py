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
versionNum = "2.0.3"

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

#Define common function for reporting malformed sqm file
def malformed(reason):
    return "// Error: SQM file is malformed, {0}\n".format(reason)

#Returns first group of match if match made, otherwise default value
def matchValue(valueType,value,item,default):
    #Numerical config values
    if valueType == 0:
        match = re.search(r"\b" + value + r"=(-?\d+(\.\d+)?(e[+-]\d+)?);",item,re.I)
    #String config entries
    elif valueType == 1:
        match = re.search(r"\b" + value + r"=\"(.+)\";",item,re.I)
    #Array config entries
    elif valueType == 2:
        match = re.search(r"\b" + value + r"\[\]=\{(.+)\};",item,re.I)
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

#Define processing functions for later (they all take a iter of match objects)
def procMarker(mark):
    markCode = ""
    markIndex = mark.group(1)
    mark = mark.group(0)

    markText = matchValue(1,"text",mark,"")
    if markText != "!SMC":
        #Required marker values
        markName = matchValue(1,"name",mark,"")
        markPos = matchValue(2,"position",mark,"")

        #Optional marker values
        markAlpha = matchValue(0,"alpha",mark,"")
        markAngle = matchValue(0,"angle",mark,"")
        markBrush = matchValue(1,"fillName",mark,"")
        markColour = matchValue(1,"colorName",mark,"")
        markShape = matchValue(1,"markerType",mark,"ICON")
        markSizeA = matchValue(0,"a",mark,"")
        markSizeB = matchValue(0,"b",mark,"")
        markType = matchValue(1,"type",mark,"")

        #Create the marker
        if markName:
            if markPos:
                #Z and Y coordinates flipped in SQM, split string
                markPos = markPos.split(",")
                if len(markPos) == 3:
                    markPos.append(markPos.pop(1))
                else:
                    return malformed("marker {0} has invalid position coordinates".format(markIndex))

                #Join list back into position string
                markPos = ",".join(markPos)

                markCode += "createMarker [\"{0}\",[{1}]];\n".format(markName,markPos)
            else:
                return malformed("marker {0} has no position".format(markIndex))
        else:
            return malformed("marker {0} has no name".format(markIndex))

        #Marker alpha (hidden config value)
        if markAlpha:
            markCode += "\t\"{0}\" setMarkerAlpha {1};\n".format(markName,markAlpha)

        #Marker shape
        if markShape:
            markShape = markShape.upper()
            markCode += "\t\"{0}\" setMarkerShape \"{1}\";\n".format(markName,markShape)

        #Marker type (only applies to icons)
        if markType and (markShape == "ICON"):
            markCode += "\t\"{0}\" setMarkerType \"{1}\";\n".format(markName,markType)

        #Marker angle
        if markAngle:
            markCode += "\t\"{0}\" setMarkerDir {1};\n".format(markName,markAngle)

        #Marker size (can exist independently)
        if markSizeA or markSizeB:
            if not markSizeA:
                markSizeA = "1"
            if not markSizeB:
                markSizeB = "1"
            markCode += "\t\"{0}\" setMarkerSize [{1},{2}];\n".format(markName,markSizeA,markSizeB)

        #Marker brush
        if markBrush and (markShape != "ICON"):
            markCode += "\t\"{0}\" setMarkerBrush \"{1}\";\n".format(markName,markBrush)

        #Marker colour
        if markColour:
            markCode += "\t\"{0}\" setMarkerColor \"{1}\";\n".format(markName,markColour)

        #Marker text
        if markText:
            markCode += "\t\"{0}\" setMarkerText \"{1}\";\n".format(markName,markText)

    return markCode

def procVehicle(veh):
    vehCode = ""
    vehIndex = veh.group(1)
    veh = veh.group(0)

    vehDesc = matchValue(1,"description",veh,"")
    if vehDesc != "!SMC":
        #Required vehicle values
        vehType = matchValue(1,"vehicle",veh,"")
        vehPos = matchValue(2,"position",veh,"")
        vehRadius = matchValue(0,"placement",veh,"0")
        vehSpecial = matchValue(1,"special",veh,"CAN_COLLIDE")

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
        vehSyncID = matchValue(0,"syncId",veh,"")
        vehSyncs = matchValue(2,"synchronizations",veh,"")

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
            vehCode += "if (({0}) && (random 1 < {1})) then {{\n".format(vehCond,vehChance)
        elif vehCond:
            vehCond = vehCond.replace("\"\"","\"")
            vehCode += "if ({0}) then {{\n".format(vehCond)
        elif vehChance:
            vehChance = str(round(float(vehChance),2))
            vehCode += "if (random 1 < {0}) then {{\n".format(vehChance)

        #Create the vehicle
        if vehType:
            if vehPos:
                #Z and Y coordinates flipped in SQM, split string
                vehPos = vehPos.split(",")
                if len(vehPos) == 3:
                    vehPos.pop(1)
                    vehPos.append("0")
                else:
                    return malformed("vehicle {0} has invalid position coordinates".format(vehIndex))

                #Join list back into position string
                vehPos = ",".join(vehPos)

                vehCode += "{0} = createVehicle [\"{1}\",[{2}],[],{3},\"{4}\"];\n".format(vehVariable,vehType,vehPos,vehRadius,vehSpecial)
            else:
                return malformed("vehicle {0} has no position".format(vehIndex))
        else:
            return malformed("vehicle {0} has no classname".format(vehIndex))

        #Set vehicle name
        if vehName:
            vehCode += "\t{0} setVehicleVarName \"{1}\";\n".format(vehVariable,vehName)


        #Vehicle syncID (assign standardised var for synchronization)
        if vehSyncID:
            vehCode += "\tSMC_sync{0} = {1};\n".format(vehSyncID,vehVariable)
            #Store syncID if created (can check that it exists)
            syncList(vehSyncID)

            #Syncronize vehicle, only possible with syncID
            if vehSyncs:
                vehSyncs = vehSyncs.split(",")
                validSyncs = []
                #Build list of IDs that have been created earlier
                for sync in vehSyncs:
                    if sync in syncList(""):
                        sync = "SMC_sync{0}".format(sync)
                        validSyncs.append(sync)
                if validSyncs:
                    validSyncs = ",".join(validSyncs)
                    vehCode += "\t{0} synchronizeObjectsAdd [{1}];\n".format(vehVariable,validSyncs)

        #Vehicle heading
        if vehDir:
            vehCode += "\t\t{0} setFormDir {1}; {0} setDir {1};\n".format(vehVariable,vehDir)

        #Vehicle elevation offset (Arma 3)
        if vehOff:
            vehPos = vehPos.split(",")
            vehPos.pop(2)
            vehPos.append(vehOff)
            vehPos = ",".join(vehPos)
            vehCode += "\t{0} setPosATL [{1}];\n".format(vehVariable,vehPos)

        #Vehicle lock
        if vehLock:
            vehLock = vehLock.upper()
            vehCode += "\t{0} setVehicleLock \"{1}\";\n".format(vehVariable,vehLock)

        #Vehicle fuel
        if vehFuel:
            vehCode += "\t{0} setFuel {1};\n".format(vehVariable,vehFuel)
        #Vehicle ammo
        if vehAmmo:
            vehCode += "\t{0} setVehicleAmmo {1};\n".format(vehVariable,vehAmmo)
        #Vehicle health
        if vehHP:
            vehHP = 1 - float(vehHP)
            vehCode += "\t{0} setDamage {1};\n".format(vehVariable,vehHP)

        #Run init lines inline
        if vehInit:
            #Strings all the way down
            vehInit = vehInit.replace("\"\"","\"")
            #Remove leading/trailing whitespace
            vehInit = vehInit.strip()
            #No magic variable
            vehInit = re.sub(r"\bthis\b",vehVariable,vehInit,0,re.I)
            #Ensure statement is complete
            if not vehInit.endswith(";"):
                vehInit += ";"
            vehCode += "\t{0}\n".format(vehInit)

        #Must close condition block if present
        if vehCond or vehChance:
            vehCode += "};\n"

    return vehCode

def procUnit(unit,groupIndex):
    unitCode = ""
    unitIndex = unit.group(1)
    unit = unit.group(0)

    unitPlayer = matchValue(1,"player",unit,"")
    unitDesc = matchValue(1,"description",unit,"")
    #Player and marked units should be skipped
    if not (unitPlayer or (unitDesc == "!SMC")):
        #Required unit values
        unitID = matchValue(0,"id",unit,"")
        unitName = matchValue(1,"text",unit,"")
        unitPos = matchValue(2,"position",unit,"")
        unitRadius = matchValue(0,"placement",unit,"0")
        unitSpecial = matchValue(1,"special",unit,"FORM")
        unitType = matchValue(1,"vehicle",unit,"")

        #Optional unit values
        unitAmmo = matchValue(0,"ammo",unit,"")
        unitCond = matchValue(1,"presenceCondition",unit,"")
        unitChance = matchValue(0,"presence",unit,"")
        unitDir = matchValue(0,"azimut",unit,"")
        unitFuel = matchValue(0,"fuel",unit,"")
        unitHP = matchValue(0,"health",unit,"")
        unitInit = matchValue(1,"init",unit,"")
        unitLeader = matchValue(0,"leader",unit,"")
        unitLock = matchValue(1,"lock",unit,"")
        unitOff = matchValue(0,"offsetY",unit,"")
        unitRank = matchValue(1,"rank",unit,"")
        unitSkill = matchValue(0,"skill",unit,"0.60000002")
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
                    unitPos.pop(1)
                    unitPos.append("0")
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

        #Set unit name
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
                    unitCode += "\t\t{0} synchronizeObjectsAdd [{1}];\n".format(unitVariable,validSyncs)

        #Set group leader
        if unitLeader:
            unitCode += "\t\t(group {0}) selectLeader {0};\n".format(unitVariable)
            #Unit heading (only matters for group leader)
            if unitDir:
                unitCode += "\t\t{0} setFormDir {1};\n\t\t{0} setDir {1};\n".format(unitVariable,unitDir)

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
            #Remove leading/trailing whitespace
            unitInit = unitInit.strip()
            #No magic variable
            unitInit = re.sub(r"\bthis\b",unitVariable,unitInit,0,re.I)
            #Ensure statement is complete
            if not unitInit.endswith(";"):
                unitInit += ";"
            unitCode += "\t\t{0}\n".format(unitInit)

        #Must close condition block if present
        if unitCond or unitChance:
            unitCode += "};\n"

    return unitCode

def procWaypoint(wp,groupIndex):
    wpCode = ""
    wpIndex = wp.group(1)
    wp = wp.group(0)

    wpDesc = matchValue(1,"description",wp,"")
    if wpDesc != "!SMC":
        #Required waypoint values
        wpPos = matchValue(2,"position",wp,"")
        wpRadius = matchValue(0,"placement",wp,"0")

        #Optional waypoint values
        wpAct = matchValue(1,"expActiv",wp,"")
        wpBehave = matchValue(1,"combat",wp,"")
        wpCombat = matchValue(1,"combatMode",wp,"")
        wpComp = matchValue(0,"completitionRadius",wp,"")
        wpCond = matchValue(1,"expCond",wp,"")
        wpHouse = matchValue(0,"housePos",wp,"")
        wpForm = matchValue(1,"formation",wp,"")
        wpName = matchValue(1,"name",wp,"")
        wpScript = matchValue(1,"script",wp,"")
        wpShow = matchValue(1,"showWP",wp,"NEVER")
        wpSpeed = matchValue(1,"speed",wp,"")
        wpStatic = matchValue(0,"idStatic",wp,"")
        wpTimeMin = matchValue(0,"timeoutMin",wp,"")
        wpTimeMid = matchValue(0,"timeoutMid",wp,"")
        wpTimeMax = matchValue(0,"timeoutMax",wp,"")
        wpType = matchValue(1,"type",wp,"")
        wpSyncID = matchValue(0,"syncId",wp,"")
        wpSyncs = matchValue(2,"synchronizations",wp,"")

        #Waypoint variable
        wpVariable = "_wp{0}{1}".format(groupIndex,wpIndex)

        #Create the waypoint
        if wpPos:
            #Z and Y coordinates flipped in SQM, split string
            wpPos = wpPos.split(",")
            if len(wpPos) == 3:
                wpPos.pop(1)
                wpPos.append("0")
            else:
                return malformed("waypoint {0} in group {1} has invalid position coordinates".format(wpIndex,groupIndex))

            #Join list back into position string
            wpPos = ",".join(wpPos)

            wpCode += "{0} = _group{1} addWaypoint [[{2}],{3}];\n".format(wpVariable,groupIndex,wpPos,wpRadius)
        else:
            return malformed("waypoint {0} in group {1} has no position".format(wpIndex,groupIndex))

        #Waypoint syncID (assign standardised var for synchronization)
        if wpSyncID:
            wpCode += "\tSMC_sync{0} = {1};\n".format(wpSyncID,wpVariable)
            #Store syncID if created (can check that it exists)
            syncList(wpSyncID)

            #Syncronize waypoint, only possible with syncID
            if wpSyncs:
                wpSyncs = wpSyncs.split(",")
                validSyncs = []
                #Build list of IDs that have been created earlier
                for sync in wpSyncs:
                    if sync in syncList(""):
                        sync = "SMC_sync{0}".format(sync)
                        validSyncs.append(sync)
                if validSyncs:
                    validSyncs = ",".join(validSyncs)
                    wpCode += "\t{0} synchronizeWaypoint [{1}];\n".format(wpVariable,validSyncs)

        #Waypoint static attachment
        if wpStatic:
            wpCode += "\t_wpObj{1} = ([{0}] nearestObject {1});\n".format(wpPos,wpStatic)
            wpCode += "\tif !(isNull _wpObj{0}) then {{\n".format(wpStatic)
            wpCode += "\t\t{0} waypointAttachObject _wpObj{1};\n".format(wpVariable,wpStatic)
            #Waypoint building position
            if wpHouse:
                wpCode += "\t\t{0} setWaypointHousePosition {1};\n".format(wpVariable,wpHouse)
            wpCode += "\t};\n"

        #Waypoint type
        if wpType:
            wpCode += "\t{0} setWaypointType \"{1}\";\n".format(wpVariable,wpType)

        #Waypoint statements (can exist independently)
        if wpCond or wpAct:
            if not wpCond:
                wpCond = "true"
            wpCode += "\t{0} setWaypointStatements [\"{1}\",\"{2}\"];\n".format(wpVariable,wpCond,wpAct)

        #Waypoint timeout (can exist independently)
        if wpTimeMin or wpTimeMid or wpTimeMax:
            if not wpTimeMin:
                wpTimeMin = "0"
            if not wpTimeMid:
                wpTimeMid = "0"
            if not wpTimeMax:
                wpTimeMax = "0"
            wpCode += "\t{0} setWaypointTimeout [{1},{2},{3}];\n".format(wpVariable,wpTimeMin,wpTimeMid,wpTimeMax)

        #Waypoint combat mode
        if wpCombat:
            wpCombat = wpCombat.upper()
            wpCode += "\t{0} setWaypointCombatMode \"{1}\";\n".format(wpVariable,wpCombat)

        #Waypoint behaviour
        if wpBehave:
            wpBehave = wpBehave.upper()
            wpCode += "\t{0} setWaypointBehaviour \"{1}\";\n".format(wpVariable,wpBehave)

        #Waypoint speed
        if wpSpeed:
            wpSpeed = wpSpeed.upper()
            wpCode += "\t{0} setWaypointSpeed \"{1}\";\n".format(wpVariable,wpSpeed)

        #Waypoint formation
        if wpForm:
            wpForm = wpForm.upper()
            wpCode += "\t{0} setWaypointFormation \"{1}\";\n".format(wpVariable,wpForm)

        #Waypoint completion radius
        if wpComp:
            wpCode += "\t{0} setWaypointCompletionRadius {1};\n".format(wpVariable,wpComp)

        #Waypoint name
        if wpName:
            wpCode += "\t{0} setWaypointName \"{1}\";\n".format(wpVariable,wpName)

        #Waypoint show
        wpShow = wpShow.upper()
        if wpShow != "NEVER":
            wpCode += "\t{0} showWaypoint \"{1}\";\n".format(wpVariable,wpShow)

        #Waypoint script
        if wpScript:
            wpCode +="\t{0} setWaypointScript \"{1}\";\n".format(wpVariable,wpScript)

    return wpCode

def procSensor(sensor):
    sensorCode = ""
    sensorIndex = sensor.group(1)
    sensor = sensor.group(0)

    sensorText = matchValue(1,"text",sensor,"")
    if sensorText != "!SMC":
        #Required sensor values
        sensorName = matchValue(1,"name",sensor,"")
        sensorPos = matchValue(2,"position",sensor,"")

        #Optional sensor values
        sensorAct = matchValue(1,"expActiv",sensor,"")
        sensorActBy = matchValue(1,"activationBy",sensor,"")
        sensorActType = matchValue(1,"activationType",sensor,"")
        sensorAngle = matchValue(0,"angle",sensor,"")
        sensorCond = matchValue(1,"expCond",sensor,"")
        sensorDeact = matchValue(1,"expDesactiv",sensor,"")
        sensorInterupt = matchValue(0,"interruptable",sensor,"")
        sensorRectangle = matchValue(0,"rectangular",sensor,"")
        sensorRepeat = matchValue(0,"repeating",sensor,"")
        sensorSizeA = matchValue(0,"a",sensor,"")
        sensorSizeB = matchValue(0,"b",sensor,"")
        sensorSyncID = matchValue(0,"syncId",sensor,"")
        sensorSyncs = matchValue(2,"synchronizations",sensor,"")
        sensorTimeMin = matchValue(0,"timeoutMin",sensor,"")
        sensorTimeMid = matchValue(0,"timeoutMid",sensor,"")
        sensorTimeMax = matchValue(0,"timeoutMax",sensor,"")
        sensorType = matchValue(1,"type",sensor,"")

        #Sensor variable
        if sensorName:
            sensorVariable = sensorName
        else:
            sensorVariable = "_sensor{0}".format(sensorIndex)

        #Create the sensor
        if sensorPos:
            #Z and Y coordinates flipped in SQM, split string
            sensorPos = sensorPos.split(",")
            if len(sensorPos) == 3:
                sensorPos.append(sensorPos.pop(1))
            else:
                return malformed("trigger {0} has invalid position coordinates".format(sensorIndex))

            #Join list back into position string
            sensorPos = ",".join(sensorPos)

            sensorCode += "{0} = createTrigger [\"EmptyDetector\",[{1}]];\n".format(sensorVariable,sensorPos)
        else:
            return malformed("trigger {0} has no position".format(sensorIndex))

        #Sensor syncID (assign standardised var for synchronization)
        if sensorSyncID:
            sensorCode += "\tSMC_sync{0} = {1};\n".format(sensorSyncID,sensorVariable)
            #Store syncID if created (can check that it exists)
            syncList(sensorSyncID)

            #Syncronize sensor, only possible with syncID
            if sensorSyncs:
                sensorSyncs = sensorSyncs.split(",")
                validSyncs = []
                #Build list of IDs that have been created earlier
                for sync in sensorSyncs:
                    if sync in syncList(""):
                        sync = "SMC_sync{0}".format(sync)
                        validSyncs.append(sync)
                if validSyncs:
                    validSyncs = ",".join(validSyncs)
                    sensorCode += "\t{0} synchronizeTrigger [{1}];\n".format(sensorVariable,validSyncs)

        #Sensor type
        if sensorType:
            sensorType = sensorType.upper()
            sensorCode += "\t{0} setTriggerType \"{1}\";\n".format(sensorVariable,sensorType)

        #Sensor timeout/countdown (can exist independently)
        if sensorTimeMin or sensorTimeMid or sensorTimeMax:
            if not sensorTimeMin:
                sensorTimeMin = "0"
            if not sensorTimeMid:
                sensorTimeMid = "0"
            if not sensorTimeMax:
                sensorTimeMax = "0"
            if sensorInterupt == "1":
                sensorInterupt = "true"
            else:
                sensorInterupt = "false"
            sensorCode += "\t{0} setTriggerTimeout [{1},{2},{3},{4}];\n".format(sensorVariable,sensorTimeMin,sensorTimeMid,sensorTimeMax,sensorInterupt)

        #Sensor area (can exist independently)
        if sensorSizeA or sensorSizeB or sensorAngle or sensorRectangle:
            if not sensorSizeA:
                sensorSizeA = "50"
            if not sensorSizeB:
                sensorSizeB = "50"
            if not sensorAngle:
                sensorAngle = "0"
            if sensorRectangle == "1":
                sensorRectangle = "true"
            else:
                sensorRectangle = "false"
            sensorCode += "\t{0} setTriggerArea [{1},{2},{3},{4}];\n".format(sensorVariable,sensorSizeA,sensorSizeB,sensorAngle,sensorRectangle)

        #Sensor statements (can exist independently)
        if sensorCond or sensorAct or sensorDeact:
            if not sensorCond:
                sensorCond = "this"
            sensorCode += "\t{0} setTriggerStatements [\"{1}\",\"{2}\",\"{3}\"];\n".format(sensorVariable,sensorCond,sensorAct,sensorDeact)

        #Sensor activation (can exist independently)
        if sensorActBy or sensorActType or sensorRepeat:
            if not sensorActBy:
                sensorActBy = "NONE"
            if not sensorActType:
                sensorActType = "PRESENT"
            if sensorRepeat == "1":
                sensorRepeat = "true"
            else:
                sensorRepeat = "false"
            sensorCode += "\t{0} setTriggerActivation [\"{1}\",\"{2}\",{3}];\n".format(sensorVariable,sensorActBy,sensorActType,sensorRepeat)

    return sensorCode
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
    if fileName.endswith(".sqm"):
        sqmFiles.append(fileName)

for fileName in sqmFiles:
    missionPath = scriptDirectory + "\\" + fileName
    #Make sure the file exists before opening to avoid errors
    if os.path.isfile(missionPath):
        #Initialise the output code with file header
        outputCode = "// Created by SMC v{0}\n".format(versionNum)
        outputCode += "// {0}\n\n".format(time.strftime("%c"))

        #Open the file this way so that it closes automatically when done
        with open(missionPath) as missionFile:
            fileContent = missionFile.read()
            #Extract the top-level sections of mission.sqm
            classMarkers = re.search(r"^\tclass\sMarkers.+?^\t\};",fileContent,re.I|re.M|re.S)
            classVehicles = re.search(r"^\tclass\sVehicles.+?^\t\};",fileContent,re.I|re.M|re.S)
            classGroups = re.search(r"^\tclass\sGroups.+?^\t\};",fileContent,re.I|re.M|re.S)
            classSensors = re.search(r"^\tclass\sSensors.+?^\t\};",fileContent,re.I|re.M|re.S)
            #Clear content variable
            fileContent = None

        #Compile common shared regex object
        reSubClass = re.compile(r"^\t\tclass\sItem(\d+).+?^\t\t\};",re.I|re.M|re.S)
        reGroupSub = re.compile(r"^\t{4}class\sItem(\d+).+?^\t{4}\};",re.I|re.M|re.S)

        #Process sections in order they will appear in SQF
        #Allows sync variables to be checked in correct scope
        if classMarkers:
            classMarkers = reSubClass.finditer(classMarkers.group(0))
            outputCode += "// --Markers--\n"
            for marker in classMarkers:
                outputCode += procMarker(marker)

        if classVehicles:
            classVehicles = reSubClass.finditer(classVehicles.group(0))
            outputCode += "// --Vehicles/Objects--\n"
            for vehicle in classVehicles:
                outputCode += procVehicle(vehicle)

        if classGroups:
            classGroups = reSubClass.finditer(classGroups.group(0))
            listUnits = []
            listWaypoints = []
            for group in classGroups:
                groupIndex = group.group(1)
                groupSide = matchValue(1,"side",group.group(0),"")

                groupSide = groupSide.upper()
                if groupSide in sideDict:
                    groupSide = sideDict[groupSide]

                    if groupSide != "sideLogic":
                        classUnits = re.finditer(r"^\t{3}class\sVehicles.+?^\t{3}\};",group.group(0),re.I|re.M|re.S)
                        classWaypoints = re.finditer(r"^\t{3}class\sWaypoints.+?^\t{3}\};",group.group(0),re.I|re.M|re.S)
                        listUnits.append([groupIndex,groupSide,classUnits])
                        listWaypoints.append([groupIndex,classWaypoints])
                else:
                    outputCode += malformed("group {0} uses unknown side \"{1}\"".format(groupIndex,groupSide))

            if listUnits:
                outputCode += "// --Units--\n"
                for uList in listUnits:
                    outputCode += "_group{0} = createGroup {1};\n".format(uList[0],uList[1])
                    for groupUnits in uList[2]:
                        groupUnits = reGroupSub.finditer(groupUnits.group(0))
                        for unit in groupUnits:
                            outputCode += procUnit(unit,uList[0])

            if listWaypoints:
                outputCode += "// --Waypoints--\n"
                for wpList in listWaypoints:
                    for groupWPs in wpList[1]:
                        groupWPs = reGroupSub.finditer(groupWPs.group(0))
                        for wp in groupWPs:
                            outputCode += procWaypoint(wp,wpList[0])

        if classSensors:
            classSensors = reSubClass.finditer(classSensors.group(0))
            outputCode += "// --Sensors--\n"
            for sensor in classSensors:
                outputCode += procSensor(sensor)

        #The written file should be created/overwritten in the same directory
        outputPath = scriptDirectory + "\\" + fileName[:-1] + "f"
        with open(outputPath, 'w') as outputFile:
            outputFile.write(outputCode)
