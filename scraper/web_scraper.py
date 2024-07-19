import requests
from requests.exceptions import RequestException
import pandas as pd
import time
import random
from bs4 import BeautifulSoup
import json
import os


# allows us to scrape the website without being blocked
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36"
}

# Load the boroughs json file
boroughs = json.load(open('data/raw_data/boroughs.json'))

'''
00 PARSE RIGHTMOVE WEBSITE FOR PROPERTY DATA
'''
def scrape_rightmove(num_pages, user_location):
    '''
    Function to scrape the Rightmove website for property data
    :param url: URL of the Rightmove website
    :return: List of prices, addresses, descriptions and links
    '''

    # num_pages = int(input("How many pages would you like to scrape? (0 for all pages) "))
    # user_location = str(input("Enter the borough you would like to scrape: "))
    borough = boroughs[user_location]

    # Lists to store the desired data
    price_list = []
    address_list = []
    description_list = []
    link_list = []

    url = f"https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=REGION%{borough}&sortType=6&propertyTypes=&includeSSTC=false&mustHave=&dontShow=&furnishTypes=&keywords="
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    if num_pages < 1:
        entries = soup.find('span', class_='searchHeader-resultCount').text
        if ',' in entries:
            entries = entries.replace(',', '')
        num_pages = int(entries)//24 + 1

    '''
    01 PAGINATE & EXTRACT THE RELEVANT DATA FROM THE WEBPAGE
    '''

    # index is the page number of the website
    index = 0

    for page in range(num_pages):
        print(f"Scraping page {page + 1}/{num_pages}...")

        # the website changes if the you are on page 1 as compared to other pages
        if index == 0:
            url = f"https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=REGION%{borough}&sortType=6&propertyTypes=&includeSSTC=false&mustHave=&dontShow=&furnishTypes=&keywords="

        elif index != 0:
            url = f"https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=REGION%{borough}&sortType=6&index={index}&propertyTypes=&includeSSTC=false&mustHave=&dontShow=&furnishTypes=&keywords="

       
        for attempt in range(5):  # Retry up to 5 times
            try:
                # get the webpage
                response = requests.get(url, headers=headers)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # get max pages per borough
                # entries = int(soup.find('span', class_='searchHeader-resultCount').text)
                entries = soup.find('span', class_='searchHeader-resultCount').text
                if ',' in entries:
                    entries = entries.replace(',', '')
                max_pages = int(entries)//24 + 1
                
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
                unique_links = set()
                for link in links:
                    href = link['href']
                    if href not in unique_links:
                        unique_links.add(href)
                        full_link = f'https://www.rightmove.co.uk{href}' if href else "missing"
                        link_list.append(full_link)
                
                # Check if list lengths match
                if len(price_list) == len(address_list) == len(description_list) == len(link_list):
                    break  # Exit the retry loop if successful

                else:
                    print(f"Mismatch in lengths after page {page + 1}, attempt {attempt + 1}. Retrying...")

            except RequestException as e:
                print(f"Error on page {page + 1}, attempt {attempt + 1}: {e}")
                time.sleep(2)  # Wait before retrying
                continue

                
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

    # add borough to the data
    data['borough'] = user_location

    # Convert to dataframe and export csv
    pd.DataFrame(data).to_csv('data/processed_data/rightmove_data.csv', index=False)

    return data, user_location

