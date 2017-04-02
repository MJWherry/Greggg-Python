import time
import threading
import os
import logging
import RPi.GPIO as GPIO #
from termcolor import colored


class SonarController:
    # region Variables

    # region GPIO Pin Numbers
    front_left_sonar_pin = 0
    front_middle_sonar_pin = 0
    front_right_sonar_pin = 0
    middle_back_sonar_pin = 0
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
    run_thread = False
    # endregion

    # endregion

    # region Accessors/Mutators
    def set_ping_time_interval(self, seconds):
        self.ping_time_interval = seconds

    def get_ping_time_interval(self):
        return self.ping_time_interval

    def get_all_sonar_sensor_distances(self):
        return self.front_middle_sonar_distance, ',', self.front_left_sonar_distance, ',', self.middle_back_sonar_distance, ',', self.front_right_sonar_distance

    def get_front_left_sonar_distance(self):
        return self.front_left_sonar_distance

    def get_front_middle_sonar_distance(self):
        return self.front_middle_sonar_distance

    def get_front_right_sonar_distance(self):
        return self.front_right_sonar_distance

    def get_middle_back_sonar_distance(self):
        return self.middle_back_sonar_distance

    # endregion

    # region Sonar functions
    def read_sonar_distances(self, pin):
        """
        Calculates the distance of the sensor on the pin.
        :param pin: The pin number
        :return: the distance in centimeters
        """
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, 0)
        time.sleep(0.000002)
        GPIO.output(pin, 1)
        time.sleep(0.000005)
        GPIO.output(pin, 0)
        GPIO.setup(pin, GPIO.IN)
        while GPIO.input(pin) == 0:
            start_time = time.time()
        while GPIO.input(pin) == 1:
            end_time = time.time()
        duration = end_time - start_time
        distance = ((duration * 34000 / 2)* 0.3937)
        return distance

    def print_sonar_distances(self):
        """
        Prints all the distances for all the sonars
        """
        print ' {:<6} {:<7} {:<15} {}'.format('Front', 'Left:', self.front_left_sonar_distance, 'inches.')
        print ' {:<6} {:<7} {:<15} {}'.format('Front', 'Middle:', self.front_middle_sonar_distance, 'inches.')
        print ' {:<6} {:<7} {:<15} {}'.format('Front', 'Right:', self.front_right_sonar_distance, 'inches.')
        print ' {:<6} {:<7} {:<15} {}'.format('Middle', 'Back:', self.middle_back_sonar_distance, 'inches.')

    # endregion

    # region Thread Functions
    def start_sonar_thread(self):
        self.thread.start()

    def sonar_thread_running(self):
        return threading.Thread.isAlive(self.thread)

    def stop_sonar_thread(self):
        None
        # Implement

    def restart_sonar_thread(self):
        None
        # Implement

    def run(self):
        while True:
            time.sleep(float(self.ping_time_interval))
            self.front_left_sonar_distance = self.read_sonar_distances(self.front_left_sonar_pin)
            time.sleep(.0002)
            self.front_middle_sonar_distance = self.read_sonar_distances(self.front_middle_sonar_pin)
            time.sleep(.0002)
            self.front_right_sonar_distance = self.read_sonar_distances(self.front_right_sonar_pin)
            time.sleep(.0002)
            self.middle_back_sonar_distance = self.read_sonar_distances(self.middle_back_sonar_pin)

    # endregion

    def __init__(self):
        self.load_settings()
        logging.info('Creating the sonar controller thread.')
        self.thread = threading.Thread(target=self.run, args=())
        # FIND A WAY TO TEST PINS
        try:
            GPIO.setmode(GPIO.BOARD)
        except:
            logging.error('Couldn\'t set GPIO mode')

    def load_settings(self):
        # Terminal commands
        logging.info('Loading terminal commands for the sonar controller.')
        try:
            cmd_file = open('info/Sonar/TerminalCommands.txt', 'r')
            for line in cmd_file:
                word_list = line.split(',')
                self.valid_terminal_commands.append((word_list[0], word_list[1].rstrip()))
            cmd_file.close()
        except:
            logging.error('Could not load the sonar controller command file.')

        # Sonar commands

        # Settings
        logging.info('Loading settings for the sonar controller.')
        try:
            cfg = False
            cfg_file = open('info/Config.txt', 'r')
            for line in cfg_file:
                if line == '[Sonar]':
                    cfg = True
                    continue
                elif line == '[/Sonar]':
                    break
                if cfg:
                    word_list = line.split('=')
                    if word_list[0] == 'ping_time_interval': self.ping_time_interval = float(word_list[1].rstrip())
                    elif word_list[0] == 'front_left_sonar_pin': self.front_left_sonar_pin = int(word_list[1].rstrip())
                    elif word_list[0] == 'front_middle_sonar_pin': self.front_middle_sonar_pin = int(word_list[1].rstrip())
                    elif word_list[0] == 'front_right_sonar_pin': self.front_right_sonar_pin = int(word_list[1].rstrip())
                    elif word_list[0] == 'middle_back_sonar_pin': self.middle_back_sonar_pin = int(word_list[1].rstrip())
                    else: logging.info('Invalid line in sonar config file: ',line)
            cfg_file.close()
        except:
            logging.error('Could not load the sonar controller config file.')

    def save_settings(self):
        cfg_file = open('info/Sonar/Config.txt', 'w')
        cfg_file.writelines(('ping_time_interval=', self.ping_time_interval))
        cfg_file.writelines(('front_left_sonar_pin=', self.front_left_sonar_pin))
        cfg_file.writelines(('front_middle_sonar_pin=', self.front_middle_sonar_pin))
        cfg_file.writelines(('front_right_sonar_pin=', self.front_right_sonar_pin))
        cfg_file.writelines(('middle_back_sonar_pin=', self.middle_back_sonar_pin))

    def parse_terminal_command(self, cmd):
        cmd = cmd.lower()
        if cmd == 'c':
            os.system(self.clear)
            self.print_menu()
        elif cmd == 'h':
            if self.hide_menu: self.hide_menu = False
            else: self.hide_menu = True
            self.parse_terminal_command('c')
        elif cmd == 'r':
            self.return_to_main_menu = True
        elif cmd == 'q':
            exit(0)

    def print_menu(self):
        if self.hide_menu: return
        print colored(' {:_^54}'.format(''), 'magenta')
        print ' {:1}{:^61}{:1}'.format(colored('|', 'magenta'), colored('SONAR TERMINAL', 'white'),
                                       colored('|', 'magenta'))
        print colored(' {}{:_^52}{}'.format('|', '', '|'), 'magenta')
        print ' {}{:^61}{}'.format(colored('|', 'magenta'), colored('CONNECTION INFORMATION', 'white'),
                                   colored('|', 'magenta'))
        print colored(' {}{:_^52}{}'.format('|', '', '|'), 'magenta')
        print ' {}{:^61}{}'.format(colored('|', 'magenta'), colored('TERMINAL COMMANDS', 'white'),
                                   colored('|', 'magenta'))
        for cmd in self.valid_terminal_commands:
            print ' {} \'{:^3}\' {:46} {}'.format(colored('|', 'magenta'), colored(cmd[0], 'white'), cmd[1],
                                                  colored('|', 'magenta'))
        print colored(' {}{:_^52}{}'.format('|', '', '|'), 'magenta')

    def terminal(self):
        os.system(self.clear)
        self.print_menu()
        while not self.return_to_main_menu:
            cmd = raw_input(colored(' Enter a command: ', 'cyan'))
            self.parse_terminal_command(cmd)
        self.return_to_main_menu = False
        return