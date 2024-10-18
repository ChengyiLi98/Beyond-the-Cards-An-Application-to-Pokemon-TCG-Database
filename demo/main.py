import streamlit as st
from pymongo import MongoClient

from streamlit.errors import StreamlitAPIException

from project import search_by_name, filter_by_type, search_pokemon_info, advanced_search, handle_login, upsert_data  # import function defined in project.py
import json
from project import database_manager_username,database_manager_password

def display_pokemon_info(pokemon_name):
    pokemon_info_list= search_pokemon_info(pokemon_name)
    if pokemon_info_list:
        for pokemon_info in pokemon_info_list:
            with st.expander(f"Pokémon: {pokemon_info['Pokemon_Name']}"):
                print("Type_Details:", pokemon_info.get('Type_Details', 'Not available'))
                cols = st.columns([1, 2])
                if show_pokemon_image:
                    with cols[0]:
                        st.image(pokemon_info['img_link'], width=200)
                else:
                    cols = st.columns([1])
                with cols[-1]:
                    if show_height: st.write(f"Height: {pokemon_info['Height']}m")
                    if show_weight: st.write(f"Weight: {pokemon_info['Weight']}kg")
                    if show_bmi: st.write(f"BMI: {pokemon_info['BMI']}")
                    if show_pokemon_type:
                        type_text = ', '.join(pokemon_info.get('Type', ['Unknown']))
                        st.write(f"Type: {type_text}")

                    if show_trainer:
                        trainer_text = ', '.join(pokemon_info['Trainer'])
                        st.write(f"Trainer: {trainer_text}")

                    if show_regions:
                        region_text = ', '.join(r for r in pokemon_info['Region'])
                        st.write(f"Region: {region_text}")

                    if 'Type_Details' in pokemon_info and any(pokemon_info['Type_Details']):
                        for type_detail in pokemon_info['Type_Details']:
                            if type_detail:
                                if show_super_effective and 'Super_effective_against' in type_detail:
                                    super_effective_text = ', '.join(type_detail['Super_effective_against'])
                                    st.write(f"Super Effective Against: {super_effective_text}")

                                if show_not_effective and 'Not_effective_against' in type_detail:
                                    not_effective_text = ', '.join(type_detail['Not_effective_against'])
                                    st.write(f"Not Effective Against: {not_effective_text}")

                                if show_no_effect and 'No_effect' in type_detail:
                                    no_effect_text = ', '.join(type_detail['No_effect'])
                                    st.write(f"No Effect Against: {no_effect_text}")

                                if show_pokemon_weakness and 'Weakness' in type_detail:
                                    weakness_text = ', '.join(type_detail['Weakness'])
                                    st.write(f"Weakness: {weakness_text}")
    else:
        st.write("No matching Pokémon found.")

def initialize_paginator_state(key):
    ''' Initializes the state for a paginator based on the provided key. '''
    if key not in st.session_state:
        st.session_state[key] = 0
