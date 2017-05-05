import logging
import os
import sys
import time
import pynmea2
import serial
from termcolor import colored
from Skeletons import SleepableThread
from Skeletons import SettingsManager

logging.basicConfig(filename='/home/pi/Desktop/greggg-python/run.log', level=logging.DEBUG,
                    format=('%(asctime)s %(levelname)s %(message)s'))


class GPSController(SleepableThread.SleepableThread):
    # REFERENCE: http://aprs.gids.nl/nmea/

    # region Variables
    settings = SettingsManager.SettingsManager()

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
    valid_terminal_commands = []
    hide_menu = False
    return_to_main_menu = False
    clear = 'cls' if os.name == 'nt' else 'clear'
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

    # region Thread Functions=
    def run(self):
        reader = pynmea2.NMEAStreamReader(self.serial_stream, 'yield')
        while self.thread_state != 4:
            if self.thread_state == 3:
                while self.thread_state == 3:
                    time.sleep(1)
            else:
                for message in reader.next():
                    self.store_message_data(message)

    # endregion

    def __init__(self):
        self.settings.load_settings('gps')
        self.serial_port = self.settings.get_setting_value('serial_port')
        self.serial_baud_rate = int(self.settings.get_setting_value('serial_baud_rate'))
        try:
            self.serial_stream = serial.Serial(self.serial_port, self.serial_baud_rate)
            logging.info('(GPS) Serial object created')
        except:
            logging.error('(GPS) Couldn\'t create serial object.')
        super(GPSController, self).__init__()

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
            self.parse_thread_command(cmd.split()[1])
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
        print ' {} {:68} {}'.format(bar,colored('THREAD: {}'.format(self.thread_status()), 'white'), bar)
        print ' {} {:59} {}'.format(bar,colored('THREAD PROCESS ID: {}'.format(self.thread_pid),'white'), bar)
        print ' {} {:59} {}'.format(bar,colored('THREAD SPAWN COUNT: {}'.format(self.thread_spawn_count),'white'), bar)
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
