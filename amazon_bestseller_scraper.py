from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

# Now parse with BeautifulSoup
from bs4 import BeautifulSoup


def setup_driver():
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode (optional)
    chrome_options.add_argument("--ignore-certificate-errors")  # Ignore SSL certificate errors
    chrome_options.add_argument("--allow-insecure-localhost")  # Allow insecure localhost

    # Create a new instance of the Chrome driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    return driver 

# Load the webpage
def load_webpage(driver, url):
    driver.get(url)
    driver.implicitly_wait(10)  # Optionally wait for elements to load
    html = driver.page_source
    driver.quit()
    return html


# Parse the product data
def parse_products(html):
    product_soup = BeautifulSoup(html, 'html.parser')
    all_products = product_soup.find_all('div', attrs={"class": "_octopus-search-result-card_style_apbSearchResultItem__2-mx4"})
    
    return all_products

# Extract product details
def extract_product_details(all_products):
    links = []
    names = []
    ratings = []

    for product in all_products:
        for product_link in product:
            pr = product_link.find_all('div', attrs={"class": 'a-section a-spacing-small puis-padding-left-small puis-padding-right-small'})
            for link in pr:
                product_links = link.find('a')
                href = product_links.get('href')
                if href.startswith('https:'):
                    links.append(href)
                else:
                    links.append('https://www.amazon.in' + href)
                
                # Extract reviews and ratings
                review = link.find('div', attrs={"class": 'a-section a-spacing-none a-spacing-top-micro'})
                span = review.find_all('span')
                rating = span[0].text
                last_month_sale = span[-1].text
                ratings.append((rating, last_month_sale))

    return links, ratings 
  
# Save data to CSV
def save_to_csv(links, ratings, file_name='firstcry_bestsellers.csv'):
    products_dict = {
        'Product_link': links,
        'Rating': [rating[0] for rating in ratings],
        'Last Month Sale': [rating[1] for rating in ratings]
    }
    data = pd.DataFrame(products_dict)
    data.to_csv(file_name, index=False)
    print(f"Data saved to {file_name}")

def scrape_amazon_products(url):
    driver = setup_driver()
    html = load_webpage(driver, url)
    all_products = parse_products(html)
    links, ratings = extract_product_details(all_products)
    save_to_csv(links, ratings)




if __name__ == '__main__':
    #url = 'https://www.amazon.in/s?bbn=1953135031&rh=n%3A1571274031%2Cn%3A1953111031%2Cn%3A1953135031%2Cn%3A1953139031&dc&qid=1729063335&rnid=1953135031&ref=lp_1953135031_nr_n_3'
    url = 'https://www.firstcry.com/baby-diapers/1/27?scat=29@@@@@@@@@@1@0@20@@@@@@@@@@&sort=Popularity&ref2=menu_dd_diapering_baby-wipes_H'
    scrape_amazon_products(url)