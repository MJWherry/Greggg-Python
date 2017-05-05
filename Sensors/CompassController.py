import logging
import os
import sys
import time
import hmc5883l
from Skeletons import SettingsManager
from termcolor import colored
from Skeletons import SleepableThread

logging.basicConfig(filename='run.log', level=logging.DEBUG, format=('%(asctime)s %(levelname)s %(message)s'))

class CompassController(SleepableThread.SleepableThread):
    # region Variables

    SM = SettingsManager.SettingsManager()

    # region I2C settings
    i2c_port = 1
    i2c_bus_address = 0x1E
    # endregion

    # region Compass settings
    try:
        compass = hmc5883l
        logging.info('(COMPASS) Compass set to hmc5883l instance.')
    except:
        logging.error('(COMPASS) Couldn\'t set compass to hmc5883l instance.')
    gauss = 0
    declination_degrees = -9
    declination_minutes = 23
    update_time_interval = 0.5
    current_heading = None
    # endregion

    # region ETC Variables
    valid_terminal_commands = []
    hide_menu = False
    return_to_main_menu = False
    clear = 'cls' if os.name == 'nt' else 'clear'
    # endregion

    # endregion

    # region Compass functions

    # endregion

    # region Thread Functions
    def run(self):
        while self.thread_state != 4:
            if self.thread_state == 3:
                while self.thread_state == 3:
                    time.sleep(1)
            else:
                self.current_heading = str(self.compass.degrees(self.compass.heading()))
                time.sleep(self.update_time_interval)

    # endregion

    def __init__(self):
        self.SM.load_settings('compass')
        self.i2c_port = int(self.SM.get_setting_value('i2c_port'))
        self.i2c_bus_address = str(self.SM.get_setting_value('i2c_bus_address'))
        self.declination_minutes = int(self.SM.get_setting_value('declination_minutes'))
        self.declination_degrees = int(self.SM.get_setting_value('declination_degrees'))
        self.gauss = float(self.SM.get_setting_value('gauss'))
        self.update_time_interval = float(self.SM.get_setting_value('update_time_interval'))
        try:
            self.compass = hmc5883l.hmc5883l(gauss=self.gauss,
                                             declination=(self.declination_degrees,self.declination_minutes))
            logging.info('(COMPASS) Compass object created.')
        except:
            logging.error('(COMPASS) Couldn\'t create compass object.')
        super(CompassController, self).__init__()

    def parse_terminal_command(self, cmd):
        cmd = cmd.lower()
        type = cmd.split()[0]
        parameters = cmd.replace(type, '').split()
        split = cmd.split()

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
        elif type == 'thread':
            self.parse_thread_command(cmd.split()[1])
        elif type == 'get' or type == 'print':
            data = ' '
            for cmd in parameters:
                if cmd == 'heading':
                    data += '{},'.format(self.current_heading)
                elif cmd == 'declination_degrees':
                    data += '{},'.format(self.declination_degrees)
                elif cmd == 'declination_minutes':
                    data += '{},'.format(self.declination_minutes)
                elif cmd == 'declination':
                    data += '({}, {}),'.format(self.declination_degrees,self.declination_minutes)
                elif cmd == 'update_time_interval' or cmd == 'interval':
                    data += '{},'.format(self.update_time_interval)
                elif cmd == 'i2c_bus_address' or cmd == 'i2c_addr':
                    data += '{},'.format('{}'.format(self.i2c_bus_address, '#04x'))
                elif cmd == 'i2c_bus_port' or cmd == 'i2c_port':
                    data += '{},'.format(self.i2c_port)
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
        print ' {} {:59} {}'.format(bar, colored('STATUS: {}'.format('is connected? implement'), 'white'), bar)
        print ' {} {:33} {:34} {}'.format(bar, colored('I2C PORT: {}'.format(self.i2c_port), 'white'),
                                          colored('I2C ADDRESS: {}'.format(self.i2c_bus_address), 'white'), bar)
        print ' {} {:33} {:34} {}'.format(bar,
                                          colored('DECLINATION MINUTES: {}'.format(self.declination_minutes), 'white'),
                                          colored('DECLINATION DEGREES: {}'.format(self.declination_degrees), 'white'),
                                          bar)
        print colored(' {}{:52}{}'.format('|', '', '|'), 'magenta')
        print ' {} {:68} {}'.format(bar, colored('THREAD: {}'.format(self.thread_status()), 'white'),bar)
        print ' {} {:59} {}'.format(bar, colored('THREAD PROCESS ID: {}'.format(self.thread_pid), 'white'), bar)
        print ' {} {:59} {}'.format(bar, colored('THREAD SPAWN COUNT: {}'.format(self.thread_spawn_count), 'white'),bar)
        print colored(' {}{:_^52}{}'.format('|', '', '|'), 'magenta')

    def terminal(self):
        os.system(self.clear)
        sys.stdout.write("\x1b]2;Compass Controller Terminal\x07")
        self.print_menu()
        while not self.return_to_main_menu:
            cmd = raw_input(colored(' Enter a command: ', 'cyan'))
            self.parse_terminal_command(cmd)
        self.return_to_main_menu = False


if __name__ == "__main__":
    cc = CompassController()
    cc.terminal()
