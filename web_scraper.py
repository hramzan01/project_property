import requests
import pandas as pd 
import time
import random
from bs4 import BeautifulSoup

''' 
00 PARSE RIGHTMOVE WEBSITE FOR PROPERTY DATA
'''

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

# allows us to scrape the website without being blocked
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36"
}

def scrape_rightmove(borough):
    '''
    Function to scrape the Rightmove website for property data
    :param url: URL of the Rightmove website
    :return: List of prices, addresses, descriptions and links
    '''
    # Lists to store the desired data
    price_list = []
    address_list = []
    description_list = []
    link_list = []




    '''
    01 PAGINATE & EXTRACT THE RELEVANT DATA FROM THE WEBPAGE
    '''

    # index is the page number of the website
    index = 0

    for pages in range(10):

        # the website changes if the you are on page 1 as compared to other pages
        if index == 0:
            url = f"https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=REGION%{borough}&sortType=6&propertyTypes=&includeSSTC=false&mustHave=&dontShow=&furnishTypes=&keywords="

        elif index != 0:
            url = f"https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=REGION%{borough}&sortType=6&index={index}&propertyTypes=&includeSSTC=false&mustHave=&dontShow=&furnishTypes=&keywords="

        # get the webpage
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # try to get the number of properties for sale in the borough
        property_count = soup.find("span", class_="searchHeader-resultCount").text
        property_count = property_count.replace(',', '')

        # now try to get the prices
        prices = soup.find_all('div', class_="propertyCard-priceValue")
        prices = [price.text.strip() for price in prices]
        for price in prices:
            price = price.replace('£', '')
            price = price.replace(',', '')
            price_list.append(price)

        # now try to get the addresses
        locations = soup.find_all('address', class_="propertyCard-address")
        locations = [address.text.strip() for address in locations]
        for address in locations:
            address_list.append(address)

        # next is description of the property
        description = soup.find_all('div', class_="propertyCard-description")
        description = [desc.text.strip() for desc in description]
        for desc in description:
            description_list.append(desc)

        # # finaly the link to the property
        links = soup.find_all('a', class_="propertyCard-link")
        links = [link['href'] for link in links]
        ulinks = []
        for link in links:
            if link not in ulinks:
                ulinks.append(link)

        # Replace missing links with "missing"
        links = [f'https://www.rightmove.co.uk{link}' if link else "missing" for link in ulinks]
        for link in links:
            link_list.append(link)

        # code to ensure that we do not overwhelm the website
        time.sleep(random.randint(1, 3))

        # Code to count how many listings we have scrapped already.
        index = index + 24

        if index >= int(property_count):
            break


    '''
    03 CONVERT THE SCRAPED DATA INTO A PANDAS DATAFRAME & EXPORT TO CSV
    '''

    #Create a dictionary to store the data
    data = {
        "prices": price_list,
        "locations": address_list,
        "description": description_list,
        "links": link_list
    }

    # Debug to check output
    print(len(price_list))
    print(len(address_list))
    print(len(description_list))
    print(len(link_list))

    # Convert to dataframe and export csv
    pd.DataFrame(data).to_csv('data/raw_data/rightmove_data.csv', index=False)
    
    return data

# Call the function
# scrape_rightmove(borough)

'''
SCRAPE ADDITIONAL DATA FROM INDIVIDUAL PROPERTY PAGES
'''

# initiate lists to store the data
property_type = []
bedrooms = []
bathrooms = []
sq_ft = []
sq_m = []
tenure = []

# import existing links from csv
df = pd.read_csv('data/raw_data/rightmove_data.csv')
links = df['links']

sample_links = links[0:10]

counter = 1

for link in sample_links:
    print(f"Scraping link {counter} of {len(sample_links)}...")
    
    url = link
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    property_card = soup.find_all('dd', class_='_3ZGPwl2N1mHAJH3cbltyWn')
    info = [i.text.strip() for i in property_card]
    info[3] = info[3].replace(' sq m', '').replace('sq ft', '').replace(',', '').split()


    # append the data to the lists
    property_type.append(info[0])
    bedrooms.append(info[1])
    bathrooms.append(info[2])
    sq_ft.append(info[3][0])
    sq_m.append(info[3][1])
    tenure.append(info[4])

    # code to ensure that we do not overwhelm the website
    time.sleep(random.randint(1, 3))
    counter += 1
    
# Debug to check output
# print(property_type)
# print(bedrooms)
# print(bathrooms)
# print(sq_ft)
# print(sq_m)
# print(tenure)

if len(property_type) == len(bedrooms) == len(bathrooms) == len(sq_ft) == len(sq_m) == len(tenure):
    print("Data scraped successfully!")
else:
    print('length of list not matching!')
