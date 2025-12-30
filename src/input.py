import os
import sys


USE_WINDOWS = os.name == "nt"
if USE_WINDOWS:
    import msvcrt
else:
    import termios, tty, select

class KeyReader:
    """Cross-platform non-blocking key reader."""
    def __enter__(self):
        if not USE_WINDOWS:
            self.fd = sys.stdin.fileno()
            self.old = termios.tcgetattr(self.fd)
            tty.setcbreak(self.fd)
        return self
    def __exit__(self, exc_type, exc, tb):
        if not USE_WINDOWS:
            termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old)

    def read_key(self):
        if USE_WINDOWS:
            if msvcrt.kbhit():
                ch = msvcrt.getwch()
                return ch
            return None
        else:
            rlist, _, _ = select.select([sys.stdin], [], [], 0)
            if rlist:
                return sys.stdin.read(1)
            return None
