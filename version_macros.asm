
	.macro .vdefinelabel, label_name, cf_offset, cg_offset
		.if IS_FALZAR == 1
			.definelabel label_name, cf_offset
		.else
			.definelabel label_name, cg_offset
		.endif
	.endmacro

	.macro .vorg, cf_offset, cg_offset
		.if IS_FALZAR == 1
			.org cf_offset
		.else
			.org cg_offset
		.endif
	.endmacro

	.macro .vbranch, cf_offset, cg_offset
		.if IS_FALZAR == 1
			b cf_offset
		.else
			b cg_offset
		.endif
	.endmacro

	.macro .vinclude, cf_file, cg_file
		.if IS_FALZAR == 1
			.include cf_file
		.else
			.include cg_file
		.endif
	.endmacro

	.expfunc vequ(cf_value, cg_value), IS_FALZAR == 1 ? cf_value : cg_value
