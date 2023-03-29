
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

	.pool

ACDCTown_OnInitMapScript_NEW:
	ms_jump_if_flag_set CS_VAR_IMM, EVENT_402, @@alreadyInitialized
	ms_set_event_flag CS_VAR_IMM, EVENT_402
	ms_set_enter_map_screen_fade 0x1c, 0xff
	ms_start_cutscene ACDCTown_GiveRandomBattleItemsAndPrintMessage, 0x0
@@alreadyInitialized:
	ms_end

ACDCTown_ContinuousMapScript_NEW:
	ms_end
; 	ms_jump_if_flag_clear CS_VAR_IMM, EVENT_403, @@doNotStartBattle
; 	ms_start_cutscene ACDCTown_StartTrainingModeCutsceneScript, 0x0
; 	ms_clear_event_flag CS_VAR_IMM, EVENT_403
; @@doNotStartBattle:
; 	ms_jump_if_flag_clear CS_VAR_IMM, EVENT_404_TALKED_TO_MODE_NPC, @@notTalkedToModeNPC
; 	ms_start_cutscene ACDCTown_SetTrainingModeCutsceneScript, 0x0
; 	ms_clear_event_flag CS_VAR_IMM, EVENT_404_TALKED_TO_MODE_NPC
; @@notTalkedToModeNPC:
; 	ms_end

; ACDCTown_MegaManNPCScript:
; 	npc_set_active_and_visible
; 	npc_set_text_script_index 1
; 	npc_set_sprite SPRITE_NPC_MEGA_MAN
; 	npc_set_coords 65520, 162, 0
; 	npc_set_animation 7 ; up left
; 	npc_jump_with_link NPCScript_StationaryNPC

ACDCTown_GiveRandomBattleItemsAndPrintMessage:
	cs_lock_player_for_non_npc_dialogue_809e0b0
	cs_run_text_script CS_VAR_IMM, 0
	cs_give_item ITEM_REGUP1, 26
	cs_give_item ITEM_TAGCHIP, 1
	cs_wait_chatbox 0x80
	cs_warp_cmd_8038040_2 0x0, MAP_GROUP_TRANSITION_TYPE_SAME_MAP_GROUP_TYPE, ACDCTown_CutsceneWarpData
	cs_unlock_player_after_non_npc_dialogue_809e122
	cs_end_for_map_reload_maybe_8037c64

ACDCTown_MapObjects_NEW:
	.byte 0xff

	.align 4, 0
ACDCTown_NPCScripts_NEW:
	; .word ACDCTown_MegaManNPCScript
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