def display_pokemon_cards(pokemon_name, cards):
    paginator_key = f"{pokemon_name}_paginator"
    initialize_paginator_state(paginator_key)  # Initialize paginator state key
    with st.expander(f"Cards for Pokémon: {pokemon_name}"):
        if cards:
            # Paginator setup
            page_cards, page_num = paginator(paginator_key, cards, items_per_page=10)

            # Check if the current page has any cards to display
            if page_cards:
                # Create columns based on whether an image should be shown or not
                cols = st.columns([1, 2]) if any('Img_path' in card for card in page_cards) else st.columns([1])

                for card in page_cards:
                    with st.container():
                        cols = st.columns([1, 2])
                        if show_image and 'Img_path' in card:
                            with cols[0]:
                                st.image(card['Img_path'], width=200)
                        else:
                            cols = st.columns([1])
                        with cols[-1]:
                            if show_card_id:
                                st.write(f"Series_ID: {card['ID']}")
                            if show_hp:
                                st.write(f"HP: {card['HP']}")
                            if show_type:
                                st.write(f"Type: {', '.join(card['Type'])}")
                            if show_attack:
                                st.write(f"Attack: {', '.join(card['Attack'])}")
                            if show_weakness:
                                weakness_text = ', '.join([f"{w['Type']} {w['Value']}" for w in card['Weakness']])
                                st.write(f"Weakness: {weakness_text}")
                            if show_resistance:
                                resistance_text = ', '.join([f"{r['Type']} {r['Value']}" for r in card['Resistance']])
                                st.write(f"Resistance: {resistance_text}")
                            if show_illustrator:
                                st.write(f"Illustrator: {card['Illustrator']}")
                            if show_retreat_cost:
                                st.write(f"Retreat Cost: {card['Retreat_cost']}")
                            st.write('---------------------------')
            else:
                st.write("No cards found for this Pokémon.")

            # additional Paginator buttons
            col1, col2 = st.columns([1, 1])
            with col1:
                if page_num > 0:
                    # Create another 'Previous' button that does the same thing
                    prev_button = st.button("Previous", key=f"{pokemon_name}_prev2")
                    if prev_button:
                        # The same function called by the paginator 'Previous' button
                        st.session_state[f"{pokemon_name}_paginator"] -= 1
                        st.experimental_rerun()
            with col2:
                if page_num < (len(cards) - 1) // 10:
                    # Create another 'Next' button that does the same thing
                    next_button = st.button("Next", key=f"{pokemon_name}_{page_num}_next2")
                    if next_button:
                        # The same function called by the paginator 'Next' button
                        st.session_state[f"{pokemon_name}_paginator"] += 1
                        st.experimental_rerun()

        else:
            st.write("No cards found for this Pokémon.")

#search by name
def display_pokemon_and_card_info(pokemon_name):
    '''Display information about a Pokémon and its associated cards.'''
    pokemon_info_list = search_pokemon_info(pokemon_name)
    if pokemon_info_list:
        for pokemon_info in pokemon_info_list:
            with st.expander(f"Pokémon: {pokemon_info['Pokemon_Name']}"):

                cols = st.columns([1, 2])
                if show_pokemon_image:
                    with cols[0]:
                        st.image(pokemon_info['img_link'], width=200)
                else:
                    cols = st.columns([1])
                with cols[-1]:
                    if show_height: st.write(f"Height: {pokemon_info['Height']}m")
                    if show_weight: st.write(f"Weight: {pokemon_info['Weight']}kg")
                    if show_bmi: st.write(f"BMI: {pokemon_info['BMI']}")
                    if show_pokemon_type:
                        type_text = ', '.join(pokemon_info.get('Type', ['Unknown']))
                        st.write(f"Type: {type_text}")

                    if show_trainer:
                        trainer_text = ', '.join(pokemon_info.get('Trainer', ['Unknown']))
                        st.write(f"Trainer: {trainer_text}")

                    if show_regions:
                        region_text = ', '.join(r for r in pokemon_info['Region'])
                        st.write(f"Region: {region_text}")
                    if 'Type_Details' in pokemon_info and any(pokemon_info['Type_Details']):
                        for type_detail in pokemon_info['Type_Details']:
                            if type_detail:
                                if show_super_effective and 'Super_effective_against' in type_detail:
                                    super_effective_text = ', '.join(type_detail['Super_effective_against'])
                                    st.write(f"Super Effective Against: {super_effective_text}")

                                if show_not_effective and 'Not_effective_against' in type_detail:
                                    not_effective_text = ', '.join(type_detail['Not_effective_against'])
                                    st.write(f"Not Effective Against: {not_effective_text}")

                                if show_no_effect and 'No_effect' in type_detail:
                                    no_effect_text = ', '.join(type_detail['No_effect'])
                                    st.write(f"No Effect Against: {no_effect_text}")

                                if show_pokemon_weakness and 'Weakness' in type_detail:
                                    weakness_text = ', '.join(type_detail['Weakness'])
                                    st.write(f"Weakness: {weakness_text}")

            search_results = search_by_name(pokemon_info['Pokemon_Name'])
            if search_results:
                for result in search_results:
                    pokemon_info = result.get('Pokemon', {})
                    cards = result.get('Cards', [])
                    pokemon_name = pokemon_info.get('Pokemon_Name', [])
                    try:
                        display_pokemon_cards(pokemon_name, cards)
                    except StreamlitAPIException as e:
                        continue  # Skip to the next set of cards if meet errors
            else:
                st.write('No info about this Pokemon')
    else:
        # If no Pokémon is found at all
        st.write(f"No Pokémon found with the name '{pokemon_name}'.")

