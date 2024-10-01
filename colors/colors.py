
import json
import re
import requests
from bs4 import BeautifulSoup

r = requests.get('https://teamcolorcodes.com/nhl-team-color-codes/')
soup = BeautifulSoup(r.text, 'html.parser')

team_links = soup.find_all("a", class_="team-button")

json_output = {}

i=0
for a in team_links:
    url = a['href']

    # Regular expression to match everything between "https://teamcolorcodes.com/" 
    # and either "-color-codes/" or "-team-colors/"
    url_pattern = r'https://teamcolorcodes\.com/(.*?)-(color-codes|team-colors|colors)/'
    url_str = re.search(url_pattern, url)
    url_str = url_str.group(1)
    team_name = url_str.replace('-', ' ').title()
    
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')
    
    # Define the regular expression pattern to find "RGB: ("
    rgb_pattern = re.compile(r'RGB:\s*\(')
    rgb_strs = soup.find_all(string=rgb_pattern)

    rgb_values = {}
    
    i=0
    for match in rgb_strs:
        
        # Regular expression to match the RGB values inside parentheses
        rgb_value_pattern = r'RGB:\s*\((\d{1,3}),\s*(\d{1,3}),\s*(\d{1,3})\)'
        # Search for the pattern in the text
        rgb_value_str = re.search(rgb_value_pattern, match)
        
        if rgb_value_str:
            r, g, b = rgb_value_str.groups()
            rgb = (int(r), int(g), int(b))
            i+=1
            
            rgb_values[i] = rgb
    
    json_output[team_name] = rgb_values
    

with open('colors/colors.json', 'w') as f:
    f.write(json.dumps(json_output, indent=2))