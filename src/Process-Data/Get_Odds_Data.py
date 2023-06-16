import random
import time
import pandas as pd
import sqlite3
import os
import sys

from datetime import datetime, timedelta
import re
import requests
from tqdm import tqdm

# Import get_date from tools.py in the same directory
from tools import get_date

# Rest of the code...



class OddsAPIProvider:
    def __init__(self, api_key, sportsbook="fanduel"):
        self.api_key = api_key
        self.sportsbook = sportsbook

    def get_odds(self, date):
        url = "https://api.the-odds-api.com/v4/sports/baseball_mlb/odds"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        params = {"region": "us", "bookmaker": self.sportsbook, "date": date}

        response = requests.get(url, headers=headers, params=params)
        data = response.json()

        if "data" in data:
            return data["data"]
        else:
            return []


year = [2022, 2023]
season = ["2022", "2023"]

month = [3, 4, 5, 6, 7, 8, 9, 10]
days = list(range(1, 32))

begin_year_pointer = year[0]
end_year_pointer = year[0]
count = 0

api_key = "b0d5be034629ee1c6337a0bf380a1ef3"
sportsbook = 'fanduel'
df_data = []

con = sqlite3.connect("../../Data/odds.sqlite")

for season1 in tqdm(season):
    teams_last_played = {}
    for month1 in tqdm(month):
        for day1 in tqdm(days):
            if end_year_pointer == datetime.now().year:
                current_date = datetime.now().date()
                if datetime(int(season1), month1, day1).date() > current_date:
                    continue

            date_str = f"{season1}-{month1:02}-{day1:02}"

            odds_provider = OddsAPIProvider(api_key, sportsbook)
            games = odds_provider.get_odds(date_str)

            if not games:
                continue

            for game in games:
                home_team_name = game["teams"][0]
                away_team_name = game["teams"][1]
                money_line_home_value = money_line_away_value = totals_value = None

                for site in game["sites"]:
                    if site["site_key"] == sportsbook:
                        if "odds" in site:
                            money_line_home_value = site["odds"]["h2h"][0]
                            money_line_away_value = site["odds"]["h2h"][1]
                            totals_value = site["odds"]["totals"]["points"]

                if home_team_name not in teams_last_played:
                    teams_last_played[home_team_name] = get_date(date_str)
                    home_games_rested = timedelta(days=7)
                else:
                    current_date = get_date(date_str)
                    home_games_rested = current_date - teams_last_played[home_team_name]
                    teams_last_played[home_team_name] = current_date

                if away_team_name not in teams_last_played:
                    teams_last_played[away_team_name] = get_date(date_str)
                    away_games_rested = timedelta(days=7)
                else:
                    current_date = get_date(date_str)
                    away_games_rested = current_date - teams_last_played[away_team_name]
                    teams_last_played[away_team_name] = current_date

                df_data.append({
                    'Unnamed: 0': 0,
                    'Date': date_str,
                    'Home': home_team_name,
                    'Away': away_team_name,
                    'OU': totals_value,
                    'Spread': None,  # Modify if needed
                    'ML_Home': money_line_home_value,
                    'ML_Away': money_line_away_value,
                    'Points': None,  # Modify if needed
                    'Win_Margin': None,  # Modify if needed
                    'Days_Rest_Home': home_games_rested.days,
                    'Days_Rest_Away': away_games_rested.days
                })

            time.sleep(random.randint(1, 3))

    begin_year_pointer = year[count]

df = pd.DataFrame(df_data)
df.to_sql(f"odds_{season1}_MLB", con, if_exists="replace")
con.close()
