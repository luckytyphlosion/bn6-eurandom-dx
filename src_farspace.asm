
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
	ldr r0, =eCurRandomBattleFolder
	strb r2, [r0]
	sub r2, r2, 1
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

Hook_PatchAfterCheckMBForRegChip:
	mov r2, r1
	mov r1, 1
	tst r0, r1
	bne @@regNotAllowedVanilaRules

	push r7
	ldrh r0, [r5, 0x20]
	ldrh r1, [r5, 0x24]
	add r0, r0, r1
	mov r1, 0x20 
	mul r0, r1
	ldr r7, =word_202A020 
	add r7, r7, r0
	ldrh r0, [r7, 0x1c]
	lsr r0, r0, 7
	pop r7

	cmp r0, PANLGRAB
	beq @@isGrabChip
	cmp r0, AREAGRAB
	bne @@allowReg
@@isGrabChip:
	mov r0, SOUND_CANT_JACK_IN
	ldr r1, =PlaySoundEffect|1
	mov lr, pc
	bx r1
	ldr r0, =RandomBattleFolderNotSetProperlyTextScript
	mov r1, 4
	ldr r2, =chatbox_runScript_803FD9C|1
	mov lr, pc
	bx r2
	ldr r0, =Hook_PatchAfterCheckMBForRegChip_ReturnGrabChip|1
	bx r0

@@regNotAllowedVanilaRules:
	ldr r0, =Hook_PatchAfterCheckMBForRegChip_Return|1
	bx r0

@@allowReg:
	ldr r0, =Hook_PatchAfterCheckMBForRegChip_ReturnAllowReg|1
	bx r0

Hook_PatchCustMenuMainInput:
	push r4-r7,lr
	ldr r0, =GetBattleEffects|1
	mov lr, pc
	bx r0
	mov r1, 8
	tst r0, r1
	beq @@returnNormally
	
	mov r2, 0

	mov r0, 0
	bl GetBattleNaviStatsFolderIndex_longcall
	mov r4, r0
	tst r4, r4
	bne @@hostSetFolder
	mov r3, 1
	orr r2, r3
@@hostSetFolder:
	mov r0, 1
	bl GetBattleNaviStatsFolderIndex_longcall
	tst r0, r0
	bne @@clientSetFolder
	mov r3, 2
	orr r2, r3
@@clientSetFolder:
	mov r6, r0
	tst r2, r2
	bne @@oneOrMoreSidesFolderNotSet

	cmp r0, r4
	beq @@returnNormally

	ldrb r0, [r5, 2]
	cmp r0, 1
	beq @@alreadyInitializedTextBox

	; r4 = host folder
	; r6 = client folder

	mov r1, r10
	ldr r1, [r1, oToolkit_BattleStatePtr]
	mov r0, 0
	ldrb r3, [r1, oBattleState_NetworkSide]
	tst r3, r3 ; are we the host?
	beq @@settingHostFolderName_isHost
	mov r0, 1
@@settingHostFolderName_isHost:
	mov r2, r4
	bl WriteFolderIndexToBuffer

	; swap buffer index for other client
	mov r2, 1
	eor r0, r2
	mov r2, r6
	bl WriteFolderIndexToBuffer
	mov r1, 3
	b @@runTextScript
@@oneOrMoreSidesFolderNotSet:
	ldrb r0, [r5, 2]
	cmp r0, 1
	beq @@alreadyInitializedTextBox

	; r4 = host folder
	; r6 = client folder
	sub r2, r2, 1
	; in r2:
	; 0: host didn't set folder
	; 1: client didn't set folder
	; 2: both didn't set folder
	cmp r2, 2
	beq @@bothDidntSetFolder

	; get folder index of person who set folder (client)
	mov r3, r6

	cmp r2, 0
	beq @@gotFolderIndexOfPersonWhoSetFolder
	mov r3, r4
@@gotFolderIndexOfPersonWhoSetFolder:

	mov r1, r10
	ldr r1, [r1, oToolkit_BattleStatePtr]
	
	ldrb r1, [r1, oBattleState_NetworkSide]
	tst r1, r1
	beq @@folderNotSet_isHost
	; invert r2 if client to get the following:
	; 0: opponent didn't set folder
	; 1: client didn't set folder
	mov r0, 1
	eor r2, r0
@@folderNotSet_isHost:
	; r2 - text script index
	; r3 - get folder index of person who set folder
	push r2
	mov r0, 0
	mov r2, r3
	bl WriteFolderIndexToBuffer
	pop r2

