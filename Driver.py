import os
import time
import sys
from termcolor import colored
import xml.etree.ElementTree as ET
from Bluetooth import BluetoothController
from Motors import MotorController
from Sensors import SonarController, GPSController, CompassController
import logging

logging.basicConfig(filename='/home/pi/Desktop/greggg-python/run.log', level=logging.DEBUG, format=('%(asctime)s %(levelname)s %(message)s'))

class Driver:
    # region VARIABLES

    # region ETC VARIABLES
    valid_terminal_commands = []
    clear = 'cls' if os.name == 'nt' else 'clear'
    hide_menu = False
    # endregion

    # region CONTROLLER VARIABLES
    mc = None
    sc = None
    gc = None
    cc = None
    bc = None

    # endregion

    # endregion

    def __init__(self):
        os.system(self.clear)

        # Read in commands and settings
        self.load_settings()

        # Setup objects
        logging.info('(DRIVER) Creating controllers.')
        self.mc = MotorController.MotorController()
        self.sc = SonarController.SonarController()
        self.gc = GPSController.GPSController()
        self.cc = CompassController.CompassController()
        self.bc = BluetoothController.BluetoothController(self.mc, self.sc, self.gc, self.cc)

        # Start the appropriate threads automatically
        logging.info('(DRIVER) Starting threads.')
        time.sleep(1)
        self.sc.start_sonar_thread()

        time.sleep(1)
        self.gc.start_gps_thread()

        time.sleep(1)
        self.cc.start_compass_thread()

        time.sleep(1)
        self.bc.start_server_thread()

        print ' Finished, starting up in 3 seconds.'
        time.sleep(3)
        logging.info('(DRIVER) Starting up.')

    def load_settings(self):
        logging.info('(DRIVER) Loading settings.')
        try:
            tree = ET.parse('/home/pi/Desktop/greggg-python/config.xml')
        except:
            logging.error('(DRIVER) Couldn\'t open config file.')
            return
        root = tree.getroot()
        device = root.find('driver')
        for child in device.iter('terminal_commands'):
            for command in child.iter('command'):
                self.valid_terminal_commands.append((command.attrib['name'], command.attrib['description']))
        logging.info('(DRIVER) Settings loaded.')

    def print_menu(self):
        if self.hide_menu: return
        bar = colored('|', 'magenta')
        print colored(' {:_^54}'.format(''), 'magenta')
        print ' {}{:^61}{}'.format(bar, colored('MAIN MENU', 'white'), bar)
        print colored(' {}{:_^52}{}'.format('|', '', '|'), 'magenta')
        print ' {}{:^61}{}'.format(bar, colored('INFORMATION', 'white'), colored('|', 'magenta'))
        print ' {} {:68} {}'.format(colored('|', 'magenta'), colored('BLUETOOTH SERVER CONNECTED: {}'.format(
            colored('CONNECTED', 'green') if self.bc.is_connected() else colored(
                'DISCONNECTED', 'red')), 'white'), bar)
        print ' {} {:68} {}'.format(bar, colored('BLUETOOTH SERVER LISTENING: {}'.format(colored('LISTENING',
                                                                                                 'green') if self.bc.server_thread_running() else colored(
            'NOT LISTENING', 'red')), 'white'), bar)
        print colored(' {}{:52}{}'.format('|', '', '|'), 'magenta')
        print ' {} {:68} {}'.format(bar, colored(
            'MOTOR CONTROLLER: {}'.format(colored('CONNECTED', 'green') if self.mc.is_connected else colored(
                'DISCONNECTED', 'red')), 'white'), bar)
        print colored(' {}{:52}{}'.format('|', '', '|'), 'magenta')
        print ' {} {:68} {}'.format(bar, colored(
            'SONAR THREAD: {}'.format(colored('RUNNING', 'green') if self.sc.sonar_thread_running() else colored(
                'NOT RUNNING', 'red')), 'white'), bar)
        print ' {} {:68} {}'.format(bar, colored(
            'GPS THREAD: {}'.format(colored('RUNNING', 'green') if self.gc.gps_thread_running() else colored(
                'NOT RUNNING', 'red')), 'white'), bar)
        print ' {} {:68} {}'.format(bar, colored(
            'COMPASS THREAD: {}'.format(colored('RUNNING', 'green') if self.cc.compass_thread_running() else colored(
                'NOT RUNNING', 'red')), 'white'), bar)
        print colored(' {}{:_^52}{}'.format('|', '', '|'), 'magenta')
        print ' {} {:^59} {}'.format(bar, colored('TERMINAL COMMANDS', 'white'), bar)
        for command in self.valid_terminal_commands:
            if len(command[0]) is 1:
                print ' {} \'{:^3}\' {:46} {}'.format(colored('|', 'magenta'), colored(command[0], 'white'), command[1],
                                                      colored('|', 'magenta'))
            else:
                print ' {} \'{:^3}\' {:44} {}'.format(colored('|', 'magenta'), colored(command[0], 'white'), command[1],
                                                      colored('|', 'magenta'))
        print colored(' {}{:_^52}{}'.format('|', '', '|'), 'magenta')

    def parse_terminal_command(self, cmd):
        prefix = cmd.split()[0]
        suffix = cmd[3:]

        # Accept/forward commands based on controller prefix
        if prefix == 'mc' or prefix == 'motorcontroller' or prefix == 'motor_controller':
            self.mc.parse_terminal_command(suffix)
        elif prefix == 'sc' or prefix == 'sonarcontroller' or prefix == 'sonar_controller':
            self.sc.parse_terminal_command(suffix)
        elif prefix == 'gc' or prefix == 'gpscontroller' or prefix == 'gps_controller':
            self.gc.parse_terminal_command(suffix)
        elif prefix == 'cc' or prefix == 'compasscontroller' or prefix == 'compass_controller':
            self.cc.parse_terminal_command(suffix)
        elif prefix == 'bc' or prefix == 'bluetoothcontroller' or prefix == 'bluetooth_controller':
            self.bc.parse_terminal_command(suffix)

        # Switch to different controller terminals
        elif cmd == 'mct':
            self.mc.terminal(), self.parse_terminal_command('c'), sys.stdout.write("\x1b]2;Driver Terminal\x07")
        elif cmd == 'sct':
            self.sc.terminal(), self.parse_terminal_command('c'), sys.stdout.write("\x1b]2;Driver Terminal\x07")
        elif cmd == 'gct':
            self.gc.terminal(), self.parse_terminal_command('c'), sys.stdout.write("\x1b]2;Driver Terminal\x07")
        elif cmd == 'cct':
            self.cc.terminal(), self.parse_terminal_command('c'), sys.stdout.write("\x1b]2;Driver Terminal\x07")
        elif cmd == 'bct':
            self.bc.terminal(), self.parse_terminal_command('c'), sys.stdout.write("\x1b]2;Driver Terminal\x07")

        # Basic commands
        elif cmd == 'c':
            os.system(self.clear), self.print_menu()
        elif cmd == 'h':
            if self.hide_menu:
                self.hide_menu = False
            else:
                self.hide_menu = True
            self.parse_terminal_command('c')
        elif cmd == 'q':
            self.cc.stop_compass_thread()
            self.gc.stop_gps_thread()
            self.sc.stop_sonar_thread()
            self.bc.stop_server_thread()
            os.system(self.clear)
            exit(0)

    def terminal(self):
        sys.stdout.write("\x1b]2;Driver Terminal\x07")
        self.print_menu()
        while True:
            cmd = raw_input(colored(' Enter an option: ', 'cyan'))
            self.parse_terminal_command(cmd)

if __name__ == "__main__":
    d = Driver()
    d.terminal()
