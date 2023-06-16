from datetime import datetime
import re
import requests
import pandas as pd

games_header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/57.0.2987.133 Safari/537.36',
    'Dnt': '1',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'en',
    'origin': 'http://www.mlb.com',
    'Referer': 'https://github.com'
}

data_headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Host': 'statsapi.mlb.com',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.mlb.com/',
    'Connection': 'keep-alive'
}


def get_json_data(url):
    raw_data = requests.get(url, headers=data_headers)
    try:
        json = raw_data.json()
    except Exception as e:
        print(e)
        return {}
    return json


def get_todays_games_json(url):
    raw_data = requests.get(url, headers=games_header)
    json = raw_data.json()
    return json.get('dates', [])


def to_data_frame(data):
    try:
        return pd.DataFrame(data)
    except Exception as e:
        print(e)
        return pd.DataFrame()


def create_todays_games(input_list):
    games = []
    for game in input_list:
        home_team = game['teams']['home']['team']['name']
        away_team = game['teams']['away']['team']['name']
        games.append([home_team, away_team])
    return games


def create_todays_games_from_odds(input_dict):
    games = []
    for game in input_dict.keys():
        home_team, away_team = game.split(":")
        games.append([home_team, away_team])
    return games


def get_date(date_string):
    year, month, day = re.search(r'(\d+)-(\d+)-(\d+)', date_string).groups()
    return datetime.strptime(f"{year}-{month}-{day}", '%Y-%m-%d')
