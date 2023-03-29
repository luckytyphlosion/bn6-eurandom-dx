
mkdir -p "temp/"

rm -rf "temp/"
tools/TextPet.exe run-script gen_compressed_text.tps
tools/TextPet.exe run-script gen_text.tps
tools/armips.exe lzpad.s
tools/lzss.exe -ewn "temp/ACDCTownScript.msg.lz"

if [[ $? -ne 0 ]] ; then
    exit 1
fi

# falzar
tools/armips.exe build.asm -sym bn6f-random-battle.sym -equ IS_FALZAR 1

# gregar
tools/armips.exe build.asm -sym bn6g-random-battle.sym -equ IS_FALZAR 0

if [[ $? -ne 0 ]] ; then
    exit 1
fi

# Make patches
#mkdir -p "out_patch/bn5_gate_redux/v1.2.0"
#./tools/floating/flips.exe -c -b "bn5p.gba" "bn5p-link-navis-redux.gba" "out_patch/bn5_gate_redux/v1.2.0/BRBE_00.bps"
#./tools/floating/flips.exe -c -b "bn5c.gba" "bn5c-link-navis-redux.gba" "out_patch/bn5_gate_redux/v1.2.0/BRKE_00.bps"
#touch out_patch/bn5_gate_redux/info.toml
