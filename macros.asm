
	.include "version_macros.asm"
	.include "include/macros/enum.inc"
	.include "include/bytecode/map_script.inc"
	.include "include/bytecode/cutscene_script.inc"
	.include "include/bytecode/cutscene_camera_script.inc"
	.include "include/bytecode/npc_script.inc"
	.include "include/bytecode/gfx_anim_script.inc"

	.macro movflag, flag16
	mov r0, (flag16 >> 8)
	mov r1, (flag16 & 0xFF)
	.endmacro

	.macro chip_and_code, chip_id, code
	.halfword (chip_id & 0x1ff) | code << 9
	.endmacro
