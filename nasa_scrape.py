# Import dependencies
from bs4 import BeautifulSoup as bs
from webdriver_manager.chrome import ChromeDriverManager
from splinter import Browser
import pandas as pd
import requests
import pymongo
import os
import time
from config import nasa_url, facts_url, mars_hemisphere_url

def init_browser():
    executable_path = {'executable_path': ChromeDriverManager().install()}
    return Browser('chrome', **executable_path, headless=False)

def scrape():

    # Init browser with above function
    browser = init_browser()

    # URL of page to be scraped
    url = nasa_url

    # Retrieve page with the requests module
    response = requests.get(url, verify=True)

    # Parse HTMl
    soup = bs(response.text, 'html.parser')

    # Grab latest headline and tagline
    headline = soup.find_all('div', class_="content_title")[0].text
    # Grab the tagline for the above headline
    tagline = soup.find_all('div', class_="rollover_description_inner")[0].text

    # Use Splinter to visit site for featured image - First init Splinter
    executable_path = {'executable_path': ChromeDriverManager().install()} # Ensure latest version is installed
    browser = Browser('chrome', **executable_path, headless=False) # Initialize browser

    # Visit URL
    ft_img_grab_url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    browser.visit(ft_img_grab_url)

    # Open featured image full res destination
    browser.links.find_by_partial_text('FULL IMAGE').click()
    time.sleep(6)

    # Parse scraped HTML
    scraped_html = browser.html
    img_parse = bs(scraped_html, 'html.parser')

    # Grab full res image
    featured_image_scrape = img_parse.find('img', class_="fancybox-image")
    featured_image_url = featured_image_scrape.attrs['src']

    # Get full link
    featured_img_final = f"https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/{featured_image_url}"

    # Scrape table with Pandas
    table_url = "https://space-facts.com/mars/"

    # read_html to automatically scrape every table from page
    tables = pd.read_html(requests.get(table_url).text)
    tables
    # Assign to dataframe to view data - [0] index is the table we wanted
    df = tables[0]

    # Clean DataFrame
    # Rename column
    df = df.rename(columns={1: "Values", 0:"Query"})
    # Set New Index
    df = df.set_index('Query')

    # Convert to HTML so we can plug it right into the website
    df_html = df.to_html()


    # NEED TO CHANGE NAMING SCHEME AND ADD COMMENTS

    # executable_path = {'executable_path': ChromeDriverManager().install()} # Ensure latest version is installed
    # browser = Browser('chrome', **executable_path, headless=False) # Initialize browser

    browser.visit(mars_hemisphere_url)

    time.sleep(4)

    # Assign the HTML content of the page to a variable
    hemisphere_html = browser.html
    # Parse HTML with Beautifulsoup
    soup = bs(hemisphere_html,'html.parser')

    # Collect the urls for the hemisphere images
    items = soup.find_all("div", class_="item")
    # Main Website URL - For later appending
    main_url = "https://astrogeology.usgs.gov"
    # Hemisphere list to fill with URL parts for later appending
    hemisphere_urls = []

    for item in items:
        hemisphere_urls.append(f"{main_url}{item.find('a', class_='itemLink')['href']}")

    # Create a list to store the data
    hemisphere_image_urls=[]

    # Loop through each url
    for url in hemisphere_urls:
        # Navigate to the page
        browser.visit(url)
        # Sleep through each iteration to avoid block
        time.sleep(1)
        # Rip HTML from page that has full image
        hemisphere_html = browser.html
        # Parse that above HTML that was just grabbed 
        soup = bs(hemisphere_html,'html.parser')
        # Grab full image
        img_url = soup.find('img', class_="wide-image")['src']
        title = soup.find('h2', class_="title").text
        # Append into a dictionary
        hemisphere_image_urls.append({"title":title,"img_url":f"https://astrogeology.usgs.gov{img_url}"})


    # Create Dictionary to retun and pass through mongoDB
    mars_data_dict = {
            "news_title": headline,
            "news_tagline": tagline,
            "mars_img": featured_img_final,
            "mars_fact": df_html,
            "mars_hemisphere": hemisphere_image_urls
        }


    # CLOSE SCRAPE BROWSER
    browser.quit()

    # Return Data - In app.py this gets put into Mongo
    return mars_data_dict

