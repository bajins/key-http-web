import email
import sys
import time
from http import HTTPStatus


def date_time_string(timestamp=None):
    """Return the current date and time formatted for a message header."""
    if timestamp is None:
        timestamp = time.time()
    return email.utils.formatdate(timestamp, usegmt=True)


def log_date_time_string(self):
    """Return the current time formatted for logging."""
    now = time.time()
    year, month, day, hh, mm, ss, x, y, z = time.localtime(now)
    s = "%02d/%3s/%04d %02d:%02d:%02d" % (
        day, self.monthname[month], year, hh, mm, ss)
    return s


weekdayname = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

monthname = [None,
             'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
             'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


def address_string(self):
    """Return the client address."""

    return self.client_address[0]


def log_request(self, code='-', size='-'):
    """Log an accepted request.

    This is called by send_response().

    """
    if isinstance(code, HTTPStatus):
        code = code.value
    self.log_message('"%s" %s %s',
                     self.requestline, str(code), str(size))


def log_error(self, format, *args):
    """Log an error.

    This is called when a request cannot be fulfilled.  By
    default it passes the message on to log_message().

    Arguments are the same as for log_message().

    XXX This should go to the separate error log.

    """

    self.log_message(format, *args)


def log_message(self, format, *args):
    """Log an arbitrary message.

    This is used by all other logging functions.  Override
    it if you have specific logging wishes.

    The first argument, FORMAT, is a format string for the
    message to be logged.  If the format string contains
    any % escapes requiring parameters, they should be
    specified as subsequent arguments (it's just like
    printf!).

    The client ip and current date/time are prefixed to
    every message.

    """

    sys.stderr.write("%s - - [%s] %s\n" %
                     (self.address_string(),
                      self.log_date_time_string(),
                      format % args))
