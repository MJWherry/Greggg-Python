import logging
import os
import pynmea2
import serial
import threading
import time
from termcolor import colored


class GPSController:
    ser = None
    connected = False
    commands = []
    hideMenu = False
    ret = False
    thread = None
    data = ''
    clear = 'cls' if os.name == 'nt' else 'clear'

    # region THREAD FUNCTIONS
    def StartGPSThread(self):
        self.thread.start()

    def GPSThreadRunning(self):
        return threading.Thread.isAlive(self.thread)

    def StopGPSThread(self):
        self.run = False

    def run(self):
        while True:
            self.data = self.ser.read(175)
            time.sleep(0.5)

    # endregion

    def __init__(self):
        logging.info('Creating GPS Controller thread.')
        self.thread = threading.Thread(target=self.run, args=())
        logging.info('Trying to connect to the gps hardware.')
        try:
            self.ser = serial.Serial('/dev/ttyS0', 9600)
            self.connected = True
            logging.info('GPS hardware connected.')
        except:
            logging.error('Could not establish a connection to the gps hardware.')
            self.connected = False

    def PrintMenu(self):
        print colored(' {:_^54}'.format(''), 'magenta')
        print ' {:1}{:^61}{:1}'.format(colored('|', 'magenta'), colored('GPS TERMINAL', 'white'),
                                       colored('|', 'magenta'))
        print colored(' {}{:_^52}{}'.format('|', '', '|'), 'magenta')
        print ' {}{:^61}{}'.format(colored('|', 'magenta'), colored('CONNECTION INFORMATION', 'white'),
                                   colored('|', 'magenta'))
        print colored(' {}{:_^52}{}'.format('|', '', '|'), 'magenta')
        print ' {}{:^61}{}'.format(colored('|', 'magenta'), colored('TERMINAL COMMANDS', 'white'),
                                   colored('|', 'magenta'))
        for command in self.commands:
            print ' {} \'{:^3}\' {:46} {}'.format(colored('|', 'magenta'), colored(command[0], 'white'), command[1],
                                                  colored('|', 'magenta'))
        print colored(' {}{:_^52}{}'.format('|', '', '|'), 'magenta')

    def RunTerminalCommand(self, command):
        command = command.lower()
        if command == 'c':
            os.system(self.clear)
            if not self.hideMenu:
                self.PrintMenu()
        elif command == 'h':
            if self.hideMenu:
                self.hideMenu = False
            else:
                self.hideMenu = True
            self.RunTerminalCommand('c')
        elif command == 'r':
            self.ret = True
        if command == 'q':
            exit(0)

    def Terminal(self):
        logging.info('Starting gps terminal.')
        os.system(self.clear)
        if not self.hideMenu:
            self.PrintMenu()
        while not self.ret:
            command = raw_input(colored(' Enter a command: ', 'cyan'))
            self.RunTerminalCommand(command)
        self.ret = False
        return

    def PrintData(self):
        print(self.data)

    def mainLoop(self):
        streamreader = pynmea2.NMEAStreamReader()
        while 1:
            data = self.ser.read()
            for msg in streamreader.next(data):
                print msg
                msg = pynmea2.parse("$GPGGA,184353.07,1929.045,S,02410.506,E,1,04,2.6,100.00,M,-33.9,M,,0000*6D")
                print msg
        self.ser.close()
