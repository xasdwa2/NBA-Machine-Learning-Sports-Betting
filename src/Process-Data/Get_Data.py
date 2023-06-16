import os
import random
import sqlite3
import time
import sys
from datetime import date, datetime, timedelta

from tqdm import tqdm
import requests
from bs4 import BeautifulSoup

sys.path.insert(1, os.path.join(sys.path[0], '..'))
from Utils.tools import to_data_frame

url = 'https://www.mlb.com/teams'

year = [2022, 2023]
season = ["2022", "2023"]

month = [3, 4, 5, 6, 7, 8, 9, 10]
days = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]

begin_year_pointer = year[0]
end_year_pointer = year[0]
count = 0

con = sqlite3.connect("../../Data/teams.sqlite")

for season1 in tqdm(season):
    for month1 in tqdm(month):
        if month1 == 3 and begin_year_pointer == year[0]:
            count += 1
            end_year_pointer = year[count]
        for day1 in tqdm(days):
            if month1 == 3 and day1 < 1:
                continue
            if month1 in [4, 6, 9, 11] and day1 > 30:
                continue
            if month1 == 2 and day1 > 28:
                continue
            if end_year_pointer == datetime.now().year:
                if month1 == datetime.now().month and day1 > datetime.now().day:
                    continue
                if month1 > datetime.now().month:
                    continue
            
            # Make a GET request to the MLB teams page
            response = requests.get(url)
            if response.status_code == 200:
                page_content = response.text
                soup = BeautifulSoup(page_content, 'html.parser')
                
                # Extract the teams data from the page
                team_elements = soup.find_all('a', {'class': 'p-featured-teams__logo-link'})
                teams_data = []
                for team_element in team_elements:
                    team_name = team_element.find('span', {'class': 'p-featured-teams__team-name'}).text
                    team_logo_url = team_element.find('img', {'class': 'p-featured-teams__logo-img'})['src']
                    teams_data.append({'team_name': team_name, 'team_logo_url': team_logo_url})
                
                general_df = to_data_frame(teams_data)
                real_date = date(year=end_year_pointer, month=month1, day=day1) + timedelta(days=1)
                general_df['Date'] = str(real_date)
    
                x = str(real_date).split('-')
                general_df.to_sql(f"mlb_teams_{season1}-{str(int(x[1]))}-{str(int(x[2]))}", con, if_exists="replace")
    
                time.sleep(random.randint(1, 3))
    begin_year_pointer = year[count]

con.close()
