
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

	.org BaseNaviStatsTable+10
	.byte 0x3b ; shield

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

