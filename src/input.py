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
            # If stdin isn't a real terminal (e.g., under pytest), skip setup
            if not sys.stdin.isatty():
                self.fd = None
                return self
            self.fd = sys.stdin.fileno()
            self.old = termios.tcgetattr(self.fd)
            tty.setcbreak(self.fd)
        return self

    def __exit__(self, exc_type, exc, tb):
        if not USE_WINDOWS and self.fd is not None:
            termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old)

    def read_key(self):
        if not USE_WINDOWS:
            if self.fd is None:  # running under pytest or non‑TTY
                return None
            rlist, _, _ = select.select([sys.stdin], [], [], 0)
            if rlist:
                return sys.stdin.read(1)
            return None
        else:
            if msvcrt.kbhit():
                return msvcrt.getwch()
            return None
