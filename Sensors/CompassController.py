try:
    import hmc5883l
except:
    None
import logging
import os
import threading
import time
import xml.etree.ElementTree as ET
from termcolor import colored


class CompassController:
    # region Variables

    # region I2C settings
    i2c_port = 1
    i2c_bus_address = 0x1E
    # endregion

    # region Compass settings
    try:
        compass = hmc5883l
    except:
        None
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
    run_thread = False

    # endregion

    # endregion

    # region Accessors/Mutators/Printers

    # region Mutators
    def set_gauss(self, gauss):
        self.gauss = gauss

    def set_declination_degrees(self,degrees):
        self.declination_degrees = degrees
        self.declination = (self.declination_degrees, self.declination_minutes)

    def set_declination_minutes(self,minutes):
        self.declination_minutes = minutes
        self.declination=(self.declination_degrees, self.declination_minutes)

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
        return (self.declination_degrees,self.declination_minutes)

    def get_declination_degrees(self):
        return self.declination_degrees

    def get_declination_minutes(self):
        return self.declination_minutes

    def get_update_time_interval(self):
        return self.update_time_interval

    def get_i2c_port(self):
        return self.i2c_port

    def get_i2c_bus_address(self):
        return self.i2c_bus_address

    def get_x_axis(self):
        return self.compass.axes()[0]

    def get_y_axis(self):
        return self.compass.axes()[1]

    def get_z_axis(self):
        return self.compass.axes()[2]

    def get_heading(self):
        return self.compass.degrees(self.compass.heading())

    # endregion

    # region Printers
    def print_gauss(self):
        print 'Gauss: {}'.format(self.gauss)

    def print_declination(self):
        print 'Declination: {}'.format(self.get_declination())

    def print_declination_degrees(self):
        print 'Declination degrees: {}'.format(self.declination_degrees)

    def print_declination_minutes(self):
        print 'Declination minutes: {}'.format(self.declination_minutes)

    def print_update_time_interval(self):
        print 'Update time interval: {}'.format(self.update_time_interval)

    def print_i2c_port(self):
        print 'I2C port: {}'.format(self.i2c_port)

    def print_i2c_bus_address(self):
        print 'I2C bus address: {}'.format(self.i2c_bus_address)

    def print_x_axes(self):
        print 'X-Axis: {}'.format(self.compass.axes()[0])

    def print_y_axes(self):
        print 'Y-Axes: {}'.format(self.compass.axes()[1])

    def print_z_axes(self):
        print 'Z-Axes: {}'.format(self.compass.axes()[2])

    def print_heading(self):
        print 'Heading: {}'.format(self.compass.degrees(self.compass.heading()))

    # endregion

    # endregion

    # region Compass functions

    # endregion

    # region Thread Functions
    def start_compass_thread(self):
        self.run_thread = True
        self.thread.start()

    def compass_thread_running(self):
        if self.thread is None: return False
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
        try:
            self.compass = hmc5883l.hmc5883l(gauss=self.gauss, declination=(self.declination_degrees, self.declination_minutes))
        except:
            None
        self.thread = threading.Thread(target=self.run, args=())

    def load_settings(self):
        try:
            tree = ET.parse('config.xml')
        except:
            return
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

    def save_settings(self):
        None

    def print_settings(self):
        print 'COMPASS CONTROLLER SETTINGS'
        self.print_i2c_bus_address()
        self.print_i2c_port()
        self.print_gauss()
        self.print_declination()
        self.print_update_time_interval()

    def parse_terminal_command(self, cmd):
        cmd = cmd.lower()
        split = cmd.split()
        type = split[0]
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
        elif type == 'get' or type == 'print':
            data = ''
            for cmd in split:
                if cmd == 'heading':
                    data += str(self.get_heading()) + ','
                elif cmd == 'declination':
                    data += str(self.get_declination()) + ','
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
        print ' {} {:68} {}'.format(bar,
                                    colored('THREAD: {}'.format(colored('RUNNING', 'green') if self.compass_thread_running()
                                                                else colored('NOT RUNNING', 'red')), 'white'), bar)
        print ' {} {:59} {}'.format(bar,colored('STATUS: {}'.format('is connected? implement'),'white'),bar)

        print ' {} {:34} {:33} {}'.format(bar, colored('I2C PORT: {}'.format(self.i2c_port),'white'), colored('I2C ADDRESS: {}'.format(self.i2c_bus_address),'white'),bar)
        print ' {} {:34} {:33} {}'.format(bar, colored('DECLINATION MINUTES: {}'.format(self.declination_minutes), 'white'),
                                          colored('DECLINATION DEGREES: {}'.format(self.declination_degrees), 'white'), bar)
        print colored(' {}{:_^52}{}'.format('|', '', '|'), 'magenta')
        print ' {}{:^61}{}'.format(bar, colored('TERMINAL COMMANDS', 'white'),bar)
        for cmd in self.valid_terminal_commands:
            print ' {} \'{:^3}\' {:46} {}'.format(bar, colored(cmd[0], 'white'), cmd[1], bar)
        print colored(' {}{:_^52}{}'.format('|', '', '|'), 'magenta')

    def terminal(self):
        os.system(self.clear)
        self.print_menu()
        while not self.return_to_main_menu:
            cmd = raw_input(colored(' Enter a command: ', 'cyan'))
            self.parse_terminal_command(cmd)
        self.return_to_main_menu = False

if __name__ == "__main__":
    cc = CompassController()
    cc.terminal()