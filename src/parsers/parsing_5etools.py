import csv, re

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

damage_types = ['Piercing', 'Bludgeoning', 'Slashing', 'Cold', 'Fire', 'Lightning', 'Thunder', 'Poison', 'Acid',
                'Necrotic', 'Radiant', 'Force', 'Psychic']
abilities = ['Strength', 'Dexterity', 'Constitution', 'Intelligence', 'Wisdom', 'Charisma']
conditions = ['Blinded', 'Charmed', 'Deafened', 'Exhaustion', 'Frightened', 'Grappled', 'Incapacitated', 'Invisible',
              'Paralyzed', 'Petrified', 'Poisoned', 'Prone', 'Restrained', 'Stunned', 'Unconscious']
areas = ['Cube', 'Line', 'Cone', 'Cylinder', 'Sphere']
upcast_words = ['Using a Higher-Level Spell Slot.', 'At Higher Levels.', 'Cantrip Upgrade.']
bolded_words = upcast_words + conditions + damage_types + abilities + areas
bolded_patterns = [r'[0-9]+d[0-9]+( [+-] [0-9]+)?', r'[+-][0-9]+', '[0-9]+[ -]fe*o*t']
bolded_regex = re.compile('(' + '|'.join(bolded_words + bolded_patterns) + ')')

italic_words = upcast_words + conditions
italic_regex = re.compile('(' + '|'.join(italic_words) + ')')


def parse_csv(path: str) -> [dict[str, str]]:
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
    spell["Lvl"] = lvl

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