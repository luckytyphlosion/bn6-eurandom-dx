
	.align 4
Hook_PatchMainMapLoop:
	push lr
	movflag EVENT_1900_NEVER_SET_IN_VANILLA
	ldr r2, =TestEventFlagFromImmediate|1
	mov lr, pc
	bx r2
	beq @@oldSaveDetected

	ldr r0, =clearCutsceneScriptPosIfMagicValue0x1_8036F24|1
	mov lr, pc
	bx r0
	ldr r0, =sub_8034BB8|1
	mov lr, pc
	bx r0
	ldr r0, =Hook_PatchMainMapLoop_Return|1
	bx r0

@@oldSaveDetected:
	movflag EVENT_TRIGGERED_OLD_SAVE
	ldr r2, =TestEventFlagFromImmediate|1
	mov lr, pc
	bx r2
	bne @@alreadyRanWarningMsg
	movflag EVENT_TRIGGERED_OLD_SAVE
	ldr r2, =SetEventFlagFromImmediate|1
	mov lr, pc
	bx r2

	ldr r0, =LoadNewGameSaveTextScript
	mov r1, 0
	ldr r2, =chatbox_runScript|1
	mov lr, pc
	bx r2
@@alreadyRanWarningMsg:
	pop pc

Hook_PatchLoadOtherBaseNaviStats:
	; enable super armor and airshoes, set giga level to 1, set b pwr atk to charge shot
	mov r0, 1
	mov r1, oNaviStats_SuperArmor 
	strb r0, [r7,r1]
	strb r0, [r7,oNaviStats_AirShoes]
	strb r0, [r7,oNaviStats_UnderShirt]
	strb r0, [r7,oNaviStats_GigaLevel]
	strb r0, [r7,oNaviStats_BPwrAtk]
	mov r1, oNaviStats_ChipShuffle
	strb r0, [r7,r1]

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
	ldr r0, =LoadOtherBaseNaviStats_StartingAtBLeftAbility|1
	bx r0

GiveRandomFolder:
	push r4-r7,lr
	ldrb r2, [r5,8] ; folder index
	sub r2, r2, 1
	ldr r0, =eCurRandomBattleFolder
	strb r2, [r0]
	mov r0, 0x01
	ldr r1, =GiveFolder|1
	mov lr, pc
	bx r1
	mov r1, oNaviStats_Folder1Reg
	mov r2, 0xff
	bl SetMegaManNaviStatsByte_longcall
	mov r1, oNaviStats_Folder1Tag1
	mov r2, 0xff
	bl SetMegaManNaviStatsByte_longcall
	mov r1, oNaviStats_Folder1Tag2
	mov r2, 0xff
	bl SetMegaManNaviStatsByte_longcall
	mov r0, 0
	pop r4-r7,lr

SetMegaManNaviStatsByte_longcall:
	mov r0, 0
	ldr r3, =SetNaviStatsByte|1
	bx r3

	.pool


ACDCTown_OnInitMapScript_NEW:
	ms_jump_if_flag_set CS_VAR_IMM, EVENT_402, @@alreadyInitialized
	ms_set_event_flag CS_VAR_IMM, EVENT_402
	ms_set_enter_map_screen_fade 0x1c, 0xff
	ms_start_cutscene ACDCTown_GiveRandomBattleItemsAndPrintMessage, 0x0
@@alreadyInitialized:
	ms_end

ACDCTown_ContinuousMapScript_NEW:
 	ms_jump_if_flag_clear CS_VAR_IMM, EVENT_403_START_BATTLE, @@notTalkedToMegaMan
 	ms_start_cutscene StartBattleGeneric, 0x1ff0018
 	ms_clear_event_flag CS_VAR_IMM, EVENT_403_START_BATTLE
@@notTalkedToMegaMan:
 	ms_end

ACDCTown_MegaManNPCScript:
 	npc_set_active_and_visible
 	npc_set_text_script_index 1
 	npc_set_sprite SPRITE_NPC_MEGA_MAN
 	npc_set_coords 65520, 162, 0
 	npc_set_animation 7 ; up left
 	npc_jump_with_link NPCScript_StationaryNPC

ACDCTown_GiveRandomBattleItemsAndPrintMessage:
	cs_lock_player_for_non_npc_dialogue_809e0b0
	cs_run_text_script CS_VAR_IMM, 0
	cs_give_item ITEM_REGUP1, 41
	cs_give_item ITEM_TAGCHIP, 1
	cs_give_bugfrags 9999
	cs_wait_chatbox 0x80
	cs_warp_cmd_8038040_2 0x0, MAP_GROUP_TRANSITION_TYPE_SAME_MAP_GROUP_TYPE, ACDCTown_CutsceneWarpData
	cs_unlock_player_after_non_npc_dialogue_809e122
	cs_end_for_map_reload_maybe_8037c64

