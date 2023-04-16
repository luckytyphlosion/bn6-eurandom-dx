from chip_db import ChipDB, dump_noref_yaml, mb_to_max_chip_count
import random as randomlib
import json
import itertools
import collections
import functools
import sys
import jsbeautifier
import argparse
import pathlib
import glob
import statistics

random = None

def weighted_random(population_and_weights):
    return random.choices(tuple(population_and_weights.keys()), tuple(population_and_weights.values()), k=1)[0]

class FolderChip:
    __slots__ = ("name", "codes")

    def __init__(self, name, codes):
        self.name = name
        self.codes = codes

    @property
    def quantity(self):
        return len(self.codes)

    @classmethod
    def from_code(cls, name, code):
        return cls(name, [code])

    def __repr__(self):
        return f"{self.name}: {', '.join(self.codes)}"

class IllegalFolderError(Exception):
    pass

class OuterBreakError(Exception):
    pass

class Folder:
    __slots__ = ("data", "chip_game_info", "pa_chips", "non_pa_chips", "cur_alphabet_pa_code", "all_chips_by_name")

    def __init__(self, chip_game_info, all_chips_by_name):
        self.data = {}
        self.non_pa_chips = {}
        self.pa_chips = {}
        self.chip_game_info = chip_game_info
        self.all_chips_by_name = all_chips_by_name
        self.cur_alphabet_pa_code = 0

    def __add_chip_common(self, folder_dest, name, code, is_pa=False):
        #if len(self.data) >= 30:
        #    raise RuntimeError(f"Folder has {len(self.data)} chips! data:\n{data}")

        chip_in_folder = folder_dest.get(name)
        if chip_in_folder is None:
            folder_dest[name] = FolderChip.from_code(name, code)
        else:
            max_chip_count = mb_to_max_chip_count(self.chip_game_info[name]["mb"])
            if max_chip_count <= chip_in_folder.quantity:
                raise IllegalFolderError(f"{name} with {self.chip_game_info[name]['mb']}MB has max count of {max_chip_count}! (quantity: {chip_in_folder.quantity})")

            chip_in_folder.codes.append(code)

    def add_chip(self, name, code):
        self.__add_chip_common(self.data, name, code)
        self.__add_chip_common(self.non_pa_chips, name, code)

    def has_chip(self, name):
        return name in self.data

    def max_chip_count_reached(self, name):
        max_chip_count = mb_to_max_chip_count(self.chip_game_info[name]["mb"])
        return max_chip_count <= self.data.get(name).quantity

    def add_pa(self, pa):
        pa_codes = set()
        for chip in pa["parts"]:
            self.__add_chip_common(self.data, chip["name"], chip["code"])
            pa_codes.add(chip["code"])

        if "*" in pa_codes:
            pa_codes.remove("*")
            if len(pa_codes) == 0:
                pa_code = "*"
            elif len(pa_codes) == 1:
                pa_code = next(iter(pa_codes))
            else:
                raise RuntimeError()
        elif len(pa_codes) == 1:
            pa_code = next(iter(pa_codes))
        else:
            pa_code = str(self.cur_alphabet_pa_code)
            self.cur_alphabet_pa_code += 1

        self.__add_chip_common(self.pa_chips, pa["name"], pa_code, is_pa=True)
        return pa["name"], pa_code

    def num_chips(self):
        count = 0
        for folder_chip in self.data.values():
            count += folder_chip.quantity

        return count

    def data_pas_as_chip_iterator(self):
        return itertools.chain(self.pa_chips.items(), self.non_pa_chips.items())

    def count_num_of_category(self, category_name):
        category_count = 0

        for name, folder_chip in self.data.items():
            #try:
            if self.all_chips_by_name[name]["category"] == category_name:
                category_count += 1
            #except Exception as e:
            #    dump_noref_yaml(self.all_chips_by_name, "all_chips_by_name_debug.yml")                
            #    raise RuntimeError(e)

        return category_count

    def __repr__(self):
        return "\n".join(f"{folder_chip}" for folder_chip in self.data.values())

    def output_ungrouped_folder(self):
        output = ""
        for folder_chip in self.data.values():
            for code in folder_chip.codes:
                output += f"{folder_chip.name} {code}\n"

        return output

    def output_ungrouped_non_pa_folder(self):
        output = ""
        for folder_chip in self.non_pa_chips.values():
            for code in folder_chip.codes:
                output += f"{folder_chip.name} {code}\n"

        return output

    def get_families(self):
        families = set()

        for name, folder_chip in self.data.items():
            families.add(self.all_chips_by_name[name]["family"])

        return families

    def get_non_soup_pa_codes_except_asterisk_and_gigas(self):
        codes = set()

        for folder_chip in self.pa_chips.values():
            codes.update(code for code in folder_chip.codes if not code.isdigit() and code != "*")

        for chip_name, folder_chip in self.non_pa_chips.items():
            codes.update(code for code in folder_chip.codes if code != "*" and self.all_chips_by_name[chip_name]["category"] != "gigaChips")

        return codes

    def get_code_count(self, wanted_code):
        code_count = 0

        for folder_chip in self.pa_chips.values():
            for code in folder_chip.codes:
                if wanted_code == code:
                    code_count += 1

        for folder_chip in self.non_pa_chips.values():
            for code in folder_chip.codes:
                if wanted_code == code:
                    code_count += 1

        return code_count

    def find_codes_of_chip(self, chip_name):
        return self.non_pa_chips.get(chip_name, self.pa_chips.get(chip_name)).codes

HIGH_PA = 0
MEDIUM_PA = 1
LOW_PA = 2
HIGH_HIGH_PA = 3
HIGH_MEDIUM_PA = 4

class ChipWeight:
    __slots__ = ("weight", "reasons")

    def __init__(self, weight=0, reason=None):
        self.weight = weight
        self.reasons = []
        if isinstance(reason, str):
            self.reasons.append(reason)
        elif isinstance(reason, list):
            self.reasons.extend(reason)

    def __repr__(self):
        return f"ChipWeight(weight={self.weight}, reasons={self.reasons})"

    def __add__(self, other):
        return ChipWeight(self.weight + other.weight, self.reasons + other.reasons)

    def __mul__(self, other):
        return ChipWeight(self.weight * other.weight, self.reasons + other.reasons)

    def add_subreason(self, weight, subreason):
        self.weight += weight
        self.reasons[-1] += subreason

    def mul_subreason(self, weight, subreason):
        self.weight *= weight
        self.reasons[-1] += subreason

    def add(self, other):
        self.weight += other.weight
        self.reasons.extend(other.reasons)

    def add_weight(self, weight, reason):
        self.weight += weight
        if isinstance(reason, list):
            self.reasons.extend(reason)
        else:
            self.reasons.append(reason)

    def sub_weight(self, weight, reason):
        self.weight -= weight
        self.reasons.append(reason)

    def mul_weight(self, weight, reason):
        self.weight *= weight
        self.reasons.append(reason)

    def to_debug_dict(self):
        return {"weight": self.weight, "reasons": self.reasons}

    def is_no_reason(self):
        return self.reasons[0] == "None"

class ChipWeights(collections.defaultdict):
    def __init__(self):
        super(ChipWeights, self).__init__(ChipWeight)

    #def __getitem__(self, item):
    #    
    def __setitem__(self, item, value):
        #if isinstance(value, tuple):
        #    value = ChipWeight(value[0], value[1])

        super(ChipWeights, self).__setitem__(item, value)

    def to_debug_dict(self):
        return {item: weight.to_debug_dict() for item, weight in self.items() if weight.weight != 0 and not weight.is_no_reason()}

    def to_dict(self):
        return {item: weight.weight for item, weight in self.items()}

