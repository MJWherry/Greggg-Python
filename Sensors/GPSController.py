import logging
import os
import threading
import time
import pynmea2
import serial
import xml.etree.ElementTree as ET
from termcolor import colored


class GPSController:

    # REFERENCE: http://aprs.gids.nl/nmea/

    # region Variables

    # region Setting variables
    serial_stream = None
    serial_port = '/dev/ttyS0'
    serial_baud_rate = 9600
    update_time_interval = 0.5
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
    run_thread = False
    # endregion

    # endregion

    # region Accessors/Mutators/Printers

    # region Accessors
    def get_latitude(self):
        return self.latitude

    def get_longitude(self):
        return self.longitude

    def get_latitude_direction(self):
        return self.latitude_direction

    def get_longitude_direction(self):
        return self.longitude_direction

    def get_altitude(self):
        return self.altitude

    def get_time(self):
        return self.time

    def get_position(self):
        return '{},{}'.format(self.latitude, self.longitude)

    def get_serial_port(self):
        return self.serial_port

    def get_serial_baud_rate(self):
        return self.serial_baud_rate

    def get_update_time_interval(self):
        return self.update_time_interval

    def is_connected(self):
        return self.serial_stream.is_open

    # endregion

    # region Mutators
    def set_serial_port(self, port):
        self.serial_port = port

    def set_serial_baud_rate(self, baud_rate):
        self.serial_baud_rate = baud_rate

    def set_update_time_interval(self, interval):
        if 0.2 > interval:
            self.update_time_interval = interval
    # endregion

    # region Printers
    def print_latitude(self):
        print 'Latitude: {}'.format(self.latitude)

    def print_latitude_direction(self):
        print 'Latitude direction: {}'.format(self.latitude_direction)

    def print_longitude(self):
        print 'Longitude: {}'.format(self.longitude)

    def print_longitude_direction(self):
        print 'Longitude direction: {}'.format(self.longitude_direction)

    def print_altitude(self):
        print 'Depth: {}'.format(self.altitude)

    def print_time(self):
        print 'Time: {}'.format(self.time)

    def print_position(self):
        print '{},{}'.format(self.latitude, self.longitude)

    def print_serial_port(self):
        print 'Serial port: {}'.format(self.serial_port)

    def print_serial_baud_rate(self):
        print 'Serial baud rate: {}'.format(self.serial_baud_rate)

    def print_update_time_interval(self):
        print 'Update time interval: {}'.format(self.update_time_interval)

    # endregion

    # endregion

    # region GPS functions
    def store_message_data(self, message):
        if message.identifier() == 'GPGGA,':
            try:
                self.time = message.timestamp
                self.latitude = message.lat
                self.latitude_direction = message.lat_dir
                self.longitude = message.lon
                self.longitude_direction = message.lon_dir
                self.altitude = message.altitude
                self.number_satellites = message.num_sats
                self.connected_to_satellites = True
            except:
                self.connected_to_satellites = False

    def is_connected_to_satellites(self):
        return self.connected_to_satellites

    # endregion

    # region Thread Functions
    def start_gps_thread(self):
        self.run_thread = True
        self.thread.start()

    def gps_thread_running(self):
        if not self.run_thread:
            return False
        return threading.Thread.isAlive(self.thread)

    def stop_gps_thread(self):
        self.run_thread = False
        # Test implementation

    def restart_gps_thread(self):
        None
        # Implement

    def run(self):
        reader = pynmea2.NMEAStreamReader(self.serial_stream, 'yield')
        while self.run_thread:
            for message in reader.next():
                self.store_message_data(message)
                time.sleep(self.update_time_interval)

    # endregion

    def __init__(self):
        self.load_settings()
        self.thread = threading.Thread(target=self.run, args=())
        try:
            self.serial_stream = serial.Serial(self.serial_port, self.serial_baud_rate)
        except:
            None

    def load_settings(self):
        try:
            tree = ET.parse('config.xml')
        except:
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
            elif child.attrib['name'] == 'update_time_interval': self.update_time_interval = int(child.attrib['value'])

    def save_settings(self):
        None

    def print_settings(self):
        print 'GPS CONTROLLER SETTINGS'
        self.print_serial_port()
        self.print_serial_baud_rate()
        self.print_update_time_interval()

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
        elif type == 'print' or cmd[0] == 'get':
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
                    data += str(self.get_position()) + ','
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
        print ' {} {:68} {}'.format(bar,
                                    colored('THREAD: {}'.format(colored('RUNNING', 'green') if self.gps_thread_running()
                                    else colored('NOT RUNNING', 'red')), 'white'), bar)
        print ' {} {:59} {}'.format(bar, colored('PORT: {}'.format(self.serial_port),'white'), bar)
        print ' {} {:59} {}'.format(bar, colored('BAUD RATE: {}'.format(self.serial_baud_rate),'white'), bar)
        print colored(' {}{:_^52}{}'.format('|', '', '|'), 'magenta')
        print ' {}{:^61}{}'.format(bar, colored('TERMINAL COMMANDS', 'white'), bar)
        for cmd in self.valid_terminal_commands:
            print ' {} \'{:^3}\' {:46} {}'.format(bar, colored(cmd[0], 'white'), cmd[1], bar)
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

if __name__ == "__main__":
    gc = GPSController()
    gc.terminal()