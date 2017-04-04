# import hmc5883l
import logging
import os
import threading
import time
import xml.etree.ElementTree as ET
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
    declination_minutes=0
    declination_degrees=0
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

    # region Accessors/Mutators/Printers

    # region Mutators
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

    # endregion

    # region Accessors
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

    # region Printers
    def print_gauss(self):
        print 'Gauss: ', self.gauss

    def print_declination(self):
        print 'Declination: ', self.declination

    def print_update_time_interval(self):
        print 'Update time interval: ', self.update_time_interval

    def print_i2c_port(self):
        print 'I2C port: ', self.i2c_port

    def print_i2c_bus_address(self):
        print 'I2C bus address: ', self.i2c_bus_address

    def print_x_axes(self):
        print 'X-Axis: ', self.compass.axes()[0]

    def print_y_axes(self):
        print 'Y-Axes: ', self.compass.axes()[1]

    def print_z_axes(self):
        print 'Z-Axes: ', self.compass.axes()[2]

    def print_heading(self):
        print 'Heading: ', self.compass.heading()

    def print_compass_object(self):
        print 'Compass object: ', self.compass

    # endregion

    # endregion

    # region Compass functions
    def print_compass(self):
        print self.compass

    def print_compass_heading(self):
        print 'Heading: ' + str(self.compass.degrees(self.compass.heading())) + '     '

    # endregion

    # region Thread Functions
    def start_compass_thread(self):
        self.run_thread = True
        self.thread.start()

    def compass_thread_running(self):
        return threading.Thread.isAlive(self.thread)

    def stop_compass_thread(self):
        self.run_thread = False
        # Test implementation

    def restart_compass_thread(self):
        None
        # Implement

    def run(self):
        while self.run_thread:
            self.current_heading = str(self.compass.degrees(self.compass.heading()))
            time.sleep(self.update_time_interval)

    # endregion

    def __init__(self):
        self.load_settings()
        # self.compass = hmc5883l.hmc5883l(gauss=4.7, declination=(-2, 5))
        self.thread = threading.Thread(target=self.run, args=())

    def load_settings(self):
        tree = ET.parse('config.xml')
        root = tree.getroot()
        device = root.find('compass')
        for child in device.iter('terminal_commands'):
            for command in child.iter('command'):
                self.valid_terminal_commands.append((command.attrib['name'], command.attrib['description']))
        for child in device.iter('setting'):
            if child.attrib['name'] == 'i2c_port': self.i2c_port = int(child.attrib['value'])
            elif child.attrib['name'] == 'i2c_bus_address': self.i2c_bus_address = str(child.attrib['value'])
            elif child.attrib['name'] == 'declination_minutes': self.declination_minutes = int(child.attrib['value'])
            elif child.attrib['name'] == 'declination_degrees': self.declination_degrees = int(child.attrib['value'])
            elif child.attrib['name'] == 'gauss': self.gauss = float(child.attrib['value'])
            elif child.attrib['name'] == 'update_time_interval': self.update_time_interval = float(child.attrib['value'])
            else: logging.info('Invalid line in compass config file: ', child.attrib['name'])


    def save_settings(self):
        None

    def print_settings(self):
        print 'COMPASS CONTROLLER SETTINGS'
        print 'I2C Specific'
        print 'Port: ', self.i2c_port
        print 'Bus Address: ', self.i2c_bus_address
        print '\nCompass Specific'
        print 'Declination minutes: ', self.declination_minutes
        print 'Declination degrees: ', self.declination_degrees
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