def display_filtered_pokemon_cards(selected_types):
    if len(selected_types) > 2:
        st.error('Please select no more than two types.')
    elif selected_types:
        filtered_results = filter_by_type(selected_types)
        if filtered_results:
            for result in filtered_results:
                # Display Pokémon cards using the display_pokemon_cards function
                pokemon_name = result['Pokemon']['Pokemon_Name']
                display_pokemon_info(pokemon_name)
                cards = result.get('Cards', [])
                display_pokemon_cards(pokemon_name, cards)
        else:
            st.write("No matching Pokémon or cards found.")
    else:
        st.write("Please select at least one type.")

def display_advance_search():
    # 'Pokémon card types' are different from 'Pokémon types'
    pokemon_card_types = [
        'Grass', 'Fire', 'Psychic', 'Fairy', 'Fighting', 'Dragon', 'Colorless', 'Water', 'Electric', 'Metal', 'Darkness'
    ]
    selected_types = st.multiselect('Choose An Card Type', pokemon_card_types)
    selected_illustrator = st.text_input('Enter Illustrator Name to Search:').strip()

    hp_range = st.slider('Select HP Range:', 0, 350, (0, 350)) # Slider for HP Range
    retreat_cost_range = st.slider('Select Retreat Cost Range:', 0, 5, (0, 5)) #  Slider for Retreat Cost Range

    if st.button('Search'):
        results = advanced_search(
            selected_types=selected_types,
            selected_illustrators=[selected_illustrator] if selected_illustrator else None,
            hp_range=hp_range,
            retreat_cost_range=retreat_cost_range
        )
        if results:
            # Organize Pokémon cards with the same Pokémon name under the same expander
            grouped_results = {} # dict
            for card in results:
                pokemon_name = card['Pokemon_Name'][0]
                if pokemon_name not in grouped_results:
                    grouped_results[pokemon_name] = []
                grouped_results[pokemon_name].append(card)

            # Display results under expanders grouped by Pokémon name
            for pokemon_name, cards in grouped_results.items():
                with st.expander(f"Pokémon: {pokemon_name}"):
                    for card in cards:
                        cols = st.columns([1, 2]) if 'Img_path' in card else st.columns(1)
                        if show_image and 'Img_path' in card:
                            with cols[0]:
                                st.image(card['Img_path'], width=200)
                        with cols[-1]:
                            if show_card_id:
                                st.write(f"Series_ID: {card['ID']}")
                            if show_hp:
                                st.write(f"HP: {card['HP']}")
                            if show_type:
                                st.write(f"Type: {', '.join(card['Type'])}")
                            if show_attack:
                                st.write(f"Attack: {', '.join(card['Attack'])}")
                            if show_weakness:
                                weakness_text = ', '.join([f"{w['Type']} {w['Value']}" for w in card['Weakness']])
                                st.write(f"Weakness: {weakness_text}")
                            if show_resistance:
                                resistance_text = ', '.join([f"{r['Type']} {r['Value']}" for r in card['Resistance']])
                                st.write(f"Resistance: {resistance_text}")
                            if show_illustrator:
                                st.write(f"Illustrator: {card['Illustrator']}")
                            if show_retreat_cost:
                                st.write(f"Retreat Cost: {card['Retreat_cost']}")
        else:
            st.write("No results found.")

# for Pokemon info
pokemon_types = [
        'Normal', 'Fire', 'Water', 'Electric', 'Grass', 'Ice', 'Fighting',
        'Poison', 'Ground', 'Flying', 'Psychic', 'Bug', 'Rock',
        'Ghost', 'Dragon', 'Darkness', 'Metal', 'Fairy'
    ]

