# Externals
import threading
import queue
from subprocess import *
from subprocess import check_output as __check_output


# Timeout exception
class TimeoutExpired(CalledProcessError):
    def __init__(self, cmd, timeout, output):
        self.cmd = cmd
        self.timeout = timeout
        self.output = output


# Wrapper for check_output of 3.2
# Adds timeout functionality
def check_output(*args, **kwargs):
    # Take timeout out of kwargs
    timeout = float(kwargs.pop('timeout', None))

    # Normal execution without timeout?
    if timeout is None:
        return __check_output(*args, **kwargs)

    # Instantiate a queue
    q = queue.Queue()
    args = [q] + list(args)

    # Function to be run as a thread
    def run(q_, *args_, **kwargs_):
        # Run check_output and put result in queue
        try:
            q_.put(__check_output(*args_, **kwargs_))
        except Exception as exc:
            q_.put(exc)

    # Start thread
    thread = threading.Thread(target=run, args=args, kwargs=kwargs)
    thread.start()

    # Join thread while using a timeout
    thread.join(timeout)

    # Did a timeout occur?
    if thread.is_alive():
        # Command
        #noinspection PyBroadException
        try:
            cmd = args[1]
        except Exception:
            cmd = None

        # To do: Is cmd correct? Implement output
        raise TimeoutExpired(cmd, timeout, '<Not implemented>')

    # Get value of queue
    item = q.get()

    # Check if item is an exception and raise if necessary
    if isinstance(item, Exception):
        raise item

    # Return value
    return item