class GenFolder:
    __slots__ = ("chip_db", "chip_game_info", "chosen_pas", "folder", "all_non_pa_chips_by_name", "num_megas", "num_pseudo_megas", "num_gigas", "all_chips_by_name", "splay_codes", "chip_weights_log", "input_chips_filename", "print_stats", "chip_usage_stats", "add_lifeaur")

    def __init__(self, sorted_chips_filename, chip_game_info_filename, output_filename, seed, input_chips_filename, print_stats):
        global random
        if seed is None:
            seed = randomlib.randint(0, 10000000000)
        print(f"seed: {seed}")
        random = randomlib.Random(seed)

        # 15% chance to add LifeAur
        if random.random() < 0.15:
            self.add_lifeaur = True
        else:
            self.add_lifeaur = False

        self.chip_weights_log = ""
        self.input_chips_filename = input_chips_filename
        self.print_stats = print_stats

        #random.seed(4444)
        with open(chip_game_info_filename, "r") as f:
            self.chip_game_info = json.load(f)

        self.chip_db = ChipDB(sorted_chips_filename, self.chip_game_info, random, self.add_lifeaur)
        self.__gen_all_chips_by_name()

        self.folder = Folder(self.chip_game_info, self.all_chips_by_name)

        self.chip_usage_stats = self.__calc_chip_usage_stats(False)
        try:
            self.chosen_pas = []
            self.splay_codes = True

            if self.input_chips_filename is None:
                self.__gen_pas()

            self.__todo_algo1()
            output = self.folder.output_ungrouped_folder()
            with open(output_filename, "w+") as f:
                f.write(output)

            used_pa_names = self.folder.pa_chips.keys()
            output_filepath = pathlib.Path(output_filename)
            output_filepath_parent = output_filepath.parent
            output_basename = output_filepath.name
            pa_output_filepath = output_filepath_parent / "pas" / output_basename
            non_pa_output_filepath = output_filepath_parent / "non_pas" / output_basename

            pa_output_filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(pa_output_filepath, "w+") as f:
                f.write("\n".join(used_pa_names) + "\n")

            used_non_pa_chip_names = self.folder.output_ungrouped_non_pa_folder()
            non_pa_output_filepath.parent.mkdir(parents=True, exist_ok=True)

            with open(non_pa_output_filepath, "w+") as f:
                f.write(used_non_pa_chip_names)

            with open(f"{pathlib.Path(output_basename).stem}_chip_weights_log.dump", "w+") as f:
                f.write(self.chip_weights_log)

            print(output)
            if self.print_stats:
                self.__calc_chip_usage_stats()
        except Exception as e:
            print(f"Exception occurred: folder below\n{self.folder}")
            with open("chip_weights_log.dump", "w+") as f:
                f.write(self.chip_weights_log)
            raise e

    def __gen_all_chips_by_name(self):
        self.all_non_pa_chips_by_name = self.querydict_db(
            category_names=("ranged", "constrained", "pseudoMega", "nonAttacking", "megaChips", "gigaChips")
        )
        
        self.all_chips_by_name = self.querydict_db()
        dump_noref_yaml(self.all_chips_by_name, "all_chips_by_name.yml")

    def __gen_pas(self):
        pa_type = weighted_random({
            HIGH_PA: 0.3,
            MEDIUM_PA: 0.2,
            LOW_PA: 0.1,
            HIGH_HIGH_PA: 0.2,
            HIGH_MEDIUM_PA: 0.2
        })

        print(f"pa_type: {pa_type}")
        if pa_type in {HIGH_PA, HIGH_HIGH_PA, HIGH_MEDIUM_PA}:
            wanted_rank = "highChips"
        elif pa_type == MEDIUM_PA:
            wanted_rank = "mediumChips"
        else:
            wanted_rank = "lowChips"

        pa_chips_1 = self.query_db(
            category_names=("programAdvances",),
            ranks=(wanted_rank,)
        )

        #dump_noref_yaml(pa_chips_1, "pa_chips_1.yml")
        chosen_pa_1 = random.choice(pa_chips_1)
        self.add_pa(chosen_pa_1)

        if pa_type == HIGH_HIGH_PA:
            wanted_rank = "highChips"
        elif pa_type == HIGH_MEDIUM_PA:
            wanted_rank = "mediumChips"
        else:
            wanted_rank = None

        if wanted_rank is not None:
            chosen_pa_1_name = chosen_pa_1["name"]
            while True:
                pa_chips_2 = self.query_db(
                    category_names=("programAdvances",),
                    ranks=(wanted_rank,)
                )
                chosen_pa_2 = random.choice(pa_chips_2)
                
                if chosen_pa_1_name != chosen_pa_2["name"]:
                    if (chosen_pa_1_name == "FlmHook" and chosen_pa_2["name"] == "MstrCros") or (chosen_pa_1_name == "MstrCros" and chosen_pa_2["name"] == "FlmHook"):
                        if chosen_pa_1_name == "FlmHook":
                            flmhook_pa = chosen_pa_1
                        else:
                            flmhook_pa = chosen_pa_2
    
                        if flmhook_pa["parts"][0]["name"] != "FireHit3":
                            break
                    else:
                        break
            try:
                self.add_pa(chosen_pa_2)
            except Exception as e:
                raise RuntimeError(f"chosen_pa_1_name: {chosen_pa_1_name}, chosen_pa_2['name']: {chosen_pa_2['name']}")
        #print(self.folder)

    def __add_input_chips(self):
        ADDING_PAS = 0
        ADDING_CHIPS = 1

        input_chips_state = ADDING_PAS

        with open(self.input_chips_filename, "r") as f:
            for line in f:
                line = line.strip()
                if line == "":
                    continue
                if line == "---":
                    input_chips_state = ADDING_CHIPS
                else:
                    line_split = line.split(", ", maxsplit=1)
                    if len(line_split) == 1:
                        chip_name_and_code = line_split[0]
                        ignore_necessity = False
                    else:
                        chip_name_and_code, ignore_necessity_str = line_split
                        ignore_necessity = True if ignore_necessity_str.lower() == "true" else False

                    if input_chips_state == ADDING_PAS:
                        pa_info = chip_name_and_code.split(" | ")
                        pa_name = pa_info[0]
                        pa_parts_packed = pa_info[1:]
                        pa_parts = []
                        for pa_part_packed in pa_parts_packed:
                            chip_name, chip_code = pa_part_packed.split(" ", maxsplit=1)
                            pa_parts.append({"name": chip_name, "code": chip_code})

                        chosen_pa = {
                            "name": pa_name,
                            "parts": pa_parts
                        }
                        self.add_pa(chosen_pa, ignore_necessity)
                    elif input_chips_state == ADDING_CHIPS:
                        chip_name_and_code_split = chip_name_and_code.split(" ", maxsplit=1)
                        if len(chip_name_and_code_split) == 1:
                            chip_name = chip_name_and_code_split[0]
                            chip_code = None
                        else:
                            chip_name, chip_code = chip_name_and_code_split
    
                        chosen_chip = self.all_chips_by_name[chip_name]

                        if chip_code is None:
                            chip_code = self.random_code(chosen_chip["codes"])

                        self.add_chip(chip_name, chip_code, ignore_necessity)
                    else:
                        raise RuntimeError()

    def query_db(self, **kwargs):
        return self.chip_db.query(**kwargs)

    def querydict_db(self, **kwargs):
        return self.chip_db.querydict(**kwargs)

    def add_pa(self, chosen_pa, ignore_necessity=False):
        self.chosen_pas.append(chosen_pa)
        pa_name, pa_code = self.folder.add_pa(chosen_pa)
        if not ignore_necessity:
            self.try_add_necessity(pa_name, pa_code)

    def add_chip(self, name, code, ignore_necessity=False):
        self.folder.add_chip(name, code)
        if not ignore_necessity:
            self.try_add_necessity(name, code)
            
    def try_add_necessity(self, name, code):
        necessities = self.all_chips_by_name[name]["necessity"]
        if len(necessities) != 0:
            #print(f"necessity chip name: {name}")
            # first check all current chips if they have an effect that matches the newly chip's necessity
            necessities_as_set = set(necessities)
            immobilization_like_effects_in_necessities = len({"paralysis", "frozen", "bubbled", "immobilization"} & necessities_as_set) != 0
            for cur_chip_name, folder_chip in self.folder.data_pas_as_chip_iterator():
                if cur_chip_name == name:
                    continue
                chip_data = self.all_chips_by_name[cur_chip_name]
                for effect in itertools.chain(chip_data["almostAllEffects"], (cur_chip_name,)):
                    if effect in necessities_as_set:
                        if name == "BlkBomb" or (immobilization_like_effects_in_necessities and effect in {"paralysis", "frozen", "bubbled", "immobilization"}):
                            if "*" not in chip_data["codes"] and code not in chip_data["codes"]:
                                continue

                        return

            # if not, then choose a random necessity and fulfill it
            necessity = random.choice(sorted(necessities))
            folder_families = self.folder.get_families()
            if code == "*" or necessity == "uninstall":
                code = None

            category_chips = self.query_db(
                category_names=("ranged", "constrained", "pseudoMega", "nonAttacking", "megaChips", "gigaChips"),
                exclude_families=folder_families,
                effects=(necessity,),
                code=code
            )

            #print(f"category_chips: {category_chips}")
            try:
                necessity_chip = random.choice(category_chips)
            except IndexError as e:
                raise RuntimeError(f"necessities: {necessities}, necessity: {necessity}")

            necessity_chip_name = necessity_chip["name"]
            if name == "BlkBomb":
                filtered_codes = [necessity_chip_code_candidate for necessity_chip_code_candidate in necessity_chip["codes"] if necessity_chip_code_candidate == "*" or necessity_chip_code_candidate == code]
            else:
                filtered_codes = necessity_chip["codes"]

            necessity_chip_code = self.random_code(necessity_chip["codes"])

            self.add_chip(necessity_chip_name, necessity_chip_code)

    #class CategoryRank:
    #    __slots__ = ("category", "rank")
    #
    #    def __init__(self, category, rank):
    #    
    #    def __key(self):
    #        return (self.category_names, self.ranks)
    #
    #    def __hash__(self):
    #        return hash(self.__key())
    #
    #    def __eq__(self, other):
    #        if isinstance(other, QueryParams):
    #            return self.__key() == other.__key()
    #        return NotImplemented

        
    #@staticmethod
    #def pick_two_random_different_family
    def __todo_algo1(self):
        self.num_megas = random.randint(3, 4)
        self.num_pseudo_megas = weighted_random({0: 0.8, 1: 0.2})
        self.num_gigas = 1

        if self.input_chips_filename is not None:
            self.__add_input_chips()
        else:
            if len(self.chosen_pas) == 1:
                self.initial_chip_pick_common("ranged", 2,
                    {"highChips": 1.0},
                    {"highChips": {2: 1.0}}
                )
                self.initial_chip_pick_common("constrained", 1,
                    {"highChips": 0.5, "mediumChips": 0.5},
                    {
                        "highChips": {
                            1: 0.8,
                            2: 0.2
                        },
                        "mediumChips": {
                            1: 0.3,
                            2: 0.7
                        }
                    }
                )
                self.initial_chip_pick_common("nonAttacking", 1,
                    {"highChips": 36, "mediumChips": 5},
                    {
                        "highChips": {
                            1: 0.8,
                            2: 0.2
                        },
                        "mediumChips": {
                            1: 0.8,
                            2: 0.2
                        }
                    }
                )
            else:
                self.initial_chip_pick_common("ranged", 1,
                    {"highChips": 0.5, "mediumChips": 0.5},
                    {
                        "highChips": {
                            1: 0.8,
                            2: 0.2
                        },
                        "mediumChips": {
                            1: 0.3,
                            2: 0.7
                        }
                    }
                )
                self.initial_chip_pick_common("constrained", 2,
                    {"highChips": 0.5, "mediumChips": 0.5},
                    {
                        "highChips": {
                            1: 0.8,
                            2: 0.2
                        },
                        "mediumChips": {
                            1: 0.3,
                            2: 0.7
                        }
                    }
                )
                self.initial_chip_pick_common("nonAttacking", 1,
                    {"highChips": 36, "mediumChips": 5},
                    {
                        "highChips": {
                            1: 0.8,
                            2: 0.2
                        },
                        "mediumChips": {
                            1: 0.8,
                            2: 0.2
                        }
                    }
                )

        if len(self.chosen_pas) == 1:
            category_rank_weights = {
                ("ranged", "highChips"): 40,
                #("ranged", "mediumChips"): 8,
                ("constrained", "highChips"): 3,
                ("constrained", "mediumChips"): 3,
                ("nonAttacking", "highChips"): 6,
                ("nonAttacking", "mediumChips"): 1,
            }

            found_code_count_weights = {
                1: 1.0,
                2: 0.8,
                3: 0.6,
                4: 0.5,
                5: 0.4,
                6: 0
            }

            category_rank_quantity_weights = {
                ("ranged", "highChips"): {
                    1: 0.2,
                    2: 0.7,
                    3: 0.1
                },
                ("ranged", "mediumChips"): {
                    1: 0.2,
                    2: 0.8
                },
                ("constrained", "highChips"): {
                    1: 0.8,
                    2: 0.2
                },
                ("constrained", "mediumChips"): {
                    1: 0.6,
                    2: 0.4
                },
                ("nonAttacking", "highChips"): {
                    1: 0.7,
                    2: 0.3
                },
                ("nonAttacking", "mediumChips"): {
                    1: 0.7,
                    2: 0.3
                }
            }
            if self.splay_codes:
                synergy_picks_weight = 0.1
            else:
                synergy_picks_weight = 0.4
            #print(f"folder: {self.folder}")
        else:
            category_rank_weights = {
                ("ranged", "highChips"): 11,
                ("ranged", "mediumChips"): 11,
                ("constrained", "highChips"): 11,
                ("constrained", "mediumChips"): 11,
                ("nonAttacking", "highChips"): 6,
                ("nonAttacking", "mediumChips"): 1,
            }

            found_code_count_weights = {
                1: 1.0,
                2: 0.8,
                3: 0.6,
                4: 0.5,
                5: 0.4,
                6: 0
            }

            category_rank_quantity_weights = {
                ("ranged", "highChips"): {
                    1: 0.8,
                    2: 0.2
                },
                ("ranged", "mediumChips"): {
                    1: 0.3,
                    2: 0.7
                },
                ("constrained", "highChips"): {
                    1: 0.8,
                    2: 0.2
                },
                ("constrained", "mediumChips"): {
                    1: 0.3,
                    2: 0.7
                },
                ("nonAttacking", "highChips"): {
                    1: 0.7,
                    2: 0.3
                },
                ("nonAttacking", "mediumChips"): {
                    1: 0.7,
                    2: 0.3
                }
            }

            if self.splay_codes:
                synergy_picks_weight = 0.35
            else:
                synergy_picks_weight = 0.7

        if self.folder.count_num_of_category("gigaChips") == 0:
            giga_weights = {
                "Bass": 3,
                "BigHook": 3,
                "DeltaRay": 3,
                "ColForce": 3,
                "BugRSwrd": 1,
                "BassAnly": 3,
                "MetrKnuk": 3,
                "CrossDiv": 3,
                "HubBatc": 2,
                "BgDthThd": 1,
            }

            giga_chip_name = weighted_random(giga_weights)
            giga_chip_code = self.all_chips_by_name[giga_chip_name]["codes"][0]
            self.add_chip(giga_chip_name, giga_chip_code)

        # 25% chance to add in area
        if random.randint(0, 3) == 0:
            # six possible area types
            # panlgrab
            # areagrab
            # panlgrab, panlgrab
            # areagrab, panlgrab
            # areagrab, areagrab

            area_weights = {
                ("AreaGrab",): 2,
                ("PanlGrab",): 2,
                ("PanlGrab", "PanlGrab"): 1,
                ("PanlGrab", "AreaGrab"): 1,
                ("AreaGrab", "AreaGrab"): 1,
            }

            area_chip_names = weighted_random(area_weights)
            for area_chip_name in area_chip_names:
                self.add_chip(area_chip_name, "*")

            # 50% chance to add grabback
            if random.randint(0, 1) == 0:
                grabback_weights = {
                    "GrabBnsh B": 1,
                    "GrabBnsh M": 1,
                    "GrabBnsh S": 1,
                    "GrabRvng I": 1,
                    "GrabRvng Q": 1,
                    "GrabRvng Z": 1,
                    "JudgeMan *": 1,
                    "JudgeMnEX J": 1,
                    "JudgeMnSP J": 1
                }
                chip_name, chip_code = weighted_random(grabback_weights).split(" ", maxsplit=1)
                self.add_chip(chip_name, chip_code)

        # 10% chance to add uninstall
        if random.random() < 0.1:
            if "Uninstll" not in self.folder.data:
                chip_name = "Uninstll"
                chip_code = random.choice("GLR")
                self.add_chip(chip_name, chip_code)

        if self.add_lifeaur and "LifeAur" not in self.folder.data:
            self.add_chip("LifeAur", "U")

        # 15% chance to add Invisibl
        if random.random() < 0.15:
            if "Invisibl" not in self.folder.data:
                self.add_chip("Invisibl", "*")

        # 15% chance to add AntiDmg
        if random.random() < 0.15:
            if "AntiDmg" not in self.folder.data:
                self.add_chip("AntiDmg", "*")
        
        cur_main_loop_iteration = 0

        while self.folder.num_chips() + (self.num_megas - self.folder.count_num_of_category("megaChips")) + (self.num_pseudo_megas - self.folder.count_num_of_category("pseudoMegas")) < 30:
            self.chip_weights_log += f"=== Iteration {cur_main_loop_iteration} ===\n"
            #print(f"self.folder.num_chips(): {self.folder.num_chips()}")
            #print(f"remaining megas: {self.num_megas - self.folder.count_num_of_category('megaChips')}")
            #print(f"remaining pseudo-megas: {self.num_pseudo_megas - self.folder.count_num_of_category('pseudoMegas')}")

            category_name, rank = weighted_random(category_rank_weights)
        
            # allows megas in ("ranged", "highChips") and low in ("ranged", "mediumChips")

            allow_synergy_picks = random.random() <= synergy_picks_weight
            category_names = (category_name,)
            ranks = (rank,)
        
            if allow_synergy_picks:
                if category_name == "ranged":
                    if rank == "highChips":
                        category_names = ["ranged"]
                        if self.folder.count_num_of_category("megaChips") < self.num_megas:
                            category_names.append("megaChips")
                        if self.folder.count_num_of_category("pseudoMegas") < self.num_pseudo_megas:
                            category_names.append("pseudoMegas")

                    elif rank == "mediumChips":
                        ranks = ("mediumChips", "lowChips")

            if len(self.chosen_pas) == 1 and (category_name, rank) == ("ranged", "highChips"):
                ranks = ("highChips", "mediumChips")

            folder_families = self.folder.get_families()

            category_chips = self.query_db(
                category_names=category_names,
                ranks=ranks,
                #groupby="family"
                exclude_families=folder_families
            )

            chip_weights_dict, chip_weights, effect_counter = self.tally_folder_synergies(category_chips)
            if self.splay_codes:
                try:
                    name_and_code = weighted_random(chip_weights_dict)
                except IndexError as e:
                    raise RuntimeError(f"chip_weights_dict: {chip_weights_dict}, category_chips: {category_chips}, category_names: {category_names}, ranks: {ranks}") from e
                chip_name, chip_code = name_and_code.split(" ", maxsplit=1)
            else:
                code_counter = {effect: count for effect, count in effect_counter.items() if len(effect) == 1 and not effect.isdigit()}

                while True:
                    chip_name = weighted_random(chip_weights_dict)
                    chip_data = self.all_chips_by_name[chip_name]
                    code_weights = {}
                    found_codes = {}

                    chip_code = None

                    if "*" in chip_data["codes"]:
                        if code_counter.get("*") is None:
                            chip_code = "*"
                        else:
                            codes = ["*"]
                    else:
                        codes = chip_data["codes"]

                    if chip_code is None:
                        for code in codes:
                            code_count = code_counter.get(code)
                            if code_count is not None:
                                found_codes[code] = code_count
    
                        if len(found_codes) != 0:
                            successful_codes = []
                            for found_code, found_code_count in found_codes.items():
                                if found_code_count > 6:
                                    found_code_count = 6
                                if random.random() < (found_code_count_weights[found_code_count] + (0.1 if found_code == "*" else 0)):
                                    successful_codes.append(found_code)
                            if len(successful_codes) == 0:
                                continue
    
                            chip_code = self.random_code(successful_codes)
                        else:
                            total_code_count = 0
                            for code, count in code_counter.items():
                                total_code_count += count
                            avg_code_count = total_code_count/len(code_counter)
    
                            if random.random() < 0.75 - 0.15*avg_code_count:
                                continue
                            chip_code = self.random_code(chip_data["codes"])
                    break

            self.chip_weights_log += f"--- Chose {chip_name} {chip_code} "
            if self.splay_codes:
                chip_name_for_weights = name_and_code
            else:
                chip_name_for_weights = chip_name

            if chip_weights[chip_name_for_weights].is_no_reason():
                self.chip_weights_log += f"(No reason, weight: {self.chip_usage_stats.chip_usages[chip_name_for_weights].z_score_multiplier:.4f})"

            self.chip_weights_log += "---\n"

            quantity = weighted_random(category_rank_quantity_weights[(category_name, rank)])
            for cur_iteration in range(quantity):
                self.add_chip(chip_name, chip_code)
                if self.folder.max_chip_count_reached(chip_name):
                    break

            cur_main_loop_iteration += 1
            #category_chips_weights = {}
            #category_chips_filtered = {
            #for category_chip in category_chips:
            #    if 
            #category_chips

        remaining_mega_count = self.num_megas - self.folder.count_num_of_category("megaChips")
        remaining_pseudo_mega_count = self.num_pseudo_megas - self.folder.count_num_of_category("pseudoMegas")
        remaining_giga_count = self.num_gigas - self.folder.count_num_of_category("gigaChips")

        folder_families = self.folder.get_families()
        mega_chips = self.query_db(
            category_names=("megaChips",),
            ranks=("highChips",),
            exclude_families=folder_families
        )

        #print(f"self.folder: {self.folder}")
        if remaining_mega_count > 0:
            chosen_mega_chips = random.sample(mega_chips, k=remaining_mega_count)
            for chosen_mega_chip in chosen_mega_chips:
                self.add_chip(chosen_mega_chip["name"], self.random_code(chosen_mega_chip["codes"]))

        if remaining_pseudo_mega_count == 1:
            pseudo_mega_chips = self.query_db(
                category_names=("pseudoMega",),
                ranks=("highChips",),
                exclude_families=folder_families
            )
            chosen_pseudo_mega = random.choice(pseudo_mega_chips)
            self.add_chip(chosen_pseudo_mega["name"], self.random_code(chosen_pseudo_mega["codes"]))

        #print(f"folder: {self.folder}")

    def initial_chip_pick_common(self, category_name, num_picks, rank_weights, quantity_weights_by_rank):
        rank = weighted_random(rank_weights)
        quantity_weights = quantity_weights_by_rank[rank]

        while True:
            try:
                for cur_pick_index in range(num_picks):
                    folder_families = self.folder.get_families()

                    category_chips = self.query_db(
                        category_names=(category_name,),
                        ranks=(rank,),
                        groupby="family",
                        exclude_families=folder_families
                    )

                    #n_category_chip_families = random.sample(category_chips, k=num_picks)

                    #print(f"n_category_chip_family: {n_category_chip_family}")
                    if len(self.chip_usage_stats.all_nonfound_chips) == 0:
                        try_force_new_chips = False
                    else:
                        try_force_new_chips = True

                    while True:
                        n_category_chip_weights = {}
                        for n_category_chip_family in category_chips:
                            for cur_n_category_chip in n_category_chip_family["chips"]:
                                cur_n_category_chip_name = cur_n_category_chip["name"]
                                cur_n_category_chip_codes = GenFolder.simplify_codes(cur_n_category_chip["codes"])
                                for cur_n_category_chip_code in cur_n_category_chip_codes:
                                    cur_n_category_chip_name_and_code = f"{cur_n_category_chip_name} {cur_n_category_chip_code}"
                                    #print(f"cur_n_category_chip_name_and_code: {cur_n_category_chip_name_and_code}")
                                    if try_force_new_chips:
                                        if self.chip_usage_stats.chip_usages[cur_n_category_chip_name_and_code].count == 0:
                                            n_category_chip_weights[cur_n_category_chip_name_and_code] = 1
                                    else:
                                        n_category_chip_weights[cur_n_category_chip_name_and_code] = self.chip_usage_stats.chip_usages[cur_n_category_chip_name_and_code].z_score_multiplier ** 4

                        if len(n_category_chip_weights) == 0:
                            if try_force_new_chips:
                                print(f"Ran out of new chips! category_name: {category_name}, rank: {rank}, n_category_chip_family['chips']: {n_category_chip_family['chips']}")
                                try_force_new_chips = False
                                continue
                            else:
                                raise RuntimeError()
                        else:
                            break

                    n_category_chip_name_and_code = weighted_random(n_category_chip_weights)
                    n_category_chip_name, n_category_chip_code = n_category_chip_name_and_code.split(" ", maxsplit=1)

                    if self.has_chip(n_category_chip_name):
                        raise RuntimeError()

                    quantity = weighted_random(quantity_weights)
                    for i in range(quantity):
                        self.add_chip(n_category_chip_name, n_category_chip_code)
    
                    self.chip_usage_stats.all_nonfound_chips.discard(n_category_chip_name_and_code)

            except (OuterBreakError, IllegalFolderError) as e:
                continue

            break

    def counter_key_func(a, b):
        if a[1] > b[1]:
            return 1
        elif a[1] < b[1]:
            return -1
        else:
            if a[0] > b[0]:
                return 1
            elif a[0] < b[0]:
                return -1
            else:
                return 0

    # for_chips = chips not in the folder

    def tally_folder_synergies(self, category_chips):
        effect_counter = collections.Counter()

        used_chips = set(x[0] for x in self.folder.data_pas_as_chip_iterator())

        for_chips = {chip["name"]: FolderChip(chip["name"], chip["codes"]) for chip in category_chips}

        for name, folder_chip in self.folder.data_pas_as_chip_iterator():
            chip_data = self.all_chips_by_name[name]
            for effect in (name,):#itertools.chain(chip_data["almostAllEffects"], (name,)):
                effect_counter[effect] += folder_chip.quantity
                if "effect" in {"paralysis", "bubbled", "frozen", "timpani"}:
                    effect_counter["immobilization"] += folder_chip.quantity
                if "effect" == "selfcracked":
                    effect_counter["selfbroken"] += folder_chip.quantity / 2
                elif "effect" == "oppcracked":
                    effect_counter["oppbroken"] += folder_chip.quantity / 2

            for code in folder_chip.codes:
                #if self.all_chips_by_name[name]["category"] != "gigaChips":
                effect_counter[code] += 1

        output = (''.join(f"{k}: {v}\n" for k, v in sorted(effect_counter.items(), key=functools.cmp_to_key(GenFolder.counter_key_func))))

        #print(f"== before ==\n{output}\n")
        #with open("tally_folder_synergies_before_out.txt", "w+") as f:
        #    f.write(output)

        #synergy_weights = {
        #    "reliability": 
        #    "bonus":
        #    "counter":
        #    "countereffect

        #chip_weights = collections.Counter()

        chip_weights = ChipWeights()
        current_non_soup_pa_codes = self.folder.get_non_soup_pa_codes_except_asterisk_and_gigas()
        asterisk_code_count = self.folder.get_code_count("*")
        #print(effect_counter)
        #if 'AreaGrab' in for_chips:
        #    print(f"for_chips: {for_chips}")
        #print(f"areagrab in for_chips: {}")
        for name, folder_chip in for_chips.items():
            candidate_chip_data = self.all_non_pa_chips_by_name[name]
            codes = GenFolder.simplify_codes(folder_chip.codes)

            if self.splay_codes:
                cur_chip_names = [f"{name} {code}" for code in codes]
            else:
                cur_chip_names = [name]

            candidate_chip_data_interesting = candidate_chip_data["interesting"]
            candidate_chip_data_interesting_operator, candidate_chip_data_interesting_value_str = candidate_chip_data_interesting.split(maxsplit=1)
            candidate_chip_data_interesting_value = int(candidate_chip_data_interesting_value_str)

            for name_and_code in cur_chip_names:
                if self.splay_codes:
                    cur_chip_name, code = name_and_code.split(" ", maxsplit=1)
                else:
                    cur_chip_name, code = name_and_code, name_and_code

                synergy_weights = {
                    "reliability": 4*10,
                    "bonus": 4*10,
                    "necessity": 4*10
                }

                for synergy_class, synergy_weight in synergy_weights.items():
                    for suffix in ("from", "for"):
                        synergy_class_full = f"{synergy_class}{suffix}"
                        #print(candidate_chip_data[synergy_class_full])
                        for chip_name_fulfilling_synergy_of_chip_candidate in candidate_chip_data[synergy_class_full]:
                            if "|" in chip_name_fulfilling_synergy_of_chip_candidate:
                                continue

                            if effect_counter[chip_name_fulfilling_synergy_of_chip_candidate] == 0:
                                #if name == "AreaGrab":
                                #    print(f"effect_counter: {effect_counter}")
                                continue

                            chip_name_of_chip_in_folder_fulfilling_synergy_of_chip_candidate = chip_name_fulfilling_synergy_of_chip_candidate
                            chip_data_of_chip_in_folder_fulfilling_synergy_of_chip_candidate = self.all_chips_by_name[chip_name_of_chip_in_folder_fulfilling_synergy_of_chip_candidate]

                            chip_codes_of_chip_in_folder_fulfilling_synergy_of_chip_candidate = self.folder.find_codes_of_chip(chip_name_of_chip_in_folder_fulfilling_synergy_of_chip_candidate)

                            chip_in_folder_fulfilling_synergy_of_chip_candidate_matches_candidate_chip_code = (code == "*") or (code in  chip_codes_of_chip_in_folder_fulfilling_synergy_of_chip_candidate)

                            if suffix == "from":
                                synergy_chip_effects = self.all_chips_by_name[chip_name_of_chip_in_folder_fulfilling_synergy_of_chip_candidate]["almostAllEffects"] | frozenset((chip_name_of_chip_in_folder_fulfilling_synergy_of_chip_candidate,))
                                cur_chip_synergy_wanted_effects = candidate_chip_data[synergy_class] | frozenset((cur_chip_name,))
                            else:
                                synergy_chip_effects = candidate_chip_data["almostAllEffects"] | frozenset((cur_chip_name,))
                                cur_chip_synergy_wanted_effects = self.all_chips_by_name[chip_name_of_chip_in_folder_fulfilling_synergy_of_chip_candidate][synergy_class] | frozenset((chip_name_of_chip_in_folder_fulfilling_synergy_of_chip_candidate,))

                            matching_effects = self.debug_find_matching_effects(synergy_chip_effects, cur_chip_synergy_wanted_effects, synergy_weight, chip_name_of_chip_in_folder_fulfilling_synergy_of_chip_candidate, name_and_code)
                            matching_effect_passes_code_check = False

                            try:
                                for matching_effect in matching_effects:
                                    if matching_effect in {"invispierce", "immobilization", "bubbled"}:
                                        if chip_in_folder_fulfilling_synergy_of_chip_candidate_matches_candidate_chip_code:
                                            matching_effect_passes_code_check = True
                                    elif (chip_data_of_chip_in_folder_fulfilling_synergy_of_chip_candidate["family"] in {"AirSpin1", "AirSpin", "AirRaid"} or candidate_chip_data["family"] in {"AirSpin1", "AirSpin", "AirRaid"}) and matching_effect in {"object", "objectremove"}:
                                        if chip_in_folder_fulfilling_synergy_of_chip_candidate_matches_candidate_chip_code:
                                            matching_effect_passes_code_check = True
                            except KeyError as e:
                                raise RuntimeError(f"candidate_chip_data: {candidate_chip_data}") from e

                            if not matching_effect_passes_code_check:
                                continue

                            candidate_chip_data_rank = candidate_chip_data["rank"]
                            candidate_chip_rank_abbrev = candidate_chip_data_rank.replace("Chips", "")

                            synergy_weight_modified = synergy_weight

                            if candidate_chip_data_rank == "mediumChips":
                                synergy_weight_modified /= 2

                            reason = f"{chip_name_of_chip_in_folder_fulfilling_synergy_of_chip_candidate} ({synergy_class}{suffix} (+{synergy_weight}; {candidate_chip_rank_abbrev}): {', '.join(sorted(matching_effects))}" 
                            synergy_chip_weight = ChipWeight(synergy_weight, reason)

                            try:
                                if self.all_chips_by_name[chip_name_of_chip_in_folder_fulfilling_synergy_of_chip_candidate]["category"] == "constrained" and synergy_class_full == "reliabilityfor":
                                    synergy_chip_weight.mul_subreason(10, "; 10x: constrained and reliabilityfor")
                                #elif cur_chip_name in {"AreaGrab", "PanlGrab"}:
                                #    synergy_chip_weight.mul_subreason(10, "; 10x: area chip")
                            except Exception as e:
                                raise RuntimeError(f"self.all_chips_by_name[chip_name_of_chip_in_folder_fulfilling_synergy_of_chip_candidate]: {self.all_chips_by_name[chip_name_of_chip_in_folder_fulfilling_synergy_of_chip_candidate]}") from e

                            synergy_chip_weight.mul_subreason(effect_counter[chip_name_of_chip_in_folder_fulfilling_synergy_of_chip_candidate], "")
                            chip_weights[name_and_code].add(synergy_chip_weight)

                counter_avg_counter = ChipWeights()
                for synergy_class in ("counter", "effectcounter"):
                    for suffix in ("from", "for"):
                        synergy_class_full = f"{synergy_class}{suffix}"
                        for chip_name_fulfilling_synergy_of_chip_candidate in candidate_chip_data[synergy_class_full]:
                            if effect_counter[chip_name_fulfilling_synergy_of_chip_candidate] != 0:
                                chip_name_of_chip_in_folder_fulfilling_synergy_of_chip_candidate = chip_name_fulfilling_synergy_of_chip_candidate
                                count = counter_avg_counter.get(chip_name_of_chip_in_folder_fulfilling_synergy_of_chip_candidate)

                                reason = f"{chip_name_of_chip_in_folder_fulfilling_synergy_of_chip_candidate} ({synergy_class}{suffix}) ("

                                if count is None:
                                    synergy_weight_value = effect_counter[chip_name_of_chip_in_folder_fulfilling_synergy_of_chip_candidate] * 2
                                    reason += f"+{synergy_weight_value}): "
                                else:
                                    synergy_weight_value = (count.weight + effect_counter[chip_name_of_chip_in_folder_fulfilling_synergy_of_chip_candidate] * 2)/2
                                    reason += f"={synergy_weight_value}): "

                                if suffix == "from":
                                    synergy_chip_effects = self.all_chips_by_name[chip_name_of_chip_in_folder_fulfilling_synergy_of_chip_candidate]["almostAllEffects"] | frozenset((chip_name_of_chip_in_folder_fulfilling_synergy_of_chip_candidate,))
                                    cur_chip_synergy_wanted_effects = candidate_chip_data[synergy_class] | frozenset((cur_chip_name,))
                                else:
                                    synergy_chip_effects = candidate_chip_data["almostAllEffects"] | frozenset((cur_chip_name,))
                                    cur_chip_synergy_wanted_effects = self.all_chips_by_name[chip_name_of_chip_in_folder_fulfilling_synergy_of_chip_candidate][synergy_class] | frozenset((chip_name_of_chip_in_folder_fulfilling_synergy_of_chip_candidate,))

                                matching_effects = self.debug_find_matching_effects(synergy_chip_effects, cur_chip_synergy_wanted_effects, chip_weights[name_and_code], chip_name_of_chip_in_folder_fulfilling_synergy_of_chip_candidate, name_and_code)
                                reason += ", ".join(sorted(matching_effects))

                                if count is None:
                                    reason += ")"
                                    counter_avg_counter[chip_name_of_chip_in_folder_fulfilling_synergy_of_chip_candidate].add_weight(synergy_weight_value, reason)
                                else:
                                    reason += "; effectcounter dampened)"
                                    count.weight = synergy_weight_value
                                    count.reasons.append(reason)

                for chip_name_of_chip_in_folder_fulfilling_synergy_of_chip_candidate, chip_weight in counter_avg_counter.items():
                    chip_weights[name_and_code].add(chip_weight)

                candidate_chip_data_interesting_reason = ""
                if candidate_chip_data_interesting != "+ 0":
                    if candidate_chip_data_interesting_operator == "*":
                        chip_weights[name_and_code].mul_weight(candidate_chip_data_interesting_value, f"{candidate_chip_data_interesting_value}x: interesting")
                    elif candidate_chip_data_interesting_operator == "+":
                        chip_weights[name_and_code].add_weight(candidate_chip_data_interesting_value, f"+{candidate_chip_data_interesting_value}: interesting")

                z_score_multiplier = self.chip_usage_stats.chip_usages[name_and_code].z_score_multiplier
                #if z_score_multiplier < 0:
                #    print(f"{name_and_code} z_score_multiplier: {z_score_multiplier}")
                if not name_and_code in chip_weights:
                    chip_weights[name_and_code] = ChipWeight(z_score_multiplier, "None")
                else:
                    chip_weights[name_and_code].mul_weight(z_score_multiplier, f"{z_score_multiplier:.4f}x: keeping usage even")

                if self.splay_codes:
                    if code != "*":
                        code_count = effect_counter.get(code)

                        if code_count is None:
                            if len(self.chosen_pas) == 1:
                                max_unique_codes = 6
                            else:
                                max_unique_codes = 5

                            if len(current_non_soup_pa_codes) >= max_unique_codes and not candidate_chip_data["ignoreCodeLimit"]:
                                #print(f"current_non_soup_pa_codes: {current_non_soup_pa_codes}")
                                chip_weights[name_and_code] = ChipWeight(0, "max codes reached")
                    else:
                        if asterisk_code_count >= 6 and not candidate_chip_data["ignoreCodeLimit"] and random.random() >= 1/(asterisk_code_count - 5):
                            chip_weights[name_and_code] = ChipWeight(0, "max * code reached")

                    #else:
                    #    chip_weights[name_and_code] *= 
                    #   current_non_soup_pa_codes

            #for chip_name_fulfilling_synergy_of_chip_candidate, count in chip_weights.items():
            #    effect_counter[unique_effect] -= 1#folder_chip.quantity

        #del effect_counter["none"]

        #if random.randint(0, 1) >= 0:
        #for name, folder_chip in for_chips.items():
        #    if "*" in folder_chip.codes:
        #        codes = ("*",)
        #        #if name in {"PanlGrab", "AreaGrab", "RockCube"}:
        #        #    codes *= 4
        #    else:
        #        codes = folder_chip.codes
        #
        #    if self.splay_codes:
        #        cur_chip_names = [f"{name} {code}" for code in codes]
        #    else:
        #        cur_chip_names = [name]
        #
        #    for name_and_code in cur_chip_names:
        #        
        #        if name_and_code not in chip_weights:
                
        #for name_and_code, chip_weight in chip_weights.items():
        #    chip_weight.weight += 1

        options = jsbeautifier.default_options()
        options.indent_size = 2

        self.chip_weights_log += jsbeautifier.beautify(json.dumps(chip_weights.to_debug_dict()), options) + "\n"
        chip_weights_dict = chip_weights.to_dict()
        output = (''.join(f"{k}: {v}\n" for k, v in sorted(chip_weights_dict.items(), key=functools.cmp_to_key(GenFolder.counter_key_func))))

        #print(f"== after ==\n{output}\n")

        #with open("tally_folder_synergies_out.txt", "w+") as f:
        #    f.write(output)

        return chip_weights_dict, chip_weights, effect_counter

    def debug_find_matching_effects(self, synergy_chip_effects, cur_chip_synergy_wanted_effects, synergy_weight_modified, chip_name_of_chip_in_folder_fulfilling_synergy_of_chip_candidate, name_and_code):
        matching_effects = synergy_chip_effects & cur_chip_synergy_wanted_effects
        if len(matching_effects) == 0:
            matching_effects = set()
            if "selfbroken" in cur_chip_synergy_wanted_effects and "selfcracked" in synergy_chip_effects:
                matching_effects.add("selfbroken")
            if "oppbroken" in cur_chip_synergy_wanted_effects and "oppcracked" in synergy_chip_effects:
                matching_effects.add("oppbroken")
            if "selfcracked" in cur_chip_synergy_wanted_effects and "selfbroken" in synergy_chip_effects:
                matching_effects.add("selfbroken")
            if "oppcracked" in cur_chip_synergy_wanted_effects and "oppbroken" in synergy_chip_effects:
                matching_effects.add("oppbroken")
            if "immobilization" in cur_chip_synergy_wanted_effects and ({"paralysis", "bubbled", "frozen", "timpani"} | synergy_chip_effects):
                matching_effects.add("immobilization")
            elif "immobilization" in synergy_chip_effects and ({"paralysis", "bubbled", "frozen", "timpani"} | cur_chip_synergy_wanted_effects):
                matching_effects.add("immobilization")

        if len(matching_effects) == 0:
            raise RuntimeError(f"fromsynergy: synergy_weight_modified: {synergy_weight_modified}, chip_name_of_chip_in_folder_fulfilling_synergy_of_chip_candidate: {chip_name_of_chip_in_folder_fulfilling_synergy_of_chip_candidate}, cur chip: {name_and_code}, synergy_chip_effects: {synergy_chip_effects}, cur_chip_synergy_wanted_effects: {cur_chip_synergy_wanted_effects}")
        #elif chip_name_of_chip_in_folder_fulfilling_synergy_of_chip_candidate == "Anubis" and name_and_code == "FireBrn2 T":
        #    print(f"matching_effects: {matching_effects}")
        #print(f"matching_effects: {matching_effects}")

        return matching_effects

    def random_code(self, codes):
        if codes[-1] == "*":
            return "*"
        else:
            return random.choice(codes)

    def has_chip(self, name):
        return self.folder.has_chip(name)

    @staticmethod
    def simplify_codes(codes):
        if "*" in codes:
            return ("*",)
        else:
            return codes

    class ChipCodesUsageStats:
        __slots__ = ("folder_filenames", "stats")

        def __init__(self):
            self.folder_filenames = set()
            self.stats = collections.defaultdict(set)

    class ChipUsage:
        __slots__ = ("name_and_code", "count", "z_score", "z_score_multiplier")

        def __init__(self, name_and_code, count):
            self.name_and_code = name_and_code
            self.count = count
            self.z_score = -22222
            self.z_score_multiplier = -44444

    null_chip_usage = ChipUsage("", 0)

    class ChipUsageStats:
        __slots__ = ("chip_usages", "stddev", "mean", "all_nonfound_chips")

        def __init__(self):
            self.chip_usages = {}

        def calc_stddev_and_mean(self):
            self.stddev = statistics.pstdev(chip_usage.count for chip_usage in self.chip_usages.values())
            self.mean = statistics.mean(chip_usage.count for chip_usage in self.chip_usages.values())

        def calc_zscores(self):
            for name_and_code, chip_usage in self.chip_usages.items():
                chip_usage.z_score = (chip_usage.count - self.mean) / self.stddev
                if chip_usage.z_score >= 0:
                    chip_usage.z_score_multiplier = 1 / (chip_usage.z_score + 1)
                else:
                    chip_usage.z_score_multiplier = 1 - chip_usage.z_score

                #if chip_usage.z_score_multiplier < 0:
                #    print(f"name_and_code: {name_and_code}, chip_usage.z_score: {chip_usage.z_score}, chip_usage.z_score_multiplier: {chip_usage.z_score_multiplier}")

    @staticmethod
    def __chip_usage_stats_sort_func(a, b):
        if len(a[1]) > len(b[1]):
            return 1
        elif len(a[1]) < len(b[1]):
            return -1
        else:
            if a[0] > b[0]:
                return 1
            elif a[0] < b[0]:
                return -1
            else:
                return 0

    @staticmethod
    def __chip_codes_usage_stats_sort_func(a, b):
        len_a_folder_filenames = len(a[1].folder_filenames)
        len_b_folder_filenames = len(b[1].folder_filenames)
        if len_a_folder_filenames > len_b_folder_filenames:
            return 1
        elif len_a_folder_filenames < len_b_folder_filenames:
            return -1
        else:
            if a[0] > b[0]:
                return 1
            elif a[0] < b[0]:
                return -1
            else:
                return 0

    def __calc_chip_usage_stats(self, format_stats=True):
        pa_usage_stats = collections.defaultdict(set)
        non_pa_usage_stats = collections.defaultdict(GenFolder.ChipCodesUsageStats)
        all_found_chips = set()
        all_nonfound_chips = set()
        chip_usage_stats = GenFolder.ChipUsageStats()

        for good_folder_filename in glob.glob("good_folders/*.txt"):
            good_folder_filepath = pathlib.Path(good_folder_filename)
            good_folder_filepath_parent = good_folder_filepath.parent
            good_folder_basename = good_folder_filepath.name

            good_folder_pa_filepath = good_folder_filepath_parent / "pas" / good_folder_basename
            good_folder_non_pa_filepath = good_folder_filepath_parent / "non_pas" / good_folder_basename

            #print(f"good_folder_filename: {good_folder_filename}")
            with open(good_folder_pa_filepath, "r") as f:
                for line in f:
                    line = line.strip()
                    if line == "":
                        continue
                    pa_usage_stats[line].add(good_folder_filename)

            with open(good_folder_non_pa_filepath, "r") as f:
                for line in f:
                    line = line.strip()
                    if line == "":
                        continue
                    chip_name, chip_code = line.split(" ", maxsplit=1)
                    non_pa_usage_stats[chip_name].stats[chip_code].add(good_folder_filename)
                    non_pa_usage_stats[chip_name].folder_filenames.add(good_folder_filename)
                    all_found_chips.add(f"{chip_name} {chip_code}")

        for chip_name, chip_data in self.all_non_pa_chips_by_name.items():
            codes = GenFolder.simplify_codes(chip_data["codes"])

            for chip_code in codes:
                chip_name_and_code = f"{chip_name} {chip_code}"
                if chip_name_and_code not in all_found_chips:
                    all_nonfound_chips.add(chip_name_and_code)
                    chip_usage_stats.chip_usages[chip_name_and_code] = GenFolder.ChipUsage(chip_name_and_code, 0)
                else:
                    chip_count = len(non_pa_usage_stats[chip_name].stats[chip_code])
                    chip_usage_stats.chip_usages[chip_name_and_code] = GenFolder.ChipUsage(chip_name_and_code, chip_count)
                    #non_pa_usage_stats[chip_name].stats[chip_code]

        chip_usage_stats.all_nonfound_chips = all_nonfound_chips
        chip_usage_stats.calc_stddev_and_mean()
        chip_usage_stats.calc_zscores()

        total_pas = sum(len(folder_filenames_with_pa) for folder_filenames_with_pa in pa_usage_stats.values())
        total_non_pas = sum(len(chip_codes_usage_stats.folder_filenames) for chip_codes_usage_stats in non_pa_usage_stats.values())

        sorted_pa_usage_stats = sorted(pa_usage_stats.items(), key=functools.cmp_to_key(GenFolder.__chip_usage_stats_sort_func), reverse=True)
        sorted_non_pa_usage_stats = sorted(non_pa_usage_stats.items(), key=functools.cmp_to_key(GenFolder.__chip_codes_usage_stats_sort_func), reverse=True)

        if format_stats:
            output = ""
            output += "== PA usage stats ==\n"
            #output += "".join(f"{pa_name}: {len(folder_filenames_with_pa)/total_pas:.2f} ({len(folder_filenames_with_pa)}/{total_pas}) [{', '.join(sorted(set(folder_filenames_with_pa)))}]\n" for pa_name, folder_filenames_with_pa in sorted_pa_usage_stats)
            output += "".join(f"{pa_name}: {len(folder_filenames_with_pa)/total_pas:.2f} ({len(folder_filenames_with_pa)}/{total_pas})\n" for pa_name, folder_filenames_with_pa in sorted_pa_usage_stats)
    
            output += "\n"
            output += "== Non-PA usage stats ==\n"
            for chip_name, chip_codes_usage_stats in sorted_non_pa_usage_stats:
                chip_codes_total_codes = len(chip_codes_usage_stats.folder_filenames)
                sorted_chip_codes_usage_stats_stats_counter = sorted(chip_codes_usage_stats.stats.items(), key=functools.cmp_to_key(GenFolder.__chip_usage_stats_sort_func))
                #output += f"{chip_name}: {chip_codes_total_codes/total_non_pas:.2f} ({chip_codes_total_codes}/{total_non_pas}) [{', '.join(sorted(set(chip_codes_usage_stats.folder_filenames)))}]\n"
                output += f"{chip_name}: {chip_codes_total_codes/total_non_pas:.2f} ({chip_codes_total_codes}/{total_non_pas})\n"
                
                #output += "".join(f"- {chip_code}: {len(chip_code_folder_filenames)/chip_codes_total_codes:.2f} ({len(chip_code_folder_filenames)}/{chip_codes_total_codes}) (mul: {chip_usage_stats.chip_usages.get(chip_name + ' ' + chip_code, GenFolder.null_chip_usage).z_score_multiplier:.4f}) [{', '.join(sorted(set(chip_code_folder_filenames)))}]\n" for chip_code, chip_code_folder_filenames in sorted_chip_codes_usage_stats_stats_counter)
                output += "".join(f"- {chip_code}: {len(chip_code_folder_filenames)/chip_codes_total_codes:.2f} ({len(chip_code_folder_filenames)}/{chip_codes_total_codes}) (mul: {chip_usage_stats.chip_usages.get(chip_name + ' ' + chip_code, GenFolder.null_chip_usage).z_score_multiplier:.4f})\n" for chip_code, chip_code_folder_filenames in sorted_chip_codes_usage_stats_stats_counter)
    
            output += "\n"
            output += "== Non-found non-PA chips ==\n"
            output += "\n".join(sorted(all_nonfound_chips)) + "\n"
    
            with open("chip_usage_stats_out.dump", "w+") as f:
                f.write(output)

        return chip_usage_stats
        #print(f"\n{output}")

    #def add_chips
        #dump_noref_yaml(pa_chips, "pa_chips_high.yml")
        #print(random.choice(pa_chips)["parts"])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--output-filename", dest="output_filename", default="gen_folder_out.txt", help="Output filename of folder.")
    ap.add_argument("-s", "--seed", dest="seed", default=None, type=int, help="Seed to use for folder generation.")
    ap.add_argument("-p", "--print-stats", dest="print_stats", action="store_true", help="Whether to print chip usage stats.")
    ap.add_argument("-i", "--input-chips_filename", dest="input_chips_filename", default=None, help="Manual input chips to use for folder generation. Format is list of PAs on a new line separated by --- (and new line) separated by list of chips.")

    args = ap.parse_args()

    GenFolder("sorted_chips.yml", "bn6_chips.json", args.output_filename, args.seed, args.input_chips_filename, args.print_stats)

if __name__ == "__main__":
    main()
