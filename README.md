# CompendiumUpdater
Automation for Hex Compendium to import missing cards

Run ./update_compendium.py

The script will pull all existing cards from Hex PvP Tools, then for each relevant card (has rarity of either 'Common', 'Uncommon', 'Rare', 'Legendary' or 'Land'), and then query hexcompendium.com to see if a page for that card already exists. If it doesn't, the script will format the data for the wiki and create the page, then it will go to the next card.

In order to login to the Hex Compendium, the script will read the COMPENDIUM_USER and COMPENDIUM_PASS environment variables. Set them to valid HexCompendium credentials before running the script.
