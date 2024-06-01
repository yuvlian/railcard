from mihomo import Attribute, Character
import json

def combine_attr_fields(a: list[Attribute], b: list[Attribute]) -> set[str]:
    return set([x.field for x in a] + [x.field for x in b])

def search(lst: list[Attribute], field: str) -> Attribute:
    a = [x for x in lst if x.field == field]
    return a[0] if a else None

def comb_attr_stats(a: Attribute, b: Attribute) -> str:
    if a.is_percent != b.is_percent: return f"{a.displayed_value} + {b.displayed_value}"

    p = a.is_percent
    f = (lambda x: int(x*1000) / 10) if p else int
    sum = f(a.value) + f(b.value)
    return f"{round(sum, 1)}%" if p else str(sum)

def comb_stats(lst1: list[Attribute], lst2: list[Attribute], field: str) -> str:
    a = search(lst1, field)
    b = search(lst2, field)

    if not a and not b: return "N/A"
    if not a: return b.displayed_value
    if not b: return a.displayed_value

    return comb_attr_stats(a, b)

def get_atk_boosts(ch: Character) -> list[list[str]]:
    elemental = [x for x in ch.properties if x.type.endswith("AddedRatio") and x.field.endswith("_dmg") and x.field != "all_dmg"]
    all_dmg = search(ch.properties, "all_dmg")
    if not elemental: return [[all_dmg.field, all_dmg.icon, all_dmg.name, all_dmg.displayed_value]] if all_dmg else []

    return [[x.field, x.icon, x.name, comb_attr_stats(x, all_dmg) if all_dmg else x.displayed_value] for x in elemental]

def get_config() -> dict:
    with open("config.json", "r") as f:
        return json.load(f)

def sort_fields(lst: list[str]) -> list[str]:
    ref = ["crit_rate", "crit_dmg", "break_dmg", "heal_rate", "sp_rate", "effect_hit", "effect_res"]
    return sorted(lst, key=lambda x: ref.index(x) if x in ref else len(ref))
