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
versionNum = 1.0

#Import needed libraries
import os
import re

#Path to .sqm files required for reading
#Mission files should be in same directroy as script
scriptDirectory = os.path.dirname(os.path.realpath(__file__))
sqmFiles = []
for fileName in os.listdir(scriptDirectory):
    if fileName[len(fileName)-4:] == ".sqm":
        sqmFiles.append(fileName)
scriptDirectory += "\\"

for fileName in sqmFiles:
    missionPath = scriptDirectory + fileName
    #Make sure the file exists before opening to avoid errors
    if os.path.isfile(missionPath):
        #Compile the frequently used reset regular expressions for efficency
        reReset = re.compile(r"\s;\n")
        reSubReset = re.compile(r"\s{2}\};\n")

        #Loop through each line in the mission file for omtimization
        with open(missionPath) as missionFile:
            outputString = "// Created by SMC v{0}\nprivate [\"_currentGroup\",\"_currentUnit\"];\n\n".format(versionNum)
            subScope = "" #Will temporarily store each class in the scope
            mode = 0 #Mode will refer to the current config scope 0-None, 1-Groups
            for line in missionFile:
                if mode == 0:
                    if re.search(r"\sclass Groups\n",line,re.I):
                        mode = 1
                        outputString += "// ### GROUPS ###\ncreateCenter west;\ncreateCenter east;\ncreateCenter resistance;\ncreateCenter civilian;\n"
                elif mode == 1:
                    #The current group can be processed when the end of it is reached
                    if reSubReset.match(line):
                        groupSide = re.search(r"\s{3}side=\"(\w+?)\";",subScope,re.I)
                        itemsArray = re.findall(r"\s{4}class Item\d+\n\s{4}\{.+?\s{4}\};",subScope,re.I|re.S)

                        #Correctly sided group must be created before units can be
                        if groupSide:
                            if groupSide.group(1) == "CIV":
                                groupSide = "civilian"
                            elif groupSide.group(1) == "GUER":
                                groupSide = "resistance"
                            else:
                                groupSide = groupSide.group(1).lower()
                            outputString += "\n//--New Group--\n_currentGroup = createGroup {0};".format(groupSide)

                        #Units and waypoints can now be created
                        for currentItem in itemsArray:
                            #Only waypint classes contain an effects class
                            if re.search(r"\s{5}class Effects",currentItem,re.I):
                                #itemDetails = re.search()
                                outputString += "Waypoint\n"
                            else:
                                #Condition and probability of presence should be checked first before unit is created
                                vehPresence = re.search(r"presenceCondition=\"(.+)\";",currentItem,re.I)
                                vehProbability = re.search(r"presence=(\d\.?\d*);",currentItem,re.I)
                                if vehPresence and vehProbability:
                                    outputString += "\nif (({0}) and (random 1 < {1})) then {2}\n\t".format(vehPresence.group(1),vehProbability.group(1)[:4],"{")
                                elif vehPresence and not vehPresence:
                                    outputString += "\nif ({0}) then {1}\n\t".format(vehPresence.group(1),"{")
                                elif vehProbability and not vehPresence:
                                    outputString += "\nif (random 1 < {0}) then {1}\n\t".format(vehProbability.group(1)[:4],"{")

                                #Use variable name if it exists - instead of a local variable
                                vehVarName = re.search(r"text=\"(.+)\";",currentItem,re.I)
                                if vehVarName:
                                    vehVarName = vehVarName.group(1)
                                else:
                                    vehVarName = "_currentUnit"

                                #Classname, position, placement radius and special attributes are all needed for unit creation
                                vehName = re.search(r"vehicle=(\".+\");",currentItem,re.I).group(1)
                                vehPosition = "[" + ",".join(re.search(r"position\[\]=\{(\d+\.?\d*),.+,(\d+\.?\d*)\};",currentItem,re.I).group(1,2)) + ",0]"
                                vehRadius = re.search(r"placement=(\d+\.?\d*);",currentItem,re.I)
                                if vehRadius:
                                    vehRadius = vehRadius.group(1)
                                else:
                                    vehRadius = "0"
                                vehSpecial = re.search(r"special=(\".*\");",currentItem,re.I)
                                if vehSpecial:
                                    vehSpecial = vehSpecial.group(1)
                                else:
                                    vehSpecial = "\"FORM\""
                                if not (vehPresence or vehProbability):
                                    outputString += "\n"
                                outputString += "{0} = _currentGroup createUnit [{1}];\n".format(vehVarName,",".join([vehName,vehPosition,"[]",vehRadius,vehSpecial]))

                                #Vehicles won't work with createUnit so this workaround is needed
                                for appendString in ["if !(alive {0}) then {1}\n".format(vehVarName,"{"),"\t{0} = createVehicle [{1}];\n".format(vehVarName,",".join([vehName,vehPosition,"[]",vehRadius,vehSpecial])),"\t[{0},_currentGroup] call BIS_fnc_spawnCrew;\n".format(vehVarName),"};\n"]:
                                    if vehPresence or vehProbability:
                                        outputString += "\t"
                                    outputString += appendString

                                #Set unit direction if necessary
                                vehDir = re.search(r"azimut=(\d+\.?\d*);",currentItem,re.I)
                                if vehDir:
                                    if vehPresence or vehProbability:
                                        outputString += "\t"
                                    outputString += "{0} setDir {1};\n".format(vehVarName,vehDir.group(1))

                                #If the unit is the leader of the group then it should be scripted to make sure
                                if re.search(r"leader=1;",currentItem,re.I):
                                    if vehPresence or vehProbability:
                                        outputString += "\t"
                                    outputString += "_currentGroup selectLeader {0};\n".format(vehVarName)

                                #Rank should be set to preserve chain of command + ratings
                                vehRank = re.search(r"rank=(\".*\");",currentItem,re.I)
                                if vehRank:
                                    if vehPresence or vehProbability:
                                        outputString += "\t"
                                    outputString += "{0} setRank {1};\n".format(vehVarName,vehRank.group(1))

                                #Set health, fuel, skill and ammo only if necessary
                                vehHealth = re.search(r"health=(\d+\.?\d*);",currentItem,re.I)
                                vehFuel = re.search(r"fuel=(\d+\.?\d*);",currentItem,re.I)
                                vehSkill = re.search(r"skill=(\d+\.?\d*);",currentItem,re.I)
                                vehAmmo = re.search(r"ammo=(\d+\.?\d*);",currentItem,re.I)
                                if vehHealth:
                                    if vehPresence or vehProbability:
                                        outputString += "\t"
                                    outputString += "{0} setDamage {1};\n".format(vehVarName,str(1 - float(vehHealth.group(1)))[:4])
                                if vehFuel:
                                    if vehPresence or vehProbability:
                                        outputString += "\t"
                                    outputString += "{0} setFuel {1};\n".format(vehVarName,vehFuel.group(1)[:4])
                                if vehSkill.group(1) != "0.60000002":
                                    if vehPresence or vehProbability:
                                        outputString += "\t"
                                    outputString += "{0} setSkill {1};\n".format(vehVarName,vehSkill.group(1)[:4])
                                if vehAmmo:
                                    if vehPresence or vehProbability:
                                        outputString += "\t"
                                    outputString += "{0} setVehicleAmmo {1};\n".format(vehVarName,vehAmmo.group(1)[:4])

                                #If any condition of presence is present then the if statement must be closed
                                if vehPresence or vehProbability:
                                    outputString += "};\n"

                        subScope = ""
                    else:
                        subScope += line
                #Mode should be set back to 0 when current config scope is exited
                if mode != 0 and reReset.match(line):
                    mode = 0

        #The written file should be created/overwritten in the same directory
        outputPath = scriptDirectory + fileName[:len(fileName)-1] + "f"
        with open(outputPath, 'w') as outputFile:
            outputFile.write(outputString)