import pandas as pd
import json
import random
import os
import re


####################
######  Type  ######
####################

# Load the excel into python
type_effectiveness_df = pd.read_excel("project/raw_data/pokemon_type_effectiveness_chart.xlsx")

# Extract Type ID and Type Name
type_id_dict = type_effectiveness_df.set_index('Type')['ID'].to_dict()

# Helper function to convert type names to type IDs using the mapping
def type_names_to_ids(type_names):

    # If the cell is NaN (empty), return an empty list
    if pd.isnull(type_names) or type_names == '':
        return []
    # Otherwise, split the string by commas, strip whitespace, and convert to IDs
    return [type_id_dict[type_name.strip()] for type_name in type_names.split(',')]

# Apply the conversion to each column that contains type names
for column in ['Super Effective Against (2x)', 'Not Very Effective Against (0.5x)', 'No Effect (0x)', 'Weakness to']:
    type_effectiveness_df[column] = type_effectiveness_df[column].apply(type_names_to_ids)

# Rename the columns to match the desired JSON keys
type_effectiveness_df.rename(columns={
    'ID': 'Type_ID',
    'Type': 'Type_name',
    'Super Effective Against (2x)': 'Super_effective_against',
    'Not Very Effective Against (0.5x)': 'Not_effective_against',
    'No Effect (0x)': 'No_effect',
    'Weakness to': 'Weakness'
}, inplace=True)

# Convert to JSON format
json_ready_df = type_effectiveness_df[['Type_ID', 'Type_name', 'Super_effective_against', 'Not_effective_against', 'No_effect', 'Weakness']]
json_result = json_ready_df.to_json(orient='records', force_ascii=False)

# json_result is a string, parse it back to a json object
json_object = json.loads(json_result)

# Write the JSON data to the Type.json file
with open('project/demo/data/Type.json', 'w', encoding='utf-8') as json_file:
    json.dump(json_object, json_file, indent=4)


#####################
###### Trainer ######
#####################

# Load data
trainer_df = pd.read_csv("project/raw_data/pokemon_trainers.csv")

# Define possible regions
regions = ["Kanto", "Johto", "Hoenn", "Sinnoh", "Unova", "Kalos", "Alola", "Galar", "Hisui", "Paldea"]

# Create data
json_data = []

for index, row in trainer_df.iterrows():
    trainer = {
        "Trainer_ID": row["ID"],
        "Trainer_name": row["Trainer"],
        "Pokemon_team": row["Team used?"],
        "Badges_obtained": random.randint(0, 5),  # Randomly insert 1-5 Badges
        "Region": random.sample(regions, random.randint(1, 5))  # Randomly insert 1-5 regions
    }
    json_data.append(trainer)

# Write the JSON data to the Trainer.json file
with open("project/demo/data/Trainer.json", "w", encoding='utf-8') as json_file:
    json.dump(json_data, json_file, ensure_ascii=False, indent=4)


#######################
######  Pokemon  ######
#######################

# Load the csv into python
pokemon_df = pd.read_csv("project/raw_data/pokemon_height_weight.csv")

# Get Type ID and Name data
type_effectiveness_df = pd.read_excel("project/raw_data/pokemon_type_effectiveness_chart.xlsx")
type_name_to_id = dict(zip(type_effectiveness_df['Type'], type_effectiveness_df['ID']))

# Function to convert type names to type IDs
def convert_type_names_to_ids(type_names_str):
    # Convert string to list
    type_names = json.loads(type_names_str.replace("'", '"'))
    # Convert type names to IDs
    return [type_name_to_id[type_name] for type_name in type_names]

# Apply the function to the "Type" column
pokemon_df['Type'] = pokemon_df['Type'].apply(convert_type_names_to_ids)

# Define possible regions
regions = ["Kanto", "Johto", "Hoenn", "Sinnoh", "Unova", "Kalos", "Alola", "Galar", "Hisui", "Paldea"]

# Create JSON
json_data = []

for _, row in pokemon_df.iterrows():

    # Randomly apply Region (1-5)
    selected_regions = random.sample(regions, random.randint(1, 5))

    # Randomly select 1-6 Trainer_IDs
    selected_trainer_ids = random.sample(range(1, 270), random.randint(1, 6))

    pokemon = {
        "Pokemon_ID": row["Number"],
        "Pokemon_Name": row["Name"],
        "Height": row["Height(m)"],
        "Weight": row["Weight(lbs)"],
        "BMI": row["BMI"],
        "Type_ID": row["Type"],
        "Trainer_ID": selected_trainer_ids,
        "Region": selected_regions,
        "img_link": row["Image Link"]
    }
    json_data.append(pokemon)

