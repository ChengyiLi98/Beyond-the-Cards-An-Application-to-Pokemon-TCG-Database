import os
import json
import streamlit as st
from pymongo import MongoClient


def create_users_and_roles():
    try:
        # Database connection parameters
        client = MongoClient('localhost', 27017)

        # Roles with their respective privileges
        roles = {
            "admin": ["anyAction"],
            "database_manager": ["find", "insert", "update"],
            "user": ["find"]
        }

        secondary_user = {
            "username": "database_manager",
            "password": "Dsci-551",
            "roles": ["database_manager"]  # Roles to grant to the secondary user
        }

        third_user = {
            "username": "user",
            "password": "Dsci-551",
            "roles": ["user"]  # Roles to grant to the secondary user
        }
        database_names = ['db1', 'db2', 'db3', 'db4', 'db5']
        databases = [client['db1'], client['db2'], client['db3'], client['db4'], client['db5']]
        # Create collections
        for db in databases:
            for collection_name in db.list_collection_names():
                db[collection_name].drop()
        admin_db = client['admin']
        existing_roles = admin_db.command("rolesInfo")["roles"]
        for role, actions in roles.items():
            # Check if the role already exists
            if any(existing_role["role"] == role for existing_role in existing_roles):
                print(f"Role '{role}' already exists in database '{admin_db.name}'. Deleting and recreating...")
                admin_db.command("dropRole", role)
            privileges = [
                {"resource": {"db": db_name, "collection": ""}, "actions": actions} for db_name in database_names
            ]
            command = {
                "createRole": role,
                "privileges": privileges,
                "roles": []
            }
            admin_db.command(command)
            print(f"Role '{role}' created successfully in database '{admin_db.name}'")
        admin_db.command('dropAllUsersFromDatabase')
        admin_db.command('createUser', 'admin', pwd='Dsci-551', roles=['root'])
        admin_db.command('createUser', secondary_user['username'], pwd=secondary_user['password'], roles=secondary_user['roles'])
        admin_db.command('createUser', third_user['username'], pwd=third_user['password'], roles=third_user['roles'])
        print("Roles and users created successfully")
        return secondary_user, third_user

    except Exception as e:
        print(f"Error creating roles: {e}")

def get_database_index(unique_id, databases):
    total = sum(ord(char) for char in str(unique_id))
    return total % len(databases)


def get_database(unique_id, databases):
    return databases[get_database_index(unique_id, databases)]

def insert_data(collection_name, documents, databases):
    unique_identifiers = {'Pokemon_Card': 'Card_ID', 'Pokemon': 'Pokemon_ID', 'Attack': 'Attack_ID', 'Type': 'Type_ID',
                          'Trainer': 'Trainer_ID'}
    db = get_database(documents[unique_identifiers[collection_name]], databases)
    collection = db[collection_name]
    collection.insert_one(documents)


def upsert_data(collection_name, document, databases):
    unique_identifiers = {'Pokemon_Card': 'Card_ID', 'Pokemon': 'Pokemon_ID', 'Attack': 'Attack_ID', 'Type': 'Type_ID',
                          'Trainer': 'Trainer_ID'}
    document = json.loads(document)
    db = get_database(document[unique_identifiers[collection_name]], databases)
    collection = db[collection_name]

    unique_field = unique_identifiers[collection_name]
    query = {unique_field: document[unique_field]}
    update = {"$set": document}
    collection.update_one(query, update, upsert=True)


def populate_databases(databases, collection_names, data_dir='./data/'):
    # Create collections
    for db in databases:
        for collection_name in db.list_collection_names():
            db[collection_name].drop()
        for collection_name in collection_names:
            db.create_collection(collection_name)
            # print(f"Created collection: {db.name}.{collection_name}")

    # Loop through each JSON file in the directory
    for collection_name in collection_names:
        json_file_path = os.path.join(data_dir, f"{collection_name}.json")

        # Read the JSON file
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # Distribute data into different databases based on hash value
        for item in data:
            insert_data(collection_name, item, databases)
        print(f'Finished inserting for {collection_name}')

