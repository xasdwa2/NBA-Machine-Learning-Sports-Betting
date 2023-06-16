import os
import sqlite3
import numpy as np
import pandas as pd
import sys
from datetime import datetime
from tqdm import tqdm
import requests

sys.path.insert(1, os.path.join(sys.path[0], '..'))
from Utils.Dictionaries import team_index_current

# MLB API endpoint for today's games
api_url = "https://statsapi.mlb.com/api/v1/schedule/games/?sportId=1"

df = pd.DataFrame()
scores = []
win_margin = []
OU = []
OU_Cover = []
games = []
days_rest_away = []
days_rest_home = []
teams_con = sqlite3.connect("../../Data/teams.sqlite")
odds_con = sqlite3.connect("../../Data/odds.sqlite")

# Fetch today's MLB games from the API
response = requests.get(api_url)
if response.status_code == 200:
    game_data = response.json()["dates"][0]["games"]
else:
    print("Error fetching MLB games from the API.")
    sys.exit(1)

for game in tqdm(game_data):
    home_team = game["teams"]["home"]["team"]["name"]
    away_team = game["teams"]["away"]["team"]["name"]

    date = datetime.strptime(game["gameDate"], "%Y-%m-%dT%H:%M:%SZ")
    date_str = date.strftime("%Y-%m-%d")
    year = date.strftime("%Y")
    month = date.strftime("%m")
    day = date.strftime("%d")

    team_df = pd.read_sql_query(f"select * from \"teams_{year}-{month}-{day}\"", teams_con, index_col="index")

    if len(team_df.index) == 30:
        scores.append(None)
        OU.append(None)
        days_rest_home.append(None)
        days_rest_away.append(None)
        win_margin.append(None)
        OU_Cover.append(None)

        home_team_series = team_df.iloc[team_index_current.get(home_team)]
        away_team_series = team_df.iloc[team_index_current.get(away_team)]

        game = pd.concat([home_team_series, away_team_series.rename(index={col: f"{col}.1" for col in team_df.columns.values})])
        games.append(game)

odds_con.close()
teams_con.close()

if len(games) > 0:
    season = pd.concat(games, ignore_index=True, axis=1)
    season = season.T
    frame = season.drop(columns=['TEAM_ID', 'CFID', 'CFPARAMS', 'Unnamed: 0', 'Unnamed: 0.1', 'CFPARAMS.1', 'TEAM_ID.1', 'CFID.1'])
    frame['Score'] = np.asarray(scores)
    frame['Home-Team-Win'] = np.asarray(win_margin)
    frame['OU'] = np.asarray(OU)
    frame['OU-Cover'] = np.asarray(OU_Cover)
    frame['Days-Rest-Home'] = np.asarray(days_rest_home)
    frame['Days-Rest-Away'] = np.asarray(days_rest_away)

    # Fix types
    for field in frame.columns.values:
        if 'TEAM_' in field or 'Date' in field or field not in frame:
            continue
        frame[field] = frame[field].astype(float)

    con = sqlite3.connect("../../Data/dataset.sqlite")
    frame.to_sql("mlb_dataset", con, if_exists="replace")
    con.close()
else:
    print("No MLB games found for today.")