# A dictionary showing the names and types of fields in each table, with input limitations for those fields.
collection_fields = {
    "Pokemon": {
        "Pokemon_ID": "number",
        "Pokemon_Name": "text",
        "Height": "float_number",  # 0-20
        "Weight": "float_number",  # 0-2300
        "BMI": "float_number",  # 0-1000
        "Type_ID": "list_number",  # 1-19
        "Trainer_ID": "list_number",
        "Region": "list_text",   # Only Region = Kanto, Johto, Hoenn, Sinnoh, Unova, Kalos, Alola, Galar, Hisui, Paldea
        "img_link": "text"
    },
    "Pokemon_Card": {
        "Card_ID": "number",
        "ID": "text",
        "Pokemon_ID": "list_number",
        "HP": "number",  # 0-350
        "Type_ID": "list_number",  # 1-19
        "Illustrator": "text",
        "Img_path": "text",
        "Weakness": "json",  # within each, Type_ID 1-19, Value 0-100 (add limitations in input_complex_list）
        "Resistance": "json",  # within each, Type_ID 1-19, Value 0-100 (add limitations in input_complex_list）
        "Retreat_cost": "number",  # 0-5
        "Attack_ID": "list_number"
    },
    "Trainer": {
        "Trainer_ID": "number",
        "Trainer_name": "text",
        "Pokemon_team": "text",
        "Badges_obtained": "number",
        "Region": "list_text"  # has to match str in Region
    },
    "Type": {
        "Type_ID": "number",  # 1-19
        "Type_name": "text",  # has to match str in pokemon_type
        "Super_effective_against": "list_number",  # list of number each has to be 1-19
        "Not_effective_against": "list_number",  # list of number each has to be 1-19
        "No_effect": "list_number",  # list of number each has to be 1-19
        "Weakness": "list_number"  # list of number each has to be 1-19
    },
    "Attack": {
        "Attack_ID": "number",
        "Attack_name": "text",
        "Type_ID": "list_number",  # 1-19 #not single number
        "Damage": "number",  # 0-350
        "Description": "text"
    }
}

# Adding Input Limitations
def validate_data(inputs, collection_name):
    error_messages = []

    # General Limit conditions
    number_fields = {
        "Height": (0.0, 20.0),
        "Weight": (0.0, 2300.0),
        "BMI": (0.0, 1000.0),
        "HP": (0, 350),
        "Retreat_cost": (0, 5),
        "Damage": (0, 350)
    }

    # Verifying min/max for numerical fields
    for field, (min_val, max_val) in number_fields.items():
        if field in inputs:
            if not (min_val <= inputs[field] <= max_val):
                error_messages.append(f"{field} must be between {min_val} and {max_val}.")

    # Verifying count of Types
    if collection_name == "Pokemon":
        if "Type_ID" in inputs and inputs["Type_ID"]: # check if type_id is provided and not empty
            if not (1 <= len(inputs["Type_ID"]) <= 19):
                error_messages.append("Type_ID must have at least one entry and less than or equal to 19 entries.")

    # Verifying Type_ID has to be Integer between 1-19
    type_id_fields = ["Type_ID", "Super_effective_against", "Not_effective_against", "No_effect"]
    for field in type_id_fields:
        if field in inputs:
            if isinstance(inputs[field], list):
                for type_id in inputs[field]:
                    if not isinstance(type_id, int) or not (1 <= type_id <= 19):
                        error_messages.append(f"Each {field} must be an integer between 1 and 19.")
            else:
                if not isinstance(inputs[field], int) or not (1 <= inputs[field] <= 19):
                    error_messages.append(f"{field} must be an integer between 1 and 19.")

    # Verifying Type_name matches those within pokemon_types or is empty
    if "Type_name" in inputs:
        if inputs["Type_name"] and inputs["Type_name"] not in pokemon_types:
            error_messages.append(
                f"Type_name must match a name in pokemon_types: {', '.join(pokemon_types)} or be empty.")

    # Weakness + Resistance
    if collection_name == "Pokemon_Card":
        for entry in inputs.get("Weakness", []) + inputs.get("Resistance", []):
            if not (1 <= entry["Type_ID"] <= 19):
                error_messages.append("Each Type_ID in Weakness and Resistance must be between 1 and 19.")
            # no restrict for value here
    # Region
    valid_regions = ['Kanto', 'Johto', 'Hoenn', 'Sinnoh', 'Unova', 'Kalos', 'Alola', 'Galar', 'Hisui', 'Paldea']
    if collection_name in ["Pokemon", "Trainer"]:
        if isinstance(inputs.get("Region"), list):
            for region in inputs["Region"]:
                if region not in valid_regions:
                    error_messages.append(f"Region must be one of the specified regions: {', '.join(valid_regions)}.")
        else:
            if inputs.get("Region") not in valid_regions:
                error_messages.append(f"Region must be one of the specified regions: {', '.join(valid_regions)}.")

    return error_messages

