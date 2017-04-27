import os
import sys
import threading
import bluetooth
from termcolor import colored
import xml.etree.ElementTree as ET
import logging
import time

logging.basicConfig(filename='/home/pi/Desktop/greggg-python/run.log', level=logging.DEBUG, format=('%(asctime)s %(levelname)s %(message)s'))

# region Imports
try:
    import Motors.MotorController
    logging.info('(BLUETOOTH) Imported Motors.MotorController.')
except:
    logging.error('(BLUETOOTH) Couldn\'t import Motors.MotorController')
try:
    import Sensors.CompassController
    logging.info('(BLUETOOTH) Imported Sensors.CompassController.')
except:
    logging.error('(BLUETOOTH) Couldn\'t import Sensors.CompassController')
try:
    import Sensors.GPSController
    logging.info('(BLUETOOTH) Imported Sensors.GPSController.')
except:
    logging.error('(BLUETOOTH) Couldn\'t import Sensors.GPSController')
try:
    import Sensors.SonarController
    logging.info('(BLUETOOTH) Imported Sensors.SonarController.')
except:
    logging.error('(BLUETOOTH) Couldn\'t import Sensors.SonarController')


# endregion


class BluetoothController:
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
    connected = False

    socket_in_created = False
    socket_in_bound = False
    socket_out_created = False
    socket_out_bound = False
    # endregion

    # region Controller Variables
    try:
        mc = Motors.MotorController
        logging.info('(BLUETOOTH) Set mc to MotorController instance.')
    except:
        logging.error('(BLUETOOTH) Couldn\'t set mc to MotorController instance.')
    try:
        sc = Sensors.SonarController.SonarController
        logging.info('(BLUETOOTH) Set sc to SonarController instance.')
    except:
        logging.error('(BLUETOOTH) Couldn\'t set sc to SonarController instance.')
    try:
        gc = Sensors.GPSController.GPSController
        logging.info('(BLUETOOTH) Set gc to GPSController instance.')
    except:
        logging.error('(BLUETOOTH) Couldn\'t set gc to GPSController instance.')
    try:
        cc = Sensors.CompassController
        logging.info('(BLUETOOTH) Set cc to CompassController instance.')
    except:
        logging.error('(BLUETOOTH) Couldn\'t set cc to CompassController instance.')
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

    # region Server Functions
    def is_connected(self):
        return False if self.client_address_in == '' and self.client_address_out == '' else True

    def sockets_created_and_bound(self):
        return True if self.socket_in_created and self.socket_in_bound and self.socket_out_created and self.socket_out_bound else False

    def create_socket(self):
        try:
            self.server_sock_in = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            logging.info('(BLUETOOTH) Server_sock_in created.')
            self.socket_in_created = True
        except:
            logging.error('(BLUETOOTH) Couldn\'t create server_sock_in.')
            self.socket_in_created = False
        try:
            self.server_sock_out = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            logging.info('(BLUETOOTH) Server_sock_out created.')
            self.socket_out_created = True
        except:
            logging.error('(BLUETOOTH) Couldn\'t create server_sock_out.')
            self.socket_out_created = False

    def set_timeouts(self):
        try:
            self.server_sock_in.settimeout(self.server_in_connection_timeout)
            logging.error('Set server_sock_in timeout to {}.'.format(self.server_in_connection_timeout))
        except:
            logging.error('Couldn\'t set server_sock_in timeout to {}.'.format(self.server_in_connection_timeout))
        try:
            self.server_sock_out.settimeout(self.server_out_connection_timeout)
            logging.error('Set server_sock_out timeout to {}.'.format(self.server_out_connection_timeout))
        except:
            logging.error('Couldn\'t set server_sock_out timeout to {}.'.format(self.server_out_connection_timeout))

    def bind_server_in_port(self):
        try:
            self.server_sock_in.bind((self.server_address, self.server_in_port))
            logging.info('(BLUETOOTH) Server_sock_in bound on address {} on port {}.'.format(self.server_address,
                                                                                             self.server_in_port))
            self.socket_in_bound = True
        except:
            logging.error('(BLUETOOTH) Couldn\'t bind server_sock_in {} on port {}.'.format(self.server_address,
                                                                                            self.server_in_port))
            self.socket_in_bound = False

    def bind_server_out_port(self):
        try:
            self.server_sock_out.bind((self.server_address, self.server_out_port))
            logging.info('(BLUETOOTH) Server_sock_out bound on address {} on port {}.'.format(self.server_address,
                                                                                              self.server_out_port))
            self.socket_out_bound = True
        except:
            logging.error('(BLUETOOTH) Couldn\'t bind server_sock_out {} on port {}.'.format(self.server_address,
                                                                                             self.server_out_port))
            self.socket_out_bound = False

    def listen(self):
        try:
            self.server_sock_in.listen(self.server_backlog)
            logging.info('(BLUETOOTH) Server_sock_in started listening.')
        except:
            logging.error('(BLUETOOTH) Server_sock_in couldn\'t start listening.')
        try:
            self.server_sock_out.listen(self.server_backlog)
            logging.info('(BLUETOOTH) Server_sock_out started listening.')
        except:
            logging.error('(BLUETOOTH) Server_sock_in couldn\;t start listening.')

    def accept_connections(self):
        try:
            self.client_sock_in, self.client_address_in = self.server_sock_in.accept()
        except:
            logging.error('Couldn\'t accept inbound connection.')
        try:
            self.client_sock_out, self.client_address_out = self.server_sock_out.accept()
        except:
            logging.error('Couldn\'t accept outbound connection.')

    def close_sockets(self):
        try:
            self.client_sock_in.close()
            logging.info('(BLUETOOTH) Closed client_sock_in.')
        except:
            logging.error('(BLUETOOTH) Couldn\'t close client_sock_in.')
        try:
            self.client_sock_out.close()
            logging.info('(BLUETOOTH) Closed client_sock_out.')
        except:
            logging.error('(BLUETOOTH) Couldn\'t close client_sock_out.')
        try:
            self.server_sock_in.close()
            logging.info('(BLUETOOTH) Closed server_sock_in.')
        except:
            logging.error('(BLUETOOTH) Couldn\'t close server_sock_in.')
        try:
            logging.info('(BLUETOOTH) Closed server_sock_out.')
            self.server_sock_out.close()
        except:
            logging.error('(BLUETOOTH) Couldn\'t close server_sock_out.')
        self.client_address_in=''
        self.client_address_out=''
        self.connected = False

    def setup(self):
        self.create_socket()
        # self.set_timeouts()
        self.bind_server_in_port()
        self.bind_server_out_port()
        self.listen()
        self.accept_connections()
        if not self.run_thread:
            self.start_server_thread()
        self.connected = True

    def send_data(self, data):
        # TEST
        try:
            self.client_sock_out.send(data)
        except:
            print ' No outbound connection available.'

    # endregion

    # region Thread Functions
    def start_server_thread(self):
        # if self.sockets_created_and_bound():
        try:
            self.thread.start()
            self.run_thread = True
        except:
            logging.error('(BLUETOOTH) Couldn\'t start thread.')
            # else:
            #    logging.error('(BLUETOOTH) Couldn\'t start thread; Couldn\'t verify the objects were created.')
            #    print ' Could not start bluetooth thread.'

    def server_thread_running(self):
        return threading.Thread.isAlive(self.thread)

    def stop_server_thread(self):
        self.run_thread = False

    def restart_server_thread(self):
        None
        # Implement

    def run(self):
        print ' Starting bluetooth thread...'
        logging.info('(BLUETOOTH) Thread started.')
        while self.run_thread:
            try:
                self.setup()
                self.parse_terminal_command('c')
                while self.connected:
                    try:
                        data = self.client_sock_in.recv(self.server_in_byte_size)
                        if data:
                            self.parse_terminal_command(data)
                    except:
                        self.close_sockets()
                        self.parse_terminal_command('c')
            except:
                print 'Could not setup(), waiting...'
                time.sleep(10)

    # endregion

    def __init__(self, motor, sonar, gps, compass):
        self.load_settings()
        self.mc = motor
        self.sc = sonar
        self.gc = gps
        self.cc = compass
        self.thread = threading.Thread(target=self.run, args=())

    def load_settings(self):
        try:
            tree = ET.parse('/home/pi/Desktop/greggg-python/config.xml')
        except:
            logging.error('(BLUETOOTH) Couldn\'t load settings..')
            return
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
        logging.info('(BLUETOOTH) Settings loaded.')

    def save_settings(self):
        # Implement
        None

    def parse_terminal_command(self, command):
        prefixes = ['mc', 'motorcontroller', 'motor_controller',
                    'sc', 'sonarcontroller', 'sonar_controller',
                    'gc', 'gpscontroller', 'gps_controller',
                    'cc', 'compasscontroller', 'compass_controller',
                    'bc', 'bluetoothcontroller', 'cluetooth_controller']

        data = ''
        command = command.lower()
        split = command.split()
        prefix = command.split()[0]
        try:
            type = command.split()[1]
        except:
            type='none'
        suffix = command.replace(prefix + ' ', '')
        parameters = suffix.replace(type + ' ', '')

        # BASIC COMMAND PARSING (if command == 'h' or c and so on)
        # If command in valid_commands
        # Else below
        # If a non valid prefix is sent

        if prefix in prefixes:
            if prefix == 'mc' or prefix == 'motorcontroller' or prefix == 'motor_controller':
                self.mc.run_motor_command(suffix)

            elif prefix == 'sc' or prefix == 'sonarcontroller' or prefix == 'sonar_controller':
                data = self.sc.parse_terminal_command(suffix)

            elif prefix == 'gc' or prefix == 'gpscontroller' or prefix == 'gps_controller':
                data = self.gc.parse_terminal_command(suffix)

            elif prefix == 'cc' or prefix == 'compasscontroller' or prefix == 'compass_controller':
                data = self.cc.parse_terminal_command(suffix)

            elif prefix == 'bc' or prefix == 'bluetoothcontroller' or prefix == 'bluetooth_controller':
                for cmd in parameters:
                    if cmd == 'in_port':
                        data += str(self.server_in_port) + ','
                    elif cmd == 'out_port':
                        data += str(self.server_out_port) + ','

            data = data[:-1] + ';'

            if type == 'get':
                self.client_sock_out.send(data)
            elif type == 'print':
                print ' ', data
        else:
            if command == 'c':
                os.system(self.clear)
                self.print_menu()
            elif command == 'h':
                if self.hide_menu:
                    self.hide_menu = False
                else:
                    self.hide_menu = True
                self.parse_terminal_command('c')
            elif command == 'r':
                self.return_to_main_menu = True
            elif command == 'q':
                exit(0)
            elif type == 'thread':
                if split[1] == 'start':
                    self.start_server_thread()
                    self.parse_terminal_command('c')
                elif split[1] == 'stop':
                    self.stop_server_thread()
                    self.parse_terminal_command('c')

    def print_menu(self):
        if self.hide_menu: return
        bar = colored('|', 'magenta')

        print colored(' {:_^54}'.format(''), 'magenta')
        print ' {:1}{:^61}{:1}'.format(bar, colored('SERVER TERMINAL', 'white'), bar)
        print colored(' {}{:_^52}{}'.format('|', '', '|'), 'magenta')
        print ' {}{:^61}{}'.format(bar, colored('CONNECTION INFORMATION', 'white'), bar)
        print ' {} {:68} {}'.format(colored('|', 'magenta'), colored(
            'SERVER CONNECTED: {}'.format(colored('CONNECTED', 'green') if self.is_connected() else colored(
                'DISCONNECTED', 'red')), 'white'), bar)
        print ' {} {:68} {}'.format(bar, colored(
            'SERVER LISTENING: {}'.format(colored('LISTENING', 'green') if self.server_thread_running() else colored(
                'NOT LISTENING', 'red')), 'white'), bar)
        print colored(' {}{:_^52}{}'.format('|', '', '|'), 'magenta')
        print ' {}{:^61}{}'.format(bar, colored('TERMINAL COMMANDS', 'white'), bar)
        for cmd in self.valid_terminal_commands:
            print ' {} \'{:^3}\' {:46} {}'.format(bar, colored(cmd[0], 'white'), cmd[1], bar)
        print colored(' {}{:_^52}{}'.format('|', '', '|'), 'magenta')

    def terminal(self):
        os.system(self.clear)
        sys.stdout.write("\x1b]2;Bluetooth Controller Terminal\x07")
        self.print_menu()
        while not self.return_to_main_menu:
            cmd = raw_input(colored(' Enter a command: ', 'cyan'))
            self.parse_terminal_command(cmd)
        self.return_to_main_menu = False
        return


if __name__ == "__main__":
    bc = BluetoothController(Motors.MotorController.MotorController(), Sensors.SonarController.SonarController(),
                             Sensors.GPSController.GPSController(), Sensors.CompassController.CompassController())
    bc.terminal()