@@bothDidntSetFolder:
	mov r1, r2

@@runTextScript:
	ldr r0, =RandomBattleFolderNotSetProperlyTextScript
	ldr r2, =chatbox_runScript|1
	mov lr, pc
	bx r2

	mov r0, 1
	strb r0, [r5, 2]

@@alreadyInitializedTextBox:
	pop r4-r7,pc

@@returnNormally:
	pop r4-r7
	pop r0
	mov lr, r0
	ldr r0, =CustMenuMainInput|1
	bx r0

; input:
; r0 - buffer index
; r2 - folder index
WriteFolderIndexToBuffer:
	push r0-r3, lr
	sub r2, r2, 1
	mov r3, r0

	lsl r0, r0, 3
	; get folder name buffer addr
	ldr r1, =eFolderNameBuffer
	add r0, r1, r0

	; store folder name into buffer
	ldr r1, =FolderIndexToName
	ldrb r1, [r1, r2]
	cmp r1, 0x01 ; zero
	bne @@notZero
	mov r1, 0x24 ; Z
	strb r1, [r0]
	mov r1, 0x2A ; e
	strb r1, [r0, 1]
	mov r1, 0x37 ; r
	strb r1, [r0, 2]
	mov r1, 0x34 ; o
	strb r1, [r0, 3]
	mov r1, 0xe6 ; terminator
	strb r1, [r0, 4]
	b @@wroteToBuffer
@@notZero:
	strb r1, [r0]
	mov r1, 0xe6
	strb r1, [r0, 1]
@@wroteToBuffer:

	; store buffer addr into chatbox
	mov r1, r10
	ldr r1, [r1, oToolkit_ChatboxPtr]
	lsl r3, r3, 2
	add r3, 0x4c
	str r0, [r1, r3]
	pop r0-r3, pc

GetBattleNaviStatsFolderIndex_longcall:
	push r1-r3,lr
	mov r1, oNaviStats_FolderIndex
	ldr r2, =GetBattleNaviStatsByte|1
	mov lr, pc
	bx r2
	pop r1-r3,pc
	
	.pool

FolderIndexToName:
	.byte 0x0B ; A
	.byte 0x0C ; B
	.byte 0x0D ; C
	.byte 0x0E ; D
	.byte 0x0F ; E
	.byte 0x10 ; F
	.byte 0x11 ; G
	.byte 0x12 ; H
	.byte 0x14 ; J
	.byte 0x15 ; K
	.byte 0x16 ; L
	.byte 0x17 ; M
	.byte 0x18 ; N
	.byte 0x19 ; O
	.byte 0x1A ; P
	.byte 0x1B ; Q
	.byte 0x1C ; R
	.byte 0x1D ; S
	.byte 0x1E ; T
	.byte 0x1F ; U
	.byte 0x20 ; V
	.byte 0x21 ; W
	.byte 0x22 ; X
	.byte 0x23 ; Y
	.byte 0x24 ; Z
	.byte 0x26 ; a
	.byte 0x27 ; b
	.byte 0x28 ; c
	.byte 0x29 ; d
	.byte 0x2A ; e
	.byte 0x2B ; f
	.byte 0x2C ; g
	.byte 0x2D ; h
	.byte 0x2E ; i
	.byte 0x2F ; j
	.byte 0x30 ; k
	.byte 0x32 ; m
	.byte 0x33 ; n
	.byte 0x34 ; o
	.byte 0x35 ; p
	.byte 0x36 ; q
	.byte 0x37 ; r
	.byte 0x38 ; s
	.byte 0x39 ; t
	.byte 0x3A ; u
	.byte 0x3B ; v
	.byte 0x3C ; w
	.byte 0x3D ; x
	.byte 0x3E ; y
	.byte 0x3F ; z
	.byte 0x01 ; 0
	.byte 0x02 ; 1
	.byte 0x03 ; 2
	.byte 0x04 ; 3
	.byte 0x05 ; 4
	.byte 0x06 ; 5
	.byte 0x07 ; 6
	.byte 0x08 ; 7
	.byte 0x09 ; 8
	.byte 0x0A ; 9

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

	.align 4, 0
ChooseRandomBattleFolderTextScript:
	.import "temp/ChooseRandomBattleFolderTextScript.msg"

	.align 4, 0
RandomBattleFolderNotSetProperlyTextScript:
	.import "temp/RandomBattleFolderNotSetProperlyTextScript.msg"

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