def get_input(field_type):
    '''Return the corresponding input component function based on the field type.'''
    if field_type == "text":
        return st.text_input
    elif field_type == "number":
        return lambda label, value=0: st.number_input(label, value=value, format="%d")
    elif field_type == "float_number":
        return lambda label, value=0.0: st.number_input(label, value=value, step = 0.1)
    elif field_type == "list_text":
        return lambda label, default='': [x.strip() for x in st.text_input(label, default).split(',') if x.strip()]
    elif field_type == "list_number":
        def handle_list_number_input(label, default=''):
            input_str = st.text_input(label, default)
            try:
                return [int(x.strip()) for x in input_str.split(',') if x.strip()]
            except ValueError:
                st.error("Invalid input. Please enter a comma-separated list of integers.")
                return []
        return handle_list_number_input

def input_complex_list(label):
    st.write(f"Enter details for {label}:")
    # Ask the user for the number of entries they want to input
    count = st.number_input(f"Number of entries for {label}", min_value=0, max_value=3, step=1, format="%d")
    entries = []
    for i in range(count):
        with st.container():
            type_id = st.number_input(f"Type_ID for {label} #{i + 1}", min_value=1, max_value=19, step=1, format="%d")
            value = st.text_input(f"Value for {label} #{i + 1}, remember to add +/-/x")
            entries.append({"Type_ID": type_id, "Value": value})  # Add the Type_ID and Value to the entries list as a dictionary
    return entries

def db_entry():
    st.write('')
    json_data = None

    # Select the collection to modify
    collection_name = st.selectbox("Choose the collection to modify:", tuple(collection_fields.keys()))

    # Dynamically create input fields based on the collection selected
    inputs = {}
    for field, f_type in collection_fields[collection_name].items():
        if field in ["Weakness", "Resistance"] and collection_name == "Pokemon_Card":
            inputs[field] = input_complex_list(field)
        elif field == "img_link" or field == "img_path":
            # For image fields, if leave blank then use a default picture
            url = st.text_input(f"Enter {field}:")
            if url.strip() == "":
                url = "https://images.pokemontcg.io"
            inputs[field] = url
        else:
            input_function = get_input(f_type)
            inputs[field] = input_function(f"Enter {field}:")

    if st.button("Create JSON"):
        # Validate inputs
        error_messages = validate_data(inputs, collection_name)
        if error_messages:
            # If there are errors, display them and stop further processing
            for error in error_messages:
                st.error(error)
        else:
            # Convert specified fields to strings for JSON output
            string_fields = ["HP", "Damage"]
            for field in string_fields:
                if field in inputs:
                    if isinstance(inputs[field], list):
                        inputs[field] = [str(item) for item in inputs[field]]
                    else:
                        inputs[field] = str(inputs[field])

            # Convert inputs and show them as JSON
            try:
                json_data = json.dumps(inputs, indent=4)

                client = MongoClient(
                    f'mongodb://{database_manager_username}:{database_manager_password}@localhost:27017/')
                databases = [client['db1'], client['db2'], client['db3'], client['db4'], client['db5']]
                upsert_data(collection_name,json_data, databases)
                client.close()
                st.json(json_data)
                # Create a download button for the json data
                st.download_button(
                    label="Download JSON",
                    data=json_data,
                    file_name=f"{collection_name.lower()}_data.json",
                    mime='application/json'
                )
            except Exception as e:
                st.error(f"Error creating JSON: {e}")

