import logging
import os
import sys
import serial
import time
from termcolor import colored
from Utilities.SettingsManager import SettingsManager
import xml.etree.ElementTree as ET


class MotorController:
    # region Variables

    SM = SettingsManager(settings_name='motor', file_path='../config.xml')
    log_name = '../Logs/{}-run.log'.format(time.strftime("%Y-%m-%d %H-%M"))
    logging.basicConfig(filename=log_name, level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s %(message)s')

    # region Motor Setting Variables
    serial = None
    serial_baud_rate = 19200
    serial_port = '/dev/serial/by-id/usb-Prolific_Technology_Inc._USB-Serial_Controller-if00-port0'
    # endregion

    # region ETC Variables
    valid_terminal_commands = []
    valid_motor_commands = []
    check_motor_commands = False
    hide_menu = False
    return_to_main_menu = False
    clear = 'cls' if os.name == 'nt' else 'clear'

    # endregion

    # endregion

    # region Motor functions
    def is_connected(self):
        if self.serial is None: return False
        return True

    def connect(self):
        try:
            self.serial = serial.Serial(self.serial_port, self.serial_baud_rate)
        except:
            None

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
                else:
                    return False
        return valid

    def run_motor_command(self, cmd):
        #valid = True
        #if self.check_motor_commands:
        #    valid = self.check_motor_command(cmd)
        #if valid:
        print colored(' Sending command...', 'yellow')
        try:
            self.serial.write(cmd + '\r')
            print colored(' Command sent.', 'green')
            return ' True;'
        except:
            print colored(' Command not sent.', 'red')
            return ' False;'

    # endregion

    def __init__(self):
        self.apply_settings()
        self.connect()

    def apply_settings(self):
        try:self.serial_port = str(self.SM.get_setting_value('serial_port'))
        except AttributeError: print ' Could not set setting for serial_port via the setting manager.'
        try:self.serial_baud_rate = int(self.SM.get_setting_value('serial_baud_rate'))
        except: print ' Could not set setting for serial_baud_rate via the setting manager.'

    def load_settings(self):
        try:
            tree = ET.parse('/home/pi/Desktop/greggg-python/config.xml')
        except:
            return
        root = tree.getroot()
        device = root.find('motor')
        for child in device.iter('hardware_commands'):
            for command in child.iter('command'):
                valid_command = (command.attrib['name'], command.attrib['parameter_count'], [])
                for parameter in command.iter('parameter'):
                    valid_command[2].append((parameter.attrib['description'], parameter.attrib['range']))
                self.valid_motor_commands.append(valid_command)
        #for child in device.iter('terminal_commands'):
        #    for command in child.iter('command'):
        #        self.valid_terminal_commands.append((command.attrib['name'], command.attrib['description']))

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
        else:
            print self.run_motor_command(cmd)

    def print_menu(self):
        if self.hide_menu: return

        bar = colored('|', 'magenta')

        print colored(' {:_^54}'.format(''), 'magenta')
        print ' {}{:^61}{}'.format(bar, colored('MOTOR CONTROLLER TERMINAL', 'white'), bar)
        print colored(' {}{:_^52}{}'.format('|', '', '|'), 'magenta')
        print ' {}{:^61}{}'.format(bar, colored('CONNECTION INFORMATION', 'white'), bar)
        print ' {} {:68} {}'.format(bar, colored('STATUS: {}'.format(
            colored('CONNECTED', 'green') if self.is_connected() else colored('DISCONNECTED', 'red')), 'white'), bar)
        print ' {} {:59} {}'.format(bar, colored('PORT: {}'.format(self.serial_port[:41]) + '...', 'white'), bar)
        print ' {} {:59} {}'.format(bar, colored('BAUD RATE: {}'.format(self.serial_baud_rate), 'white'), bar)
        print colored(' {}{:_^52}{}'.format('|', '', '|'), 'magenta')

    def terminal(self):
        os.system(self.clear)
        if os.name != 'nt':
            sys.stdout.write("\x1b]2;Motor Control Terminal\x07")
        self.print_menu()
        while not self.return_to_main_menu:
            cmd = raw_input(colored(' Enter a command: ', 'cyan'))
            self.parse_terminal_command(cmd)
        self.return_to_main_menu = False
        return


if __name__ == "__main__":
    mc = MotorController()
    mc.terminal()
