
	INPUT_ROM equ vequ("bn6f.gba", "bn6g.gba")
	OUTPUT_ROM equ vequ("bn6f-random-battle.gba", "bn6g-random-battle.gba")
	.definelabel fspace, 0x087FE36C

	; version-specific patch defines
	.vdefinelabel ACDCTownMapTextPtrAddr, 0x80445e0, 0x80445b8
	.vdefinelabel PatchLoadShopData, 0x8048C98, 0x8048c38
	.vdefinelabel ACDCTownGroup_MapObjectTables, 0x804CF9C, 0x804de20
	.vdefinelabel ACDCTown_OnInitMapScripts, 0x804d0a4, 0x804df28
	.vdefinelabel ACDCTown_ContinuousMapScripts, 0x804d0ac, 0x804df30
	.vdefinelabel ACDCTown_MapGroupNPCScriptPointers, 0x804d0b4, 0x804df38

	; version-independent patch defines
	.definelabel PatchLoadBaseNaviHP, 0x8013b80
	.definelabel PatchLoadOtherBaseNaviStats, 0x8013b90
	.definelabel LoadOtherBaseNaviStats_StartingAtBLeftAbility, 0x8013bbc
	.definelabel PatchCheckWarps, 0x80058d0
	.definelabel PatchMainMapLoop, 0x8005268
	.definelabel PatchCanJackIn, 0x8034d34
	.definelabel CanJackIn_Failure, 0x8034d44
	.definelabel PatchInitNewGameData, 0x80050ca
	.definelabel PatchInitNewGameData_Continue, 0x80050de

	.definelabel StartingMapAddr, 0x80050e4
	.definelabel BaseNaviStatsTable, 0x80210DD

	.definelabel eCurRandomBattleFolder, 0x2003f50

	; version-independent game functions
	.definelabel ClearEventFlagRangeFromImmediate, 0x802f1a8
	.definelabel SetEventFlagFromImmediate, 0x802f110
	.definelabel TestEventFlagFromImmediate, 0x802f164
	.definelabel clearCutsceneScriptPosIfMagicValue0x1_8036F24, 0x8036f24
	.definelabel sub_8034BB8, 0x8034bb8

	; version-specific game functions
	.vdefinelabel chatbox_runScript, 0x8040384, 0x8040358

