![demo](pokemon%20demo%20pic/title.jpg)
# Beyond the Cards: An Application to Pokemon TCG Database
## Team Members

Chengyi Li 
Lewei Lin
Zhanyang Sun 
## Installation & Usage
***Please ensure you have access to a stable Wi-Fi connection before using our app. If you do not have Wifi access, please uncheck “show images” in the checkbox shown at the beginning of the interface after executing main.py.***

1.	Please make sure your MongoDB is properly installed. Login as localhost: 27017. Make sure your MongoDB database is empty before starting.

2.	Download all the files, and move it to your desired workspace.


3.	Navigate to the demo directory in your Terminal:

	cd demo

4.	Install dependencies:

pip install -r requirements.txt

5.	Run project.py. You should see the below printout if data insertion is successful:
…
Finished inserting for Pokemon_Card
Finished inserting for Pokemon
Finished inserting for Attack
Finished inserting for Type
Finished inserting for Trainer
6.	Go to MongoDB to verify there exists db1 to db5. 

7.	In your Terminal, execute the main.py:

streamlit run main.py

8.	Log in to interact with our web application as:

user (only search)
●	username: user
●	password: Dsci-551

database manager (all access of general users, plus insert & update)
●	username: database_manager
●	password: Dsci-551

admin (all access of general users and database managers, plus deletion)
●	username: admin
●	password: Dsci-551
## File Structure
├── demo/  
│   └── comments.txt     		# Store data for the user comment section	
│   └── data/				# Containing our JSON files for this project
│   	└── Attack.json
│   	└── Pokemon.json
│   	└── Pokemon_Card.json
│   	└── Trainer.json
│   	└── Type.json
│   └── decoration pictures/		# Illustrations for our UI 
│   └── main.py		   	# Main script for Front-End web application and UI design
│   └── project.py			# Main script for Back-End hash functions and queries
│   └── requirements.txt		# Install required libraries and dependencies for the project
├── Final Report.pdf    # Documentation of the overall implementation of our project 
├── raw_data/
│   └── pokemon_tcg_data/			   # Raw data for our Pokemon_Card and Attack tables 
│   └── get_json.py				   # Supplementary script for creating our raw JSON files
│   └── pokemon_height_weight.csv		   # Raw data for our Pokemon table
│   └── pokemon_trainers.csv			   # Raw data for our Trainer table
│   └── pokemon_type_effetiveness_chart.xlsx    # Raw data for our Type table
│   └── web_scrap_height_weight.py		   #  Supplementary script for scraping & cleaning
└── README.docx                		# Description of directories and what each file does.
## Our Raw Data (Supplementary Notes)

The raw data files are stored in the “raw_data” folder.

The script for creating JSONs for our project is get_json.py in the “raw_data” folder

***You don’t need to execute get_json.py as it is only used for preliminary preparation, creating the JSON files for our project.***

There are 5 JSON files used for this project, stored in the “data” folder under the “demo” directory: 
●	Attack.json
●	Pokemon.json
●	Pokemon_Card.json
●	Trainer.json
●	Type.json

Below are descriptions of our collection schema and process for data cleaning and JSON creation:

Type.json
●	Schema: 
○	Type_ID  				# PRIMARY KEY    int
○	Type_name 				# str
○	Super_effective_against			# list (of Type_IDs)
○	Not_effective_against	 		# list (of Type_IDs)
○	No_effect 				# list (of Type_IDs)
○	Weakness 				# list (of Type_IDs)

●	The information was gathered from https://pokemondb.net/type, we made some adjustments and scraped it into an Excel file called “pokemon_type_effectiveness_chart.xlsx”, including necessary information for Type_ID, Type_Name, Super_Effective_Against, Not_Very_Effective_Against, No_Effect, and Weakness. We wrote a script and converted this Excel into Type.json. In particular, we use the corresponding Type_IDs to represent their Type_Names for easier search later on. A sample entry is as follows:

{"Type_ID": 1, "Type_name": "Normal", "Super_effective_against": [], "Not_effective_against": [13, 17], "No_effect": [14], "Weakness": [7]},

Trainer.json
●	Schema:
○	Trainer_ID		# PRIMARY KEY    int
○	Trainer_name		# str
○	Pokemon_team 		# str
○	Badges_obtained	# int
○	Region			# list (of different regions)
●	The information was gathered from https://docs.google.com/spreadsheets/d/1GvuxjOBSZchMM4 q5z3lDGw0KLOSY3viEDI6HqDxsnDA/edit#gid=0 and scraped into a CSV file called “pokemon_trainers.csv,” including relevant information needed for Trainer_ID, Trainer_Name, and Pokemon_team. Although some Trainers have the same name, we applied unique Trainer_IDs to distinguish them. For Badges_obtained, we randomly insert a number between 1-5 for each Trainer. As for Region, we learned from https://pokemondb.net/location that there are 10 major regions in the Pokemon world: [Kanto, Johto, Hoenn, Sinnoh, Unova, Kalos, Alola, Galar, Hisui, Paldea]. We would also randomly insert 1-5 regions for each Trainer for testing purposes. A sample entry is as follows:

