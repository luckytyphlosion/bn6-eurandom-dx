
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
VERSION="v0.0.4"
mkdir -p "out_patch/bn6_random_battle/${VERSION}"
./tools/floating/flips.exe -c -b "bn6f.gba" "bn6f-random-battle.gba" "out_patch/bn6_random_battle/${VERSION}/BR6E_00.bps"
./tools/floating/flips.exe -c -b "bn6g.gba" "bn6g-random-battle.gba" "out_patch/bn6_random_battle/${VERSION}/BR5E_00.bps"
touch out_patch/bn6_random_battle/info.toml
