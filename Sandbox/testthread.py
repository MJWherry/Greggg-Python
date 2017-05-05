import SleepableThread
import time
import os

class testthread(SleepableThread.SleepableThread):


    def __init__(self):
       pass

    def terminal(self):
        while True:
            print 'CHILD Thread spawn count: ', self.thread_spawn_count, ' | Thread state: ', self.thread_state, ' | ', self.thread_status()
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
                None

    def run(self):
        print ' CHILD Starting child version. PID: '
        while self.thread_state != 4:
            if self.thread_state == 3:
                while self.thread_state == 3:
                    print 'Sleeping Child '
                    time.sleep(5)
            else:
                print 'Running Child'
                time.sleep(5)


if __name__ == "__main__":
    ti = testthread()
    ti.terminal()
