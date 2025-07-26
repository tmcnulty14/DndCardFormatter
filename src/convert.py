import sys
from typing import Optional

from parsers.parsing_5etools import parse_csv
from writers.homebrewery import generate_card_html


def convert(input_path: str, output_path: str, source_override: Optional[str]):
    # TODO: Support other formats
    print(f'Converting {input_path} from {'5e.tools CSV'} to {'Homebrewery HTML'}')

    cards = list(parse_csv(input_path))
    if source_override:
        for card in cards:
            card['Source'] = source_override
    html_blocks = [generate_card_html(spell_dict) for spell_dict in cards]

    with open(output_path, 'w') as writer:
        i = 0
        for block in html_blocks:
            if i == 9:
                writer.write('\\page\n\n\n')
                i = 0

            writer.write(block)
            writer.write('\n\n\n')
            i += 1


if __name__ == "__main__":
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    source_override = sys.argv[3] if len(sys.argv) > 3 else None
    convert(input_path, output_path, source_override)