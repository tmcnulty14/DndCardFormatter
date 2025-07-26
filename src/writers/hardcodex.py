import csv

from parsers.parsing_5etools import parse_csv

data_dir = "C:\\Users\\tommc\\PycharmProjects\\DndCardFormatter\\data"
class_name = 'Ranger'
input_file = data_dir + f'\\{class_name}Spells-5et.csv'
output_file = data_dir + f"\\{class_name}Spells-hardcodex.csv"

fieldnames_hardcodex = [
    'Lvl',
    'Name',
    'Level and School',
    'Casting Time',
    'Range',
    'Components Short',
    'Duration',
    'Card Text',
    'Class',
]

def test(path):
    rows = parse_csv(path)
    for row in rows:
        print(row)
        print()


def write_hardcodex_csv(path, cards):
    with open(path, 'w') as file:
        writer = csv.DictWriter(file,
                                fieldnames=fieldnames_hardcodex,
                                delimiter=';',
                                extrasaction='ignore',
                                quotechar='"',
                                quoting=csv.QUOTE_ALL,
                                lineterminator='\n')

        for card in cards:
            if 'Materials' in card:
                card['Card Text'] = card['Materials'] + " " + card['Card Text']

            writer.writerow(card)


# def write_homebrewery_html(path, cards: List[dict[str, str]]):
#     with open(path, 'w') as file:
#
#         for card in cards:



# test(input_file)

spells = list(parse_csv(input_file))
write_hardcodex_csv(output_file, spells)
