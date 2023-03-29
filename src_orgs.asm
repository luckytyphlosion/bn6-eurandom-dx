
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

	.org PatchMainMapLoop
	ldr r0, =Hook_PatchMainMapLoop|1
	bx r0
	.pool
	nop
Hook_PatchMainMapLoop_Return:

	.org PatchInitNewGameData
	.area 0x80050de - 0x80050ca
	mov r2, 3
	bl ClearEventFlagRangeFromImmediate
	movflag EVENT_1900_NEVER_SET_IN_VANILLA
	bl SetEventFlagFromImmediate
	b PatchInitNewGameData_Continue
	.endarea

	; == stat stuff ==
	.org PatchLoadBaseNaviHP
	mov r0, 2000 >> 4
	lsl r0, r0, 4

	.org PatchLoadOtherBaseNaviStats
	.area 0x8013bbc - 0x8013b90
	; enable super armor and airshoes, set giga level to 1, set b pwr atk to charge shot
	mov r0, 1
	mov r1, oNaviStats_SuperArmor 
	strb r0, [r7,r1]
	strb r0, [r7,oNaviStats_AirShoes]
	strb r0, [r7,oNaviStats_UnderShirt]
	strb r0, [r7,oNaviStats_GigaLevel]
	strb r0, [r7,oNaviStats_BPwrAtk]

	; disable float shoes, fstbarr, no a pwr atk
	mov r0, 0
	strb r0, [r7,oNaviStats_FloatShoes]
	strb r0, [r7,oNaviStats_FstBarr]
	strb r0, [r7,oNaviStats_APwrAtk]

	; set mega level to 5
	mov r0, 5
	strb r0, [r7,oNaviStats_MegaLevel]

	; set cust level to 8
	mov r0, 8
	strb r0, [r7,oNaviStats_CustomLevel]

	; set atk to atk4 (starts from 0)
	mov r0, 3
	strb r0, [r7,oNaviStats_Attack]

	; set speed and charge to 4
	mov r0, 4
	strb r0, [r7,oNaviStats_Speed]
	strb r0, [r7,oNaviStats_Charge]
	b LoadOtherBaseNaviStats_StartingAtBLeftAbility
	.endarea

	.org BaseNaviStatsTable+10
	.byte 0x3b ; shield
