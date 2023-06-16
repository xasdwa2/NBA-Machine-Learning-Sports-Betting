import random
import time
import pandas as pd
import sqlite3
import os
import sys

from datetime import datetime, timedelta
from tqdm import tqdm
from sbrscrape import MLB_Scoreboard  # Import MLB_Scoreboard instead of Scoreboard
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from Utils.tools import get_date

year = [2022, 2023]
season = ["2022", "2023"]  # Update season to the desired years in string format

month = [3, 4, 5, 6, 7, 8, 9, 10]  # Update months based on the MLB season
days = list(range(1, 32))  # Update days to cover the entire month

begin_year_pointer = year[0]
end_year_pointer = year[0]
count = 0

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

            sb = MLB_Scoreboard(date=f"{season1}-{month1:02}-{day1:02}")  # Use MLB_Scoreboard instead of Scoreboard
            if not hasattr(sb, "games"):
                continue
            for game in sb.games:
                if game['home_team'] not in teams_last_played:
                    teams_last_played[game['home_team']] = get_date(f"{season1}-{month1:02}{day1:02}")
                    home_games_rested = timedelta(days=7)  # Start of season, use a suitable value
                else:
                    current_date = get_date(f"{season1}-{month1:02}{day1:02}")
                    home_games_rested = current_date - teams_last_played[game['home_team']]
                    teams_last_played[game['home_team']] = current_date
                    # todo update row

                if game['away_team'] not in teams_last_played:
                    teams_last_played[game['away_team']] = get_date(f"{season1}-{month1:02}{day1:02}")
                    away_games_rested = timedelta(days=7)  # Start of season, use a suitable value
                else:
                    current_date = get_date(f"{season1}-{month1:02}{day1:02}")
                    away_games_rested = current_date - teams_last_played[game['away_team']]
                    teams_last_played[game['away_team']] = current_date

                try:
                    df_data.append({
                        'Unnamed: 0': 0,
                        'Date': f"{season1}-{month1:02}-{day1:02}",
                        'Home': game['home_team'],
                        'Away': game['away_team'],
                        'OU': game['total'][sportsbook],
                        'Spread': game['away_spread'][sportsbook],
                        'ML_Home': game['home_ml'][sportsbook],
                        'ML_Away': game['away_ml'][sportsbook],
                        'Points': game['away_score'] + game['home_score'],
                        'Win_Margin': game['home_score'] - game['away_score'],
                        'Days_Rest_Home': home_games_rested.days,
                        'Days_Rest_Away': away_games_rested.days
                    })
                except KeyError:
                    print(f"No {sportsbook} odds data found for game: {game}")
            time.sleep(random.randint(1, 3))
    begin_year_pointer = year[count]

    df = pd.DataFrame(df_data,)
    df.to_sql(f"odds_{season1}_MLB", con, if_exists="replace")  # Update table name with "_MLB"
con.close()
