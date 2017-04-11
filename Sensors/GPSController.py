import logging
import os
import threading
import time
import pynmea2
import serial
import xml.etree.ElementTree as ET
from termcolor import colored


class GPSController:
    # region Variables

    # region Serial variables
    serial_stream = None
    serial_data = ''
    serial_port = ''
    serial_baud_rate = 0
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

    # region Accessors/Mutators/Printers

    # region Accessors
    def get_current_latitude(self):
        return self.current_latitude

    def get_current_longitude(self):
        return self.current_longitude

    def get_current_depth(self):
        return self.current_depth

    def get_current_position(self):
        return '{},{}'.format(self.current_latitude, self.current_longitude)

    def get_serial_data(self):
        return self.serial_data

    def get_serial_port(self):
        return self.serial_port

    def get_serial_baud_rate(self):
        return self.serial_baud_rate

    # endregion

    # region Mutators
    def set_serial_port(self, port):
        self.serial_port = port

    def set_serial_baud_rate(self, baud_rate):
        self.serial_baud_rate = baud_rate

    # endregion

    # region Printers
    def print_current_latitude(self):
        print 'Latitude: {}'.format(self.current_latitude)

    def print_current_longitude(self):
        print 'Longitude: {}'.format(self.current_longitude)

    def print_current_depth(self):
        print 'Depth: {}'.format(self.current_depth)

    def print_current_position(self):
        print '{},{}'.format(self.current_latitude, self.current_longitude)

    def print_serial_data(self):
        print 'Serial data: {}'.format(self.serial_data)

    def print_serial_port(self):
        print 'Serial port: {}'.format(self.serial_port)

    def print_serial_baud_rate(self):
        print 'Serial baud rate: {}'.format(self.serial_baud_rate)

    def print_serial_object(self):
        print 'Serial object: {}'.format(self.serial_stream)

    # endregion

    # endregion

    # region GPS functions


    # endregion

    # region Thread Functions
    def start_gps_thread(self):
        self.run_thread = True
        self.thread.start()

    def gps_thread_running(self):
        if self.thread is None: return False
        return threading.Thread.isAlive(self.thread)

    def stop_gps_thread(self):
        self.run_thread = False
        # Test implementation

    def restart_gps_thread(self):
        None
        # Implement

    def run(self):
        streamreader = pynmea2.NMEAStreamReader(self.serial_stream,'ignore')
        while self.run_thread:
            for msg in streamreader.next():
                None
		time.sleep(1)
    # endregion

    def __init__(self):
        self.load_settings()
        self.thread = threading.Thread(target=self.run, args=())
        try:
            self.serial_stream = serial.Serial(self.serial_port, self.serial_baud_rate)
            logging.info('GPS hardware connected.')
        except:
            logging.error('Could not establish a connection to the gps hardware.')

    def load_settings(self):
        tree = ET.parse('config.xml')
        root = tree.getroot()
        device = root.find('gps')
        for child in device.iter('terminal_commands'):
            for command in child.iter('command'):
                self.valid_terminal_commands.append((command.attrib['name'], command.attrib['description']))

        for child in device.iter('setting'):
            if child.attrib['name'] == 'serial_port':
                self.serial_port = str(child.attrib['value'])
            elif child.attrib['name'] == 'serial_baud_rate':
                self.serial_baud_rate = int(child.attrib['value'])
            else:
                logging.info('Invalid line in GPS config file: ', child.attrib['name'])

    def save_settings(self):
        None

    def print_settings(self):
        print 'GPS CONTROLLER SETTINGS'
        self.print_serial_port()
        self.print_serial_baud_rate()

    def parse_terminal_command(self, cmd):
        cmd = cmd.lower()
        split = cmd.split()
        type = split[0]
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
        elif cmd[0] == 'print' or cmd[0] == 'get':
            data=''
            for cmd in split:
                if cmd == 'latitude' or cmd == 'lat':
                    data += str(self.gc.get_current_latitude()) + ','
                elif cmd == 'longitude' or cmd == 'lon':
                    data += str(self.gc.get_current_longitude()) + ','
                elif cmd == 'depth' or cmd == 'dep':
                    data += str(self.gc.get_current_depth()) + ','
                elif cmd == 'all' or cmd == 'position':
                    data += str(self.gc.get_current_position()) + ','
            data = data[:-1] + ';'
            if type == 'get':
                return data
            elif type == 'print':
                print colored(data, 'green')

    def print_menu(self):
        print colored(' {:_^54}'.format(''), 'magenta')
        print ' {:1}{:^61}{:1}'.format(colored('|', 'magenta'), colored('GPS TERMINAL', 'white'),
                                       colored('|', 'magenta'))
        print colored(' {}{:_^52}{}'.format('|', '', '|'), 'magenta')
        print ' {}{:^61}{}'.format(colored('|', 'magenta'), colored('CONNECTION INFORMATION', 'white'),
                                   colored('|', 'magenta'))
        print ' {} {} {:<47} {}'.format(colored('|', 'magenta'), colored('THREAD:', 'white'),
                                        colored('RUNNING', 'green') if self.gps_thread_running() else colored(
                                            'NOT RUNNING', 'red'), colored('|', 'magenta'))
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
