import json
import re
import urllib.parse
import urllib.request

class CardCreator:
    HPT_CARDS_ENDPOINT = 'https://hexpvptools.net/api/static/cards/{0}'
    HPT_CARD_ENDPOINT = 'https://hexpvptools.net/api/static/card/{0}'
    HPT_SET_ENDPOINT = 'https://hexpvptools.net/api/static/sets/{0}'

    CARD_PAGE_TEXT = '''
{{{{Card/Infobox
{18}|set = {0}
|type = {1}
|race = {2}
|class = {3}
|subtype = {4}
|subtype2 =
|subtype3 =
|hiddensubtype =
|hiddensubtype2 =
|rarity = {5}
|faction = {6}
|sockets = {7}
|unique = {8}
|threshold = {9}
|cost = {10}
|atk = {11}
|def = {12}
|keyword = {13}
|price = {14}
}}}}
== Game Text ==
{15}

== Equipment ==


== Artist ==
{16}

== Lore Text ==
{17}
'''

    def __init__(self):
        self.all_cards_data = json.loads(urllib.request.urlopen(self.HPT_CARDS_ENDPOINT.format('')).read().decode('utf-8'))['cards']
        print('Found {0} cards'.format(len(self.all_cards_data)))

    def card_data_from_name(self, name):
        for card in self.all_cards_data:
            if card['name'] == name and card['equipment_modified_card'] == False and (card['card_rarity'] in ('Common', 'Uncommon', 'Rare', 'Legendary')):
                return card

        return None

    def format_card_data(self, card_data):
        print("Processing {0}".format(card_data['name']))

        try:
            card_set = json.loads(urllib.request.urlopen(self.HPT_SET_ENDPOINT.format(card_data['hex_card_set_id'])).read().decode('utf-8'))['name']
        except:
            print("Error getting {0}".format(card_id))
            return None

        card_type = self.extract_type(card_data['card_type'])
        subtypes = self.extract_subtype(card_data['card_subtype'])

        race = ''
        card_class = ''
        card_subtype = ''
        i = 1
        for r in subtypes[0]:
            if i > 1:
                race += "\n|race{0} = ".format(i)
            race += r
            i += 1
        i = 1
        for c in subtypes[1]:
            if i > 1:
                card_class += "\n|class{0} = ".format(i)
            card_class += c
            i += 1
        i = 1
        for s in subtypes[2]:
            if i > 1:
                card_subtype += "\n|subtype{0} = ".format(i)
            card_subtype += s
            i += 1

        rarity = card_data['card_rarity']
        faction = 'Ardent' if card_data['faction'] == 'Aria' else ('' if (card_data['faction'] is None or card_data['faction'] == 'None') else card_data['faction'])

        card_text = self.extract_display_text(card_data['game_text'], (None if card_data['display_text'] is None else json.loads(card_data['display_text']) ))

        if card_text is None or len(card_text) == 0:
            card_text = 'None'

        sockets = ''

        if (re.search(r'SOCKETABLE MAJOR', str(card_text))) is not None:
            sockets += 'Major '
        if (re.search(r'SOCKETABLE MAJOR', str(card_text))) is not None:
            sockets += 'Minor '
        sockets = sockets.strip().replace(' ', ', ')

        threshold = ((card_data['threshold_blood'] * '1 Blood, ') + (card_data['threshold_diamond'] * '1 Diamond, ') + (card_data['threshold_ruby'] * '1 Ruby, ') + (card_data['threshold_sapphire'] * '1 Sapphire, ') + (card_data['threshold_wild'] * '1 Wild, ')).strip()[:-1]
        if len(threshold) == 0:
            treshold = 'Shardless'
        
        unique = 'Yes' if card_data['unique'] == 1 else ''

        if card_data['card_type'] == 'Resource':
            cost = ''
        else:
            cost = str(card_data['resource_cost'])
            if card_data['variable_cost'] == 1:
                cost += 'X'
            if card_data['variable_cost_double'] == 1:
                cost += 'XX'
            if len(cost) > 1 and cost[0] == '0':
                cost = cost[1:]

        attack = card_data['base_attack_value'] if 'Troop' in card_data['card_type'] else ''
        defense = card_data['base_health_value'] if 'Troop' in card_data['card_type'] else ''

        keyword = ''
        keywords = self.extract_keywords(card_text)
        i = 1
        for k in keywords:
            if i > 1:
                keyword += "\n|keyword{0} = ".format(i)
            keyword += k
            i += 1

        price = card_data['name']
        game_text = self.format_game_text(card_text)

        artist = card_data['artist_name']
        if artist is not None and len(artist) > 0:
            artist = '[[{0}]]'.format(artist)

        lore_text = 'None' if card_data['flavor_text'] is None else card_data['flavor_text'].replace(r'\n', "\n")

        image_link = ''
        if re.search(r'[:\']', card_data['name']):
            image_replace = card_data['name'].replace("'", '%27').replace(':','').replace(' ', '%20')
            image_link = "|image = {0}\n".format(image_replace)

        wiki_text = self.CARD_PAGE_TEXT.format(
            card_set, # 0
            card_type, # 1
            race.strip(), # 2
            card_class.strip(), # 3
            card_subtype, # 4
            rarity, # 5
            faction, # 6
            sockets, # 7
            unique, # 8
            threshold, # 9
            cost, # 10
            attack, # 11
            defense, # 12
            keyword, # 13
            price, # 14
            game_text, # 15
            artist, # 16
            lore_text, # 17
            image_link # 18
            ).strip()

