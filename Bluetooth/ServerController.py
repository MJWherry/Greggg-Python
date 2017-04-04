import os
import threading
import bluetooth
from termcolor import colored

import Motors.MotorController
import Sensors.CompassController
import Sensors.GPSController
import Sensors.SonarController

class ServerController:
    # region Variables

    # region Bluetooth Variables
    server_sock = None
    client_sock = None
    client_address = None
    server_backlog = 0
    in_port = 0
    out_port = 0
    size = 0
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
    hide_menu = False
    return_to_main_menu = False
    clear = 'cls' if os.name == 'nt' else 'clear'
    run_thread = False

    # endregion

    # endregion

    # region Accessors/Mutators/Printers

    # region Accessors


    # endregion

    # region Mutators


    # endregion

    # region Printers


    # endregion

    # endregion

    # region Server Functions
    def create_socket(self):
        self.server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

    def bind_in_port(self):
        self.server_sock.bind(("", self.in_port))

    def bind_out_port(self):
        self.server_sock.bind(("", self.out_port))

    def listen(self):
        self.server_sock.listen(self.server_backlog)

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
        self.mc = motor
        self.sc = sonar
        self.gc = gps
        self.cc = compass
        self.thread = threading.Thread(target=self.run, args=())

    def load_settings(self):
        None

    def save_settings(self):
        None

    def print_settings(self):
        None

    def parse_terminal_command(self, command):
        command = command.lower()
        self.commandList.append(command)

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
                            ret = ret, ',', self.sc.GetFrontLeftData()
                        elif cmd == 'fm':
                            ret = ret, ',', self.sc.GetFrontMiddleData()
                        elif cmd == 'fr':
                            ret = ret, ',', self.sc.GetFrontRightData()
                        elif cmd == 'mb':
                            ret = ret, ',', self.sc.GetMiddleBackData()
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
        None

    def terminal(self):
        None