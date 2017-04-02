# import hmc5883l
import logging
import os
import threading
import time

from termcolor import colored


class CompassController:
    # region Variables

    # region I2C settings
    i2c_port = None
    i2c_bus_address = None
    # endregion

    # region Compass settings
    # compass = hmc5883l

    gauss = None
    declination = (0, 0)
    update_time_interval = 0
    current_heading = None
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
    def set_gauss(self, gauss):
        self.gauss = gauss

    def set_declination(self, degrees, minutes):
        self.declination = (degrees, minutes)

    def set_update_time_interval(self, seconds):
        self.update_time_interval = seconds

    def set_i2c_port(self, port):
        self.i2c_port = port

    def set_i2c_bus_address(self, bus_address):
        self.i2c_bus_address = bus_address

    def get_gauss(self):
        return self.gauss

    def get_declination(self):
        return self.declination

    def get_update_time_interval(self):
        return self.update_time_interval

    def get_i2c_port(self):
        return self.i2c_port

    def get_i2c_bus_address(self):
        return self.i2c_bus_address

    # endregion

    # region Compass functions
    def print_compass(self):
        print self.compass

    def print_compass_heading(self):
        print 'Heading: ' + str(self.compass.degrees(self.compass.heading())) + '     '

    # endregion

    # region Thread Functions
    def start_compass_thread(self):
        self.thread.start()

    def compass_thread_running(self):
        return threading.Thread.isAlive(self.thread)

    def stop_compass_thread(self):
        None
        # Implement

    def restart_compass_thread(self):
        None
        # Implement

    def run(self):
        while True:
            self.current_heading = str(self.compass.degrees(self.compass.heading()))
            time.sleep(self.update_time_interval)

    # endregion

    def __init__(self):
        self.load_settings()
        # self.compass = hmc5883l.hmc5883l(self.i2c_port,self.i2c_bus_address,self.gauss, self.declination)

    def load_settings(self):
        # Terminal commands
        logging.info('Loading terminal commands for the compass controller.')
        try:
            cmd_file = open('info/Compass/TerminalCommands.txt', 'r')
            for line in cmd_file:
                word_list = line.split(',')
                self.valid_terminal_commands.append((word_list[0], word_list[1].rstrip()))
            cmd_file.close()
        except:
            logging.error('Could not load the compass controller command file.')

        # Settings
        logging.info('Loading settings for the compass controller.')
        try:
            cfg_file = open('info/Config.txt', 'r')
            cfg = False
            for line in cfg_file:
                if line.rstrip() == '[Compass]':
                    cfg = True
                    continue
                elif line.rstrip() == '[/Compass]':
                    break
                if cfg:
                    word_list = line.split('=')
                    if word_list[0] == 'i2c_port':
                        self.i2c_port = int(word_list[1].rstrip())
                    elif word_list[0] == 'i2c_bus_address':
                        self.i2c_bus_address = str(word_list[1].rstrip())
                    elif word_list[0] == 'declination':
                        self.declination = (int(word_list[1].split(',')[0]), int(word_list[1].split(',')[1]))
                    elif word_list[0] == 'gauss':
                        self.gauss = float(word_list[1].rstrip())
                    elif word_list[0] == 'update_time_interval':
                        self.update_time_interval = float(word_list[1].rstrip())
                    else:
                        logging.info('Invalid line in compass config file: ', line)
            cfg_file.close()
        except:
            logging.error('Could not load the compass controller config file.')

    def save_settings(self):
        None

    def print_settings(self):
        print 'I2C SETTINGS'
        print 'I2C port: ', self.i2c_port
        print 'I2C bus address: ', self.i2c_bus_address
        print '\nCOMPASS SETTINGS'
        print 'Declination: ', self.declination
        print 'Gauss: ', self.gauss

    def parse_terminal_command(self, cmd):
        cmd = cmd.lower()
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

    def print_menu(self):
        print colored(' {:_^54}'.format(''), 'magenta')
        print ' {:1}{:^61}{:1}'.format(colored('|', 'magenta'), colored('COMPASS TERMINAL', 'white'),
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
