
	; == map stuff ==
	.org StartingMapAddr
	.byte GROUP_ACDC_TOWN
	.byte MAP_ACDC_TOWN

	; map text pointer for ACDC Town
	.org ACDCTownMapTextPtrAddr
	.word ACDCTownTextScript_NEW

	; don't load in shop data
	.org PatchLoadShopData
	mov pc, lr

	; off_804CF9C, map object pointer for ACDC Town
	.org ACDCTownGroup_MapObjectTables
	.word ACDCTown_MapObjects_NEW

	; ACDCTown_OnInitMapScripts_804d0a4
	.org ACDCTown_OnInitMapScripts
	.word ACDCTown_OnInitMapScript_NEW

	; ACDCTown_ContinuousMapScripts_804d0ac
	.org ACDCTown_ContinuousMapScripts
	.word ACDCTown_ContinuousMapScript_NEW

	; ACDCTown_MapGroupNPCScriptPointers_804d0b4
	.org ACDCTown_MapGroupNPCScriptPointers
	.word ACDCTown_NPCScripts_NEW

	; prevent warps
	.org PatchCheckWarps
	mov pc, lr

	; prevent jacking in at all
	.org PatchCanJackIn
	b CanJackIn_Failure

; 	.org PatchMainMapLoop
; 	ldr r0, =Hook_PatchMainMapLoop|1
; 	bx r0
; 	.pool
; 	nop
Hook_PatchMainMapLoop_Return:

	.org PatchInitNewGameData
	.area 0x80050de - 0x80050ca
	mov r2, 3
	bl ClearEventFlagRangeFromImmediate
	movflag EVENT_1900_NEVER_SET_IN_VANILLA
	bl SetEventFlagFromImmediate
	b PatchInitNewGameData_Continue
	.endarea

	.org LButtonCutsceneScriptAddr
	cs_jump PatchLButtonCutsceneScript

	; == stat stuff ==
	.org PatchLoadBaseNaviHP
	mov r0, 2000 >> 4
	lsl r0, r0, 4

	.org PatchLoadOtherBaseNaviStats
	.area 0x8013bbc - 0x8013b90
	ldr r0, =Hook_PatchLoadOtherBaseNaviStats|1
	bx r0
	.pool
	.endarea

	; .org
	; push r4,r5,lr
	; mov r4, r0
	; mov r1, oNaviStats_FolderIndex
	; ldrb r5, [r4, r1]
	; 

	.org BaseNaviStatsTable+10
	.byte 0 ; no b+left

	; prevent folder editing
	.org PatchPackFolderSwitch
	mov r0, 1
	tst r0, r0
	mov pc, lr
	
	; prevent chip selection
	.org PatchFolderSelectChip
	mov r0, 0
	tst r0, r0
	mov pc, lr

	; give folder modifications
	; folder index is in r2 now
	.org PatchGiveFolder+8
	mov r0, r2
	nop

	.org FolderTablePoolAddr
	.word FolderTable_NEW

	; unbiased shuffling
	.org PatchShuffleFolderSlice
ShuffleFolderSlice:
	push {r4-r6,lr}
	sub r4, r1, 1
	beq @@done
@@loop:
	push {r0}
	bl GetPositiveSignedRNG1
	add r1, r4, 1
	swi 6 ; r1 = rand() % (r1 + 1)
	pop {r0}

	add r1, r1, r1
	add r3, r4, r4
	ldrh r5, [r0,r1]
	ldrh r6, [r0,r3]
	strh r6, [r0,r1]
	strh r5, [r0,r3]
	sub r4, 1
	bne @@loop
@@done:
	pop {r4-r6,pc}

	; other version chips
	.if IS_FALZAR == 1
	import_chip_gfx_ptrs BASS, BassChipIcon, BassChipImage, BassChipPalette
	import_chip_gfx_ptrs BIGHOOK, BigHookChipIcon, BigHookChipImage, BigHookChipPalette
	import_chip_gfx_ptrs DELTARAY, DeltaRayChipIcon, DeltaRayChipImage, DeltaRayChipPalette
	import_chip_gfx_ptrs COLFORCE, ColForceChipIcon, ColForceChipImage, ColForceChipPalette
	import_chip_gfx_ptrs BUGRSWRD, BugRSwrdChipIcon, BugRSwrdChipImage, BugRSwrdChipPalette
	.else
	import_chip_gfx_ptrs BASSANLY, BassAnlyChipIcon, BassAnlyChipImage, BassAnlyChipPalette
	import_chip_gfx_ptrs METRKNUK, MetrKnukChipIcon, MetrKnukChipImage, MetrKnukChipPalette
	import_chip_gfx_ptrs CROSSDIV, CrossDivChipIcon, CrossDivChipImage, CrossDivChipPalette
	import_chip_gfx_ptrs HUBBATC, HubBatcChipIcon, HubBatcChipImage, HubBatcChipPalette
	import_chip_gfx_ptrs BGDTHTHD, BgDthThdChipIcon, BgDthThdChipImage, BgDthThdChipPalette
	.endif

	; just set SP chip damage this way
	set_chip_attack_power PROTOMNSP, 290
	set_chip_attack_power HEATMANSP, 260
	set_chip_attack_power ELECMANSP, 210
	set_chip_attack_power SLASHMNSP, 220
	set_chip_attack_power ERASEMNSP, 210
	set_chip_attack_power CHRGEMNSP, 130
	set_chip_attack_power SPOUTMNSP, 120
	set_chip_attack_power TMHKMANSP, 280
	set_chip_attack_power TENGUMNSP, 160
	set_chip_attack_power GRNDMANSP, 130
	set_chip_attack_power DUSTMANSP, 200
	set_chip_attack_power BLASTMNSP, 250
	set_chip_attack_power DIVEMANSP, 270
	set_chip_attack_power CRCUSMNSP, 55
	set_chip_attack_power JUDGEMNSP, 190
	set_chip_attack_power ELMNTMNSP, 240
	set_chip_attack_power COLONELSP, 300

	