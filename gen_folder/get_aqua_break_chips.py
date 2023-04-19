from chip_db import ChipDB
import random as randomlib
import collections
from gen_folder import GenFolder
import json

def add_chips_to_chips_by_code(chips, is_break=False):
    found_codes = set()
    chips_by_code = collections.defaultdict(list)

    for chip_data in chips:
        chip_name = chip_data["name"]
        chip_codes = GenFolder.simplify_codes(chip_data["codes"])

        for code in chip_codes:
            chips_by_code[code].append(chip_name)
            found_codes.add(code)

    return chips_by_code

def main():
    seed = randomlib.randint(0, 10000000000)
    print(f"seed: {seed}")
    random = randomlib.Random(seed)
    
    with open("bn6_chips.json", "r") as f:
        chip_game_info = json.load(f)

    chip_db = ChipDB("sorted_chips.yml", chip_game_info, random, False)
    aquabreak_chips_by_code = collections.defaultdict(list)

    aqua_chips = chip_db.query(
        category_names=("ranged", "constrained", "pseudoMega", "megaChips"),
        effects=("aqua",)
    )

    break_chips = chip_db.query(
        category_names=("ranged", "constrained", "pseudoMega", "megaChips"),
        effects=("break",)
    )

    aqua_chips_by_code = add_chips_to_chips_by_code(aqua_chips)
    break_chips_by_code = add_chips_to_chips_by_code(break_chips)
    aquabreak_chips_by_code = {}
    for code in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        aqua_chips_for_code = aqua_chips_by_code.get(code)
        asterisk_count = 0

        if aqua_chips_for_code is None:
            aqua_chips_for_code = [f"{chip_name} *" for chip_name in aqua_chips_by_code.get("*")]
            asterisk_count += 1

        break_chips_for_code = break_chips_by_code.get(code)
        if break_chips_for_code is None:
            break_chips_for_code = [f"{chip_name} *" for chip_name in break_chips_by_code.get("*")]
            asterisk_count += 1

        if asterisk_count == 2:
            continue

        aquabreak_chips_by_code[code] = (aqua_chips_for_code, break_chips_for_code)

    output = ""

    for code, (aqua_chips_for_code, break_chips_for_code) in aquabreak_chips_by_code.items():
        output += f"{code}: {', '.join(aqua_chips_for_code)} | {', '.join(break_chips_for_code)}\n"

    with open("get_aqua_break_chips_out.dump", "w+") as f:
        f.write(output)

if __name__ == "__main__":
    main()
