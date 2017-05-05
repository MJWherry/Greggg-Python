# Imports
import threading
from termcolor import colored

class Controller:
    # region Variables

    # region Controller-Specific Variables
    None
    # endregion

    # region Thread Variables
    thread = None
    thread_pid = ''
    thread_spawn_count = 0
    thread_state = 0
    # 0: No state, 1: Created, 2: Running, 3: Sleeping, 4: Ended
    # endregion

    # region Etc Variables
    None
    # endregion

    # endregion

    # region Controller Specific Functions
    None

    # endregion

    # region Basic Thread Functions
    def create_thread(self):
        self.thread_spawn_count += 1
        self.thread = threading.Thread(target=self.run, name='thread_{}'.format(self.thread_spawn_count), args=())
        self.thread_pid = threading.Thread(self.thread).ident
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
            self.thread_state = 2
        elif self.thread_state == 4:
            print ' The thread has already ended.'

    def stop_thread(self):
        if self.thread_state == 1:
            print ' The thread has not started yet.'
        elif self.thread_state == 2 or self.thread_state == 3:
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
        None



    # endregion

    # region Basic Class Functions
    def __init__(self):
        None

    def load_settings(self):
        None

    def get_settings(self):
        None

    def save_settings(self):
        None

    def print_menu(self):
        None

    def parse_terminal_command(self, cmd):
        None

    def terminal(self):
        None
    # endregion

if __name__ == "__main__":
    None
