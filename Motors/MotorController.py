import serial
import os
import logging
from termcolor import colored


class MotorController:
    # region Variables

    # region Motor Variables
    serial = serial_baud_rate = serial_port = None
    # endregion

    # region ETC Variables
    valid_terminal_commands = []
    valid_motor_commands = []
    valid_motor_commands2 = []
    hide_menu = False
    return_to_main_menu = False
    clear = 'cls' if os.name == 'nt' else 'clear'

    # endregion

    # endregion

    # region Accessors/Mutators
    def get_serial(self):
        return self.serial

    def get_serial_port(self):
        return self.serial_port

    def get_serial_baud_rate(self):
        return self.serial_baud_rate

    def set_serial_port(self, port):
        self.serial_port = port

    def set_serial_baud_rate(self, baud_rate):
        self.serial_baud_rate = baud_rate

    def is_connected(self):
        if self.serial is None: return False
        return self.serial.is_open
    # endregion

    # region Motor functions
    def connect(self):
        logging.info('Trying to connect to the motor hardware.')
        try:
            self.serial = serial.Serial(self.serial_port, self.serial_baud_rate)
            logging.info('Motor hardware connected.')
        except:
            logging.error('Could not establish a connection to the motor hardware.')

    def check_motor_command(self, command):
        commandBase = command.split()[0]
        if commandBase not in self.valid_motor_commands2: return False
        # Check syntax (int int and so on, after motor command file gets updated
        return True

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
        # Terminal Commands
        logging.info('Loading terminal commands for the motor controller.')
        try:
            terminal_cmd_file = open('info/Motor/TerminalCommands.txt', 'r')
            for line in terminal_cmd_file:
                word_list = line.split(',')
                self.valid_terminal_commands.append((word_list[0], word_list[1].rstrip()))
            terminal_cmd_file.close()
        except:
            logging.error('Could not load the motor controller terminal command file.')

        # Motor Commands
        logging.info('Loading motor commands for the motor controller.')
        try:
            motor_cmd_file = open('info/Motor/MotorCommands.txt', 'r')
            for line in motor_cmd_file:
                word_list = line.split(',')
                self.valid_motor_commands.append((word_list[0], word_list[1].rstrip()))
                self.valid_motor_commands2.append(word_list[0])
            motor_cmd_file.close()
        except:
            logging.error('Could not load the motor controller motor command file.')

        # Settings
        logging.info('Loading  settings for the motor controller.')
        try:
            cfg_file = open('info/Motor/Config.txt', 'r')
            for line in cfg_file:
                word_list = line.split('=')
                if word_list[0] == 'serial_baud_rate':
                    self.serial_baud_rate = word_list[1].rstrip()
                elif word_list[0] == 'serial_port':
                    self.serial_port = word_list[1].rstrip()
                else:
                    logging.info('Invalid line in motor config file: ', line)
            cfg_file.close()
        except:
            logging.error('Could not load the motor controller command file.')

    def save_settings(self):
        None

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