{"Trainer_ID": 2, "Trainer_name": "Acerola", "Pokemon_team": "USUM Elite Four rematch", "Badges_obtained": 4, "Region": ["Hisui", "Kanto", "Kalos"]},

Pokemon.json
●	Schema:
○	Pokemon_ID		# PRIMARY KEY    int
○	Pokemon_Name 	# str
○	Height 			# float
○	Weight 			# float
○	BMI 			# float 
○	Type_ID 		# FOREIGN KEY from Type    list
○	Trainer_ID 		# FOREIGN KEY from Trainer    list
○	Region			# list (of different regions)
○	img_link 		# str

●	The raw data information was scraped from https://pokemondb.net/pokedex/stats/height-weight and saved as “pokemon_height_weight.csv”. We initially excluded the duplicating Pokemons, and we had in total of 1025 unique Pokemons. When converting the CSV file to JSON, we similarly used Type_ID from the Type Excel to represent their types. For testing purposes, 1-5 Regions were randomly inserted for each Pokemon. For Pokemon’s Trainer, we also randomly picked 1-6 numbers from 1-269 (Trainer_IDs) for each Pokemon. A sample entry is as follows:

{"Pokemon_ID": 1024, "Pokemon_Name": "Terapagos", "Height": 0.2, "Weight": 14.3, "BMI": 6.5, "Type_ID": [1], "Trainer_ID": [137, 228, 229, 105], "Region": ["Hoenn", "Galar", "Kalos", "Hisui"], "img_link": "https://img.pokemondb.net/sprites/scarlet-violet/icon/terapagos-normal.png"},

Pokemon_Card.json
●	Schema: 
○	Card_ID		# PRIMARY KEY    int
○	ID 			# str (detailed ID description)
○	Pokemon_ID  		# FOREIGN KEY from Pokemon     list
○	HP 			# str
○	Type_ID 		# FOREIGN KEY from Type    list
○	Illustrator 		# str
○	Img_path 		# str
○	Weakness 		# list (list of key-value pairs)
■	Type_ID 	# list
■	Value 		# str
○	Resistance		# list (list of key-value pairs)
■	Type_ID 	# list
■	Value 		# str
○	Retreat_cost 		# int
○	Attack_ID 		# FOREIGN KEY from Attack    list

●	The raw data was pulled from a GitHub Pokemon TCG Database: https://github.com/PokemonTCG/pokemon-tcg-data/tree/master/cards/en

●	First, we clone the data from GitHub to our local directory:

		# git clone https://github.com/PokemonTCG/pokemon-tcg-data.git
# cd pokemon-tcg-data/cards/en

●	Then, we wrote a loop to loop over the 159 raw JSON files and retrieve the relevant information we need for our JSON. In particular, we applied each card with a unique Card_ID, as well as gave each Attack a unique Attack_ID. We again replaced the Type_Name in the raw file with Type_ID for our JSON. For Pokemon information, only the Pokemon_IDs are foreign keys stored in this collection as references. A sample entry is as follows:

{"Card_ID": 5, "ID": "base1-5", "Pokemon_ID": [35], "HP": "40", "Type_ID": [19], "Illustrator": "Ken Sugimori", "Img_path": "https://images.pokemontcg.io/base1/5.png", "Weakness":[{"Type_ID": 7, "Value": 2}], "Resistance":[{"Type_ID": 11, "Value": -30}], "Retreat_cost": 1, "Attack_ID": [6, 7]}
 
Attack.json
●	Schema:
○	Attack_ID		# PRIMARY KEY    int
○	Attack_name 		# str
○	Type_ID		# FOREIGN KEY from Type   list
○	Damage 		# str
○	Description 		# str

●	The Attack information was separately retrieved when we created the Pokemon_Card.json. Therefore, only the corresponding Attack_IDs were stored for each card’s Attack in Pokemon_Card.json. The Attack.json will serve as a reference if detailed information such as Attack_Name, Damage, and Description are needed. A sample entry is as follows:
 
{"Attack_ID": 24, "Attack_name": "Thunder", "Type_ID": [4, 4, 4, 19], "Damage": "60", "Description": "Flip a coin. If tails, Raichu does 30 damage to itself."}


Other Details 
●	“Lightning” type of Pokémon Cards was treated as an “Electric” type (Type_ID: 4). 
●	We manually replaced all “Dark” with “Darkness”(Type_ID: 16), “Steel” with “Metal” (Type_ID: 17) in the raw “pokemon_height_weight.csv” and “pokemon_type_effectiveness_chart.xlsx” data files after scraping the data from the websites, so that the Type_Name could better match the “type” names in raw JSON for both Pokemon and Pokemon Cards.
●	Not all attributes of each Entity have values. For example, a Pokemon card may not have Resistance. 