def get_names_from_ids(ids, collection_name, databases):
    """Define a function that retrieves names based on given IDs from specified collections across multiple databases."""

    # Initialize an empty list to store the names corresponding to the given IDs
    names = []

    # Determine the field name used to query documents in the database based on the collection type
    query_field = 'Type_ID' if collection_name == 'Type' \
        else 'Attack_ID' if collection_name == 'Attack' \
        else 'Trainer_ID' if collection_name == 'Trainer'\
        else 'Pokemon_ID' if collection_name == 'Pokemon' else '_id'

    # Create a dictionary to map collection names to the fields that hold the desired names,
    # using 'name' as a default if the collection is not recognized
    name_field = {
        'Type': 'Type_name',
        'Attack': 'Attack_name',
        'Trainer': 'Trainer_name',
        'Pokemon': 'Pokemon_Name',
    }.get(collection_name, 'name')

    # Iterate over each ID provided in the 'ids' list
    for id_ in ids:
        found = False  # Initialize a flag to indicate whether the ID has been found in any database

        # Iterate over each database in the 'databases' list
        for db in databases:
            # Attempt to find a single document in the current database's specified collection that matches the ID
            doc = db[collection_name].find_one({query_field: id_})
            if doc and name_field in doc:  # Check if the document was found and if it contains the desired name field
                names.append(doc[name_field])  # Append the name associated with the ID to the list
                found = True  # Set the flag to True indicating the ID has been found
                break

        if not found:  # If no document is found across all databases
            names.append('Unknown')

    return names

def get_type_details(type_id, databases):
    """Fetch detailed type information and convert related type IDs to names."""

    for db in databases:
        type_info = db['Type'].find_one({'Type_ID': type_id})
        if type_info:
            # Process interaction lists
            interaction_keys = ['Super_effective_against', 'Not_effective_against', 'No_effect', 'Weakness']
            for key in interaction_keys:
                # Check if the interaction list exists and is not empty
                if key in type_info and type_info[key]:
                    # Convert Type IDs in the list to their names
                    type_info[key] = get_names_from_ids(type_info[key], 'Type', databases)
            return type_info  # Return the enriched type information
    return None  # Indicate that the type information was not found

def get_type_ids(selected_types, databases):
    """Define a function to retrieve type IDs for given type names from multiple databases."""

    type_ids = []
    # Iterate over each type name provided in the 'selected_types' list.
    for type_name in selected_types:
        for db in databases:  # Iterates over each database in the 'databases' list
            # Attempt to find a single document in the 'Type' collection of the current database
            # that matches the 'Type_name' field with the current type name
            type_doc = db['Type'].find_one({'Type_name': type_name})
            # If a document is found, appends the 'Type_ID' from the document to the 'type_ids' list
            if type_doc:
                type_ids.append(type_doc['Type_ID'])
                break  # after find the result, exit the loop
    return type_ids

def get_weakness_or_resistance(list_, databases):
    """Define a function to retrieve and replace Type_IDs with their corresponding Type_name
        for either weakness or resistance data."""

    processed_list = []

    for item in list_:
        type_id = item['Type_ID']  # Extract the Type_ID from the current item
        value = item['Value']  # Extract the Value from the current item, represents weakness or resistance
        # Initialize the type name as "Unknown". This will be updated if a matching type is found in the databases
        type_name = "Unknown"

        # Iterate over each database in the list of databases
        for db in databases:
            # Query the 'Type' collection in the current database to find a single document
            # where the Type_ID matches the type_id of the current item.
            type_doc = db['Type'].find_one({'Type_ID': type_id})
            if type_doc:  # Check if a document was found.
                # Update the type name with the 'Type_name' field from the found document
                type_name = type_doc['Type_name']

                break

        # Construct a new dictionary for the processed item,
        # including the found or default type name and the original value
        processed_item = {
            'Type': type_name,
            'Value': value
        }
        processed_list.append(processed_item)  # Append the processed item to the processed_list

    return processed_list

