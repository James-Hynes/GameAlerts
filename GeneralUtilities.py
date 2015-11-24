import time
import datetime
import requests
import threading
from random import choice


class CurrentNBADay:

    def __init__(self):
        self._valid_connection = self.check_valid_connection()
        self._data = self.get_data().json()['sports_content']['games']['game']
        self.simple_game_dict, self.adv_game_dict = self.return_simple_game_dict(), self.return_adv_game_dict()
        self.simple_game_list = self.convert_to_list(self.simple_game_dict)
        self.adv_game_list = self.convert_to_list(self.adv_game_dict)
        print(self.games_today_message())

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
                                 'start_time': self.change_time_pst(game['home_start_time'], game['home']['team_key'])}
                    for game in self._data}
        except KeyError:
            return {}

    def return_adv_game_dict(self):
        try:
            return {game['id']: {'teams': [game['visitor']['team_key'], game['home']['team_key']],
                                 'start_time': self.change_time_pst(game['home_start_time'], game['home']['team_key']),
                                 'city': game['city'], 'radio':
                                     {'visitor': game['broadcasters']['radio']['broadcaster'][0]['display_name'],
                                      'home': game['broadcasters']['radio']['broadcaster'][1]['display_name']},
                                 'arena': game['arena'],
                                 'tv': {broadcast['home_visitor']: broadcast['display_name']
                                        for broadcast in game['broadcasters']['tv']['broadcaster']}, 'period_time':
                                 game['period_time']} for game in self._data}

        except KeyError:
            return {}

    def games_today_message(self):
        form = 'Today, there are {0} games... \n' \
               'The games are as follows: {1}'
        num_games = len(self.simple_game_list)
        return form.format(num_games, self.string_game_list(self.simple_game_list))

    """
    def time_until_game(self, game):
        curr_time, game_start = self.time.split(' '), game['start_time'].split(' ')
        curr_hr, curr_min = curr_time[0].split(':')
        game_hr, game_min =  game_start[0].split(':')
        print(curr_hr, curr_min, game_hr, game_min)

        if curr_time[1] == game_start[1]:
            tl_min = (((int(game_hr) - int(curr_hr)) * 60) + (int(game_min) - int(curr_min)))
            return '{}:{}'.format((int(tl_min / 60)), '0{}'.format(tl_min % 60) if tl_min % 60 < 10 else tl_min % 60)
        elif curr_time[1] == 'AM' and game_start[1] == 'PM':
            pass
        return game['start_time'] # - self.time
    """

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

    @staticmethod
    def change_time_pst(inp_time, inp_team):
        std_time = int(inp_time)
        tz_change_pst = {-300: ['IND', 'CLE', 'DET', 'ATL', 'BOS', 'NYK', 'BKN', 'ORL', 'MIA', 'PHI', 'WAS', 'TOR'],
                         0: ['GSW', 'SAC', 'LAL', 'LAC', 'POR'], -100: ['PHX', 'UTA', 'DEN'], -200:
                         ['OKC', 'DAL', 'SAS', 'HOU', 'NOP', 'MEM', 'MIN', 'MIL', 'CHI', 'CHA']}
        start_time_pst = str(std_time + [tz for tz in tz_change_pst if inp_team in tz_change_pst[tz]][0])
        min = start_time_pst[-2::]
        hr = int(start_time_pst[:2] if len(start_time_pst) % 2 == 0 else start_time_pst[:1])
        start_time_pst = '{}:{} {}'.format(hr - 12 if hr > 12 else hr, min, 'AM' if hr < 12 else 'PM')
        return start_time_pst

    @staticmethod
    def string_game_list(g_list):
        return ', '.join(['{} @ {}'.format(game['teams'][0], game['teams'][1]) for game in g_list])
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
    def time(self):
        time_obj = datetime.datetime.fromtimestamp(time.time()).time()
        am_pm = 'AM' if time_obj.hour < 12 else 'PM'
        return '{}:{} {}'.format(time_obj.hour - 12 if am_pm == 'PM' and time_obj.hour > 12 else time_obj.hour - 0,
                                 '0{}'.format(time_obj.minute) if time_obj.minute < 10 else time_obj.minute, am_pm)



CurrentNBADay()
