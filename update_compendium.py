#!/usr/bin/env python3

from card_creator import CardCreator
from hex_compendium import HexCompendium

def main():
    c = CardCreator()
    h = HexCompendium()
    num_cards_processed = 0

    for card in c.all_cards_data:
        if card['card_rarity'] in ('Common', 'Uncommon', 'Rare', 'Legendary') and card['equipment_modified_card'] == False:
            card_name = card['name']

            if h.page_exists(card_name):
                continue

            wiki_text = c.format_card_data(card)

            if wiki_text is None:
                continue

            if h.create_page(card_name, wiki_text):
                num_cards_processed += 1

            if num_cards_processed >= 20:
                return

if __name__ == '__main__':
    main()
