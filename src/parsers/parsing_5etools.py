import csv, re
import json
from typing import Any, Generator

# 5e.tools Field Names:
# fieldnames_5etools = [
#     'Name',
#     'Source',
#     'Page',
#     'Level',
#     'Casting Time',
#     'Duration',
#     'School',
#     'Range',
#     'Components',
#     'Classes',
#     'Optional/Variant Classes',
#     'Text',
#     'At Higher Levels',
# ]

abilities = ['Strength', 'Dexterity', 'Constitution', 'Intelligence', 'Wisdom', 'Charisma']
skills = ['Athletics', 'Acrobatics', 'Sleight of Hand', 'Stealth', 'Arcana', 'History', 'Investigation', 'Nature',
          'Religion', 'Animal Handling', 'Insight', 'Medicine', 'Perception', 'Survival', 'Deception', 'Intimidation',
          'Performance', 'Persuasion']
conditions = ['Blinded', 'Charmed', 'Deafened', 'Exhaustion', 'Frightened', 'Grappled', 'Incapacitated', 'Invisible',
              'Paralyzed', 'Petrified', 'Poisoned', 'Prone', 'Restrained', 'Stunned', 'Unconscious']
damage_types = ['Piercing', 'Bludgeoning', 'Slashing', 'Cold', 'Fire', 'Lightning', 'Thunder', 'Poison', 'Acid',
                'Necrotic', 'Radiant', 'Force', 'Psychic']
areas = ['Circle', 'Cone', 'Cube', 'Cylinder', 'Emanation', 'Line', 'Square', 'Sphere']
sizes = ['Tiny', 'Small', 'Medium', 'Large', 'Huge', 'Gargantuan']
upcast_words = ['Using a Higher-Level Spell Slot.', 'At Higher Levels.', 'Cantrip Upgrade.']
creature_types = ['Aberration', 'Beast', 'Celestial', 'Construct', 'Creature', 'Dragon', 'Elemental', 'Fey', 'Fiend',
                  'Giant', 'Humanoid', 'Monstrosity', 'Ooze', 'Plant', 'Undead']
actions = ['Bonus Action', 'Action', 'Attack', 'Dash', 'Disengage', 'Dodge', 'Help', 'Hide', 'Magic', 'Search', 'Study']
rules_words = ['AC', 'Armor Class', 'Advantage', 'Disadvantage', 'Difficult Terrain', 'Resistance', 'Immunity', 'Short Rest', 'Long Rest', 'Telepathy']
environmental_words = ['Bright Light', 'Dim Light', 'Lightly Obscured', 'Heavily Obscured']
senses = ['Blindsight', 'Darkvision', 'Tremorsense']
bolded_words = abilities + skills + conditions + damage_types + areas + sizes + upcast_words + creature_types + actions + rules_words + environmental_words + senses
bolded_patterns = [r'[0-9]+d[0-9]+( [+-] [0-9]+)?', r'[0-9]*[+-][0-9]+', r'[,0-9]+[ -]fe*o*t(-\w+)?', r'[0-9]+ percent']
bolded_regex = re.compile('(' + '|'.join(bolded_words + bolded_patterns) + ')')

italic_words = upcast_words + conditions
italic_regex = re.compile('(' + '|'.join(italic_words) + ')')


def parse_csv(path: str) -> Generator[dict[str | Any, str | Any], Any, None]:
    file = open(path, "r")

    reader = csv.DictReader(file)

    card_type = get_csv_type(reader)

    for entry in reader:
        entry['card_type'] = card_type
        if card_type == 'Spell':
            process_spell(entry)
        elif card_type == 'Item':
            process_item(entry)
        yield entry


def get_csv_type(reader: csv.DictReader) -> str:
    if 'Level' in reader.fieldnames:
        return 'Spell'
    elif 'Rarity' in reader.fieldnames:
        return 'Item'
    else:
        raise TypeError(f'Unknown CSV type on fieldnames: {reader.fieldnames}')


def process_spell(spell: dict[str, str]):
    # print(f'Processing spell: {spell}')
    fix_bonus_casting_time(spell)
    move_ritual(spell)
    make_lvl(spell)
    split_materials(spell)
    make_cardtext(spell)

    apply_overrides(spell)
    # print(f'Processed spell: {spell}')


def fix_bonus_casting_time(spell: dict[str, str]):
    if spell['Casting Time'] == 'Bonus':
        spell['Casting Time'] = 'Bonus Action'


def move_ritual(spell: dict[str, str]):
    ri = spell['School'].find(' (ritual)')
    if ri > 0:
        spell['School'] = spell['School'][:ri]
        spell['Casting Time'] += ' or Ritual'

def make_lvl(spell: dict[str, str]):
    lvl = spell["Level"][0]
    if lvl == 'C':
        lvl = 0
        spell['Level and School'] = f"{spell['School']} {spell["Level"]}"
    else:
        spell['Level and School'] = f"{spell["Level"]} level {spell['School']}"
    spell["Lvl"] = str(lvl)

def split_materials(spell: dict[str, str]):
    components = spell["Components"]
    i = components.find("M (")
    if i >= 0:
        spell["Components Short"] = components[:i + 1]
        spell["Materials"] = components[i + 3:-1]
    else:
        spell["Components Short"] = components


def make_cardtext(spell: dict[str, str]):
    text = spell["Text"].strip()
    if "At Higher Levels" in spell and spell["At Higher Levels"] is not None and len(spell["At Higher Levels"]) > 0:
        text += '\n:\n' + spell["At Higher Levels"]

    spell["Card Text"] = text
    sanitize_cardtext(spell)
    format_words(spell)


def sanitize_cardtext(spell: dict[str, str]):
    text = spell["Card Text"]

    text = text.strip()
    text = text.replace(';', '-')
    text = re.sub(r';', '-', text)
    text = text.replace("\n", "\n\n")
    text = re.sub(r'([.!?:]"?)(\S+)', '\\1\n\n\\2', text)

    spell["Card Text"] = text


def format_words(spell: dict[str, str]):
    spell["Card Text"] = re.sub(bolded_regex, '**\\g<1>**', spell["Card Text"])
    spell["Card Text"] = re.sub(italic_regex, '*\\g<1>*', spell["Card Text"])


def process_item(item: dict[str, str]) -> dict[str, str]:
    make_cardtext(item)
    return item


def apply_overrides(card: dict[str, str]) -> dict[str, str]:
    if card['Name'] in overrides:
        card.update(overrides[card['Name']])
    return card


def load_overrides() -> dict[str, dict[str, str]]:
    with open('overrides/card_overrides.json', 'r') as file:
        # Use json.load() to parse the file content into a Python dictionary
        return json.load(file)


overrides = load_overrides()