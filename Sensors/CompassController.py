import logging
import os
import sys
import threading
import time
import xml.etree.ElementTree as ET
from termcolor import colored

logging.basicConfig(filename='/home/pi/Desktop/greggg-python/run.log', level=logging.DEBUG, format=('%(asctime)s %(levelname)s %(message)s'))

try:
    import hmc5883l

    logging.info('(COMPASS) Imported hmc5883l.')
except:
    logging.error('(COMPASS) Couldn\'t import hmc5883l.')


class CompassController:
    # region Variables

    # region I2C settings
    i2c_port = 1
    i2c_bus_address = 0x1E
    # endregion

    # region Compass settings
    try:
        compass = hmc5883l
        logging.info('(COMPASS) Compass set to hmc5883l instance.')
    except:
        logging.error('(COMPASS) Couldn\'t set compass to hmc5883l instance.')
    gauss = 0
    declination_degrees = -9
    declination_minutes = 23
    update_time_interval = 0.5
    current_heading = None
    # endregion

    # region ETC Variables
    thread = None
    valid_terminal_commands = []
    hide_menu = False
    return_to_main_menu = False
    clear = 'cls' if os.name == 'nt' else 'clear'

    thread_status = colored('NOT STARTED', 'red')
    thread_started = False
    thread_running = False
    thread_sleeping = False
    thread_ended = False

    # endregion

    # endregion

    # region Compass functions

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
            self.thread_status = colored('SLEEPING', 'yellow')
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
        if not self.thread_started:
            print ' Thread hasn\'t started yet.'
        else:
            self.thread_running = False
            self.thread_sleeping = False
            self.thread_ended = True
            self.thread_started = True
            self.thread_status = colored('ENDED', 'red')

    def restart_compass_thread(self):
        None
        # Implement

    def get_compass_thread_status(self):
        return self.thread_status

    def run(self):
        print ' Starting compass thread...'
        logging.info('(COMPASS) Thread started.')
        while self.thread_running:
            if self.thread_sleeping:
                while self.thread_sleeping:
                    time.sleep(1)
            else:
                self.current_heading = str(self.compass.degrees(self.compass.heading()))
                time.sleep(self.update_time_interval)

    # endregion

    def __init__(self):
        self.load_settings()
        try:
            self.compass = hmc5883l.hmc5883l(gauss=self.gauss,
                                             declination=(self.declination_degrees,self.declination_minutes))
            logging.info('(COMPASS) Compass object created.')
        except:
            logging.error('(COMPASS) Couldn\'t create compass object.')
        self.thread = threading.Thread(target=self.run, args=())

    def load_settings(self):
        logging.info('(COMPASS) Loading settings.')
        try:
            tree = ET.parse('/home/pi/Desktop/greggg-python/config.xml')
        except:
            logging.warning('(COMPASS) Couldn\'t load config file.')
            return
        root = tree.getroot()
        device = root.find('compass')
        for child in device.iter('terminal_commands'):
            for command in child.iter('command'):
                self.valid_terminal_commands.append((command.attrib['name'], command.attrib['description']))
        for child in device.iter('setting'):
            if child.attrib['name'] == 'i2c_port':
                self.i2c_port = int(child.attrib['value'])
            elif child.attrib['name'] == 'i2c_bus_address':
                self.i2c_bus_address = str(child.attrib['value'])
            elif child.attrib['name'] == 'declination_minutes':
                self.declination_minutes = int(child.attrib['value'])
            elif child.attrib['name'] == 'declination_degrees':
                self.declination_degrees = int(child.attrib['value'])
            elif child.attrib['name'] == 'gauss':
                self.gauss = float(child.attrib['value'])
            elif child.attrib['name'] == 'update_time_interval':
                self.update_time_interval = float(child.attrib['value'])
        logging.info('(COMPASS) Settings loaded.')

    def save_settings(self):
        None

    def parse_terminal_command(self, cmd):
        cmd = cmd.lower()
        type = cmd.split()[0]
        parameters = cmd.replace(type, '').split()
        split = cmd.split()

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
        elif type == 'thread':
            if split[1] == 'start':
                self.start_compass_thread()
                self.parse_terminal_command('c')
            elif split[1] == 'stop':
                self.stop_compass_thread()
                self.parse_terminal_command('c')
            elif split[1] == 'sleep':
                self.sleep_compass_thread()
                self.parse_terminal_command('c')
            elif split[1] == 'wake':
                self.wake_compass_thread()
                self.parse_terminal_command('c')
        elif type == 'get' or type == 'print':
            data = ' '
            for cmd in parameters:
                if cmd == 'heading':
                    data += '{},'.format(self.compass.degrees(self.compass.heading()))
                elif cmd == 'declination_degrees':
                    data += '{},'.format(self.declination_degrees)
                elif cmd == 'declination_minutes':
                    data += '{},'.format(self.declination_minutes)
                elif cmd == 'declination':
                    data += '({}, {}),'.format(self.declination_degrees,self.declination_minutes)
                elif cmd == 'update_time_interval' or cmd == 'interval':
                    data += '{},'.format(self.update_time_interval)
                elif cmd == 'i2c_bus_address' or cmd == 'i2c_addr':
                    data += '{},'.format('{}'.format(self.i2c_bus_address, '#04x'))
                elif cmd == 'i2c_bus_port' or cmd == 'i2c_port':
                    data += '{},'.format(self.i2c_port)
            data = data[:-1] + ';'
            if type == 'get':
                return data
            elif type == 'print':
                print colored(data, 'green')

    def print_menu(self):
        if self.hide_menu: return
        bar = colored('|', 'magenta')
        print colored(' {:_^54}'.format(''), 'magenta')
        print ' {:1}{:^61}{:1}'.format(colored('|', 'magenta'), colored('COMPASS TERMINAL', 'white'),
                                       colored('|', 'magenta'))
        print colored(' {}{:_^52}{}'.format('|', '', '|'), 'magenta')
        print ' {}{:^61}{}'.format(bar, colored('CONNECTION INFORMATION', 'white'), bar)
        print ' {} {:59} {}'.format(bar, colored('STATUS: {}'.format('is connected? implement'), 'white'), bar)
        print ' {} {:33} {:34} {}'.format(bar, colored('I2C PORT: {}'.format(self.i2c_port), 'white'),
                                          colored('I2C ADDRESS: {}'.format(self.i2c_bus_address), 'white'), bar)
        print ' {} {:33} {:34} {}'.format(bar,
                                          colored('DECLINATION MINUTES: {}'.format(self.declination_minutes), 'white'),
                                          colored('DECLINATION DEGREES: {}'.format(self.declination_degrees), 'white'),
                                          bar)
        print colored(' {}{:52}{}'.format('|', '', '|'), 'magenta')
        print ' {} {:68} {}'.format(bar, colored('THREAD: {}'.format(self.thread_status), 'white'),bar)
        print colored(' {}{:_^52}{}'.format('|', '', '|'), 'magenta')
        print ' {}{:^61}{}'.format(bar, colored('TERMINAL COMMANDS', 'white'), bar)
        for cmd in self.valid_terminal_commands:
            print ' {} \'{:^3}\' {:46} {}'.format(bar, colored(cmd[0], 'white'), cmd[1], bar)
        print colored(' {}{:_^52}{}'.format('|', '', '|'), 'magenta')

    def terminal(self):
        os.system(self.clear)
        sys.stdout.write("\x1b]2;Compass Controller Terminal\x07")
        self.print_menu()
        while not self.return_to_main_menu:
            cmd = raw_input(colored(' Enter a command: ', 'cyan'))
            self.parse_terminal_command(cmd)
        self.return_to_main_menu = False


if __name__ == "__main__":
    cc = CompassController()
    cc.terminal()
