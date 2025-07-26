from jinja2 import Environment, FileSystemLoader

TEMPLATES_PATH = 'templates/'

COLOR_MAP = {
    'Barbarian': '--barbarian_orange',
    'Paladin': '--paladin_gold',
    'Bard': '--bard_pink',
    'Ranger': '--ranger_emerald',
    'Cleric': '--cleric_silver',
    'Rogue': '--rogue_ash',
    'Druid': '--druid_moss',
    'Sorcerer': '--sorcerer_blood',
    'Fighter': '--fighter_rust',
    'Warlock': '--warlock_iris',
    'Monk': '--monk_sky',
    'Wizard': '--wizard_cobalt',
    'Artificer': '--artificer_copper',
}

DEFAULT_SPELL_COLOR = '--spell-color'
DEFAULT_ITEM_COLOR = 'rgba(200,100,0,.15)'

DEFAULT_BODY_FONT_SIZE_PX = 12.85

environment = Environment(loader=FileSystemLoader(TEMPLATES_PATH))
spell_template = environment.get_template('spell_card.html')
item_template = environment.get_template('item_card.html')

def generate_card_html(card: dict[str, str]) -> str:
    card = sanitize_keys(card)

    set_fontsize(card)

    if card['card_type'] == 'Spell':
        return generate_spell_html(card)
    elif card['card_type'] == 'Item':
        return generate_item_html(card)

    raise TypeError(f'Unknown card type {card['card_type']}')


def sanitize_keys(spell: dict[str, str]) -> dict[str, str]:
    # Sanitizes spell keys for use in jinja template. Template keys must be lowercase and not contain spaces.
    return {key.lower().replace(' ', '_'): value for key, value in spell.items()}


def generate_spell_html(spell: dict[str, str]) -> str:
    # Set spell color
    source = spell['source']
    color = COLOR_MAP[source] if source in COLOR_MAP else DEFAULT_SPELL_COLOR

    spell['name'] = spell['name'].upper()

    return spell_template.render(spell, color=color)


def generate_item_html(item: dict[str, str]) -> str:
    # Title-case type and rarity.
    for field in ['type', 'rarity']:
        item[field] = item[field].title()

    # Set up attunement.
    format_attunement(item)

    return item_template.render(item, color=DEFAULT_ITEM_COLOR)


def format_attunement(item: dict[str, str]):
    # Set up attunement.
    if len(item['attunement']) > 0:
        if item['attunement'] == 'requires attunement':
            item['attunement'] = 'attuned'
        item['attunement'] = f' ({item['attunement']})'


def set_fontsize(card: dict[str, str]):
    font_size = DEFAULT_BODY_FONT_SIZE_PX

    # Reduce font size if the text likely won't fit on the card.
    if line_estimate(card['card_text']) > 14:
        font_size = 10

    card['font_size'] = f'{font_size}px'


def line_estimate(text: str) -> int:
    # About 40 chars to a line at default font size and card width.
    lines = 0
    i = 0
    while i < len(text):
        next_break = text.find('\n', i, i + 40)
        if next_break > 0:
            i = next_break + 1
        else:
            i += 40
        lines += 1
    return lines