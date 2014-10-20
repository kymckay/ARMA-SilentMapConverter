// Created by SMC v1.0
private ["_currentGroup","_currentUnit","_currentWaypoint"];

// ### GROUPS ###
createCenter west;
createCenter east;
createCenter resistance;
createCenter civilian;

_currentGroup = createGroup west;
if ((true and not(false)) and (random 1 < 0.43)) then {
	HereIsAName = _currentGroup createUnit ["CZ_Special_Forces_Scout_DES_EP1",[990.29712,1434.9325,0],[],300,"FORM"];
	if !(alive HereIsAName) then {
		HereIsAName = createVehicle ["CZ_Special_Forces_Scout_DES_EP1",[990.29712,1434.9325,0],[],300,"FORM"];
		[HereIsAName,_currentGroup] call BIS_fnc_spawnCrew;
	};
	HereIsAName setDir 30;
	HereIsAName setDamage 0.93;
	HereIsAName setFuel 0.66;
	HereIsAName setSkill 0.48;
	HereIsAName setVehicleAmmo 0.36;
	HereIsAName setRank "LIEUTENANT";
	_currentGroup selectLeader HereIsAName;
	HereIsAName setVehicleInit "SomeGlobal = this;";
};

_currentGroup = createGroup east;
_currentUnit = _currentGroup createUnit ["TK_INS_Soldier_EP1",[988.47803,1435.2903,0],[],0,"FORM"];
	if !(alive _currentUnit) then {
		_currentUnit = createVehicle ["TK_INS_Soldier_EP1",[988.47803,1435.2903,0],[],0,"FORM"];
		[_currentUnit,_currentGroup] call BIS_fnc_spawnCrew;
	};
	_currentGroup selectLeader _currentUnit;

_currentGroup = createGroup resistance;
_currentUnit = _currentGroup createUnit ["CIV_Contractor1_BAF",[988.47803,1433.4713,0],[],0,"CARGO"];
	if !(alive _currentUnit) then {
		_currentUnit = createVehicle ["CIV_Contractor1_BAF",[988.47803,1433.4713,0],[],0,"CARGO"];
		[_currentUnit,_currentGroup] call BIS_fnc_spawnCrew;
	};
	_currentGroup selectLeader _currentUnit;

_currentGroup = createGroup civilian;
_currentUnit = _currentGroup createUnit ["Citizen1",[986.33081,1434.9624,0],[],0,"FORM"];
	if !(alive _currentUnit) then {
		_currentUnit = createVehicle ["Citizen1",[986.33081,1434.9624,0],[],0,"FORM"];
		[_currentUnit,_currentGroup] call BIS_fnc_spawnCrew;
	};
	_currentGroup selectLeader _currentUnit;
_currentUnit = _currentGroup createUnit ["Citizen1",[985.55548,1434.9028,0],[],0,"FORM"];
	if !(alive _currentUnit) then {
		_currentUnit = createVehicle ["Citizen1",[985.55548,1434.9028,0],[],0,"FORM"];
		[_currentUnit,_currentGroup] call BIS_fnc_spawnCrew;
	};
_currentWaypoint = _currentGroup addWaypoint [[983.25922,1442.6265,0],0];
	_currentWaypoint setWaypointStatements["true and ("""" == """")",""];
	_currentWaypoint setWaypointTimeout [0.0, 0.0, 3.0];
_currentWaypoint = _currentGroup addWaypoint [[989.7901,1444.4753,0],0];
	_currentWaypoint setWaypointType "LEADER";
_currentWaypoint = _currentGroup addWaypoint [[982.06641,1446.2646,0],30];
	_currentWaypoint setWaypointStatements["true and not(false)","d = 1;"];
	_currentWaypoint setWaypointTimeout [4.0, 5.0, 9.0];

processInitCommands;