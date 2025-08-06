import json
import sys
from typing import Optional, Generator

from parsers import parsing_5etools
from writers import homebrewery


def convert(input_path: str, output_path: str, source_override: Optional[str]):
    # TODO: Support other formats
    print(f'Converting {input_path} from {'5e.tools CSV'} to {'Homebrewery HTML'}')
    cards = list(parsing_5etools.parse_csv(input_path))
    if source_override:
        for card in cards:
            card['Source'] = source_override

    make_output(cards, output_path)


def run_query(query: dict[str, list[str]]):
    card_database = list(parsing_5etools.parse_csv('data/Spells_Database.csv'))

    # Filter the cards
    cards = [card for card in card_database if query_filter(card, query)]

    # Map the cards
    cards = [query_map(card, query) for card in cards]

    # Sort the cards
    cards.sort(key=lambda card: card['Source'] + card['Lvl'])

    make_output(cards, generate_query_output_path(query))


def query_filter(card: dict[str, str], query: dict[str, list[str]]) -> bool:
    # Apply all query filters as value-matching ORs occurring anywhere in the corresponding field
    return not any(not any(val in card[key] for val in values) for key, values in query.items())


def query_map(card: dict[str, str], query: dict[str, list[str]]) -> dict[str, str]:
    if 'Classes' in query:
        # Only list classes that are included in the query.
        card_classes = [cl for cl in query['Classes'] if cl in card['Classes']]
        card['Source'] = ', '.join(card_classes)
    return card


def generate_query_output_path(query: dict[str, list[str]]) -> str:
    return f'output/{'_'.join('-'.join([key] + values) for key, values in query.items())}.html'


def make_output(cards: list[dict[str, str]], output_path: str):
    html_blocks = [homebrewery.generate_card_html(spell_dict) for spell_dict in cards]

    with open(output_path, 'w') as writer:
        for i, block in enumerate(html_blocks):
            writer.write(block)
            writer.write('\n\n\n')

            if (i + 1) % 9 == 0:
                writer.write('\\page\n\n\n')


if __name__ == "__main__":
    input_path = sys.argv[1]
    if input_path.endswith('.csv'):
        output_path = sys.argv[2]
        source_override = sys.argv[3] if len(sys.argv) > 3 else None
        convert(input_path, output_path, source_override)
    elif input_path.endswith('.json'):
        query = json.load(open(input_path, 'r'))
        run_query(query)
