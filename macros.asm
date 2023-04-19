
	.include "version_macros.asm"
	.include "include/macros/enum.inc"
	.include "include/bytecode/map_script.inc"
	.include "include/bytecode/cutscene_script.inc"
	.include "include/bytecode/cutscene_camera_script.inc"
	.include "include/bytecode/npc_script.inc"
	.include "include/bytecode/gfx_anim_script.inc"
	.include "bbn6/macros.asm"

	.macro movflag, flag16
	mov r0, (flag16 >> 8)
	mov r1, (flag16 & 0xFF)
	.endmacro

	.macro chip_and_code, chip_id, code
	.halfword (chip_id & 0x1ff) | code << 9
	.endmacro

	.macro import_chip_icon, chip_id
	.import OTHER_VERSION_ROM, readu32(OTHER_VERSION_ROM, CHIP_INFO_LOAD_ADDR + chip_id * 0x2c + 0x20) - 0x8000000, 0x80
	.endmacro

	.macro import_chip_image, chip_id
	.import OTHER_VERSION_ROM, readu32(OTHER_VERSION_ROM, CHIP_INFO_LOAD_ADDR + chip_id * 0x2c + 0x24) - 0x8000000, 0x20 * 42
	.endmacro

	.macro import_chip_palette, chip_id
	.import OTHER_VERSION_ROM, readu32(OTHER_VERSION_ROM, CHIP_INFO_LOAD_ADDR + chip_id * 0x2c + 0x28) - 0x8000000, 0x20 * 42
	.endmacro

	.macro import_chip_gfx_ptrs, chip_id, chip_icon_ptr, chip_image_ptr, chip_palette_ptr
	.org ChipInfo + chip_id * 0x2c + 0x20
	.word chip_icon_ptr
	.word chip_image_ptr
	.word chip_palette_ptr
	.endmacro

	.macro set_chip_attack_power, chip_id, attack_power
	.org ChipInfo + chip_id * 0x2c + 0x1a
	.halfword attack_power
	.endmacro
