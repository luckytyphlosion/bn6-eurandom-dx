from chip_db import ChipDB, dump_noref_yaml, mb_to_max_chip_count
import random as randomlib
import json
import itertools
import collections
import functools
import sys
import jsbeautifier

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

    def get_families(self):
        families = set()

        for name, folder_chip in self.data.items():
            families.add(self.all_chips_by_name[name]["family"])

        return families

    def get_non_soup_pa_codes_except_asterisk(self):
        codes = set()

        for folder_chip in self.pa_chips.values():
            codes.update(code for code in folder_chip.codes if not code.isdigit() and code != "*")

        for folder_chip in self.non_pa_chips.values():
            codes.update(code for code in folder_chip.codes if code != "*")

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
HIGH_MEDIUM_PA = 1
MEDIUM_MEDIUM_PA = 2
HIGH_LOW_PA = 3
HIGH_HIGH_PA = 4

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
        return self.weight == 1 and self.reasons[0] == "None"

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
    __slots__ = ("chip_db", "chip_game_info", "chosen_pas", "folder", "all_non_pa_chips_by_name", "num_megas", "num_pseudo_megas", "num_gigas", "all_chips_by_name", "splay_codes", "chip_weights_log")

    def __init__(self, sorted_chips_filename, chip_game_info_filename, seed):
        global random
        if seed is None:
            seed = randomlib.randint(0, 100000000)
        print(f"seed: {seed}")
        random = randomlib.Random(seed)
        self.chip_weights_log = ""

        #random.seed(4444)
        with open(chip_game_info_filename, "r") as f:
            self.chip_game_info = json.load(f)

        self.chip_db = ChipDB(sorted_chips_filename, self.chip_game_info)
        self.__gen_all_chips_by_name()

        self.folder = Folder(self.chip_game_info, self.all_chips_by_name)

        self.chosen_pas = []
        self.splay_codes = True

        self.__gen_pas()
        self.__todo_algo1()
        output = self.folder.output_ungrouped_folder()
        with open("gen_folder_out.txt", "w+") as f:
            f.write(output)

        with open("chip_weights_log.dump", "w+") as f:
            f.write(self.chip_weights_log)

        print(output)

    def __gen_all_chips_by_name(self):
        self.all_non_pa_chips_by_name = self.querydict_db(
            category_names=("ranged", "constrained", "pseudoMega", "nonAttacking", "megaChips", "gigaChips")
        )
        
        self.all_chips_by_name = self.querydict_db()
        dump_noref_yaml(self.all_chips_by_name, "all_chips_by_name.yml")

    def __gen_pas(self):
        pa_type = weighted_random({
            HIGH_PA: 0.5,
            HIGH_HIGH_PA: 0.2,
            HIGH_MEDIUM_PA: 0.1,
            MEDIUM_MEDIUM_PA: 0.1,
            HIGH_LOW_PA: 0.1
        })

        print(f"pa_type: {pa_type}")
        if pa_type in {HIGH_PA, HIGH_HIGH_PA, HIGH_MEDIUM_PA, HIGH_LOW_PA}:
            wanted_rank = "highChips"
        else:
            wanted_rank = "mediumChips"

        pa_chips_1 = self.query_db(
            category_names=("programAdvances",),
            ranks=(wanted_rank,)
        )

        chosen_pa_1 = random.choice(pa_chips_1)
        self.add_pa(chosen_pa_1)
        #

        if pa_type == HIGH_HIGH_PA:
            wanted_rank = "highChips"
        elif pa_type in {HIGH_MEDIUM_PA, MEDIUM_MEDIUM_PA}:
            wanted_rank = "mediumChips"
        elif pa_type == HIGH_LOW_PA:
            wanted_rank = "lowChips"
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
                    break

            self.add_pa(chosen_pa_2)

        #print(self.folder)

    def query_db(self, **kwargs):
        return self.chip_db.query(**kwargs)

    def querydict_db(self, **kwargs):
        return self.chip_db.querydict(**kwargs)

    def add_pa(self, chosen_pa):
        self.chosen_pas.append(chosen_pa)
        pa_name, pa_code = self.folder.add_pa(chosen_pa)
        self.try_add_necessity(pa_name, pa_code)

    def add_chip(self, name, code):
        self.folder.add_chip(name, code)
        self.try_add_necessity(name, code)
            
    def try_add_necessity(self, name, code):
        necessities = self.all_chips_by_name[name]["necessity"]
        if len(necessities) != 0:
            #print(f"necessity chip name: {name}")
            # first check all current chips if they have an effect that matches the newly chip's necessity
            necessities_as_set = set(necessities)
            for cur_chip_name, folder_chip in self.folder.data_pas_as_chip_iterator():
                if cur_chip_name == name:
                    continue
                chip_data = self.all_chips_by_name[cur_chip_name]
                for effect in itertools.chain(chip_data["almostAllEffects"], (cur_chip_name,)):
                    if effect in necessities_as_set:
                        if name == "BlkBomb" and "*" not in chip_data["codes"] and code not in chip_data["codes"]:
                            continue

                        return

            # if not, then choose a random necessity and fulfill it
            necessity = random.choice(sorted(necessities))
            folder_families = self.folder.get_families()
            category_chips = self.query_db(
                category_names=("ranged", "constrained", "pseudoMega", "nonAttacking", "megaChips", "gigaChips"),
                exclude_families=folder_families,
                effects=(necessity,),
                code=code
            )

            #print(f"category_chips: {category_chips}")
            necessity_chip = random.choice(category_chips)
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

            category_rank_weights = {
                ("ranged", "highChips"): 32,
                ("ranged", "mediumChips"): 8,
                ("constrained", "highChips"): 3,
                ("constrained", "mediumChips"): 3,
                ("nonAttacking", "highChips"): 3,
                ("nonAttacking", "mediumChips"): 3,
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

            category_rank_weights = {
                ("ranged", "highChips"): 11,
                ("ranged", "mediumChips"): 11,
                ("constrained", "highChips"): 11,
                ("constrained", "mediumChips"): 11,
                ("nonAttacking", "highChips"): 3,
                ("nonAttacking", "mediumChips"): 3,
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

        #self.add_chip("ElemTrap", "*")
        #self.tally_folder_synergies()
        #self.tally_folder_synergies2()
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
            print("area")
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
        
            folder_families = self.folder.get_families()

            category_chips = self.query_db(
                category_names=category_names,
                ranks=ranks,
                #groupby="family"
                exclude_families=folder_families
            )

            chip_weights_dict, chip_weights, effect_counter = self.tally_folder_synergies(category_chips)
            if self.splay_codes:
                name_and_code = weighted_random(chip_weights_dict)
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
                self.chip_weights_log += "(No reason)"

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

        category_chips = self.query_db(
            category_names=(category_name,),
            ranks=(rank,),
            groupby="family"
        )

        while True:
            try:
                n_category_chip_families = random.sample(category_chips, k=num_picks)
                for n_category_chip_family in n_category_chip_families:
                    #print(f"n_category_chip_family: {n_category_chip_family}")
                    n_category_chip = random.choice(n_category_chip_family["chips"])
                    n_category_chip_name = n_category_chip["name"]
                    n_category_chip_code = self.random_code(n_category_chip["codes"])

                    if self.has_chip(n_category_chip_name):
                        raise OuterBreakError()

                    quantity = weighted_random(quantity_weights)
                    for i in range(quantity):
                        self.add_chip(n_category_chip_name, n_category_chip_code)
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
                if "effect" == "cracked":
                    effect_counter["broken"] += folder_chip.quantity / 2

            for code in folder_chip.codes:
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
        current_non_soup_pa_codes = self.folder.get_non_soup_pa_codes_except_asterisk()
        asterisk_code_count = self.folder.get_code_count("*")
        #print(effect_counter)
        for name, folder_chip in for_chips.items():
            candidate_chip_data = self.all_non_pa_chips_by_name[name]
            if "*" in folder_chip.codes:
                codes = ("*",)
                #if name in {"PanlGrab", "AreaGrab", "RockCube"}:
                #    codes *= 4
            else:
                codes = folder_chip.codes

            if self.splay_codes:
                cur_chip_names = [f"{name} {code}" for code in codes]
            else:
                cur_chip_names = [name]

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
                                continue

                            chip_name_of_chip_in_folder_fulfilling_synergy_of_chip_candidate = chip_name_fulfilling_synergy_of_chip_candidate

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

                            for matching_effect in matching_effects:
                                if matching_effect in {"invispierce", "immobilization", "bubbled"}:
                                    if chip_in_folder_fulfilling_synergy_of_chip_candidate_matches_candidate_chip_code:
                                        matching_effect_passes_code_check = True
                                else:
                                    matching_effect_passes_code_check = True

                            if not matching_effect_passes_code_check:
                                continue

                            reason = f"{chip_name_of_chip_in_folder_fulfilling_synergy_of_chip_candidate} ({synergy_class}{suffix} (+{synergy_weight}): {', '.join(sorted(matching_effects))}" 
                            synergy_chip_weight = ChipWeight(synergy_weight, reason)

                            try:
                                if self.all_chips_by_name[chip_name_of_chip_in_folder_fulfilling_synergy_of_chip_candidate]["category"] == "constrained" and synergy_class_full == "reliabilityfor":
                                    synergy_chip_weight.mul_subreason(10, "; 10x: constrained and reliabilityfor")
                                elif name_and_code in {"AreaGrab", "PanlGrab"}:
                                    synergy_chip_weight.mul_subreason(10, "; 10x: area chip")
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

                if not name_and_code in chip_weights:
                    chip_weights[name_and_code] = ChipWeight(1, "None")

                if self.splay_codes:
                    if code != "*":
                        code_count = effect_counter.get(code)

                        if code_count is None:
                            if len(current_non_soup_pa_codes) >= 5:
                                #print(f"current_non_soup_pa_codes: {current_non_soup_pa_codes}")
                                chip_weights[name_and_code] = ChipWeight(0, "max codes reached")
                    else:
                        if asterisk_code_count >= 6 and random.random() >= 1/(asterisk_code_count - 5):
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
            if "broken" in cur_chip_synergy_wanted_effects and "cracked" in synergy_chip_effects:
                matching_effects.add("broken")
            elif "cracked" in cur_chip_synergy_wanted_effects and "broken" in synergy_chip_effects:
                matching_effects.add("broken")
            if "immobilization" in cur_chip_synergy_wanted_effects and ({"paralysis", "bubbled", "frozen", "timpani"} | synergy_chip_effects):
                matching_effects.add("immobilization")
            elif "immobilization" in synergy_chip_effects and ({"paralysis", "bubbled", "frozen", "timpani"} | cur_chip_synergy_wanted_effects):
                matching_effects.add("immobilization")

        if len(matching_effects) == 0:
            raise RuntimeError(f"fromsynergy: synergy_weight_modified: {synergy_weight_modified}, chip_name_of_chip_in_folder_fulfilling_synergy_of_chip_candidate: {chip_name_of_chip_in_folder_fulfilling_synergy_of_chip_candidate}, cur chip: {name_and_code}, synergy_chip_effects: {synergy_chip_effects}, cur_chip_synergy_wanted_effects: {cur_chip_synergy_wanted_effects}")

        #print(f"matching_effects: {matching_effects}")

        return matching_effects

    def random_code(self, codes):
        if codes[-1] == "*":
            return "*"
        else:
            return random.choice(codes)

    def has_chip(self, name):
        return self.folder.has_chip(name)
        
    #def add_chips
        #dump_noref_yaml(pa_chips, "pa_chips_high.yml")
        #print(random.choice(pa_chips)["parts"])

def main():
    if len(sys.argv) == 2:
        seed = int(sys.argv[1])
    else:
        seed = None

    GenFolder("sorted_chips.yml", "bn6_chips.json", seed)

    

if __name__ == "__main__":
    main()
