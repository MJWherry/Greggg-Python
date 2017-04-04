import logging
import os
import threading
import time
import xml.etree.ElementTree as ET

#import RPi.GPIO as GPIO #
from termcolor import colored

GPIO = None

class SonarController:
    # region Variables

    # region GPIO Pin Numbers
    front_left_sonar_pin = 0
    front_middle_sonar_pin = 0
    front_right_sonar_pin = 0
    middle_back_sonar_pin = 0
    update_time_interval = 0
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

    # region Accessors/Mutators/Printers

    # region Accessors
    def get_update_time_interval(self):
        return self.update_time_interval

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

    # region Mutators
    def set_update_time_interval(self, seconds):
        self.update_time_interval = seconds
    # endregion

    # region Printers
    def print_update_time_interval(self):
        print ' {:<25} {:<15}'.format('Update time interval:', self.update_time_interval)

    def print_front_left_sonar_pin(self):
        print ' {:<25} {:<15}'.format('Front left sonar pin:', self.front_left_sonar_pin)

    def print_front_middle_sonar_pin(self):
        print ' {:<25} {:<15}'.format('Front middle sonar pin:', self.front_middle_sonar_pin)

    def print_front_right_sonar_pin(self):
        print ' {:<25} {:<15}'.format('Front right sonar pin:', self.front_right_sonar_pin)

    def print_middle_back_sonar_pin(self):
        print ' {:<25} {:<15}'.format('Middle back sonar pin:', self.middle_back_sonar_pin)

    def print_front_left_sonar_distance(self):
        print ' {:<25} {:<15}'.format('Front left sonar distance:', self.front_left_sonar_distance)

    def print_front_middle_sonar_distance(self):
        print ' {:<25} {:<15}'.format('Front middle sonar distance:', self.front_middle_sonar_distance)

    def print_front_right_sonar_distance(self):
        print ' {:<25} {:<15}'.format('Front right sonar distance:', self.front_right_sonar_distance)

    def print_middle_back_sonar_distance(self):
        print ' {:<25} {:<15}'.format('Middle back sonar distance:', self.middle_back_sonar_distance)

    def print_all_sonar_distances(self):
        self.print_front_left_sonar_distance()
        self.print_front_middle_sonar_distance()
        self.print_front_right_sonar_distance()
        self.print_middle_back_sonar_distance()

    # endregion

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

    # endregion

    # region Thread Functions
    def start_sonar_thread(self):
        self.run_thread = True
        self.thread.start()

    def sonar_thread_running(self):
        return threading.Thread.isAlive(self.thread)

    def stop_sonar_thread(self):
        self.run_thread = False
        # Test implementation

    def restart_sonar_thread(self):
        None
        # Implement (how)

    def run(self):
        while self.run_thread:
            time.sleep(float(self.update_time_interval))
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
            None
            # GPIO.setmode(GPIO.BOARD)
        except:
            logging.error('Couldn\'t set GPIO mode')

    def load_settings(self):
        tree = ET.parse('config.xml')
        root = tree.getroot()
        device = root.find('sonar')
        for child in device.iter('terminal_commands'):
            for command in child.iter('command'):
                self.valid_terminal_commands.append((command.attrib['name'], command.attrib['description']))
        for child in device.iter('setting'):
            if child.attrib['name'] == 'update_time_interval': self.update_time_interval = float(child.attrib['value'])
            elif child.attrib['name'] == 'front_left_sonar_pin': self.front_left_sonar_pin = int(child.attrib['value'])
            elif child.attrib['name'] == 'front_middle_sonar_pin': self.front_middle_sonar_pin = int(child.attrib['value'])
            elif child.attrib['name'] == 'front_right_sonar_pin': self.front_right_sonar_pin = int(child.attrib['value'])
            elif child.attrib['name'] == 'middle_back_sonar_pin': self.middle_back_sonar_pin = int(child.attrib['value'])
            else: logging.info('Invalid line in sonar config: ', child.attrib['name'])

    def save_settings(self):
        cfg_file = open('info/Sonar/Config.txt', 'w')
        cfg_file.writelines(('update_time_interval=', self.update_time_interval))
        cfg_file.writelines(('front_left_sonar_pin=', self.front_left_sonar_pin))
        cfg_file.writelines(('front_middle_sonar_pin=', self.front_middle_sonar_pin))
        cfg_file.writelines(('front_right_sonar_pin=', self.front_right_sonar_pin))
        cfg_file.writelines(('middle_back_sonar_pin=', self.middle_back_sonar_pin))

    def print_settings(self):
        print ' SONAR CONTROLLER SETTINGS'
        self.print_update_time_interval()
        self.print_front_left_sonar_pin()
        self.print_front_middle_sonar_pin()
        self.print_front_right_sonar_pin()
        self.print_middle_back_sonar_pin()

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