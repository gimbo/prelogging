__author__ = 'brianoneill'

import library

import logging

try:
    import logging_config
except ImportError:
    import sys
    sys.path[0:0] = ['..']          # , '../..'
from logging_config import LCDict


def configure_logging():
    d = LCDict(attach_handlers_to_root=True)  # default: disable_existing_loggers=False
    d.add_stdout_handler('stdout', formatter='logger_level_msg', level='DEBUG')
    # NOTE: root level is 'WARNING',
    #  .    'library.module' logger level is 'INFO'.
    #  .    Messages of 'library.module' propagate,
    #  .        and those of levels INFO and up *are logged*.
    d.config()


def main():
    # Exercise:
    # Comment out and uncomment the following two lines, individually
    # (4 cases); observe the console output in each case.
    configure_logging()
    logging.getLogger().warning("I must caution you about that.")

    library.do_something()
    library.do_something_else()

    # Results:
    """
    (1)
            configure_logging()
            logging.getLogger().warning("I must caution you about that.")
      writes to stdout:
            root                : WARNING : I must caution you about that.
            library.module      : INFO    : INFO msg
            Did something.
            library.module.other: WARNING : WARNING msg
            Did something else.
    (2)
            # configure_logging()
            logging.getLogger().warning("I must caution you about that.")

      writes (to stdout)
            Did something.
            Did something else.
      and (to stderr)
          I must caution you about that.
      (possibly between or after the lines written to stdout).

    (3)
            configure_logging()
            # logging.getLogger().warning("I must caution you about that.")
      writes to stdout:
            library.module      : INFO    : INFO msg
            Did something.
            library.module.other: WARNING : WARNING msg
            Did something else.
    (4)
            # configure_logging()
            # logging.getLogger().warning("I must caution you about that.")
      writes to stdout
            Did something.
            Did something else.
    """


if __name__ == '__main__':
    main()