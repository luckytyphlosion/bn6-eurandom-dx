
	.macro create_lz, filename
		.create filename + ".lz", 0
			.dw ((filesize(filename) + 4) << 8) | 0x10
			.import filename
		.close
	.endmacro

	.gba

	create_lz "temp/ACDCTownScript.msg"
