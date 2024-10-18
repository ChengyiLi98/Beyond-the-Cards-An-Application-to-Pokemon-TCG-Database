import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

# URL of the page to scrape
url = 'https://pokemondb.net/pokedex/stats/height-weight'

# Sending a request to the webpage
response = requests.get(url)
response.raise_for_status()  # This will raise an exception if there was an error fetching the page

# Parsing the HTML content of the page
soup = BeautifulSoup(response.content, 'html.parser')

# Lists to store the extracted information
pokemon_data = []

# Find the table containing the Pokémon data
table = soup.find('table', class_='data-table')

# Loop through all rows in the table
for row in table.tbody.find_all('tr'):
    cols = row.find_all('td')

    # Extracting the required information
    num_and_image = cols[0].find('span', class_='infocard-cell-data').text
    name = cols[1].get_text(strip=True)
    type_ = cols[2].get_text(strip=True).split()  # lots of pokemons have multiple types
    height_m = cols[4].text.strip()
    weight_lbs = cols[5].text.strip()
    bmi = cols[6].text.strip()
    image_link = cols[0].find('img')['src']


    pokemon_data.append({
        'Number': num_and_image,
        'Name': name,
        'Type': type_,
        'Height(m)': height_m,
        'Weight(lbs)': weight_lbs,
        'BMI': bmi,
        'Image Link': image_link
    })

# data cleaning
# Define a function to split types on capital letters (assuming types are concatenated without spaces)

def split_types(types):
    return re.findall('[A-Z][^A-Z]*', types[0])

def keep_up_to_second_capital(name):
    # This regex will capture words leading up to the second uppercase letter
    matches = re.match(r"([A-Z][a-z]+)([A-Z])", name)
    if matches:
        # Return the part of the name up to the second capital letter
        return matches.group(1)
    else:
        # If there's no second capital letter, return the name as is
        return name


df = pd.DataFrame(pokemon_data)
# Apply the function to the 'Name' column
df['Name'] = df['Name'].apply(keep_up_to_second_capital)

# Apply the function to the 'Type' column
df['Type'] = df['Type'].apply(split_types)
# Create a DataFrame

df_cleaned = df.drop_duplicates(subset=['Number'], keep='first')
df_cleaned.to_csv('pokemon_height_weight.csv', index=False)

# than manually check the name column for number 29, 32, 669, and 718 delete special char in them.