def delete_entry():
    global database_manager_username, database_manager_password

    # Connection to MongoDB
    client = MongoClient(f'mongodb://{database_manager_username}:{database_manager_password}@localhost:27017/')
    databases = [client['db1'], client['db2'], client['db3'], client['db4'], client['db5']]

    # Dictionary to map collection names to their unique identifiers
    unique_identifiers = {
        'Pokemon_Card': 'Card_ID', 'Pokemon': 'Pokemon_ID',
        'Attack': 'Attack_ID', 'Type': 'Type_ID', 'Trainer': 'Trainer_ID'
    }

    # Select the collection type to delete from
    collection_type = st.selectbox("Select the collection type to delete from:", list(unique_identifiers.keys()))
    unique_id = st.number_input(f'Input the {unique_identifiers[collection_type]} to search:', min_value=1, format='%d')

    if st.button("Search for Entry"):
        if unique_id > 0:
            entry_found = None
            target_db = None
            for db in databases:
                # find info of this entry use id
                entry_found = db[collection_type].find_one({unique_identifiers[collection_type]: unique_id})
                if entry_found:
                    target_db = db
                    break

            if entry_found:
                # Store entry info in session state, for deletion.
                st.session_state['entry_found'] = entry_found
                st.session_state['target_db'] = target_db

                # Display entry details and image if applicable
                st.write(f"Entry Found in {collection_type}, please review before deleting:")
                if collection_type == 'Pokemon_Card' and 'Img_path' in entry_found:
                    st.image(entry_found['Img_path'], width=200, caption=f"ID: {entry_found['ID']}")
                elif collection_type == 'Pokemon' and 'img_link' in entry_found:
                    st.image(entry_found['img_link'], width=200,
                             caption=f"Name: {entry_found['Pokemon_Name']}")
                elif collection_type == 'Attack':
                    st.write(f"Attack Name: {entry_found['Attack_name']}")
                elif collection_type == 'Type':
                    st.write(f"Type Name: {entry_found['Type_name']}")
                elif collection_type == 'Trainer':
                    st.write(f"Trainer Name: {entry_found['Trainer_name']}")
            else:
                st.error("No entry found with the given ID.")
        else:
            st.warning("Please enter a valid ID to search.")

    # confirm deletion
    if 'entry_found' in st.session_state and st.button("Delete Entry"):
        # Delete a document based on primary key, which is unique_identifiers[collection_type] found in the entry_found document stored in the session state,
        # within the selected database (st.session_state['target_db']) and collection (collection_type).
        result = st.session_state['target_db'][collection_type].delete_one({unique_identifiers[collection_type]: st.session_state['entry_found'][unique_identifiers[collection_type]]})
        if result.deleted_count > 0:
            st.success(f"Entry has been successfully deleted from {collection_type}.")
            # Clear session state after deletion
            del st.session_state['entry_found']
            del st.session_state['target_db']
        else:
            st.error("Failed to delete the entry.")

FILE_PATH = "comments.txt"
def load_comments():
    """Load existing comments from comments.txt."""
    try:
        with open(FILE_PATH, "r") as file:
            comments = file.readlines()
        return comments
    except FileNotFoundError:
        return []

def save_comment(comment):
    """Append a new comment to the file."""
    with open(FILE_PATH, "a") as file:
        file.write(comment + "\n")

def comment_section():
    # User Comments Section
    # Display existing comments
    comments = load_comments()
    if comments:
        for comment in comments:
            st.text_area("Comment", value=comment.strip(), height=75, disabled=True)

    # User inputs a new comment
    new_comment = st.text_area("Write your comment")
    if st.button("Submit Comment"):
        save_comment(new_comment)
        st.success("Comment submitted successfully!")
        st.experimental_rerun()  # Rerun the app to update the comments list

