import yaml
import json
import re
import collections
import itertools
import copy

class NoAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True

class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set) or isinstance(obj, frozenset):
            return sorted(obj)
        return json.JSONEncoder.default(self, obj)

def dump_noref_yaml(data, output_filename):
    data_norefs = json.loads(json.dumps(data, cls=SetEncoder))

    with open(output_filename, "w+") as f:
        yaml.safe_dump(data_norefs, f)

def mb_to_max_chip_count(mb):
    if 0 <= mb <= 19:
        return 5
    elif 20 <= mb <= 29:
        return 4
    elif 30 <= mb <= 39:
        return 3
    elif 40 <= mb <= 49:
        return 2
    else:
        return 1

class ChipDB:
    __slots__ = ("sorted_chips", "chip_game_info", "temp_all_family_fields", "query_cache", "query_unflat_cache")

    synergy_classes = ("necessity", "reliability", "bonus", "counter", "effectcounter")

    def __init__(self, sorted_chips_filename, chip_game_info):
        with open(sorted_chips_filename, "r") as f:
            contents = f.read()
            contents = re.sub(r"\belementalpanel\b", "ice, grass", contents)
            self.sorted_chips = yaml.safe_load(contents)

        self.chip_game_info = chip_game_info
        self.query_cache = {}
        self.query_unflat_cache = {}

        #self.temp_all_family_fields = set()

        self.__convert_sorted_chips_to_chip_db()

        dump_noref_yaml(self.sorted_chips, "sorted_chips_out.yml")
            #yaml.safe_dump(self.sorted_chips, f)

        #print(sorted(self.temp_all_family_fields))

    # chip_category_name in (
    #     "ranged", "constrained", "pseudoMega",
    #     "nonAttacking", "megaChips", "gigaChips",
    #     "programAdvances"
    # ):

    # convert chips field to something better
    # add default fields
    # add implicit synergies
    # make synergies two-way

    def __convert_sorted_chips_to_chip_db(self):
        all_synergies = set()

        for category_name, category_chips in self.sorted_chips.items():
            for chip_family_full in category_chips:
                chip_family = next(iter(chip_family_full.values()))

                try:
                    self.__add_default_fields(chip_family)

                    if category_name != "programAdvances":
                        self.__unpack_chip_family_chips(chip_family)
                    else:
                        self.__unpack_chip_family_chips_for_pas(chip_family)

                    self.__add_rule_based_synergies_and_fields(chip_family, category_name)

                    #for synergy_name in ("bonus", "counter", "effect", "effectcounter", "necessity", "reliability"):
                    #    all_synergies.update(chip_family[synergy_name])

                except Exception as e:
                    raise RuntimeError(f"chip_family: {chip_family}") from e

        self.__make_for_synergies()
        self.__make_from_synergies()
        print(sorted(all_synergies))

            #chip_category = sorted_chips[chip_category_name]

    def __unpack_chip_family_chips(self, chip_family):
        chip_family["highChips"] = []
        chip_family["mediumChips"] = []
        chip_family["lowChips"] = []
        chip_family["allChips"] = []

        chips_packed = chip_family["chips"]

        for chip_packed in chips_packed:
            chip = {}

            chip_name_and_codes_and_possibly_rank = chip_packed.split(", ", maxsplit=1)
            chip_name_and_codes = chip_name_and_codes_and_possibly_rank[0]
            if len(chip_name_and_codes_and_possibly_rank) == 1:
                chip_rank_key = "highChips"
            else:
                chip_rank_key = f"{chip_name_and_codes_and_possibly_rank[1]}Chips"

            chip_name, chip_codes_str = chip_name_and_codes.split(" ", maxsplit=1)
            chip_codes = tuple(chip_codes_str)
            chip_mb = self.chip_game_info[chip_name]["mb"]
            max_chip_count = mb_to_max_chip_count(chip_mb)

            chip["name"] = chip_name
            chip["codes"] = chip_codes
            chip["maxCount"] = max_chip_count
            chip_family[chip_rank_key].append(chip)
            chip_family["allChips"].append(chip)

        chip_family["allChipNames"] = tuple(chip["name"] for chip in chip_family["allChips"])

    def __unpack_chip_family_chips_for_pas(self, chip_family):
        chip_family["highChips"] = []
        chip_family["mediumChips"] = []
        chip_family["lowChips"] = []
        chip_family["allChips"] = []

        pas_packed = chip_family["chips"]
        for pa_packed in pas_packed:
            pa_rank, pa_chips_packed = next(iter(pa_packed.items()))
            pa_rank_key = f"{pa_rank}Chips"
            pa_chips = []

            if pa_chips_packed[0] == True:
                alphabet_asterisk_sub = True
                pa_chips_packed = pa_chips_packed[1:]
            else:
                alphabet_asterisk_sub = False

            for pa_chip_packed in pa_chips_packed:
                pa_chip_name, pa_chip_code = pa_chip_packed.split(" ", maxsplit=1)
                pa_chip = {
                    "name": pa_chip_name,
                    "code": pa_chip_code
                }

                pa_chips.append(pa_chip)

            chip_family[pa_rank_key].append(pa_chips)
            chip_family["allChips"].append(pa_chips)

        chip_family["allChipNames"] = []

    # 'isobject', 'reliability', 'element2', 'chips', 'counter', 'effect', 'necessity', 'bonus', 'effectcounter', 'dimming', 'element'
    # ['bonus', 'chips', 'counter', 'dimming', 'effect', 'effectcounter', 'element', 'element2', 'isobject', 'necessity', 'reliability']
    def __add_default_fields(self, chip_family, ):
        for synergy_field in ChipDB.synergy_classes:
            for suffix in ("", "from", "for"):
                synergy_field_full = f"{synergy_field}{suffix}"
                synergy_field_values = chip_family.get(synergy_field_full)
                if synergy_field_values is None:
                    chip_family[synergy_field_full] = set()
                else:
                    chip_family[synergy_field_full] = set(synergy_field_values)

        effect_values = chip_family.get("effect")
        if effect_values is None:
            chip_family["effect"] = set()
        else:
            effect_values_set = set(effect_values)
            if {"flinching", "paralysis"}.issubset(effect_values_set):
                effect_values_set.remove("flinching")

            chip_family["effect"] = set(effect_values)
        
        for bool_field in ("dimming", "isobject"):
            if bool_field not in chip_family:
                chip_family[bool_field] = False

        if "element" not in chip_family:
            chip_family["element"] = "none"

        if "element2" not in chip_family:
            if chip_family["element"] in {"sword", "break"}:
                chip_family["element2"] = chip_family["element"]
            else:
                chip_family["element2"] = "none"

    def __add_rule_based_synergies_and_fields(self, chip_family, category_name):
        element = chip_family["element"]
        if element == "fire":
            chip_family["bonus"].add("grass")
        elif element == "aqua":
            chip_family["bonus"].add("ice")
        elif element == "elec":
            chip_family["bonus"].add("bubbled")

        element2 = chip_family["element2"]
        if element2 == "break":
            chip_family["bonus"].add("frozen")
        elif element2 == "sword":
            chip_family["counter"].add("antisword")

        if category_name == "megaChips":
            chip_family["dimming"] = True

        if chip_family["dimming"] and category_name != "nonAttacking":
            chip_family["counter"].update(("invisible", "antidmg", "barrier", "bblwrap", "aura"))

        chip_family["almostAllEffects"] = frozenset(tuple(chip_family["effect"]) + tuple({element, element2}))

    class TryAddForSynergy:
        __slots__ = ("chip_family", "fulfilling_chips_for_all_synergies_of_synergy_class", "synergy_class_for")

        def __init__(self, chip_family, fulfilling_chips_for_all_synergies_of_synergy_class, synergy_class_for):
            self.chip_family = chip_family
            self.fulfilling_chips_for_all_synergies_of_synergy_class = fulfilling_chips_for_all_synergies_of_synergy_class
            self.synergy_class_for = synergy_class_for

        def try_add(self, effect, *plus_effects):
            chip_names_with_effect_for_synergy_class = self.fulfilling_chips_for_all_synergies_of_synergy_class[effect]
            if chip_names_with_effect_for_synergy_class is not None:
                if len(plus_effects) == 0:
                    self.chip_family[self.synergy_class_for].update(chip_names_with_effect_for_synergy_class)
                else:
                    self.chip_family[self.synergy_class_for].update(f"{chip_name}|{'|'.join(plus_effects)}" for chip_name in chip_names_with_effect_for_synergy_class)

    def __make_for_synergies(self):        
        chip_synergy_partition_table = {}

        for synergy_class in ChipDB.synergy_classes:
            chip_synergy_partition_table[synergy_class] = collections.defaultdict(list)

        for category_name, category_chips in self.sorted_chips.items():
            for chip_family_full in category_chips:
                chip_family_name, chip_family = next(iter(chip_family_full.items()))
                #effects = chip_family["effect"]

                chip_family_chip_names = []

                for synergy_class, synergy_partition in chip_synergy_partition_table.items():
                    for effect in chip_family[synergy_class]:
                        chip_names_with_effect_for_synergy_class = chip_synergy_partition_table[synergy_class][effect]
                        
                        if category_name == "programAdvances":
                            chip_names_with_effect_for_synergy_class.append(chip_family_name)
                        else:
                            chip_names_with_effect_for_synergy_class.extend(chip_family["allChipNames"])

        with open("chip_synergy_partition_table.json", "w+") as f:
            json.dump(chip_synergy_partition_table, f, indent=2)

        for category_name, category_chips in self.sorted_chips.items():
            for chip_family_full in category_chips:
                chip_family_name, chip_family = next(iter(chip_family_full.items()))

                effects = chip_family["effect"]
                element = chip_family["element"]
                element2 = chip_family["element2"]
                all_chip_names = chip_family["allChipNames"]

                for synergy_class in ChipDB.synergy_classes:
                    fulfilling_chips_for_all_synergies_of_synergy_class = chip_synergy_partition_table[synergy_class]
                    synergy_class_for = f"{synergy_class}for"
                    try_add_synergy = ChipDB.TryAddForSynergy(chip_family, fulfilling_chips_for_all_synergies_of_synergy_class, synergy_class_for)

                    for effect in itertools.chain(effects, {element, element2}, all_chip_names):
                        try_add_synergy.try_add(effect)
                        if effect in {"paralysis", "bubbled", "frozen", "timpani"}:
                            try_add_synergy.try_add("immobilization")
                        if effect == "cracked":
                            try_add_synergy.try_add("broken")

                        if effect in ("cracked", "broken"):
                            try_add_synergy.try_add("immobilization", "uninstall")
                        elif effect == "uninstall":
                            try_add_synergy.try_add("immobilization", "cracked")
                            try_add_synergy.try_add("immobilization", "broken")

                        #if effect == "aqua":
                        #    try_add_synergy.try_add("frozen", "ice")
                        #elif effect == "break":
                        #    try_add_synergy.try_add("frozen", "aqua")
                        #    try_add_synergy.try_add("aqua", "ice")
                        #elif effect == "ice":
                        #    try_add_synergy.try_add("break", "aqua")

    class TryAddFromSynergy:
        __slots__ = ("chip_family", "all_chip_names_by_effects", "synergy_class_from")

        def __init__(self, chip_family, all_chip_names_by_effects, synergy_class_from):
            self.chip_family = chip_family
            self.all_chip_names_by_effects = all_chip_names_by_effects
            self.synergy_class_from = synergy_class_from

        def try_add(self, effect, *plus_effects):
            chip_names_with_effect = self.all_chip_names_by_effects.get(effect)
            if chip_names_with_effect is not None:
                if len(plus_effects) == 0:
                    self.chip_family[self.synergy_class_from].update(chip_names_with_effect)
                else:
                    self.chip_family[self.synergy_class_from].update(f"{chip_name}|{'|'.join(plus_effects)}" for chip_name in chip_names_with_effect)

    def __make_from_synergies(self):
        all_chip_names_by_effects =  collections.defaultdict(list)

        for category_name, category_chips in self.sorted_chips.items():
            for chip_family_full in category_chips:
                chip_family_name, chip_family = next(iter(chip_family_full.items()))
                #effects = chip_family["effect"]

                chip_family_chip_names = []

                for effect in chip_family["effect"]:
                    if category_name == "programAdvances":
                        all_chip_names_by_effects[effect].append(chip_family_name)
                    else:
                        all_chip_names_by_effects[effect].extend(chip_family["allChipNames"])

        with open("all_chip_names_by_effects.json", "w+") as f:
            json.dump(all_chip_names_by_effects, f, indent=2)

        for category_name, category_chips in self.sorted_chips.items():
            for chip_family_full in category_chips:
                chip_family_name, chip_family = next(iter(chip_family_full.items()))
        
                #effects = chip_family["effect"]
                #element = chip_family["element"]
                #element2 = chip_family["element2"]
                #all_chip_names = chip_family["allChipNames"]
        
                for synergy_class in ChipDB.synergy_classes:
                    chip_family_synergy_effects = chip_family[synergy_class]
                    synergy_class_from = f"{synergy_class}from"

                    try_add_from_synergy = ChipDB.TryAddFromSynergy(chip_family, all_chip_names_by_effects, synergy_class_from)

                    for effect in chip_family_synergy_effects:
                        try_add_from_synergy.try_add(effect)
                        if effect == "immobilization":
                            for effect in ("paralysis", "bubbled", "frozen", "timpani"):
                                try_add_from_synergy.try_add(effect)
                            try_add_from_synergy.try_add("uninstall", "cracked")
                            try_add_from_synergy.try_add("uninstall", "broken")
                        elif effect == "broken":
                            try_add_from_synergy.try_add("cracked")

    def get_chips_by_category(self, category_name):
        return self.sorted_chips[category_name]

    def query(self, category_names=None, ranks=None, groupby=None, exclude_families=None, effects=None):
        if groupby not in (None, "family"):
            raise RuntimeError()

        wanted_category_names = category_names
        wanted_ranks = ranks
        wanted_effects = effects

        if wanted_category_names is None:
            wanted_category_names = ("ranged", "constrained", "pseudoMega", "nonAttacking", "megaChips", "gigaChips", "programAdvances")

        if wanted_ranks is None:
            wanted_ranks = ("highChips", "mediumChips", "lowChips")

        if wanted_effects is not None:
            wanted_effects = frozenset(effects)

        query_params = QueryParams(wanted_category_names, wanted_ranks, groupby, exclude_families, wanted_effects)

        cache_result = self.query_cache.get(query_params)
        if cache_result is not None:
            return cache_result

        result = []

        for category_name, category_chips in self.sorted_chips.items():
            if category_name in wanted_category_names:
                for chip_family_full in category_chips:
                    chip_family_name, chip_family = next(iter(chip_family_full.items()))

                    if exclude_families is not None and chip_family_name in exclude_families:
                        continue

                    #cur_chip_result = {}
                    groupby_result = []

                    for wanted_rank in wanted_ranks:
                        rank_chips = chip_family[wanted_rank]
                        #if chip_family_name == "BblStar":
                        #    print(f"rank_chips: {rank_chips}")
                        if len(rank_chips) != 0:
                            for rank_chip in rank_chips:
                                if groupby is None:
                                    chip_family_new = copy.deepcopy(chip_family)
                                else:
                                    chip_family_new = {}

                                if category_name == "programAdvances":
                                    chip_family_new["parts"] = rank_chip
                                    chip_family_new["name"] = chip_family_name
                                    chip_family_new["category"] = category_name
                                else:
                                    chip_family_new["codes"] = rank_chip["codes"]
                                    chip_family_new["maxCount"] = rank_chip["maxCount"]
                                    chip_family_new["name"] = rank_chip["name"]
                                    chip_family_new["family"] = chip_family_name
                                    chip_family_new["category"] = category_name

                                if wanted_effects is not None and not wanted_effects.issubset(chip_family["almostAllEffects"] | frozenset((chip_family_new["name"],))):
                                    continue

                                if groupby is None:
                                    result.append(chip_family_new)
                                elif groupby == "family":
                                    groupby_result.append(chip_family_new)

                    if groupby == "family" and len(groupby_result) != 0:
                        groupby_chip_family_new = copy.deepcopy(chip_family)
                        groupby_chip_family_new["chips"] = groupby_result
                        result.append(groupby_chip_family_new)

        self.query_cache[query_params] = result
        return result

    def querydict(self, **kwargs):
        result = self.query(**kwargs)
        return {chip["name"]: chip for chip in result}

    #def query_unflat(self, category_names=None, ranks=None):
    #    wanted_category_names = category_names
    #    wanted_ranks = ranks
    #
    #    query_params = QueryParams(wanted_category_names, wanted_ranks)
    #
    #    cache_result = self.query_cache.get(query_params)
    #    if cache_result is not None:
    #        return cache_result
    #
    #    result = []
    #
    #    for category_name, category_chips in self.sorted_chips.items():
    #        if wanted_category_names is None or category_name in wanted_category_names:
    #            for chip_family_full in category_chips:
    #                chip_family_name, chip_family = next(iter(chip_family_full.items()))
    #
    #                #cur_chip_result = {}
    #                if wanted_ranks is None:
    #                    wanted_ranks = ["highChips", "mediumChips", "lowChips"]
    #
    #                for wanted_rank in wanted_ranks:
    #                    chip_family_new = copy.deepcopy(chip_family)
    #                    rank_chips = chip_family_new[wanted_rank]
    #                    if len(rank_chips) != 0:
    #                        for rank_chip in rank_chips:
    #                            if category_name == "programAdvances":
    #                                chip_family_new["parts"] = rank_chip
    #                                chip_family_new["name"] = chip_family_name
    #                            else:
    #                                chip_family_new["codes"] = rank_chip["codes"]
    #                                chip_family_new["maxCount"] = rank_chip["maxCount"]
    #                                chip_family_new["name"] = rank_chip["name"]
    #                                chip_family_new["family"] = chip_family_name
    #
    #                        result.append(chip_family_new)
    #
    #    self.query_cache[query_params] = result
    #    return result

class QueryParams:
    __slots__ = ("category_names", "ranks", "groupby", "exclude_families", "wanted_effects")

    def __init__(self, category_names=None, ranks=None, groupby=None, exclude_families=None, wanted_effects=None):
        self.category_names = frozenset(category_names) if category_names is not None else None
        self.ranks = frozenset(ranks) if ranks is not None else None
        self.groupby = groupby
        self.exclude_families = frozenset(exclude_families) if exclude_families is not None else None
        self.wanted_effects = frozenset(wanted_effects) if wanted_effects is not None else None

    def __key(self):
        return (self.category_names, self.ranks, self.groupby, self.exclude_families, self.wanted_effects)

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, QueryParams):
            return self.__key() == other.__key()
        return NotImplemented