# Write the JSON data to the Pokemon.json file
with open("project/demo/data/Pokemon.json", "w") as json_file:
    json.dump(json_data, json_file, ensure_ascii=False, indent=4)


#####################
######  Card  #######
#####################

# First use Git Bash to clone the data to your local directory
# git clone https://github.com/PokemonTCG/pokemon-tcg-data.git
# cd pokemon-tcg-data/cards/en
# ls #make sure the json are there

path = "project/raw_data/pokemon-tcg-data/cards/en" # Update the path based on your local directory if you need

# Load type data
type_df = pd.read_excel("project/raw_data/pokemon_type_effectiveness_chart.xlsx")
type_name_to_id = dict(zip(type_df['Type'], type_df['ID']))

# Function to convert type names to Type_IDs
def convert_types_to_ids(types):
    return [4 if type_name == "Lightning" else type_name_to_id[type_name] for type_name in types if type_name in type_name_to_id or type_name == "Lightning"]

# Create Card data
cards = []
card_id_counter = 1
attack_id_counter = 1

for filename in os.listdir(path):

    if filename.endswith('.json'):
        with open(os.path.join(path, filename), 'r', encoding='utf-8') as file:
            card_data_list = json.load(file)

            for card_data in card_data_list:
                if card_data.get("supertype") == "Pokémon":
                    # Get data for weaknesses and resistances
                    weaknesses = [
                        {'Type_ID': convert_types_to_ids([w['type']])[0], 'Value': w['value']}
                        for w in card_data.get('weaknesses', []) if convert_types_to_ids([w['type']])]
                    resistances = [
                        {'Type_ID': convert_types_to_ids([r['type']])[0], 'Value': r['value']}
                        for r in card_data.get('resistances', []) if convert_types_to_ids([r['type']])]

                    # Extract Card information with embedded Attack information
                    card = {
                        "Card_ID": card_id_counter,
                        "ID": card_data["id"],
                        "Pokemon_ID": card_data.get("nationalPokedexNumbers", []),
                        "HP": card_data.get("hp", ""),
                        "Type_ID": convert_types_to_ids(card_data.get("types", [])),
                        "Attack": [{
                            "Attack_ID": attack_id_counter + i,
                            "Attack_name": attack["name"],
                            "Type_ID": convert_types_to_ids(attack["cost"]),
                            "Damage": attack.get("damage", ""),
                            "Description": attack.get("text", "")
                        } for i, attack in enumerate(card_data.get("attacks", []))],
                        "Illustrator": card_data.get("artist", ""),
                        "Img_path": card_data.get("images", {}).get("small", ""),
                        "Weakness": weaknesses,
                        "Resistance": resistances,
                        "Retreat_cost": card_data.get("convertedRetreatCost", 0)
                    }
                    # Append the Card to the list
                    cards.append(card)
                    card_id_counter += 1
                    attack_id_counter += len(card_data.get("attacks", []))

# Write the Card data to Card.json file
with open("../Card.json", "w", encoding='utf-8') as json_file:
    json.dump(cards, json_file, ensure_ascii=False, indent=4)


######################
######  Attack  ######
######################

# Load Card data
with open("../Card.json", 'r', encoding='utf-8') as file:
    card_data = json.load(file)

# Extract all attacks from Card data to create Attack.json
all_attacks = []
for card in card_data:
    for attack in card["Attack"]:
        if attack not in all_attacks:  # Avoid duplicates
            all_attacks.append(attack)

# Write the Attack data to Attack.json file
with open("project/demo/data/Attack.json", "w", encoding='utf-8') as json_file:
    json.dump(all_attacks, json_file, ensure_ascii=False, indent=4)


############################
######  Pokemon_Card  ######
############################
# Write the Card data to Card.json file
with open("../Card.json", "w", encoding='utf-8') as json_file:
    json.dump(cards, json_file, ensure_ascii=False, indent=4)

# Modify Card data to create Pokemon_Card.json
for card in cards:
    card["Attack_ID"] = [attack["Attack_ID"] for attack in card["Attack"]]
    del card["Attack"]  # Remove the Attack field

# Write the modified Card data to Pokemon_Card.json file
with open("project/demo/data/Pokemon_Card.json", "w", encoding='utf-8') as json_file:
    json.dump(cards, json_file, ensure_ascii=False, indent=4)


#############################################################
##### Some Codes for understanding and designing our UI #####
#############################################################

# Check for Unique Values

