import logging
import os
import threading
import time
import sys
import xml.etree.ElementTree as ET
from termcolor import colored

logging.basicConfig(filename='/home/pi/Desktop/greggg-python/run.log', level=logging.DEBUG, format=('%(asctime)s %(levelname)s %(message)s'))

try:
    import RPi.GPIO as GPIO

    logging.info('(SONAR) RPi.GPIO imported.')
except:
    logging.error('(SONAR) Couldn\'t import RPi.GPIO.')


class SonarController:
    # region Variables

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
    thread = None
    valid_terminal_commands = []
    hide_menu = False
    return_to_main_menu = False
    clear = 'cls' if os.name == 'nt' else 'clear'

    thread_status = 'NONE'
    thread_started = False
    thread_running = False
    thread_sleeping = False
    thread_ended = False

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
    def start_compass_thread(self):
        if not self.thread_started:
            self.thread.start()
            self.thread_started = True
            self.thread_running = True
            self.thread_ended = False
            self.thread_sleeping = False
            self.thread_status = colored('RUNNING', 'green')
        elif self.thread_ended:
            print ' Thread already ran. Try restarting thread.'
        elif self.thread_sleeping:
            print ' Thread is sleeping. Cannot start thread.'
        elif self.thread_running and self.thread_running:
            print ' Thread is currently running. Cannot start'
        else:
            print ' Error, unknown case.'

    def sleep_compass_thread(self):
        if not self.thread_ended and self.thread_running and self.thread_started:
            self.thread_sleeping = True
            self.thread_running = False
            self.thread_status = colored('SLEEPING', 'orange')
        elif self.thread_ended:
            print ' Thread already ran. Cannot sleep.'
        elif not self.thread_started or not self.thread_running:
            print ' Thread has not started yet or is not running.'

    def wake_compass_thread(self):
        if self.thread_sleeping:
            self.thread_sleeping = False
            self.thread_running = True
            self.thread_status = colored('RUNNING', 'green')
        elif self.thread_ended:
            print ' Cannot wake a thread that\'s ended.'
        elif self.thread_running:
            print ' Threads already running not sleeping. '

    def stop_compass_thread(self):
        self.thread_running = False
        self.thread_sleeping = False
        self.thread_ended = True
        self.thread_started = True
        self.thread_status = colored('NOT RUNNING', 'red')

    def restart_sonar_thread(self):
        None
        # Implement

    def run(self):
        print ' Starting sonar thread...'
        logging.info('(SONAR) Thread started.')
        while self.thread_running:
            if self.thread_sleeping:
                while self.thread_sleeping:
                    time.sleep(1)
            else:
                time.sleep(float(self.update_time_interval))
                self.update_sonar_distances()

    # endregion

    def __init__(self):
        self.load_settings()
        self.thread = threading.Thread(target=self.run, args=())
        try:
            GPIO.setmode(GPIO.BOARD)
            logging.info('(SONAR) Object created successfully.')
        except:
            logging.error('(SONAR) Couldn\'t set GPIO mode to GPIO.BOARD.')

    def load_settings(self):
        logging.info('(SONAR) Loading settings.')
        try:
            tree = ET.parse('/home/pi/Desktop/greggg-python/config.xml')
        except:
            logging.warn('(SONAR) Could\'t open the config file.')
            return
        root = tree.getroot()
        device = root.find('sonar')
        for child in device.iter('terminal_commands'):
            for command in child.iter('command'):
                self.valid_terminal_commands.append((command.attrib['name'], command.attrib['description']))
        for child in device.iter('setting'):
            if child.attrib['name'] == 'update_time_interval':
                self.update_time_interval = float(child.attrib['value'])
            elif child.attrib['name'] == 'front_left_sonar_pin':
                self.front_left_sonar_pin = int(child.attrib['value'])
            elif child.attrib['name'] == 'front_middle_sonar_pin':
                self.front_middle_sonar_pin = int(child.attrib['value'])
            elif child.attrib['name'] == 'front_right_sonar_pin':
                self.front_right_sonar_pin = int(child.attrib['value'])
            elif child.attrib['name'] == 'middle_back_sonar_pin':
                self.middle_back_sonar_pin = int(child.attrib['value'])
            elif child.attrib['name'] == 'max_cpu_iterations':
                self.max_cpu_iterations = int(child.attrib['value'])
        logging.info('(SONAR) Settings loaded.')

    def save_settings(self):
        None

    def get_settings(self):
        data = 'SONAR_SETTINGS{' \
               + 'UPDATE_TIME_INTERVAL(' + str(self.update_time_interval) + '),' \
               + 'FRONT_LEFT_SONAR_PIN(' + str(self.front_left_sonar_pin) + '),' \
               + 'FRONT_MIDDLE_SONAR_PIN(' + str(self.front_middle_sonar_pin) + '),' \
               + 'FRONT_RIGHT_SONAR_PIN(' + str(self.front_left_sonar_pin) + '),' \
               + 'MIDDLE_BACK_SONAR_PIN(' + str(self.middle_back_sonar_pin) + ')' \
               + '}'
        return data

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
            None
        elif type == 'thread':
            if split[1] == 'start':
                self.start_sonar_thread()
                self.parse_terminal_command('c')
            elif split[1]=='stop':
                self.stop_sonar_thread()
                self.parse_terminal_command('c')
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
                    data += self.get_settings() + ','
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
        print ' {} {:68} {}'.format(bar, colored(
            'THREAD: {}'.format(colored('RUNNING', 'green') if self.sonar_thread_running() else colored(
                'NOT RUNNING', 'red')), 'white'), bar)
        print colored(' {}{:_^52}{}'.format('|', '', '|'), 'magenta')
        print ' {} {:^59} {}'.format(colored('|', 'magenta'), colored('TERMINAL COMMANDS', 'white'),
                                     colored('|', 'magenta'))
        for cmd in self.valid_terminal_commands:
            print ' {} \'{:^3}\' {:46} {}'.format(colored('|', 'magenta'), colored(cmd[0], 'white'), cmd[1],
                                                  colored('|', 'magenta'))
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
