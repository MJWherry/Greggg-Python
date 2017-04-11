import logging
import os
import xml.etree.ElementTree as ET
import serial
from termcolor import colored


class MotorController:
    # region Variables

    # region Motor Variables
    serial = None
    serial_baud_rate = 0
    serial_port = ''
    # endregion

    # region ETC Variables
    valid_terminal_commands = []
    valid_motor_commands = []
    hide_menu = False
    return_to_main_menu = False
    clear = 'cls' if os.name == 'nt' else 'clear'
    # endregion

    # endregion

    # region Accessors/Mutators/Printers

    # region Accessors
    def get_serial(self):
        return self.serial

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
    def print_serial_port(self):
        print 'Serial port: ', self.serial_port

    def print_serial_baud_rate(self):
        print 'Serial baud rate: ', self.serial_baud_rate
    # endregion

    # endregion

    # region Motor functions
    def is_connected(self):
        return False if self.serial is None or self.serial.closed else True

    def connect(self):
        logging.info('Trying to connect to the motor hardware.')
        try:
            self.serial = serial.Serial(self.serial_port, self.serial_baud_rate)
            logging.info('Motor hardware connected.')
        except:
            logging.error('Could not establish a connection to the motor hardware.')

    def check_motor_command(self, cmd):
        cmd_base = cmd.split()[0]
        parameters = []
        valid = False

        for parameter in cmd.split():
            if parameter.isdigit():
                parameters.append(int(parameter))

        for command in self.valid_motor_commands:
            if command[0] == cmd_base:
                if len(parameters) == int(command[1]):
                    param_number = 0
                    for parameter_range in command[2]:
                        return True
                        param_number+=1
                        return True
                else:
                    return False
        return valid

    def run_motor_command(self,cmd):
        if self.check_motor_command(cmd):
            print colored(' Sending command...', 'yellow')
            try:
                self.serial.write(cmd + '\r')
                print colored(' Command sent.', 'green')
            except:
                print colored(' Command not sent.', 'red')
        else:
            print colored(' Invalid motor command syntax.', 'red')
    # endregion

    def __init__(self):
        self.load_settings()
        self.connect()

    def load_settings(self):
        tree = ET.parse('config.xml')
        root = tree.getroot()
        device = root.find('motor')

        for child in device.iter('hardware_commands'):
            for command in child.iter('command'):
                valid_command = (command.attrib['name'], command.attrib['parameter_count'], [])
                for parameter in command.iter('parameter'):
                    valid_command[2].append((parameter.attrib['description'], parameter.attrib['range']))
                self.valid_motor_commands.append(valid_command)

        for child in device.iter('terminal_commands'):
            for command in child.iter('command'):
                self.valid_terminal_commands.append((command.attrib['name'], command.attrib['description']))

        for child in device.iter('setting'):
            if child.attrib['name'] == 'serial_baud_rate': self.serial_baud_rate = int(child.attrib['value'])
            elif child.attrib['name'] == 'serial_port': self.serial_port = child.attrib['value']


    def save_settings(self):
        None

    def print_settings(self):
        print 'MOTOR CONTROLLER SETTINGS'
        self.print_serial_port()
        self.print_serial_baud_rate()

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
        else: self.run_motor_command(cmd)

    def print_menu(self):
        if self.hide_menu: return
        print colored(' {:_^54}'.format(''), 'magenta')
        print ' {}{:^61}{}'.format(colored('|', 'magenta'), colored('MOTOR CONTROLLER TERMINAL', 'white'),
                                   colored('|', 'magenta'))
        print colored(' {}{:_^52}{}'.format('|', '', '|'), 'magenta')
        print ' {}{:^61}{}'.format(colored('|', 'magenta'), colored('CONNECTION INFORMATION', 'white'),
                                   colored('|', 'magenta'))
        print ' {} {} {:<51} {}'.format(colored('|', 'magenta'), colored('STATUS:', 'white'),
                                        colored('CONNECTED', 'green') if self.is_connected() else colored('DISCONNECTED',
                                                                                                         'red'),
                                        colored('|', 'magenta'))

        print colored(' {} {} {:<41}{} {}'.format('|', 'PORT:', self.serial_port[:41], '...', '|'), 'magenta')
        print colored(' {} {} {:<40} {}'.format('|', 'BAUDRATE:', self.serial_baud_rate, '|'), 'magenta')
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

    def terminal(self):
        os.system(self.clear)
        self.print_menu()
        while not self.return_to_main_menu:
            cmd = raw_input(colored(' Enter a command: ', 'cyan'))
            self.parse_terminal_command(cmd)
        self.return_to_main_menu = False
        return