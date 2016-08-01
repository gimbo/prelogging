#!/usr/bin/env python

__author__ = 'brianoneill'

import logging

try:
    import lcd
except ImportError:
    import sys
    sys.path[0:0] = ['..']          # , '../..'
from lcd import LoggingConfigDictEx

from ._smtp_credentials import *

# for testing/trying the example
TEST_TO_ADDRESS = FROM_ADDRESS

def main():
    # root, console handler levels: WARNING.
    lcdx = LoggingConfigDictEx(attach_handlers_to_root=True)
    lcdx.add_stderr_handler('con-err',
                                    formatter='minimal'
    ).add_email_handler('email-handler',
        level='ERROR',
        formatter='time_logger_level_msg',
        # SMTPHandler-specific kwargs:
        mailhost='smtp.gmail.com',
        fromaddr=FROM_ADDRESS,
        toaddrs=[TEST_TO_ADDRESS, 'admin@kludge.ly'], # string or list of strings
        subject='Alert from SMTPHandler',
        username=SMTP_USERNAME,
        password=SMTP_PASSWORD
    )

    lcdx.config()

    root = logging.getLogger()
    root.debug("1.")        # not logged (loglevel too low)
    root.info("2.")         # ditto
    root.warning("3.")      # logged to console
    root.error("4.")        # logged to console, emailed
    root.critical("5.")     # ditto


if __name__ == '__main__':
    main()