'''
01 SCRAPE ADDITIONAL DATA FROM INDIVIDUAL PROPERTY PAGES
'''
def scrape_additional():

    # Additional data to scrape
    property_type = []
    bedrooms = []
    bathrooms = []
    sq_ft = []
    sq_m = []
    tenure = []
    latitude = []
    longitude = []
    postcode = []

    # import existing links from csv
    df = pd.read_csv('data/processed_data/rightmove_data.csv')
    links = df['links']

    counter = 1

    for link in links:
        print(f"Scraping link {counter} of {len(links)}...")

        url = link
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        property_card = soup.find_all('dd', class_='_3ZGPwl2N1mHAJH3cbltyWn')
        info = [i.text.strip() for i in property_card]

        # skip property if data is missing ensuring lists same length
        if len(info) < 5:
            # append empty data to the lists
            property_type.append(info[0])
            bedrooms.append(0)
            bathrooms.append(0)
            sq_ft.append(0)
            sq_m.append(0)
            tenure.append(0)
            latitude.append(0)
            longitude.append(0)
            postcode.append(0)

            # code to ensure that we do not overwhelm the website
            time.sleep(random.randint(1, 3))
            counter += 1

            # continue to next iteration
            continue

        # check if the data is missing
        if info[3] == 'Ask agent':
            info[3] = '0 sq ft 0 sq m'
        else:
            info[3] = info[3].replace(' sq m', '').replace('sq ft', '').replace(',', '').split()

        ''' extract the latitude and longitude of the property '''
        script_tag = None
        for script in soup.find_all("script"):
            if 'window.adInfo' in script.text:
                script_tag = script
                break

        script_text = script_tag.string.strip()

        # Split the script text and find the part containing 'window.PAGE_adInfo'
        parts = script_text.split('window.adInfo = ')
        converted = parts[1].strip('.propertyData.dfpAdInfo.targeting')

        # Convert the JSON to a dictionary
        dict = json.loads(converted)

        # extract lat and lon from soup
        lat = dict['propertyData']['location']['latitude']
        lon = dict['propertyData']['location']['longitude']


        # generate postcode from lat and lon
        postcode_api = f'https://api.postcodes.io/postcodes?lon={lon}&lat={lat}'

        try:
            response = requests.get(postcode_api).json()
            pcode = response.get('result', [{}])[0].get('postcode', 'N/A')
        except (KeyError, IndexError, TypeError):
            pcode = 'N/A'

        # append the data to the lists
        property_type.append(info[0])
        bedrooms.append(info[1])
        bathrooms.append(info[2])
        sq_ft.append(info[3][0])
        sq_m.append(info[3][1])
        tenure.append(info[4])
        latitude.append(lat)
        longitude.append(lon)
        postcode.append(pcode)

        # code to ensure that we do not overwhelm the website
        time.sleep(random.randint(1, 3))
        counter += 1


    if len(property_type) == len(bedrooms) == len(bathrooms) == len(sq_ft) == len(sq_m) == len(tenure):
        print("Data scraped successfully!")
    else:
        print('length of list not matching!')



    # Create a dictionary to store the data
    data = {
        "property_type": property_type,
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
        "sq_ft": sq_ft,
        "sq_m": sq_m,
        "tenure": tenure,
        'latitude': latitude,
        'longitude': longitude,
        'postcode': postcode
    }

    # Add to existing dataframe and export to csv
    pd.DataFrame(data).to_csv('data/processed_data/rightmove_extra.csv', index=False)

    
    return data

'''
02 COMBINE THE TWO DATAFRAMES INTO ONE
'''
def scrape_all(num_pages, user_location):
    
    # Call the function to scrape the data
    basic_data, user_location = scrape_rightmove(num_pages, user_location)

    # Call the two functions    
    basic_data = pd.DataFrame(basic_data)
    extra_data = pd.DataFrame(scrape_additional())

    combined_data = pd.concat([basic_data, extra_data], axis=1)

    combined_data.to_csv(f'data/processed_data/{user_location.lower()}_property_data.csv', index=False)

    # delete the individual files
    os.remove('data/processed_data/rightmove_data.csv')
    os.remove('data/processed_data/rightmove_extra.csv')


'''
03 RUN THE FUNCTIONS
'''
# scrape_rightmove()
# scrape_additional()
scrape_all(4, 'Barnet')


# # Loop through all boroughs
# for borough in list(boroughs.keys()):
#     scrape_all(4, borough)
#     print(f"Scraping for {borough} completed!")