def paginator(label, items, items_per_page=10, unique_identifier=None):
    """Split items into pages and returns the items for the current page.
    The unique_identifier ensures that session state and widget keys are unique per paginator instance.
    """

    # Generate a unique key for the paginator based on provided label and unique identifier
    unique_key = f"{label}_{unique_identifier}" if unique_identifier else label

    # Initialize the page number in session state if not already present
    if unique_key not in st.session_state:
        st.session_state[unique_key] = 0

    # Calculate the total number of pages
    num_items = len(items)
    num_pages = (num_items // items_per_page) + (num_items % items_per_page > 0)

    # Define the action for the next page button
    def next_page():
        if st.session_state[unique_key] + 1 < num_pages:
            st.session_state[unique_key] += 1

    # Define the action for the previous page button
    def prev_page():
        if st.session_state[unique_key] > 0:
            st.session_state[unique_key] -= 1

    # Create the previous and next buttons with dynamic visibility
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.session_state[unique_key] > 0:
            prev_button = st.button("Previous", on_click=prev_page, key=f"{unique_key}_prev")

    with col2:
        # Only show the "Next" button if there are more items to show
        if st.session_state[unique_key] < num_pages - 1:
            next_button = st.button("Next", on_click=next_page, key=f"{unique_key}_next")

    # Determine the range of items to display on the current page
    start_index = st.session_state[unique_key] * items_per_page
    end_index = start_index + items_per_page
    page_items = items[start_index:end_index]

    # Return the items to display on the current page
    return page_items, st.session_state[unique_key]


if __name__ == "__main__":

    st.image("decoration picture/art/title2.png")
    st.sidebar.title("DSCI 551")
    st.sidebar.header("Chengyi Li, Lewei Lin, Zhanyang Sun")
    st.sidebar.image('.\decoration picture\pikachu.jpg')
    handle_login()

    if st.session_state.logged_in:
        if st.session_state.user_role == 'admin':
            st.write('')
            st.write('')
            st.write('')
            st.image("decoration picture/art/data_entry.png", width= 700)
            db_entry()
            st.write('')
            st.image("decoration picture/art/delete_entry.png")
            delete_entry()
        elif st.session_state.user_role == 'user':
            st.sidebar.write("You have limited permissions.")
        elif st.session_state.user_role == 'database manager':
            st.write('')
            st.write('')
            st.write('')
            st.write('')
            st.image("decoration picture/art/data_entry.png", width= 700)
            db_entry()
    else:
        st.sidebar.write("Please login to access the application.")

    st.write('')
    st.write('')

    # Checkbox for Pokemon Card
    st.image("decoration picture/art/select_attr.png")
    with st.expander("Expand"):
        show_card_id = st.checkbox('Show Series ID', value=True)
        show_hp = st.checkbox('Show HP', value=True)
        show_type = st.checkbox('Show Pokemon Card Type', value=True)
        show_attack = st.checkbox('Show Attack', value=True)
        show_illustrator = st.checkbox('Show Illustrator', value=True)
        show_image = st.checkbox('Show Pokemon Card Image', value=True)
        show_weakness = st.checkbox('Show Card Weakness', value=True)
        show_resistance = st.checkbox('Show Card Resistance', value=True)
        show_retreat_cost = st.checkbox('Show Retreat Cost', value=True)

    # Checkbox for Pokemon Info
    st.image("decoration picture/art/poke_info.png")
    with st.expander(f"Expand"):
        show_height = st.checkbox('Show Height', value=True)
        show_weight = st.checkbox('Show Weight', value=True)
        show_bmi = st.checkbox('Show BMI', value=True)
        show_pokemon_type = st.checkbox('Show Pokemon Type', value=True)
        show_trainer = st.checkbox('Show Trainer', value=True)
        show_regions = st.checkbox('Show Regions', value=True)
        show_pokemon_weakness = st.checkbox('Show Pokemon Weakness', value=True)
        show_super_effective = st.checkbox('Show Super Effective Against', value=True)
        show_not_effective = st.checkbox('Show Not Effective Against', value=True)
        show_no_effect = st.checkbox('Show No Effect', value=True)
        show_pokemon_image = st.checkbox('Show Pokemon Image', value=True)
    st.write('')
    st.image("decoration picture/art/enter_name.png")
    pokemon_name = st.text_input('')
    pokemon_name = pokemon_name.strip()


    if pokemon_name:
        #if st.button('Search by Pokemon Name'):
        display_pokemon_and_card_info(pokemon_name)

    st.image("decoration picture/art/select_type.png")
    selected_types = st.multiselect(
        'Select up to 2 Type:',
        pokemon_types,
        format_func=lambda x: x,
        default=None
    )
    #if st.button('Search by Type(s)'):
    if selected_types:
        display_filtered_pokemon_cards(selected_types)
    st.write('')
    st.write('')
    st.image("decoration picture/art/advance.png")
    display_advance_search()
    st.write('')
    st.write('')
    
    st.image("decoration picture/art/user_comment.png", width=700)
    comment_section()
    st.image("decoration picture/art/comment.png")