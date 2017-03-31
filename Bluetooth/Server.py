import os
import threading
import bluetooth
import time
import logging
import Motors.MotorController
import Sensors.SonarController, Sensors.GPSController, Sensors.CompassController

from termcolor import colored


# hciconfig -a  : get bluetooth device id, needed for client



class Server():
    # region VARIABLES

    # region BLUETOOTH VARIABLES
    server_sock = None
    client_sock = None
    client_address = None
    server_backlog = 1
    in_port = 2
    out_port = 1
    size = 1024
    # endregion

    # region CONTROLLER VARIABLES
    mc = Motors.MotorController
    sc = Sensors.SonarController.SonarController
    gc = Sensors.GPSController.GPSController
    cc = Sensors.CompassController
    # endregion

    # region ETC VARIABLES
    commandList = []
    thread = None
    startedThread = False
    runThread = False
    clear = 'cls' if os.name == 'nt' else 'clear'

    # endregion

    # endregion

    def __init__(self, motor, sonar, gps):
        # assign to controllers passed.
        self.mc = motor
        self.sc = sonar
        self.gc = gps
        # self.cc = compass

        print 'Starting server'

        self.server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

        self.server_sock.bind(("", self.in_port))

        # Allow the server socket to listen
        self.server_sock.listen(self.server_backlog)
        # if the timeout doesnt occur and a connection is established, then and only then run
        self.thread = threading.Thread(target=self.run, args=())

    # region THREAD FUNCTIONS
    def StartServerThread(self):
        self.runThread = True
        if not self.startedThread:
            self.thread.start()
        else:
            self.thread = threading.Thread(target=self.run)
        self.startedThread = True

    def ServerThreadRunning(self):
        return self.thread.isAlive()

    def run(self):
        while self.runThread:
            print 'Waiting for connection...'
            try:
                self.client_sock, self.client_address = self.server_sock.accept()
                print 'Accepted connection from ', self.client_address
                while 1:
                    data = self.client_sock.recv(self.size)
                    if data:
                        print 'Received: ', data
                        self.ParseCommand(data)
            except:
                print 'Restarting socket'
                self.client_sock.close()

    # endregion

    def ParseCommand(self, command):

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

    def Connected(self):
        return not self.client_sock is None

    def Connect(self):
        self.client_sock, self.client_address = self.server_sock.accept()

    def Disconnect(self):
        self.client_sock.close()
        self.server_sock.close()
