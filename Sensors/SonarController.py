import logging
import os
import sys
import time
import RPi.GPIO as GPIO
from Skeletons import SettingsManager
from termcolor import colored
from Skeletons import SleepableThread

logging.basicConfig(filename='/home/pi/Desktop/greggg-python/run.log', level=logging.DEBUG, format=('%(asctime)s %(levelname)s %(message)s'))


class SonarController(SleepableThread.SleepableThread):
    # region Variables

    SC = SettingsManager.SettingsManager()

    # region GPIO Pin Numbers
    front_left_sonar_pin = 37
    front_middle_sonar_pin = 35
    front_right_sonar_pin = 33
    middle_back_sonar_pin = 31
    update_time_interval = 0.2
    max_cpu_iterations = 100000
    # endregion

    # region Distances
    front_left_sonar_distance = 0
    front_middle_sonar_distance = 0
    front_right_sonar_distance = 0
    middle_back_sonar_distance = 0
    # endregion

    # region ETC Variables
    valid_terminal_commands = []
    hide_menu = False
    return_to_main_menu = False
    clear = 'cls' if os.name == 'nt' else 'clear'
    # endregion

    # region Thread Variables

    # endregion

    # endregion

    # region Sonar functions
    def read_sonar_distances(self, pin):
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, 0)
        time.sleep(0.000002)
        GPIO.output(pin, 1)
        time.sleep(0.000005)
        GPIO.output(pin, 0)
        x = 0
        while GPIO.input(pin) == 0 and x < self.max_cpu_iterations:
            GPIO.setup(pin, GPIO.IN)
            start_time = time.time()
            x += 1
        if x >= self.max_cpu_iterations:
            return 0, False
        x = 0
        while GPIO.input(pin) == 1 and x < self.max_cpu_iterations:
            GPIO.setup(pin, GPIO.IN)
            end_time = time.time()
            x += 1
        if x >= self.max_cpu_iterations:
            return 0, False
        try:
            duration = end_time - start_time
        except:
            return 0, False
        distance = ((duration * 34000 / 2) * 0.3937)
        return distance, True

    def update_sonar_distances(self):
        update = self.read_sonar_distances(self.front_left_sonar_pin)
        if update[1]:
            self.front_left_sonar_distance = update[0]
        update = self.read_sonar_distances(self.front_right_sonar_pin)
        if update[1]:
            self.front_right_sonar_distance = update[0]
        time.sleep(.0002)
        update = self.read_sonar_distances(self.front_middle_sonar_pin)
        if update[1]:
            self.front_middle_sonar_distance = update[0]
        update = self.read_sonar_distances(self.middle_back_sonar_pin)
        if update[1]:
            self.middle_back_sonar_distance = update[0]

    # endregion

    # region Thread Functions
    def run(self):
        while self.thread_state != 4:
            if self.thread_state == 3:
                while self.thread_state == 3:
                    time.sleep(1)
            else:
                time.sleep(float(self.update_time_interval))
                self.update_sonar_distances()

    # endregion

    def __init__(self):
        self.SC.load_settings('sonar')
        self.update_time_interval = float(self.SC.get_setting_value('update_time_interval'))
        self.front_left_sonar_pin = int(self.SC.get_setting_value('front_left_sonar_pin'))
        self.front_middle_sonar_pin = int(self.SC.get_setting_value('front_middle_sonar_pin'))
        self.front_right_sonar_pin = int(self.SC.get_setting_value('front_right_sonar_pin'))
        self.middle_back_sonar_pin = int(self.SC.get_setting_value('middle_back_sonar_pin'))
        self.max_cpu_iterations = int(self.SC.get_setting_value('max_cpu_iterations'))
        try:
            GPIO.setmode(GPIO.BOARD)
            logging.info('(SONAR) Object created successfully.')
        except:
            logging.error('(SONAR) Couldn\'t set GPIO mode to GPIO.BOARD.')
        super(SonarController, self).__init__()

    def parse_terminal_command(self, cmd):
        cmd = cmd.lower()
        split = cmd.split()
        type = split[0]
        if cmd == 'c':
            os.system(self.clear)
            self.print_menu()
        elif cmd == 'h':
            if self.hide_menu:
                self.hide_menu = False
            else:
                self.hide_menu = True
            self.parse_terminal_command('c')
        elif cmd == 'r':
            self.return_to_main_menu = True
        elif cmd == 'q':
            exit(0)
        elif type == 'set':
            pass
        elif type == 'thread':
            self.parse_thread_command(cmd.split()[1])
        elif type == 'print' or split[0] == 'get':
            data = ' '
            for cmd in split:
                if cmd == 'fl' or cmd == 'frontleft' or cmd == 'front_left':
                    data += str(self.front_left_sonar_distance) + ','
                elif cmd == 'fm' or cmd == 'frontmiddle' or cmd == 'front_middle':
                    data += str(self.front_middle_sonar_distance) + ','
                elif cmd == 'fr' or cmd == 'frontright' or cmd == 'front_right':
                    data += str(self.front_right_sonar_distance) + ','
                elif cmd == 'mb' or cmd == 'middleback' or cmd == 'middle_back':
                    data += str(self.middle_back_sonar_distance) + ','
                elif cmd == 'update_time_interval' or cmd == 'interval':
                    data += str(self.update_time_interval) + ','
                elif cmd == 'settings':
                    data += self.SC.get_settings_string() + ','
                elif cmd == 'all':
                    data += str('{},{},{},{}'.format(self.front_middle_sonar_distance, self.front_left_sonar_distance,
                                                     self.middle_back_sonar_distance,
                                                     self.front_right_sonar_distance)) + ','
            data = data[:-1] + ';'
            if type == 'get':
                return data
            elif type == 'print':
                print colored(data, 'green')

    def print_menu(self):
        if self.hide_menu: return
        bar = colored('|', 'magenta')
        print colored(' {:_^54}'.format(''), 'magenta')
        print ' {} {:^59} {}'.format(bar, colored('SONAR TERMINAL', 'white'), bar)
        print colored(' {}{:_^52}{}'.format('|', '', '|'), 'magenta')
        print ' {} {:^59} {}'.format(bar, colored('CONNECTION INFORMATION', 'white'), bar)
        print ' {} {:59} {}'.format(bar, colored('STATUS: {}'.format('is connected? implement'), 'white'), bar)
        print ' {} {:59} {}'.format(bar, colored('UPDATE TIME INTERVAL: {}'.format(self.update_time_interval), 'white'),
                                    bar)
        print ' {} {:33} {:34} {}'.format(bar, colored('FRONT LEFT PIN: {}'.format(self.front_left_sonar_pin), 'white'),
                                          colored('FRONT MIDDLE PIN: {}'.format(self.front_middle_sonar_pin), 'white'),
                                          bar)
        print ' {} {:33} {:34} {}'.format(bar,
                                          colored('FRONT RIGHT PIN: {}'.format(self.front_right_sonar_pin), 'white'),
                                          colored('MIDDLE BACK PIN: {}'.format(self.middle_back_sonar_pin), 'white'),
                                          bar)
        print colored(' {}{: ^52}{}'.format('|', '', '|'), 'magenta')
        print ' {} {:68} {}'.format(bar, colored('THREAD: {}'.format(self.thread_status()), 'white'), bar)
        print ' {} {:59} {}'.format(bar, colored('THREAD PROCESS ID: {}'.format(self.thread_pid), 'white'), bar)
        print ' {} {:59} {}'.format(bar, colored('THREAD SPAWN COUNT: {}'.format(self.thread_spawn_count), 'white'),
                                    bar)
        print colored(' {}{:_^52}{}'.format('|', '', '|'), 'magenta')

    def terminal(self):
        os.system(self.clear)
        sys.stdout.write("\x1b]2;Sonar Controller Terminal\x07")
        self.print_menu()
        while not self.return_to_main_menu:
            cmd = raw_input(colored(' Enter a command: ', 'cyan'))
            self.parse_terminal_command(cmd)
        self.return_to_main_menu = False
        return


if __name__ == "__main__":
    sc = SonarController()
    sc.terminal()
