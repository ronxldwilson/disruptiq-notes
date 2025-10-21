# Example: Web scraping
from bs4 import BeautifulSoup
import requests

response = requests.get('https://example.com')
soup = BeautifulSoup(response.text, 'html.parser')
titles = soup.find_all('h1')
print(titles)
