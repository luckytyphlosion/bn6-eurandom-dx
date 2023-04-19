
	INPUT_ROM equ vequ("bn6f.gba", "bn6g.gba")
	OTHER_VERSION_ROM equ vequ("bn6g.gba", "bn6f.gba")

	OUTPUT_ROM equ vequ("bn6f-random-battle.gba", "bn6g-random-battle.gba")
	.definelabel fspace, 0x087FE36C

	.vinclude "bbn6/bn6f_addr.asm", "bbn6/bn6g_addr.asm"

	; version-specific patch defines
	.vdefinelabel ACDCTownMapTextPtrAddr, 0x80445e0, 0x80445b0
	.vdefinelabel PatchLoadShopData, 0x8048C98, 0x8048c38
	.vdefinelabel ACDCTownGroup_MapObjectTables, 0x804CF9C, 0x804de20
	.vdefinelabel ACDCTown_OnInitMapScripts, 0x804d0a4, 0x804df28
	.vdefinelabel ACDCTown_ContinuousMapScripts, 0x804d0ac, 0x804df30
	.vdefinelabel ACDCTown_MapGroupNPCScriptPointers, 0x804d0b4, 0x804df38
	.vdefinelabel LButtonCutsceneScriptAddr, 0x80991f4, 0x809a72c
	.vdefinelabel PatchPackFolderSwitch, 0x8133E3C, 0x8135c18
	.vdefinelabel PatchFolderSelectChip, 0x8134A3C, 0x8136818
	.vdefinelabel PatchGiveFolder, 0x8137718, 0x81394f4
	GiveFolder equ PatchGiveFolder
	.vdefinelabel FolderTablePoolAddr, 0x8137864, 0x8139640
	.vdefinelabel PatchApplyNaviCustPrograms, 0x813C684, 0x813e464
	.vdefinelabel PatchPrintBufferedStringNumBytesCopied, 0x80421f4, 0x80421c4
	.vdefinelabel PatchPrintBufferedStringTerminator, 0x80421fc, 0x80421cc

	; version-independent patch defines
	.definelabel PatchLoadBaseNaviHP, 0x8013b80
	.definelabel PatchLoadOtherBaseNaviStats, 0x8013b90
	.definelabel LoadOtherBaseNaviStats_StartingAtBLeftAbility, 0x8013bb8
	.definelabel PatchCheckWarps, 0x80058d0
	.definelabel PatchMainMapLoop, 0x8005268
	.definelabel PatchCanJackIn, 0x8034d34
	.definelabel CanJackIn_Failure, 0x8034d44
	.definelabel PatchInitNewGameData, 0x80050ca
	.definelabel PatchInitNewGameData_Continue, 0x80050de
	.definelabel PatchShuffleFolderSlice, 0x8000d12

	.definelabel StartingMapAddr, 0x80050e4
	.definelabel BaseNaviStatsTable, 0x80210DD
	.definelabel ChipInfo, 0x8021da8
	.definelabel StartingFolder, 0x80213ac
	CHIP_INFO_LOAD_ADDR equ 0x21da8

	.definelabel PatchCustMenuMainInputPointerLocation, 0x8026AA8

	; version-independent game functions
	.definelabel ClearEventFlagRangeFromImmediate, 0x802f1a8
	.definelabel SetEventFlagFromImmediate, 0x802f110
	.definelabel TestEventFlagFromImmediate, 0x802f164
	.definelabel clearCutsceneScriptPosIfMagicValue0x1_8036F24, 0x8036f24
	.definelabel sub_8034BB8, 0x8034bb8
	.definelabel GetPositiveSignedRNG1, 0x8001562
	.definelabel SetNaviStatsByte, 0x80136f0
	.definelabel eNaviStats, 0x20047cc
	.definelabel CustMenuMainInput, 0x8026CCC
	.definelabel GetBattleEffects, 0x802d246
	.definelabel GetBattleNaviStatsByte, 0x80136cc

	; .definelabel OpponentFolderNameBuffer, 0x203f7f4

	; .definelabel Folder1
	; version-specific game functions
	.vdefinelabel chatbox_runScript, 0x8040384, 0x8040358
	.vdefinelabel StartBattleGeneric, 0x80990b8, 0x809a5f0
	.vdefinelabel NPCScript_StationaryNPC, 0x809f6cc, 0x80a0bac

	; new memory
	.definelabel eFolderNameBuffer, 0x203f7f0
	.definelabel eCurRandomBattleFolder, 0x2003f50

