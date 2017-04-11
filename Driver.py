import os
from guppy import hpy; h=hpy()
from termcolor import colored
import xml.etree.ElementTree as ET
from Bluetooth import BluetoothController
from Motors import MotorController
from Sensors import SonarController, GPSController, CompassController


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
        self.mc = MotorController.MotorController()
        self.sc = SonarController.SonarController()
        self.gc = GPSController.GPSController()
        self.cc = CompassController.CompassController()

        self.bc = BluetoothController.BluetoothController(self.mc, self.sc, self.gc, self.cc)

        # Start the appropriate threads automatically
        self.sc.start_sonar_thread()
        self.gc.start_gps_thread()
        self.cc.start_compass_thread()

        # Start the terminal
        self.terminal()

    def load_settings(self):
        tree = ET.parse('config.xml')
        root = tree.getroot()
        device = root.find('driver')
        for child in device.iter('terminal_commands'):
            for command in child.iter('command'):
                self.valid_terminal_commands.append((command.attrib['name'], command.attrib['description']))

    def print_menu(self):
        if self.hide_menu: return
        print colored(' {:_^54}'.format(''), 'magenta')
        print ' {:1}{:^61}{:1}'.format(colored('|', 'magenta'), colored('MAIN MENU', 'white'), colored('|', 'magenta'))
        print colored(' {}{:_^52}{}'.format('|', '', '|'), 'magenta')
        print ' {}{:^61}{}'.format(colored('|', 'magenta'), colored('INFORMATION', 'white'), colored('|', 'magenta'))
        print ' {} {} {:<31} {}'.format(colored('|', 'magenta'), colored('BLUETOOTH SERVER CONNECTED:', 'white'),
                                        colored('CONNECTED', 'green') if self.bc.is_connected() else colored(
                                            'DISCONNECTED', 'red'), colored('|', 'magenta'))
        print ' {} {} {:<31} {}'.format(colored('|', 'magenta'), colored('BLUETOOTH SERVER LISTENING:', 'white'),
                                        colored('LISTENING',
                                                'green') if self.bc.server_thread_running() else colored(
                                            'NOT LISTENING', 'red'), colored('|', 'magenta'))
        print colored(' {}{: ^52}{}'.format('|', '', '|'), 'magenta')
        print ' {} {} {:<41} {}'.format(colored('|', 'magenta'), colored('MOTOR CONTROLLER:', 'white'),
                                        colored('CONNECTED', 'green') if self.mc.is_connected else colored(
                                            'DISCONNECTED', 'red'), colored('|', 'magenta'))
        print colored(' {}{: ^52}{}'.format('|', '', '|'), 'magenta')
        print ' {} {} {:<45} {}'.format(colored('|', 'magenta'), colored('SONAR THREAD:', 'white'),
                                        colored('RUNNING', 'green') if self.sc.sonar_thread_running() else colored(
                                            'NOT RUNNING', 'red'), colored('|', 'magenta'))
        print ' {} {} {:<47} {}'.format(colored('|', 'magenta'), colored('GPS THREAD:', 'white'),
                                        colored('RUNNING', 'green') if self.gc.gps_thread_running() else colored(
                                            'NOT RUNNING', 'red'), colored('|', 'magenta'))
        print ' {} {} {:<43} {}'.format(colored('|', 'magenta'), colored('COMPASS THREAD:', 'white'),
                                        colored('RUNNING', 'green') if self.cc.compass_thread_running() else colored(
                                            'NOT RUNNING', 'red'),
                                        colored('|', 'magenta'))
        print colored(' {}{:_^52}{}'.format('|', '', '|'), 'magenta')
        print ' {}{:^61}{}'.format(colored('|', 'magenta'), colored('TERMINAL COMMANDS', 'white'),
                                   colored('|', 'magenta'))
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
        suffix = cmd.replace(prefix, '').rstrip()
        suffix = suffix[1:]

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

        elif cmd == 'mct':
            self.mc.terminal(), self.parse_terminal_command('c')
        elif cmd == 'sct':
            self.sc.terminal(), self.parse_terminal_command('c')
        elif cmd == 'gct':
            self.gc.terminal(), self.parse_terminal_command('c')
        elif cmd == 'cct':
            self.cc.terminal(), self.parse_terminal_command('c')
        elif cmd == 'bct':
            self.bc.terminal(), self.parse_terminal_command('c')

        elif cmd == '1':
            self.sc.restart_sonar_thread()
        elif cmd == '2':
            self.sc.stop_sonar_thread()

        elif cmd == 'con':
            self.bc.setup()
        elif cmd == 'h':
            if self.hide_menu:
                self.hide_menu = False
            else:
                self.hide_menu = True
            self.parse_terminal_command('c')
        elif cmd == 'c':
            os.system(self.clear), self.print_menu()
        elif cmd == 'q':
            self.cc.stop_compass_thread()
            self.gc.stop_gps_thread()
            self.sc.stop_sonar_thread()
            self.bc.stop_server_thread()
            os.system(self.clear)
            exit(0)

        elif cmd == '8':
            self.sc.stop_sonar_thread()
        elif cmd == '9':
            if self.bc.is_connected():
                data = raw_input(' Enter data to send: ')
                self.bc.send_data(data)
            else:
                print ' Bluetooth server is not connected.'

    def terminal(self):
        self.print_menu()
        while True:
            cmd = raw_input(colored(' Enter an option: ', 'cyan'))
            self.parse_terminal_command(cmd)


d = Driver()
