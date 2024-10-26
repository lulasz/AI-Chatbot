import itertools
import time
import sys
import threading

class Spinner:
    def __init__(self, message="Text..."):
        self.spinner = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
        self.message = message
        self.lock = threading.Lock()
        self.active = True

    def set_text(self, new_text, active = False):
        self.active = active
        with self.lock:
            self.message = new_text

    def loading_circle(self):
        while self.active:
            with self.lock:
                sys.stdout.write(f'\r{next(self.spinner)} {self.message}')
            sys.stdout.flush()
            time.sleep(0.1)

        # Clear the spinner line after loading is done
        self.stop()

    def stop(self):
        self.active = False
        sys.stdout.write('\r')
        sys.stdout.write("\033[K")
        sys.stdout.flush()