PatchLButtonCutsceneScript:
	cs_lock_player_for_non_npc_dialogue_809e0b0
	cs_nop_80377d0
	cs_set_event_flag CS_VAR_IMM, 0x1731
	cs_write_ow_player_fixed_anim_select_8037dac CS_VAR_IMM, 0x4
	cs_decomp_text_archive ChooseRandomBattleFolderTextScript
	cs_run_text_script CS_VAR_IMM, 0
	cs_wait_chatbox 0x80
	cs_jump_if_var_equal 9, 1, @@abortedFolderSelection
; @@loop:
; 	cs_wait_var_equal 8, 1 ; wait for cross to be selected
; 	cs_jump_if_var_equal 9, 1, @@abortedCrossSelection
; 	cs_call_native_with_return_value AddCrossToSelectedCrosses|1
; 	cs_jump_if_var_equal 5, 5, @@allCrossesSelected
; 	cs_jump @@loop
; @@abortedCrossSelection:
; 	cs_set_var 8, 0
; 	cs_wait_chatbox 0x80
; 	cs_jump @@finishCutscene
; @@allCrossesSelected:
; 	cs_wait_chatbox 0x80
; 	cs_call_native_with_return_value WriteCrossesToCrossList|1
; @@finishCutscene:
	cs_call_native_with_return_value GiveRandomFolder|1	
@@abortedFolderSelection:
	cs_ow_player_sprite_special_with_arg 0x4, CS_VAR_IMM, 0x4
	cs_write_ow_player_fixed_anim_select_8037dac CS_VAR_IMM, 0x4
	cs_unlock_player_after_non_npc_dialogue_809e122
	cs_end_for_map_reload_maybe_8037c64

ACDCTown_MapObjects_NEW:
	.byte 0xff

	.align 4, 0
ACDCTown_NPCScripts_NEW:
	.word ACDCTown_MegaManNPCScript
	.word 0xff

	.align 4, 0
ACDCTown_CutsceneWarpData:
	.byte GROUP_ACDC_TOWN
	.byte MAP_ACDC_TOWN
	.byte 0 ; fade to black
	.byte OW_DOWN_RIGHT
	.word 0xffff0000
	.word 0x380000
	.word 0

	.align 4, 0
ACDCTownTextScript_NEW:
	.import "temp/ACDCTownScript.msg.lz"

	.align 4, 0
LoadNewGameSaveTextScript:
	.import "temp/LoadNewGameSaveTextScript.msg"

ChooseRandomBattleFolderTextScript:
	.import "temp/ChooseRandomBattleFolderTextScript.msg"

	.align 4

	.if IS_FALZAR == 1
BassChipIcon:
	import_chip_icon BASS

BassChipImage:
	import_chip_image BASS

BassChipPalette:
	import_chip_palette BASS

BigHookChipIcon:
	import_chip_icon BIGHOOK

BigHookChipImage:
	import_chip_image BIGHOOK

BigHookChipPalette:
	import_chip_palette BIGHOOK

DeltaRayChipIcon:
	import_chip_icon DELTARAY

DeltaRayChipImage:
	import_chip_image DELTARAY

DeltaRayChipPalette:
	import_chip_palette DELTARAY

ColForceChipIcon:
	import_chip_icon COLFORCE

ColForceChipImage:
	import_chip_image COLFORCE

ColForceChipPalette:
	import_chip_palette COLFORCE

BugRSwrdChipIcon:
	import_chip_icon BUGRSWRD

BugRSwrdChipImage:
	import_chip_image BUGRSWRD

BugRSwrdChipPalette:
	import_chip_palette BUGRSWRD

	.else
BassAnlyChipIcon:
	import_chip_icon BASSANLY

BassAnlyChipImage:
	import_chip_image BASSANLY

BassAnlyChipPalette:
	import_chip_palette BASSANLY

MetrKnukChipIcon:
	import_chip_icon METRKNUK

MetrKnukChipImage:
	import_chip_image METRKNUK

MetrKnukChipPalette:
	import_chip_palette METRKNUK

CrossDivChipIcon:
	import_chip_icon CROSSDIV

CrossDivChipImage:
	import_chip_image CROSSDIV

CrossDivChipPalette:
	import_chip_palette CROSSDIV

HubBatcChipIcon:
	import_chip_icon HUBBATC

HubBatcChipImage:
	import_chip_image HUBBATC

HubBatcChipPalette:
	import_chip_palette HUBBATC

BgDthThdChipIcon:
	import_chip_icon BGDTHTHD

BgDthThdChipImage:
	import_chip_image BGDTHTHD

BgDthThdChipPalette:
	import_chip_palette BGDTHTHD
	.endif

	.include "gen_folder/folders.asm"
