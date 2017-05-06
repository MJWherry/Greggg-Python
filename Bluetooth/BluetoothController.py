import logging
import os
import sys
import time
import bluetooth
from Utilities.SettingsManager import SettingsManager
from Utilities.SleepableThread import SleepableThread
from Motors.MotorController import MotorController
from Sensors.CompassController import CompassController
from Sensors.GPSController import GPSController
from Sensors.SonarController import SonarController
from termcolor import colored


class BluetoothController(SleepableThread):
    # region Variables

    SM = SettingsManager(settings_name='bluetooth', file_path='../config.xml')

    log_name = '../Logs/{}-run.log'.format(time.strftime("%Y-%m-%d %H-%M"))
    logging.basicConfig(filename=log_name, level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s %(message)s')
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
    # try:
    #     mc = MotorController
    #     logging.info('(BLUETOOTH) Set mc to MotorController instance.')
    # except:
    #     logging.error('(BLUETOOTH) Couldn\'t set mc to MotorController instance.')
    # try:
    #     sc = SonarController
    #     logging.info('(BLUETOOTH) Set sc to SonarController instance.')
    # except:
    #     logging.error('(BLUETOOTH) Couldn\'t set sc to SonarController instance.')
    # try:
    #     gc = GPSController
    #     logging.info('(BLUETOOTH) Set gc to GPSController instance.')
    # except:
    #     logging.error('(BLUETOOTH) Couldn\'t set gc to GPSController instance.')
    # try:
    #     cc = CompassController
    #     logging.info('(BLUETOOTH) Set cc to CompassController instance.')
    # except:
    #     logging.error('(BLUETOOTH) Couldn\'t set cc to CompassController instance.')
    # endregion

    # region ETC Variables
    valid_terminal_commands = []
    received_commands = []
    hide_menu = False
    return_to_main_menu = False
    clear = 'cls' if os.name == 'nt' else 'clear'
    # endregion

    # endregion

    # region Server Functions
    def is_connected(self):
        if self.client_address_in == '' and self.client_address_out == '':
            return colored('DISCONNECTED','red')
        return colored('CONNECTED', 'green')

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
        self.create_thread()
        self.connected = True

    def send_data(self, data):
        # TEST
        try:
            self.client_sock_out.send(data)
        except:
            print ' No outbound connection available.'

    # endregion

    # region Thread Functions
    def run(self):
        while self.thread_state != 4:
            if self.thread_state == 3:
                while self.thread_state == 3:
                    time.sleep(1)
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

    # endregion

    def __init__(self, motor=MotorController(), sonar=SonarController(), gps=GPSController(), compass=CompassController()):
        self.apply_settings()
        self.mc = motor
        self.sc = sonar
        self.gc = gps
        self.cc = compass
        super(BluetoothController, self).__init__()

    def apply_settings(self):
        self.server_in_port = int(self.SM.get_setting_value('server_in_port'))
        self.server_out_port = int(self.SM.get_setting_value('server_out_port'))
        self.server_backlog = int(self.SM.get_setting_value('server_backlog'))
        self.server_in_byte_size = int(self.SM.get_setting_value('server_in_byte_size'))
        self.server_in_connection_timeout = float(self.SM.get_setting_value('server_in_connection_timeout'))
        self.server_out_connection_timeout = float(self.SM.get_setting_value('server_out_connection_timeout'))
        self.server_address = str(self.SM.get_setting_value('server_address'))

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
        elif split[0] == 'thread':
            self.parse_thread_command(split[1])
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
                self.parse_thread_command(split[1])

    def print_menu(self):
        if self.hide_menu: return
        bar = colored('|', 'magenta')

        print colored(' {:_^54}'.format(''), 'magenta')
        print ' {:1}{:^61}{:1}'.format(bar, colored('SERVER TERMINAL', 'white'), bar)
        print colored(' {}{:_^52}{}'.format('|', '', '|'), 'magenta')
        print ' {}{:^61}{}'.format(bar, colored('CONNECTION INFORMATION', 'white'), bar)
        print ' {} {:68} {}'.format(colored('|', 'magenta'), colored('BLUETOOTH SERVER CONNECTED: {}'.format(
            self.is_connected()), 'white'), bar)
        print ' {} {:68} {}'.format(bar,
                                    colored('BLUETOOTH SERVER LISTENING: {}'.format(self.thread_status()), 'white'),
                                    bar)
        print ' {} {:33} {:34} {}'.format(bar, colored('SERVER ADDRESS: {}'.format(self.server_address), 'white'),
                                          colored('BACKLOG: {}'.format(self.server_backlog), 'white'), bar)
        print ' {} {:33} {:34} {}'.format(bar, colored('PORT (IN): {}'.format(self.server_in_port), 'white'),
                                          colored('PORT (OUT): {}'.format(self.server_out_port), 'white'), bar)

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
    bc = BluetoothController()
    bc.terminal()