# Pokemon_Card -- Weakness/Resistance
with open('../Pokemon_Card.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
weakness_values = set()
for record in data:
    for weakness in record.get('Resistance', []):
        weakness_values.add(weakness.get('Value'))
print(weakness_values)


# Attack -- Damage
with open('../Attack.json', 'r', encoding='utf-8') as f:
    attack_data = json.load(f)
damage_values = set()
for attack in attack_data:
    damage_values.add(attack.get('Damage'))
print(damage_values)


# Check how many unique Illustrators are there
with open('../Pokemon_Card.json', 'r') as file:
    pokemon_cards = json.load(file)

illustrators = [card['Illustrator'] for card in pokemon_cards]
unique_illustrators = set(illustrators)
num_unique_illustrators = len(unique_illustrators)

print(f"There are in total of {num_unique_illustrators} different Illustrators.")
print("The unique Illustrators are：")
for illustrator in unique_illustrators:
    print(illustrator)


# Check the Range for HP and Retreat_Cost
with open('../Pokemon_Card.json', 'r') as file:
    pokemon_cards = json.load(file)

hp_values = [int(card['HP']) for card in pokemon_cards if card['HP'].isdigit()]
retreat_cost_values = [card['Retreat_cost'] for card in pokemon_cards]

hp_range = (min(hp_values), max(hp_values))
retreat_cost_range = (min(retreat_cost_values), max(retreat_cost_values))

print(f"The Range for HP is {hp_range}")
print(f"The Range for Retreat Cost is {retreat_cost_range}")


# Check for HP data type and unique values
with open('../Pokemon_Card.json', 'r') as file:
    card_data = json.load(file)

unique_hp_values = set()

for card in card_data:
    hp = card.get('HP')
    if hp is not None:
        unique_hp_values.add(hp)

hp_data_type = type(card_data[0]['HP']) if card_data else None
print(f"HP Data Type: {hp_data_type}")
print(f"Unique HP Values: {unique_hp_values}")


# Verifying Unique Pokemon Card Types through its raw json files
def get_unique_types(directory):
    unique_types = set()
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            file_path = os.path.join(directory, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                for card in data:
                    if 'types' in card:
                        unique_types.update(card['types'])
    return unique_types

directory_path = "project/raw_data/pokemon-tcg-data/cards/en"
unique_types = get_unique_types(directory_path)
print("Unique Types:")
print(unique_types)


# Verifying Unique Pokemon Types
df = pd.read_csv('project/raw_data/pokemon_height_weight.csv')
unique_types = set()
for types in df['Type']:
    types_list = eval(types)
    unique_types.update(types_list)
print(unique_types)


# Check Unique Pokemon_Card Types in Pokemon_Card.json
with open('../Type.json', 'r') as file:
    type_data = json.load(file)

type_id_to_name = {type_entry['Type_ID']: type_entry['Type_name'] for type_entry in type_data}

with open('../Pokemon_Card.json', 'r') as file:
    card_data = json.load(file)

unique_type_names = set()

for card in card_data:
    for type_id in card['Type_ID']:
        type_name = type_id_to_name.get(type_id)
        if type_name:
            unique_type_names.add(type_name)
print(unique_type_names)


# Check If exists Dual-Type Pokemon Cards
with open('../Pokemon_Card.json', 'r') as file:
    json_data = json.load(file)

def filter_cards_with_multiple_types(json_data):

    if isinstance(json_data, str):
        data = json.loads(json_data)
    else:
        data = json_data

    cards_with_multiple_types = [
        {
            "Card_ID": card["Card_ID"],
            "Type_ID": card["Type_ID"],
            "Img_path": card["Img_path"]
        }
        for card in data if len(card['Type_ID']) > 1]

    return cards_with_multiple_types

result = filter_cards_with_multiple_types(json_data)
print(json.dumps(result, indent=4))


# Check the field types for each JSON
import json

# List of paths to your JSON files
json_files = [
    '../Attack.json',
    '../Pokemon.json',
    '../Pokemon_Card.json',
    '../Trainer.json',
    '../Type.json'
]

def print_field_types(file_path):
    try:
        with open(file_path, 'r') as file:
            card_data = json.load(file)

        if isinstance(card_data, list) and len(card_data) > 0:
            first_item = card_data[0]
            field_types = {field: type(value).__name__ for field, value in first_item.items()}
            print(f"Field Types for {file_path}:")
            for field, type_name in field_types.items():
                print(f"  {field}: {type_name}")
            print()
        else:
            print(f"No data or unexpected data format in {file_path}")
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except json.JSONDecodeError:
        print(f"Error decoding JSON in {file_path}")

for json_file in json_files:
    print_field_types(json_file)
