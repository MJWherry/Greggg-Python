import logging
import os
import pynmea2
import serial
import threading
import time
from termcolor import colored


class GPSController:

    # region Variables

    # region Serial variables
    serial_stream = None
    serial_data = None
    serial_port = None
    serial_baud_rate = None
    # endregion

    # region GPS variables
    current_latitude = 0
    current_longitude = 0
    current_depth = 0
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
    def get_current_latitude(self):
        return self.current_latitude

    def get_current_longitude(self):
        return self.current_longitude

    def get_current_depth(self):
        return self.current_depth

    def get_serial_data(self):
        return self.serial_data

    def get_serial_port(self):
        return self.serial_port

    def get_serial_baud_rate(self):
        return self.serial_baud_rate

    def set_serial_port(self, port):
        self.serial_port = port

    def set_serial_baud_rate(self, baud_rate):
        self.serial_baud_rate = baud_rate

    def test_print_loop(self):
        streamreader = pynmea2.NMEAStreamReader()
        while 1:
            data = self.ser.read()
            for msg in streamreader.next(data):
                print msg
                msg = pynmea2.parse("$GPGGA,184353.07,1929.045,S,02410.506,E,1,04,2.6,100.00,M,-33.9,M,,0000*6D")
                print msg
    # endregion

    # region GPS functions

    def test_main_loop(self):
        streamreader = pynmea2.NMEAStreamReader()
        while 1:
            data = self.serial_stream.read()
            for msg in streamreader.next(data):
                print msg
                msg = pynmea2.parse("$GPGGA,184353.07,1929.045,S,02410.506,E,1,04,2.6,100.00,M,-33.9,M,,0000*6D")
                print msg

    # endregion

    # region Thread Functions
    def start_gps_thread(self):
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
        None

    # endregion

    def __init__(self):
        self.load_settings()
        try:
            self.serial_stream = serial.Serial(self.serial_port, self.serial_baud_rate)
            logging.info('GPS hardware connected.')
        except:
            logging.error('Could not establish a connection to the gps hardware.')

    def load_settings(self):
        # Terminal commands
        logging.info('Loading terminal commands for the gps controller.')
        try:
            cmd_file = open('info/GPS/TerminalCommands.txt', 'r')
            for line in cmd_file:
                word_list = line.split(',')
                self.valid_terminal_commands.append((word_list[0], word_list[1].rstrip()))
            cmd_file.close()
        except:
            logging.error('Could not load the gps controller command file.')

        # Settings
        logging.info('Loading settings for the gps controller.')
        try:
            cfg_file = open('info/GPS/Config.txt', 'r')
            for line in cfg_file:
                word_list = line.split('=')
                if word_list[0] == 'serial_port':
                    self.serial_port = word_list[1].rstrip()
                elif word_list[0] == 'serial_baud_rate':
                    self.serial_baud_rate = word_list[1].rstrip()
                else:
                    logging.info('Invalid line in GPS config file: ', line)
            cfg_file.close()
        except:
            logging.error('Could not load the gps controller config file.')

    def save_settings(self):
        None

    def parse_terminal_command(self, cmd):
        cmd = cmd.lower()
        if cmd == 'c':
            os.system(self.clear)
            if not self.hide_menu:
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
        print ' {:1}{:^61}{:1}'.format(colored('|', 'magenta'), colored('GPS TERMINAL', 'white'),
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
        logging.info('Starting gps terminal.')
        os.system(self.clear)
        if not self.hide_menu:
            self.print_menu()
        while not self.return_to_main_menu:
            cmd = raw_input(colored(' Enter a command: ', 'cyan'))
            self.parse_terminal_command(cmd)
        self.return_to_main_menu = False
        return
