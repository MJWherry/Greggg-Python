import os
import threading
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

    def get_byte_size(self):
        return self.server_in_byte_size
    # endregion

    # region Mutators
    def set_server_backlog(self, backlog):
        self.server_backlog=backlog

    def set_server_in_port(self,port):
        self.server_in_port=port

    def set_server_out_port(self,port):
        self.server_out_port=port

    def set_byte_size(self,size):
        self.server_in_byte_size=size

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

    def print_server_in_byte_size(self):
        print 'Server in byte size: ', self.server_in_byte_size
    # endregion

    # endregion

    # region Server Functions
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
        None

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
            if child.attrib['name'] == 'server_in_port': self.server_in_port = int(child.attrib['value'])
            elif child.attrib['name'] == 'server_backlog': self.server_backlog = int(child.attrib['value'])
            elif child.attrib['name'] == 'server_out_port': self.server_out_port = int(child.attrib['value'])
            elif child.attrib['name'] == 'server_in_byte_size': self.server_in_byte_size = int(child.attrib['value'])
            elif child.attrib['name'] == 'server_address': self.server_address = str(child.attrib['value'])

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
        command = command.lower()
        self.received_commands.append(command)

        commandPrefix = command.split(' ')[0]
        commandSuffix = command.replace(commandPrefix, '').rstrip()
        splitCommand = commandSuffix.split(' ')

        prefixes = ['mc', 'sc', 'gc']

        if commandPrefix not in prefixes:
            # Inform and return ( ADD LOGGING )
            print ' No valid command sent.'
            return

        # If the command sent has a valid prefix
        else:
            # region MOTOR CONTROLLER PREFIX
            if commandPrefix == 'mc':
                print 'Motor command received...parsing'
                # Send the motor controller a command (error checking done in
                # the motor controller class itself)
                self.mc.run_motor_command(commandSuffix)
                # Reply with nothing, but still send a reply
                self.client_sock.send('')
            # endregion

            # region SONAR CONTROLLER PREFIX
            elif commandPrefix == 'sc':
                print 'sonar command received...parsing'
                # region PRINTING
                if splitCommand[0] == 'print':
                    for cmd in splitCommand:
                        if cmd == 'fl':
                            ret = ret, ',', self.sc.get_front_left_sonar_distance()
                        elif cmd == 'fm':
                            ret = ret, ',', self.sc.get_front_middle_sonar_distance()
                        elif cmd == 'fr':
                            ret = ret, ',', self.sc.get_front_right_sonar_distance()
                        elif cmd == 'mb':
                            ret = ret, ',', self.sc.get_middle_backS_sonar_distance()
                        elif cmd == 'all':
                            ret = ret, ',', self.sc.GetAllData()
                    print ret
                # endregion

                # region GETTING
                elif splitCommand[0] == 'get':
                    ret = ''
                    for cmd in splitCommand:
                        if cmd == 'fl':
                            ret = ret, ',', self.sc.get_front_left_sonar_distance()
                        elif cmd == 'fm':
                            ret = ret, ',', self.sc.get_front_middle_sonar_distance()
                        elif cmd == 'fr':
                            ret = ret, ',', self.sc.get_front_right_sonar_distance()
                        elif cmd == 'mb':
                            ret = ret, ',', self.sc.get_middle_backS_sonar_distance()
                        elif cmd == 'all':
                            ret = ret, ',', self.sc.GetAllData()
                    print ret
                    self.client_sock.send(ret)
                else:
                    print colored(' Invalid sonar command.', 'red')
                    # endregion
            # endregion

            # region GPS CONTROLLER PREFIX
            elif commandPrefix == 'gc':
                if commandSuffix == 'print':
                    self.gc.PrintData()
                if commandSuffix == 'get':
                    self.client_sock.send(self.gc.GetData())
                else:
                    print colored(' Invalid gps command.', 'red')
                    # endregion

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