#        self.hex_compendium.create_page(card_data['name'], wiki_text)
#        print(wiki_text)
        return wiki_text
        
    def extract_type(self, card_type):
        type_map = {
	    'Constant|Quick' : 'Quick Constant',
	    'Troop|Artifact' : "Artifact\n|type2 = Troop",
	    'Troop|Quick' : 'Quick Troop',
	    'BasicAction' : 'Basic Action',
	    'QuickAction' : 'Quick Action',
        }

        if card_type in type_map:
            return type_map[card_type]

        return card_type

    def extract_subtype(self, subtype):
        if subtype is None:
            return ([], [], '')

        races = [
            "Abomination",
            "Arborean",
            "Avatar",
            "Beast",
            "Berry",
            "Bird",
            "Blob",
            "Buffalo",
            "Caribaur",
            "Chaostouched",
            "Cheese",
            "Chimera",
            "Construct",
            "Coyotle",
            "Cromag",
            "Croven",
            "Cyclops",
            "Dingler",
            "Dinosaur",
            "Dragon",
            "Drokka",
            "Dwarf",
            "Elemental",
            "Elf",
            "Ender",
            "Entity",
            "Eternal",
            "Fae",
            "Faerie",
            "Fish",
            "Frog",
            "Gargoyle",
            "Ghoul",
            "Giant",
            "Gnoll",
            "Gnome",
            "Goat",
            "Gobbler",
            "Goblin",
            "Golem",
            "Gorilla",
            "Great Wolf",
            "Griffin",
            "Hag",
            "Hardshell",
            "Harpy",
            "Hexlantean",
            "Horror",
            "Human",
            "Hydra",
            "Iljuni",
            "Imp",
            "Imps",
            "Incarnation",
            "Insect",
            "Kraken",
            "Lamprax",
            "Leprechaun",
            "Manifestation",
            "Manti",
            "Minotaur",
            "Moppet",
            "Necrotic",
            "Nibblin",
            "Nymph",
            "Ogre",
            "Omen",
            "Oni",
            "Orc",
            "Pastry",
            "Pegasus",
            "Phoenix",
            "Plant",
            "Prodigen",
            "Robot",
            "Rock",
            "Satyr",
            "Scorpion",
            "Shapeshifter",
            "Shin\'hare",
            "Shroomkin",
            "Skeleton",
            "Sphinx",
            "Spider",
            "Spirit",
            "Squirrel",
            "Stormling",
            "Thrall",
            "Totem",
            "Troll",
            "Turtle",
            "Undead",
            "Unicorn",
            "Vampire",
            "Vennen",
            "Witch",
            "Woolvir",
            "Wool\'vir",
            "Worm",
            "Wormoid",
            "Yeti",
            "Zombie",
        ]

        classes = [
            "High Cleric",
            "Bard",
            "Big",
            "Cleric",
            "Concubunny",
            "Elder",
            "Familiar",
            "Hero",
            "King",
            "Knight",
            "Mage",
            "Mustachioed",
            "Mutant",
            "Pet",
            "Prince",
            "Princess",
            "Queen",
            "Ranger",
            "Rogue",
            "Sensei",
            "Slave",
            "Super",
            "Transcended",
            "Warlock",
            "Warrior",
        ]

        r = []
        c = []

        for race in races:
            if re.search(r'\b' + race + r'\b', subtype):
                r.append(race)
                subtype = re.sub(r'\b' + race + r'\b', '', subtype).strip()

            if re.search(r'\b' + race + r'\b', subtype):
                r.append(race)
                subtype = re.sub(r'\b' + race + r'\b', '', subtype).strip()

        for class_ in classes:
            if re.search(r'\b' + class_ + r'\b', subtype):
                c.append(class_)
                subtype = re.sub(r'\b' + class_ + r'\b', '', subtype).strip()

        # Remove some words that aren't traits (e.g. "the", "of")
        subtype = re.sub(r'(^| )(the|ol\'|of)($| )', ' ', subtype).strip()

        # What is remaining, each individual work is a separate subtype
        return (r, c, subtype.split(' '))

    def extract_display_text(self, game_text, display_text):
        if game_text is None:
            return ''

        sections = list(filter(None, game_text.split("<p>")))

        def replace_name_by_id(name):
            try:
                return json.loads(urllib.request.urlopen(self.HPT_CARD_ENDPOINT.format(name.group(1))).read().decode('utf-8'))['id'] + name.group(1)
            except:
                return name.group(1)

        if type(display_text) is dict:
            for i in range(len(sections)):
                section_key = re.sub(r'[\[\],:; "()/\']|</?b>','', re.sub(r'<b>([^<]*)</b>', replace_name_by_id, re.sub(r'#[^#]+#', '', sections[i])).lower()).replace('.','d').replace('-','m').replace('+','p')
                if section_key in display_text:
                    sections[i] = display_text[section_key]

        return "\n\n".join(sections)


    def extract_keywords(self, game_text):
        keywords = [
            'Allegiance',
            'Assault',
            'Boon',
            'Bury',
            'Conscript',
            'Crush',
            'Deathcry',
            'Death Sentence',
            'Deploy',
            'Diligence',
            'Empower',
            'Escalation',
            'Fateweave',
            'Feral',
            'Flight',
            'Frostform',
            'Fusion',
            'Gladiator',
            'Illuminate',
            'Inspire',
            'Invincible',
            'Lethal',
            'Lifebound',
            'Lifedrain',
            'Marked',
            'Momentum',
            'Mobilize',
            'Portal',
            'Prophecy',
            'Rabid',
            'Rage',
            'Rebirth',
            'Rowdy',
            'Runic',
            'Scrounge',
            'Shell',
            'Shift',
            'Skyguard',
            'Soulcursed',
            'Speed',
            'Spellshield',
            'Steadfast',
            'Swiftstrike',
            'Tunneling',
            'Valorous',
            'Verdict',
        ]

        k = []
        for keyword in keywords:
            if re.search(r'<b>{0}( \d)?</b>'.format(keyword), game_text):
                k.append(keyword)

        return k

    def format_game_text(self, game_text):
        symbols = {
            '[BLOOD]': '{{Icon|Blood}}',
            '[DIAMOND]': '{{Icon|Diamond}}',
            '[RUBY]': '{{Icon|Ruby}}',
            '[SAPPHIRE]': '{{Icon|Sapphire}}',
            '[WILD]': '{{Icon|Wild}}',
            '[ATK]': '[[File:Attack.png|15px]]',
            '[DEF]': '[[File:defence.png|15px]]',
            '[ACT]': '[[File:exhaust.png]]',
            '[UNDERWORLD]': '[[File:underworldicon.png|21px]]',
            '[ARDENT]': '[[File:ardenticon.png|21px]]',
            '[ARROWR]': '→',
            '[BASIC]': '[[File:Basic.png]]',
            '[ONE-SHOT]': '[[File:1shot.png]]',
        }

        for key, value in symbols.items():
            game_text = game_text.replace(key, value)

        # Keywords in bold sometimes have a number that we need to not include in the link (e.g. Gladiator 1)
        game_text = re.sub(r'<b>([^<\d]+)( \d)?</b>', r'[[\1]]\2', game_text)

        # Cost circle
        game_text = re.sub(r'\[\((\d)\)\]', r'[[File:pay\1.png|14px]]', game_text)
        game_text = re.sub(r'\[\(10\)\]', r'[[File:pay1.png|14px]][[File:pay0.png|14px]]', game_text)

        # Charge cost square
        game_text = re.sub(r'\[(\d)\]', r'<span style="color:Black; background:White">\1 </span>', game_text)

        # Escalation
        game_text = re.sub(r'\bESC:(\d)\b', r'<b>\1</b>', game_text)

        # Green bolded numbers
        game_text = re.sub(r'#VAR\d_(\d)#', r'<span style="color:#0f0; font-weight: bold;">\1</span>', game_text)

        # Resources
        game_text = re.sub(r'\[L(\d)\]\[R(\d)\]', r'<\1/\2>', game_text)

        return game_text
