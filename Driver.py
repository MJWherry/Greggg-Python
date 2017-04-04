import os

from termcolor import colored
import xml.etree.ElementTree as ET
from Bluetooth import ServerController
from Motors import MotorController
from Sensors import SonarController, GPSController, CompassController


class Driver:
    # region VARIABLES

    # region ETC VARIABLES
    valid_terminal_commands = []
    clear = 'cls' if os.name == 'nt' else 'clear'
    # endregion

    # region CONTROLLER VARIABLES
    mc = None
    sc = None
    gc = None
    cc = None
    server = None

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

        self.server = ServerController.ServerController(self.mc, self.sc, self.gc, self.cc)

        # Start the appropiate threads automatically
        # self.sc.start_sonar_thread()
        # self.gc.start_gps_thread()
        # self.cc.start_compass_thread()

        # self.server.StartServerThread()


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
        print colored(' {:_^54}'.format(''), 'magenta')
        print ' {:1}{:^61}{:1}'.format(colored('|', 'magenta'), colored('MAIN MENU', 'white'), colored('|', 'magenta'))
        print colored(' {}{:_^52}{}'.format('|', '', '|'), 'magenta')
        print ' {}{:^61}{}'.format(colored('|', 'magenta'), colored('INFORMATION', 'white'), colored('|', 'magenta'))
        #print ' {} {} {:<31} {}'.format(colored('|', 'magenta'), colored('BLUETOOTH SERVER CONNECTED:', 'white'),
        #                                colored('CONNECTED', 'green') if self.server.Connected() else colored(
        #                                   'DISCONNECTED', 'red'), colored('|', 'magenta'))
        #print ' {} {} {:<31} {}'.format(colored('|', 'magenta'), colored('BLUETOOTH SERVER LISTENING:', 'white'),
        #                                colored('LISTENING', 'green') if self.server.ServerThreadRunning() else colored(
        #                                    'NOT LISTENING', 'red'), colored('|', 'magenta'))
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
                                        colored('RUNNING', 'green') if False else colored('NOT RUNNING', 'red'),
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

    def run_terminal_command(self, cmd):
        if cmd == 'mct':
            self.mc.terminal(), self.run_terminal_command('c')
        elif cmd == 'sct':
            self.sc.terminal(), self.run_terminal_command('c')
        elif cmd == 'gct':
            self.gc.terminal(), self.run_terminal_command('c')
        elif cmd == 'cct':
            self.cc.terminal(), self.run_terminal_command('c')
        elif cmd == 'bct':
            self.server.terminal(), self.run_terminal_command('c')

        elif cmd == '1':
            self.sc.print_settings()
        elif cmd == '2':
            self.gc.print_settings()
        elif cmd == '3':
            self.cc.print_settings()
        elif cmd == '4':
            self.mc.print_settings()
        elif cmd == '5':
            self.server.print_settings()

        elif cmd == 'c':
            os.system(self.clear), self.print_menu()
        elif cmd == 'q':
            self.run_terminal_command('c')
            exit(0)

    def parse_command(self, cmd):
        cmd = cmd.lower()
        commandPrefix = cmd.split(' ')[0]
        commandSuffix = cmd.replace(commandPrefix, '').strip()

        prefixes = ['mc', 'sc', 'gc']

        if cmd not in prefixes:
            self.run_terminal_command(cmd)
        else:
            # COPY STUFF OVER FROM SERVER CLASS WHEN DONE
            None

    def terminal(self):
        self.print_menu()
        while True:
            cmd = raw_input(colored(' Enter an option: ', 'cyan'))
            self.parse_command(cmd)


d = Driver()
