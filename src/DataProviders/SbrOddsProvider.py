import requests
api_key = "b0d5be034629ee1c6337a0bf380a1ef3"
odds_provider = OddsAPIProvider(api_key)


class OddsAPIProvider:
    def __init__(self, api_key, sportsbook="fanduel"):
        self.api_key = api_key
        self.sportsbook = sportsbook

    def get_odds(self):
        url = "https://api.the-odds-api.com/v4/sports/baseball_mlb/odds"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        params = {"region": "us", "bookmaker": self.sportsbook}
        
        response = requests.get(url, headers=headers, params=params)
        data = response.json()

        dict_res = {}
        for game in data["data"]:
            home_team_name = game["teams"][0]
            away_team_name = game["teams"][1]
            money_line_home_value = money_line_away_value = totals_value = None

            for site in game["sites"]:
                if site["site_key"] == self.sportsbook:
                    if "odds" in site:
                        money_line_home_value = site["odds"]["h2h"][0]
                        money_line_away_value = site["odds"]["h2h"][1]
                        totals_value = site["odds"]["totals"]["points"]

            dict_res[home_team_name + ':' + away_team_name] = {
                'under_over_odds': totals_value,
                home_team_name: {'money_line_odds': money_line_home_value},
                away_team_name: {'money_line_odds': money_line_away_value}
            }
        return dict_res