def search_pokemon_info(pokemon_name):
    """Define a function that searches for detailed information about a specific Pokémon by name."""

    global database_manager_username, database_manager_password
    client = MongoClient(f'mongodb://{database_manager_username}:{database_manager_password}@localhost:27017/')
    databases = [client['db1'], client['db2'], client['db3'], client['db4'], client['db5']]
    pokemon_info_list = []

    # Loop through each database and iterates over each database in the list
    for db in databases:
        # Use a case-insensitive regex query to perform fuzzy search for Pokémon names that contain the provided string
        pokemon_cursor = db['Pokemon'].find({"Pokemon_Name": {"$regex": f".*{pokemon_name}.*", "$options": "i"}})

        # Iterate over each Pokémon document found in the cursor
        for pokemon_info in pokemon_cursor:
            # Convert Type_IDs to Type_names and include type details
            if 'Type_ID' in pokemon_info:
                # Retrieve detailed information for each type ID associated with the Pokémon
                type_details_list = [get_type_details(type_id, databases) for type_id in pokemon_info['Type_ID']]
                # Filter out any None responses from the type details and adds them to the Pokémon document
                pokemon_info['Type_Details'] = [detail for detail in type_details_list if detail]
                # Convert type IDs to type names and adds them to the Pokémon document.
                pokemon_info['Type'] = get_names_from_ids(pokemon_info['Type_ID'], 'Type', databases)
            else:
                pokemon_info['Type'] = 'Unknown'
                pokemon_info['Type_Details'] = []

            # Convert Trainer_ID to Trainer_name
            if 'Trainer_ID' in pokemon_info:
                pokemon_info['Trainer'] = get_names_from_ids(pokemon_info['Trainer_ID'], 'Trainer', databases)
            else:
                pokemon_info['Trainer'] = 'Unknown'

            pokemon_info_list.append(pokemon_info)

    return pokemon_info_list

def search_by_name(pokemon_name):
    """Defines a function to search for Pokémon and their associated Pokémon Cards information by Pokémon name."""

    global database_manager_username, database_manager_password
    client = MongoClient(f'mongodb://{database_manager_username}:{database_manager_password}@localhost:27017/')
    databases = [client['db1'], client['db2'], client['db3'], client['db4'], client['db5']]
    results = []  # Initialize an empty list to hold the results

    # Loop through each database and iterates over each database in the list
    for db in databases:
        # Find matching Pokémon based on the provided name
        matching_pokemon = list(db['Pokemon'].find(
            {'Pokemon_Name': {'$regex': f'.*{pokemon_name}.*', '$options': 'i'}}
        ))
        # Query the 'Pokemon' collection in the current database to find documents where the 'Pokemon_Name'
        # field matches the provided name using a case-insensitive regular expression.

        # If any Pokémon were found matching the query, iterates over each found Pokémon
        if matching_pokemon:
            for pokemon in matching_pokemon:
                # Initialize a dictionary to hold the Pokémon data and a list for associated cards
                pokemon_result = {"Pokemon": pokemon, "Cards": []}
                # Iterate over each database again to find all associated Pokémon Cards with given Pokemon_ID
                for DB in databases:
                    matching_cards = DB['Pokemon_Card'].find({'Pokemon_ID': pokemon['Pokemon_ID']})
                    # Iterate over each card found that is associated with the current Pokémon
                    for card in matching_cards:
                        # get real names for Type_IDs, Attack_IDs
                        card['Type'] = get_names_from_ids(card.get('Type_ID', []), 'Type', databases)
                        card['Attack'] = get_names_from_ids(card.get('Attack_ID', []), 'Attack', databases)
                        # get real names for weakness and resistance
                        card['Weakness'] = get_weakness_or_resistance(card.get('Weakness', []), databases)
                        card['Resistance'] = get_weakness_or_resistance(card.get('Resistance', []), databases)
                        # appending results
                        pokemon_result["Cards"].append(card)
                results.append(pokemon_result)

    return results


