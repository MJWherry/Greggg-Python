import threading
import time
import os
from termcolor import colored


class SleepableThread(threading.Thread):
    def __init__(self):
        self.create_thread()

    thread = None
    thread_pid = ''
    thread_spawn_count = 0
    thread_state = 0

    def create_thread(self):
        print 'Creating thread.'
        self.thread_spawn_count += 1
        self.thread = threading.Thread(target=self.run, name='thread_{}'.format(self.thread_spawn_count), args=())
        self.thread_pid = self.thread.ident
        self.thread_state = 1

    def start_thread(self):
        if self.thread_state == 1:
            self.thread.start()
            self.thread_state = 2
        elif self.thread_state == 2:
            print ' The thread has already started.'
        elif self.thread_state == 3:
            print ' The thread has already started and is currently asleep.'
        elif self.thread_state == 4:
            print ' The thread is ended. Try restarting the thread.'

    def sleep_thread(self):
        if self.thread_state == 1:
            print ' The thread has not started yet.'
        elif self.thread_state == 2:
            print ' Sleeping thread.'
            self.thread_state = 3
        elif self.thread_state == 3:
            print ' The thread is already sleeping.'
        elif self.thread_state == 4:
            print ' The thread has already ended.'

    def wake_thread(self):
        if self.thread_state == 1:
            print ' The thread has not started yet.'
        elif self.thread_state == 2:
            print ' The thread is running and not sleeping.'
        elif self.thread_state == 3:
            print ' Waking thread.'
            self.thread_state = 2
        elif self.thread_state == 4:
            print ' The thread has already ended.'

    def stop_thread(self):
        if self.thread_state == 1:
            print ' The thread has not started yet.'
        elif self.thread_state == 2 or self.thread_state == 3:
            print ' Stopping thread.'
            self.thread_state = 4
        elif self.thread_state == 4:
            print ' The thread has already ended.'

    def restart_thread(self):
        if self.thread_state == 2 or self.thread_state == 3:
            self.stop_thread()
        if self.thread_state == 4:
            self.create_thread()
        if self.thread_state == 1:
            self.start_thread()

    def thread_status(self):
        if self.thread_state == 1:
            return colored('READY', 'yellow')
        elif self.thread_state == 2:
            return colored('RUNNING', 'green')
        elif self.thread_state == 3:
            return colored('SLEEPING', 'yellow')
        elif self.thread_state == 4:
            return colored('ENDED', 'red')

    def run(self):
        while self.thread_state != 4:
            if self.thread_state == 3:
                while self.thread_state == 3:
                    print 'Sleeping'
                    time.sleep(5)
            else:
                print 'Running'
                time.sleep(5)

    def terminal(self):
        while True:
            print  'Thread {}({}) spawn count: '.format(self.thread.name,self.thread.ident), self.thread_spawn_count, ' | Thread state: ', self.thread_state, ' | ', self.thread_status()
            cmd = raw_input('Enter command: ')
            if cmd == 'create':
                self.create_thread()
            elif cmd == 'start':
                self.start_thread()
            elif cmd == 'sleep':
                self.sleep_thread()
            elif cmd == 'wake':
                self.wake_thread()
            elif cmd == 'stop':
                self.stop_thread()
            elif cmd == 'restart':
                self.restart_thread()
            elif cmd == 'c':
                os.system('cls')
            else:
                pass

if __name__ == "__main__":
    t = SleepableThread()
    t.terminal()
