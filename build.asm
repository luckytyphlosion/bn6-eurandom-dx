
	.gba

	.include "macros.asm"
	.include "constants.asm"
	.include "defines.asm"

	.open INPUT_ROM, OUTPUT_ROM, 0x8000000

	; === orgs ===
	.include "src_orgs.asm"
	.include "bbn6/src_orgs.asm"

	; == freespace ==
	.org fspace
	.include "src_farspace.asm"
	.include "bbn6/src_farspace.asm"

	.close
