import logging
import os
import threading
import sys
import time
import pynmea2
import serial
import xml.etree.ElementTree as ET
from termcolor import colored

logging.basicConfig(filename='/home/pi/Desktop/greggg-python/run.log', level=logging.DEBUG,
                    format=('%(asctime)s %(levelname)s %(message)s'))


class GPSController:
    # REFERENCE: http://aprs.gids.nl/nmea/

    # region Variables

    # region Setting variables
    serial_stream = None
    serial_port = '/dev/ttyS0'
    serial_baud_rate = 9600
    # endregion

    # region GPS variables
    latitude = '0'
    latitude_direction = '0'
    longitude = '0'
    longitude_direction = '0'
    altitude = '0'
    time = '0'
    number_satellites = 0
    connected_to_satellites = False
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

    # region GPS functions
    def store_message_data(self, message):
        id = ''
        try:
            id = message.identifier()
        except:
            None
            # log
        if id == 'GPGGA,':
            try:
                self.number_satellites = message.num_sats
                if int(self.number_satellites) >= 5:
                    self.connected_to_satellites = True
                else:
                    self.connected_to_satellites = False
            except:
                self.connected_to_satellites = False
            if self.connected_to_satellites:
                self.time = message.timestamp
                self.latitude = self.calculate_coord(message.lat, message.lat_dir)
                self.longitude = self.calculate_coord(message.lon, message.lon_dir)
                self.altitude = message.altitude
                logging.info(
                    '{},{} {},{} {};'.format(self.time, message.lat, message.lat_dir, message.lon, message.lon_dir))

    def calculate_coord(self, coor, dir):
        coor_degrees = int(float(coor) / 100)
        coor_mins = float(coor) % 100
        if dir == 'S' or dir == 'W':
            return float((coor_degrees + (coor_mins / 60)) * -1)
        return float(coor_degrees + (coor_mins / 60))

    def is_connected_to_satellites(self):
        return self.connected_to_satellites

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
        print ' Starting gps thread...'
        logging.info('(GPS) Thread started.')
        reader = pynmea2.NMEAStreamReader(self.serial_stream, 'yield')
        while self.thread_running:
            if self.thread_sleeping:
                while self.thread_sleeping:
                    time.sleep(1)
            else:
                for message in reader.next():
                    self.store_message_data(message)

    # endregion

    def __init__(self):
        self.load_settings()
        self.thread = threading.Thread(target=self.run, args=())
        try:
            self.serial_stream = serial.Serial(self.serial_port, self.serial_baud_rate)
            logging.info('(GPS) Serial object created')
        except:
            logging.error('(GPS) Couldn\'t create serial object.')

    def load_settings(self):
        logging.info('(GPS) Loading settings.')
        try:
            tree = ET.parse('/home/pi/Desktop/greggg-python/config.xml')
        except:
            logging.error('(GPS) Couldn\'t open the config file.')
            return
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
        logging.info('(GPS) Settings loaded.')

    def save_settings(self):
        None

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
        elif type == 'thread':
            if split[1] == 'start':
                self.start_gps_thread()
                self.parse_terminal_command('c')
            elif split[1] == 'stop':
                self.stop_gps_thread()
                self.parse_terminal_command('c')
        elif type == 'print' or type == 'get':
            data = ' '
            for cmd in split:
                if cmd == 'latitude' or cmd == 'lat':
                    data += str(self.latitude) + ','
                elif cmd == 'latitude_direction' or cmd == 'lat_dir':
                    data += str(self.latitude_direction + ',')
                elif cmd == 'longitude' or cmd == 'lon':
                    data += str(self.longitude) + ','
                elif cmd == 'longitude_direction' or cmd == 'lon_dir':
                    data += str(self.longitude_direction + ',')
                elif cmd == 'altitude' or cmd == 'alt':
                    data += str(self.altitude) + ','
                elif cmd == 'time':
                    data += str(self.time + ',')
                elif cmd == 'all' or cmd == 'position' or cmd == 'pos':
                    data += '{},{},'.format(self.latitude, self.longitude)
                elif cmd == 'coordinate' or cmd == 'coord':
                    data += '({}{},{}{},{}),'.format(self.latitude, self.latitude_direction,
                                                     self.longitude, self.longitude_direction, self.altitude)
                elif cmd == 'serial_port' or cmd == 'port':
                    data += str(self.serial_port) + ','
                elif cmd == 'serial_baud_rate' or cmd == 'baud_rate':
                    data += str(self.serial_baud_rate)
            data = data[:-1] + ';'
            if type == 'get':
                return data
            elif type == 'print':
                print colored(data, 'green')

    def print_menu(self):
        if self.hide_menu: return
        bar = colored('|', 'magenta')
        print colored(' {:_^54}'.format(''), 'magenta')
        print ' {:1}{:^61}{:1}'.format(bar, colored('GPS TERMINAL', 'white'), bar)
        print colored(' {}{:_^52}{}'.format('|', '', '|'), 'magenta')

        print ' {}{:^61}{}'.format(bar, colored('CONNECTION INFORMATION', 'white'), bar)

        print ' {} {:59} {}'.format(bar, colored('STATUS: {}'.format('is connected? implement'), 'white'), bar)
        print ' {} {:59} {}'.format(bar, colored('PORT: {}'.format(self.serial_port), 'white'), bar)
        print ' {} {:59} {}'.format(bar, colored('BAUD RATE: {}'.format(self.serial_baud_rate), 'white'), bar)
        print colored(' {}{:52}{}'.format('|', '', '|'), 'magenta')
        print ' {} {:68} {}'.format(bar,
                                    colored('THREAD: {}'.format(colored('RUNNING', 'green') if self.gps_thread_running()
                                                                else colored('NOT RUNNING', 'red')), 'white'), bar)
        print colored(' {}{:_^52}{}'.format('|', '', '|'), 'magenta')
        print ' {}{:^61}{}'.format(bar, colored('TERMINAL COMMANDS', 'white'), bar)
        for cmd in self.valid_terminal_commands:
            print ' {} \'{:^3}\' {:46} {}'.format(bar, colored(cmd[0], 'white'), cmd[1], bar)
        print colored(' {}{:_^52}{}'.format('|', '', '|'), 'magenta')

    def terminal(self):
        logging.info('Starting gps terminal.')
        os.system(self.clear)
        sys.stdout.write("\x1b]2;GPS Controller Terminal\x07")
        self.print_menu()
        while not self.return_to_main_menu:
            cmd = raw_input(colored(' Enter a command: ', 'cyan'))
            self.parse_terminal_command(cmd)
        self.return_to_main_menu = False
        return


if __name__ == "__main__":
    gc = GPSController()
    gc.terminal()
