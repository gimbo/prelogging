#!/usr/bin/env python

__author__ = 'brianoneill'

import os
import time
import math
import logging

try:
    import lcd
except ImportError:
    import sys
    sys.path[0:0] = ['..']

from lcd import LoggingConfigDictEx

import examples.child_logger_sub_noprop as sub_noprop
import examples.child_logger_sub_prop as sub_prop


LOG_PATH = '_log/child_loggers/'
SHARED_FILE_HANDLER_NAME = 'app_file'

def config_logging(logfilename):
    lcd_ex = init_logging_config(__name__, logfilename)
    sub_noprop.logging_config_sub(lcd_ex, __name__,
                                  file_handler=SHARED_FILE_HANDLER_NAME)
    sub_prop.logging_config_sub(lcd_ex, __name__)
    lcd_ex.config()


def init_logging_config(loggername, logfilename):
    # add handlers to root == False, default
    lcd_ex = LoggingConfigDictEx(log_path=LOG_PATH)

    # Create stderr console handler; output shows logger name and loglevel;
    ## loglevel higher than DEBUG.
    lcd_ex.add_formatter('busier_console_fmt',
                         format='%(name)-25s: %(levelname)-8s: %(message)s')
    lcd_ex.add_stderr_console_handler('console',
                                      formatter='busier_console_fmt',
                                      level='INFO')

    # Add main file handler, which will write to LOG_PATH + '/' + logfilename,
    # and add logger (loggername == __name__) that uses it
    lcd_ex.add_formatter(
        'my_file_formatter',
        format='%(name)-25s: %(levelname)-8s: %(asctime)24s: %(message)s'
    ).add_file_handler(
        'app_file',
        filename=logfilename,
        level='DEBUG',
        formatter='my_file_formatter'
    ).add_logger(
        loggername,
        handlers=('app_file', 'console'),
        level='DEBUG',
        propagate=False    # so it DOESN'T propagate to parent logger
    )
    return lcd_ex

def boring(n):
    logging.getLogger(__name__).debug("Doing something boring with %d" % n)
    sub_noprop.do_something_boring(n)
    sub_prop.do_something_boring(n)

def special(n):
    logging.getLogger(__name__).info("Doing something special with %d" % n)
    sub_noprop.do_something_special(n)
    sub_prop.do_something_special(n)


# print("__name__ = %r    __package__ = %r" % (__name__, __package__), flush=True)

def main():
    config_logging('child_loggers.log')

    logging.getLogger(__name__).info("Starting up... ")

    for i in range(3):
        boring(i)
        special(i)

    logging.getLogger(__name__).info("... shutting down.")


if __name__ == '__main__':
    main()

    # Written to stderr (flush left):
    '''
    __main__                 : INFO    : Starting up...
    __main__.sub_noprop      : DEBUG   : Doing something boring with 0
    __main__                 : INFO    : Doing something special with 0
    __main__.sub_noprop      : INFO    : Doing something SPECIAL with 0
    __main__.sub_prop        : INFO    : Doing something SPECIAL with 0
    __main__.sub_noprop      : DEBUG   : Doing something boring with 1
    __main__                 : INFO    : Doing something special with 1
    __main__.sub_noprop      : INFO    : Doing something SPECIAL with 1
    __main__.sub_prop        : INFO    : Doing something SPECIAL with 1
    __main__.sub_noprop      : DEBUG   : Doing something boring with 2
    __main__                 : INFO    : Doing something special with 2
    __main__.sub_noprop      : INFO    : Doing something SPECIAL with 2
    __main__.sub_prop        : INFO    : Doing something SPECIAL with 2
    __main__                 : INFO    : ... shutting down.
    '''
    # Written to _log/child_loggers/child_loggers.log (flush left):
    '''
    __main__                 : INFO    :  2016-07-07 15:23:53,424: Starting up...
    __main__                 : DEBUG   :  2016-07-07 15:23:53,424: Doing something boring with 0
    __main__.sub_noprop      : DEBUG   :  2016-07-07 15:23:53,424: Doing something boring with 0
    __main__.sub_prop        : DEBUG   :  2016-07-07 15:23:53,424: Doing something boring with 0
    __main__                 : INFO    :  2016-07-07 15:23:53,424: Doing something special with 0
    __main__.sub_noprop      : INFO    :  2016-07-07 15:23:53,424: Doing something SPECIAL with 0
    __main__.sub_prop        : INFO    :  2016-07-07 15:23:53,425: Doing something SPECIAL with 0
    __main__                 : DEBUG   :  2016-07-07 15:23:53,425: Doing something boring with 1
    __main__.sub_noprop      : DEBUG   :  2016-07-07 15:23:53,425: Doing something boring with 1
    __main__.sub_prop        : DEBUG   :  2016-07-07 15:23:53,425: Doing something boring with 1
    __main__                 : INFO    :  2016-07-07 15:23:53,425: Doing something special with 1
    __main__.sub_noprop      : INFO    :  2016-07-07 15:23:53,425: Doing something SPECIAL with 1
    __main__.sub_prop        : INFO    :  2016-07-07 15:23:53,425: Doing something SPECIAL with 1
    __main__                 : DEBUG   :  2016-07-07 15:23:53,425: Doing something boring with 2
    __main__.sub_noprop      : DEBUG   :  2016-07-07 15:23:53,425: Doing something boring with 2
    __main__.sub_prop        : DEBUG   :  2016-07-07 15:23:53,425: Doing something boring with 2
    __main__                 : INFO    :  2016-07-07 15:23:53,425: Doing something special with 2
    __main__.sub_noprop      : INFO    :  2016-07-07 15:23:53,425: Doing something SPECIAL with 2
    __main__.sub_prop        : INFO    :  2016-07-07 15:23:53,425: Doing something SPECIAL with 2
    __main__                 : INFO    :  2016-07-07 15:23:53,426: ... shutting down.
    '''
