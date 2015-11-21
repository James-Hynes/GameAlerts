import time
import datetime
import requests
import threading


class CurrentNBADay:

    def __init__(self):
        self._valid_connection = self.check_valid_connection()
        self._data = self.get_data().json()['sports_content']['games']['game']
        self.simple_game_dict, self.adv_game_dict = self.return_simple_game_dict(), self.return_adv_game_dict()
        self.simple_game_list = self.convert_to_list(self.simple_game_dict)
        self.adv_game_list = self.convert_to_list(self.adv_game_dict)

        print(self.adv_game_dict)

    def get_data(self, attempt=1):
        if self._valid_connection:
            try:
                return requests.get(self.curr_date_url)
            except requests.RequestException:
                return self.handle_error(self.get_data, attempt)
        else:
            self.handle_no_connection()
            return self.get_data()

    def handle_no_connection(self):
        connection_thread = threading.Thread(target=self.connection_check_loop)
        connection_thread.start(), connection_thread.join()

    def connection_check_loop(self, delay=2):
        while not self.check_valid_connection():
            time.sleep(delay)
            continue
        else:
            self._valid_connection = True

    def return_simple_game_dict(self):
        try:
            return {game['id']: {'teams': [game['visitor']['team_key'], game['home']['team_key']],
                                 'home_start': game['home_start_time']} for game in self._data}
        except KeyError:
            return {}

    def return_adv_game_dict(self):
        try:
            return {game['id']: {'teams': [game['visitor']['team_key'], game['home']['team_key']],
                                 'home_start': game['home_start_time'], 'city': game['city'],
                                 'radio': {'visitor': game['broadcasters']['radio']['broadcaster'][0]['display_name'],
                                           'home': game['broadcasters']['radio']['broadcaster'][1]['display_name']},
                                 'arena': game['arena'],
                                 'tv': {broadcast['home_visitor']: broadcast['display_name']
                                        for broadcast in game['broadcasters']['tv']['broadcaster']}, 'period_time':
                                 game['period_time']} for game in self._data}

        except KeyError:
            return {}

    @staticmethod
    def handle_error(callback, attempt, max_attempts=3):
        if attempt <= max_attempts:
            print("Attempt {0} failed ... trying again".format(attempt))
            return callback(attempt+1)
        else:
            return None

    @staticmethod
    def check_valid_connection():
        try:
            requests.get("https://www.google.com")
            return True
        except requests.ConnectionError:
            return False

    @staticmethod
    def convert_to_list(convert_dict):
        return [convert_dict[item] for item in convert_dict]

    """
    def handle_connection_error(self, callback):
        check_connection_thread = threading.Thread(self.check_connection)
        check_connection_thread.start()
        if not check_connection_thread.is_alive():
            return callback()

    def check_connection(self):
        while not self._valid_connection:
            try:
                requests.get("https://www.google.com")
                print(self._valid_connection)
                self._valid_connection = True
                return True
            except requests.RequestException:
                continue
    """

    @property
    def curr_date_url(self):
        if self.date:
            return "http://data.nba.com/data/1h/json/cms/noseason/scoreboard/{}/games.json".format(self.date)
        else:
            return None

    @property
    def date(self):
        curr_date = datetime.date.fromtimestamp(time.time())
        return "{}{}{}".format(curr_date.year, curr_date.month, curr_date.day)

    @property
    def year(self):
        return datetime.date.fromtimestamp(time.time()).year

CurrentNBADay()
