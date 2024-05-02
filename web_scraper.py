import requests
import pandas as pd 
from bs4 import BeautifulSoup

''' PARSE RIGHTMOVE WEBSITE FOR PROPERTY DATA '''

# Dictionary of London boroughs and their corresponding Rightmove IDs
BOROUGHS = {
    "City of London": "5E61224",
    "Barking and Dagenham": "5E61400",
    "Barnet": "5E93929",
    "Bexley": "5E93932",
    "Brent": "5E93935",
    "Bromley": "5E93938",
    "Camden": "5E93941",
    "Croydon": "5E93944",
    "Ealing": "5E93947",
    "Enfield": "5E93950",
    "Greenwich": "5E61226",
    "Hackney": "5E93953",
    "Hammersmith and Fulham": "5E61407",
    "Haringey": "5E61227",
    "Harrow": "5E93956",
    "Havering": "5E61228",
    "Hillingdon": "5E93959",
    "Hounslow": "5E93962",
    "Islington": "5E93965",
    "Kensington and Chelsea": "5E61229",
    "Kingston upon Thames": "5E93968",
    "Lambeth": "5E93971",
    "Lewisham": "5E61413",
    "Merton": "5E61414",
    "Newham": "5E61231",
    "Redbridge": "5E61537",
    "Richmond upon Thames": "5E61415",
    "Southwark": "5E61518",
    "Sutton": "5E93974",
    "Tower Hamlets": "5E61417",
    "Waltham Forest": "5E61232",
    "Wandsworth": "5E93977",
    "Westminster": "5E93980",
}
# test with single borough first before looping through all boroughs
borough = BOROUGHS["Tower Hamlets"]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36"
}

#url = f"https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=REGION%{borough}&sortType=6&propertyTypes=&includeSSTC=false&mustHave=&dontShow=&furnishTypes=&keywords="
url = f"https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=REGION%5E61417&sortType=6&propertyTypes=&includeSSTC=false&mustHave=&dontShow=&furnishTypes=&keywords="

response = requests.get(url, headers=headers)

soup = BeautifulSoup(response.text, 'html.parser')


''' EXTRACT THE RELEVANT DATA FROM THE WEBPAGE '''

# try to get the number of properties for sale in the borough
property_count = soup.find("span", class_="searchHeader-resultCount").text

# now try to get the prices
prices = soup.find_all('div', class_="propertyCard-priceValue")
prices = [price.text.strip() for price in prices]

# now try to get the addresses
locations = soup.find_all('address', class_="propertyCard-address")
locations = [address.text.strip() for address in locations]

# next is description of the property
description = soup.find_all('div', class_="propertyCard-description")
description = [desc.text.strip() for desc in description]

# # finaly the link to the property
links = soup.find_all('a', class_="propertyCard-link")
links = [link['href'] for link in links]
ulinks = []
for link in links:
    if link not in ulinks:
        ulinks.append(link)

links = [f'https://www.rightmove.co.uk{link}' for link in ulinks]


'''CONVERT THE SCRAPED DATA INTO A PANDAS DATAFRAME'''

data = {
    "prices": prices,
    "locations": locations,
    "description": description,
    "links": links
}

pd.DataFrame(data).to_csv('data/raw_data/rightmove_data.csv', index=False)




'''Debug to check output'''
#print(len(prices))
#print(len(locations))
#print(len(description))
#print(len(links))
# print(soup)



# print(property_information_divs)
# print(f'number of properties: {property_count}')
# print(f'list of prices: {prices}')
# print(f'list of addresses: {addresses}')