def filter_by_type(selected_types):
    """Defines a function to filter Pokémon and their associated cards by type names."""

    global database_manager_username, database_manager_password
    client = MongoClient(f'mongodb://{database_manager_username}:{database_manager_password}@localhost:27017/')
    databases = [client['db1'], client['db2'], client['db3'], client['db4'], client['db5']]
    results = []

    # Collect all selected Type_name's Type_ID
    type_ids = []
    # Iterate over each type name provided in 'selected_types', and iterates over each database in the list
    for type_name in selected_types:
        for db in databases:
            # Query the 'Type' collection in the current database to find a single document
            # where 'Type_name' matches the type_name.
            type_doc = db['Type'].find_one({'Type_name': type_name})
            # if the document was found, add the 'Type_ID' from the document to the list.
            if type_doc:
                type_ids.append(type_doc['Type_ID'])
                break

    for db in databases:  # Iterate over each database again to find matching Pokémon.
        if len(type_ids) > 1:
            # when select two types，use '$all' to select the cards with these two types both.
            query = {'Type_ID': {'$all': type_ids}}
        else:
            # when select only one type，use'$in' to include all cards with this type
            query = {'Type_ID': {'$in': type_ids}}

        # Query the 'Pokemon' collection with the constructed query to find matching Pokémon
        matching_pokemon = db['Pokemon'].find(query)
        # Iterate over each matching Pokémon
        for pokemon in matching_pokemon:
            # Initialize a dictionary to hold the Pokémon data and an empty list for associated cards
            pokemon_result = {"Pokemon": pokemon, "Cards": []}

            for DB in databases:
                # Query the 'Pokemon_Card' collection to find cards that reference the current Pokémon's ID
                matching_cards = DB['Pokemon_Card'].find({'Pokemon_ID': pokemon['Pokemon_ID']})

                for card in matching_cards:
                    # Switch Type_IDs and Attack_IDs to their corresponding names
                    card['Type'] = get_names_from_ids(card.get('Type_ID', []), 'Type', databases)
                    card['Attack'] = get_names_from_ids(card.get('Attack_ID', []), 'Attack', databases)
                    # get results for weakness and resistance
                    card['Weakness'] = get_weakness_or_resistance(card.get('Weakness', []), databases)
                    card['Resistance'] = get_weakness_or_resistance(card.get('Resistance', []), databases)
                    # append the results
                    pokemon_result["Cards"].append(card)
            results.append(pokemon_result)

    return results


def advanced_search(selected_types=None, selected_illustrators=None, hp_range=None, retreat_cost_range=None):
    """Define a function to perform an advanced search on a Pokémon card database.
    It allows filtering by types, illustrators, HP range, and retreat cost range."""

    global database_manager_username, database_manager_password
    client = MongoClient(f'mongodb://{database_manager_username}:{database_manager_password}@localhost:27017/')
    databases = [client['db1'], client['db2'], client['db3'], client['db4'], client['db5']]
    results = []

    query = {}  # Initializes an empty dictionary to build the MongoDB query.

    # if there are any types specified for filtering,
    # call get_type_ids to convert type names to their corresponding IDs across the databases.
    if selected_types:
        type_ids = get_type_ids(selected_types, databases)
        # If Type_IDs were found, query to filter documents where Type_ID is within the list of retrieved type IDs.
        if type_ids:
            query['Type_ID'] = {'$in': type_ids}

    # If there are any illustrators are specified for filtering,
    # query to filter documents where Illustrator is within the provided list of illustrators.
    if selected_illustrators:
        query['Illustrator'] = {'$in': selected_illustrators}

    # If a range for HP is specified for filtering, query to filter documents where HP is within the specified range.
    # HP values are converted to integers for comparison.
    if hp_range:
        query['$expr'] = {
            '$and': [
                {'$gte': [{'$toInt': '$HP'}, hp_range[0]]},
                {'$lte': [{'$toInt': '$HP'}, hp_range[1]]}
            ]
        }

    # If a range for Retreat_cost is specified for filtering,
    # query to filter documents where Retreat_cost is within the specified range.
    if retreat_cost_range:
        query['Retreat_cost'] = {'$gte': retreat_cost_range[0], '$lte': retreat_cost_range[1]}

    # Iterate over each database to perform the query on the 'Pokemon_Card' collection in the current database
    # and retrieves matching documents.
    for db in databases:
        matching_cards = db['Pokemon_Card'].find(query)

        # Iterates over each card retrieved from the query.
        for card in matching_cards:
            # Retrieve and set the Type_names for each card based on its Type_ID.
            card['Type'] = get_names_from_ids(card.get('Type_ID', []), 'Type', databases)
            # Retrieve and set the Attack_names for each card based on its Attack_IDs.
            card['Attack'] = get_names_from_ids(card.get('Attack_ID', []), 'Attack', databases)
            # Retrieve and set the Weakness and Resistance data for each card.
            card['Weakness'] = get_weakness_or_resistance(card.get('Weakness', []), databases)
            card['Resistance'] = get_weakness_or_resistance(card.get('Resistance', []), databases)
            # Retrieve and set the Pokémon name for each card based on its Pokémon_ID.
            card['Pokemon_Name'] = get_names_from_ids(card.get('Pokemon_ID', []), 'Pokemon', databases)
            # Append the data to results
            results.append(card)

    return results


