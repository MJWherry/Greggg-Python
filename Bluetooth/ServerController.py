import os
import threading
import time
import bluetooth
from termcolor import colored
import xml.etree.ElementTree as ET
import Motors.MotorController
import Sensors.CompassController
import Sensors.GPSController
import Sensors.SonarController


class ServerController:
    # region Variables

    # region Bluetooth Variables
    server_sock_in = None
    server_sock_out = None
    client_sock_in = None
    client_sock_out = None
    client_address_in = ''
    client_address_out = ''
    server_address = ''
    server_backlog = 0
    server_in_port = 0
    server_out_port = 0
    server_in_connection_timeout = 0
    server_out_connection_timeout = 0
    server_in_byte_size = 0
    # endregion

    # region Controller Variables
    mc = Motors.MotorController
    sc = Sensors.SonarController.SonarController
    gc = Sensors.GPSController.GPSController
    cc = Sensors.CompassController
    # endregion

    # region ETC Variables
    thread = None
    valid_terminal_commands = []
    received_commands = []
    hide_menu = False
    return_to_main_menu = False
    clear = 'cls' if os.name == 'nt' else 'clear'
    run_thread = False

    # endregion

    # endregion

    # region Accessors/Mutators/Printers

    # region Accessors
    def get_server_backlog(self):
        return self.server_backlog

    def get_server_in_port(self):
        return self.server_in_port

    def get_server_out_port(self):
        return self.server_out_port

    def get_server_in_connection_timeout(self):
        return self.server_in_connection_timeout

    def get_server_out_connection_timeout(self):
        return self.server_out_connection_timeout

    def get_byte_size(self):
        return self.server_in_byte_size

    # endregion

    # region Mutators
    def set_server_backlog(self, backlog):
        self.server_backlog = backlog

    def set_server_in_port(self, port):
        self.server_in_port = port

    def set_server_out_port(self, port):
        self.server_out_port = port

    def set_server_in_connection_timeout(self, value):
        self.server_in_connection_timeout = value

    def set_server_out_connection_timeout(self, value):
        self.server_out_connection_timeout = value

    def set_byte_size(self, size):
        self.server_in_byte_size = size

    # endregion

    # region Printers
    def print_server_address(self):
        print 'Server address: ', self.server_address

    def print_server_backlog(self):
        print 'Server backlog: ', self.server_backlog

    def print_server_in_port(self):
        print 'Server in port: ', self.server_in_port

    def print_server_out_port(self):
        print 'Server out port: ', self.server_out_port

    def print_server_in_connection_timeout(self):
        print 'Server in connection timeout: ', self.server_in_connection_timeout

    def print_server_out_connection_timeout(self):
        print 'Server out connection timeout: ', self.server_out_connection_timeout

    def print_server_in_byte_size(self):
        print 'Server in byte size: ', self.server_in_byte_size

    # endregion

    # endregion

    # region Server Functions

    def is_connected(self):
        return False if self.client_address_in == '' and self.client_address_out == '' else True

    def create_socket(self):
        self.server_sock_in = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.server_sock_out = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

    def bind_server_in_port(self):
        self.server_sock_in.bind((self.server_address, self.server_in_port))

    def bind_server_out_port(self):
        self.server_sock_out.bind((self.server_address, self.server_out_port))

    def listen(self):
        self.server_sock_in.listen(self.server_backlog)
        self.server_sock_out.listen(self.server_backlog)

    def setup(self):
        print 'Creating sockets...'
        self.create_socket()
        print 'Binding...'
        self.bind_server_in_port()
        self.bind_server_out_port()
        # self.server_sock_in.settimeout(10)
        # self.server_sock_out.settimeout(10)

        print 'Listening on backlog'
        self.listen()

        print 'Waiting for in connection...'
        self.client_sock_in, self.client_address_in = self.server_sock_in.accept()
        print 'In connection established with client ', self.client_address_in

        print 'Waiting for out connection...'
        self.client_sock_out, self.client_address_out = self.server_sock_out.accept()
        print 'Out connection established with client ', self.client_address_out

        print 'Starting thread...'
        self.start_server_thread()

    def send_data(self, data):
        try:
            self.client_sock_out.send(data)
        except:
            print 'No outbound connection available.'

    # endregion

    # region Thread Functions
    def start_server_thread(self):
        self.run_thread = True
        self.thread.start()

    def server_thread_running(self):
        return threading.Thread.isAlive(self.thread)

    def stop_server_thread(self):
        self.run_thread = False
        # Test implementation

    def restart_server_thread(self):
        None
        # Implement

    def run(self):
        while self.run_thread:
            data = self.client_sock_in.recv(self.server_in_byte_size)
            if data:
                print 'Received: ', data
                self.parse_terminal_command(data)

    # endregion

    def __init__(self, motor, sonar, gps, compass):
        self.load_settings()
        self.mc = motor
        self.sc = sonar
        self.gc = gps
        self.cc = compass
        self.thread = threading.Thread(target=self.run, args=())

    def load_settings(self):
        tree = ET.parse('config.xml')
        root = tree.getroot()
        device = root.find('bluetooth')
        for child in device.iter('terminal_commands'):
            for command in child.iter('command'):
                self.valid_terminal_commands.append((command.attrib['name'], command.attrib['description']))
        for child in device.iter('setting'):
            if child.attrib['name'] == 'server_in_port':
                self.server_in_port = int(child.attrib['value'])
            elif child.attrib['name'] == 'server_backlog':
                self.server_backlog = int(child.attrib['value'])
            elif child.attrib['name'] == 'server_out_port':
                self.server_out_port = int(child.attrib['value'])
            elif child.attrib['name'] == 'server_in_connection_timeout':
                self.server_in_connection_timeout = float(child.attrib['value'])
            elif child.attrib['name'] == 'server_out_connection_timeout':
                self.server_out_connection_timeout = float(child.attrib['value'])
            elif child.attrib['name'] == 'server_in_byte_size':
                self.server_in_byte_size = int(child.attrib['value'])
            elif child.attrib['name'] == 'server_address':
                self.server_address = str(child.attrib['value'])

    def save_settings(self):
        None

    def print_settings(self):
        print 'SERVER'
        self.print_server_address()
        self.print_server_backlog()
        self.print_server_in_port()
        self.print_server_out_port()
        self.print_server_in_byte_size()

    def parse_terminal_command(self, command):
        # A list of valid prefixes
        prefixes = ['mc', 'motorcontroller', 'motor_controller',
                    'sc', 'sonarcontroller', 'sonar_controller',
                    'gc', 'gpscontroller', 'gps_controller',
                    'cc', 'compasscontroller', 'compass_controller',
                    'bc', 'bluetoothcontroller', 'cluetooth_controller']
        # Data to be returned
        data = ''
        # Change the command to lower case
        command = command.lower()
        # Add the command to a list of commands received
        self.received_commands.append(command)

        prefix = command.split(' ')[0]
        type = command.split(' ')[1]

        suffix = command.replace(prefix, ' ').rstrip()
        suffix = suffix[1:]
        split = suffix.split(' ')

        # BASIC COMMAND PARSING (if command == 'h' or c and so on)
        # If command in valid_commands
        # Else below

        # If a non valid prefix is sent
        if prefix not in prefixes:
            # Informs user an invalid prefix was sent
            data = ' Invalid prefix.;'
        # If a valid prefix is sent
        else:
            # If the prefix is motor based
            if prefix == 'mc' or prefix == 'motorcontroller' or prefix == 'motor_controller':
                # send the command straight to the motor controller parser
                self.mc.run_motor_command(suffix)

            # If the prefix is sonar based
            elif prefix == 'sc' or prefix == 'sonarcontroller' or prefix == 'sonar_controller':
                data = self.sc.parse_terminal_command(suffix)

            # If the prefix is gps based
            elif prefix == 'gc' or prefix == 'gpscontroller' or prefix == 'gps_controller':
                data = self.gc.parse_terminal_command(suffix)

            elif prefix == 'cc' or prefix == 'compasscontroller' or prefix == 'compass_controller':
                data = self.cc.parse_terminal_command(suffix)

            elif prefix == 'bc' or prefix == 'bluetoothcontroller' or prefix == 'bluetooth_controller':
                for cmd in split:
                    if cmd == 'in_port':
                        data += str(self.server_in_port) + ','
                    elif cmd == 'out_port':
                        data += str(self.server_out_port) + ','

        data = data[:-1]
        data += ";"
        if type == 'get':
            self.client_sock_out.send(data)
        elif type == 'print':
            print ' ', data
        else:
            print 'Invalid command type: ', type

    def print_menu(self):
        print colored(' {:_^54}'.format(''), 'magenta')
        print ' {:1}{:^61}{:1}'.format(colored('|', 'magenta'), colored('SERVER TERMINAL', 'white'),
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
        return