def show_card_info(card_id, fields_to_show):
    """Define a function to show specific information about a Pokemon_Card based on its ID
    and the fields specified by the user."""

    global database_manager_username, database_manager_password
    client = MongoClient(f'mongodb://{database_manager_username}:{database_manager_password}@localhost:27017/')
    databases = [client['db1'], client['db2'], client['db3'], client['db4'], client['db5']]
    db_index = get_database_index(card_id)  # Determine the database index based on the card_id
    db = databases[db_index]  # Select the specific database from the list where the card is expected to be stored.

    # Create a dictionary where each key is a field to show, set to 1 to include it in the results.
    projection = {field: 1 for field in fields_to_show}
    projection['_id'] = 0  # Exclude the _id field

    # Find the card with the specified Card_ID and the selected fields
    card_info = db['Pokemon_Card'].find_one({'Card_ID': card_id}, projection)

    if card_info:
        print(card_info)  # If the query returned any document, print the information of the Pokémon Card if found.
    else:
        print("No matching Pokémon card found.")


global database_manager_username, database_manager_password
database_manager_username = 'user'  # if not logged in, default to be common user
database_manager_password = 'Dsci-551'


# Dictionary of username: password
user_accounts = {
    'admin': 'Dsci-551',
    'user': 'Dsci-551',
    'database_manager': 'Dsci-551'
}

# Dictionary of username: roles
user_roles = {
    'admin': 'admin',
    'user': 'user',
    'database_manager': 'database manager'
}


def handle_login():
    # Checks if the user is already logged in by looking for the "logged_in" key in the session state.
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user_role = None

    database_manager_username = st.sidebar.text_input("Username")
    database_manager_password = st.sidebar.text_input("Password", type="password")

    # Validates the login credentials entered by the user.
    # If the username exists in the user_accounts dictionary and the password matches the stored password for that username, the user is considered logged in.
    if st.sidebar.button("Login"):
        if database_manager_username in user_accounts and user_accounts[database_manager_username] == database_manager_password:
            st.session_state.logged_in = True
            st.session_state.user_role = user_roles.get(database_manager_username,
                                                        'user')  # Default to 'user' if no specific role is assigned
            st.sidebar.success("Logged in as {}".format(database_manager_username))
        else:
            st.sidebar.error("Incorrect Username or Password")


if __name__ == "__main__":
    database_manager_info, user_info = create_users_and_roles()
    database_manager_username, database_manager_password = database_manager_info['username'], database_manager_info['password']
    username, password = user_info['username'], user_info['password']
    client = MongoClient(f'mongodb://{database_manager_username}:{database_manager_password}@localhost:27017/')
    databases = [client['db1'], client['db2'], client['db3'], client['db4'], client['db5']]
    collection_names = ['Pokemon_Card', 'Pokemon', 'Attack', 'Type', 'Trainer']
    populate_databases(databases, collection_names, data_dir='./data/')
    # Close the connection
    client.close()
