# coding=utf-8
import sys
import os
from copy import deepcopy

from .locking_handlers import LockingStreamHandler, LockingFileHandler
from .logging_config_dict import LoggingConfigDict

__author__ = "Brian O'Neill"

class LoggingConfigDictEx(LoggingConfigDict):
    """ \
    A ``LoggingConfigDict`` subclass with a few batteries included — formatters,
    various handler-creators, multiprocessing-aware handlers that output to the console,
    to files and to rotating files.

    .. _builtin-formatters:

    .. index:: Builtin Formatters (LoggingConfigDictEx)

    .. include:: _global.rst

    Formatters provided (their names making it fairly obvious what their format strings are):

    +---------------------------------------+------------------------------------------------------------------------------------+
    || Formatter name                       || Format string                                                                     |
    +=======================================+====================================================================================+
    || ``'minimal'``                        || ``'%(message)s'``                                                                 |
    +---------------------------------------+------------------------------------------------------------------------------------+
    || ``'process_msg'``                    || ``'%(processName)-10s: %(message)s'``                                             |
    +---------------------------------------+------------------------------------------------------------------------------------+
    || ``'logger_process_msg'``             || ``'%(name)-20s: %(processName)-10s: %(message)s'``                                |
    +---------------------------------------+------------------------------------------------------------------------------------+
    || ``'logger_level_msg'``               || ``'%(name)-20s: %(levelname)-8s: %(message)s'``                                   |
    +---------------------------------------+------------------------------------------------------------------------------------+
    || ``'logger_msg'``                     || ``'%(name)-20s: %(message)s'``                                                    |
    +---------------------------------------+------------------------------------------------------------------------------------+
    || ``'process_level_msg'``              || ``'%(processName)-10s: %(levelname)-8s: %(message)s'``                            |
    +---------------------------------------+------------------------------------------------------------------------------------+
    || ``'process_time_level_msg'``         || ``'%(processName)-10s: %(asctime)s: %(levelname)-8s: %(message)s'``               |
    +---------------------------------------+------------------------------------------------------------------------------------+
    || ``'process_logger_level_msg'``       || ``'%(processName)-10s: %(name)-20s: %(levelname)-8s: %(message)s'``               |
    +---------------------------------------+------------------------------------------------------------------------------------+
    || ``'process_time_logger_level_msg'``  || ``'%(processName)-10s: %(asctime)s: %(name)-20s: %(levelname)-8s: %(message)s'``  |
    +---------------------------------------+------------------------------------------------------------------------------------+
    || ``'time_logger_level_msg'``          || ``'%(asctime)s: %(name)-20s: %(levelname)-8s: %(message)s'``                      |
    +---------------------------------------+------------------------------------------------------------------------------------+

    |br|
    """

    format_strs = {
        'minimal':
            '%(message)s',
        'process_msg':
            '%(processName)-10s: %(message)s',
        'logger_process_msg':
            '%(name)-20s: %(processName)-10s: %(message)s',
        'logger_level_msg':
            '%(name)-20s: %(levelname)-8s: %(message)s',
        'logger_msg':
            '%(name)-20s: %(message)s',
        'process_level_msg':
            '%(processName)-10s: %(levelname)-8s: %(message)s',
        'process_time_level_msg':
            '%(processName)-10s: %(asctime)s: %(levelname)-8s: %(message)s',
        'process_logger_level_msg':
            '%(processName)-10s: %(name)-20s: %(levelname)-8s: %(message)s',
        'process_time_logger_level_msg':
            '%(processName)-10s: %(asctime)s: %(name)-20s: %(levelname)-8s: %(message)s',
        'time_logger_level_msg':
            '%(asctime)s: %(name)-20s: %(levelname)-8s: %(message)s',
    }

    def __init__(self,                  # *,
                 root_level='WARNING',       # == logging default level
                 log_path='',
                 locking=False,
                 add_handlers_to_root=False,
                 disable_existing_loggers=False):  # 0.2.2, logging default value is True
        """
        :param root_level: one of 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL', 'NOTSET'
        :param log_path: is a path, absolute or relative, where logfiles will
            be created. ``add_file_handler`` prepends ``log_path`` to its ``filename`` parameter
            and uses that as the value of the ``'filename'`` key. Prepending uses ``os.path.join``.
            The directory specified by ``log_path`` must already exist.
        :param locking: if True, console handlers use locking stream handlers,
            and file handlers created by ``add_file_handler`` and ``add_rotating_file_handler``
            use locking file handlers, UNLESS ``locking=False`` is passed to the calls that
            create those handlers.
        :param disable_existing_loggers: corresponds to logging dict-config key(/value).
                    Changed default val to False so that separate packages can use
                    this class to create their own ("private") loggers before or after
                    their clients do their own logging config.
        """
        super(LoggingConfigDictEx, self).__init__(
                        root_level=root_level,
                        disable_existing_loggers=disable_existing_loggers)
        self.log_path = log_path
        self.locking = locking
        self.add_handlers_to_root = add_handlers_to_root

        # Include some batteries (Formatters) --
        # The default is class_='logging.Formatter'
        for formatter_name in self.format_strs:
            self.add_formatter(formatter_name,
                               format=self.format_strs[formatter_name])

    def clone_handler(self,     # *,
                      clone,
                      handler,
                      add_to_root=None):
        """
        :param clone:
        :param handler:
        :param add_to_root:
        :return: ``self``
        """
        add_to_root = (self.add_handlers_to_root
                       if add_to_root is None else
                       bool(add_to_root))
        clone_dict = deepcopy(self.handlers[handler])
        # Change any 'class' key back into 'class_'
        assert 'class_' not in clone_dict
        if 'class' in clone_dict:
            clone_dict['class_'] = clone_dict.pop('class')
        # Now defer:
        self.add_handler(clone,
                         add_to_root=add_to_root,
                         ** clone_dict)
        return self

    def add_handler(self, handler_name, # *,
                    add_to_root=None,
                    ** handler_dict):
        """Virtual, adds ``add_to_root`` parameter.
        :param handler_name:
        :param add_to_root:
        :param handler_dict:
        :return: ``self``
        """
        super(LoggingConfigDictEx, self).add_handler(handler_name, ** handler_dict)
        add_to_root = (self.add_handlers_to_root
                       if add_to_root is None else
                       bool(add_to_root))
        if add_to_root:
            super(LoggingConfigDictEx, self).add_root_handlers(handler_name)
        return self

    def _add_console_handler(self, handler_name,    # *,
                             stream,
                             formatter=None,    # 'logger_level_msg' or 'process_logger_level_msg'
                             level='WARNING',   # logging module default: 'NOTSET'
                             locking=None,      # 0.2.5 was True
                             add_to_root=None,
                             **kwargs):
        """
        :param handler_name:
        :param stream:
        :param formatter:
        :param level:
        :param locking: so caller can add a non-locking handler even if self.locking,
                but doesn't have to specify `locking=xxx` twice. Likewise,
                a caller can add a locking handler even if self.locking == False.
        :param add_to_root:
        :param kwargs:
        :return: ``self``
        """
        # So: self can be created with (self.)locking=False,
        # but a handler can be locking.
        locking = self.locking if locking is None else bool(locking)
        add_to_root = (self.add_handlers_to_root
                       if add_to_root is None else
                       bool(add_to_root))

        if formatter is None:
            formatter = ('process_logger_level_msg'
                         if locking else
                         'logger_level_msg')
        con_dict = dict(level=level, formatter=formatter, ** kwargs)
        if locking:
            con_dict['()'] = 'ext://lcd.LockingStreamHandler'
            con_dict['create_lock'] = True
        else:
            con_dict['class_'] = 'logging.StreamHandler'

        self.add_handler(handler_name,
                         stream=stream,
                         add_to_root=add_to_root,
                         ** con_dict)
        return self

    def add_stdout_console_handler(self, handler_name,  # *,
                             formatter=None,    # 'logger_level_msg' or 'process_logger_level_msg'
                             level='WARNING',
                             locking=None,
                             add_to_root=None,
                             **kwargs):
        """
        :param handler_name:
        :param formatter:
        :param level:
        :param locking:
        :param add_to_root:
        :param kwargs:
        :return: ``self``
        """
        self._add_console_handler(handler_name,
                                  stream='ext://sys.stdout',
                                  formatter=formatter,
                                  level=level,
                                  locking=locking,
                                  add_to_root=add_to_root,
                                  **kwargs)
        return self

    def add_stderr_console_handler(self, handler_name,  # *,
                             formatter=None,    # 'logger_level_msg' or 'process_logger_level_msg'
                             level='WARNING',
                             locking=None,
                             add_to_root=None,
                             **kwargs):
        """
        :param handler_name:
        :param formatter:
        :param level:
        :param locking:
        :param add_to_root:
        :param kwargs:
        :return: ``self``
        """
        self._add_console_handler(handler_name,
                                  stream='ext://sys.stderr',
                                  formatter=formatter,
                                  level=level,
                                  locking=locking,
                                  add_to_root=add_to_root,
                                  **kwargs)
        return self

    def add_file_handler(self, handler_name,    # *,
                         filename,
                         formatter=None,
                         mode='w',
                         level='NOTSET',    # log everything: logging module default
                         delay=False,       # logging module default
                         locking=None,
                         add_to_root=None,
                         **kwargs):
        """
        :param handler_name:
        :param filename:
        :param formatter:
        :param mode:
        :param level:
        :param delay: True ==> log file not created until written to
        :param locking:
        :param add_to_root:
        :param kwargs:
        :return: ``self``
        """
        # So: self can be created with (self.)locking=False,
        # but a handler can be locking.
        locking = self.locking if locking is None else bool(locking)
        add_to_root = (self.add_handlers_to_root
                       if add_to_root is None else
                       bool(add_to_root))

        if not formatter:
            formatter = ('process_time_logger_level_msg'
                         if locking else
                         'time_logger_level_msg')
        self.add_handler(handler_name,
                         class_='logging.FileHandler',
                         filename=os.path.join(self.log_path, filename),
                         mode=mode,
                         level=level,
                         formatter=formatter,
                         delay=delay,
                         add_to_root=add_to_root,
                         **kwargs)
        if locking:
            del self.handlers[handler_name]['class']
            self.handlers[handler_name]['()'] = 'ext://lcd.LockingFileHandler'
            self.handlers[handler_name]['create_lock'] = True
        return self

    def add_rotating_file_handler(self, handler_name,   # *,
                         filename,
                         max_bytes=0,       # logging.handlers default
                         backup_count=0,    # logging.handlers default
                         formatter=None,
                         mode='a',
                         level='NOTSET',
                         delay=False,       # logging module default
                         locking=None,
                         add_to_root=None,
                         **kwargs):
        """
        :param handler_name:
        :param filename:
        :param max_bytes: logfile size threshold. Given logfile name `lf.log`,
                          if a write would cause `lf.log` to exceed this size,
                          the following occurs, where K = backup_count:
                          if `lf.log.K` exists it is deleted;
                          all files `lf.log.1`, `lf.log.2`, ... `lf.log.K-1`
                          are renamed to `lf.log.2`, `lf.log.3`, ... `lf.log.K`;
                          `lf.log` is closed, and renamed to `lf.log.1`;
                          a new `lf.log` is created and written to.
                          The logging module calls this parameter `maxBytes`;
                          it also defaults to 0.
        :param backup_count: (max) n)umber of backup files to create and maintain.
                          The logging module calls this parameter `backupCount`;
                          it also defaults to 0.
        :param formatter:
        :param mode: NOTE -- mode is `append`, logging module default
        :param level:
        :param delay: True ==> log file not created until written to
        :param locking: Mandatory if multiprocessing -- things won't even work,
                          logfile can't be found: FileNotFoundError: [Errno 2]...
        :param add_to_root:
        :param kwargs:
        :return: ``self``
        """
        # So: self can be created with (self.)locking=False,
        # but a handler can be locking.
        locking = self.locking if locking is None else bool(locking)
        add_to_root = (self.add_handlers_to_root
                       if add_to_root is None else
                       bool(add_to_root))

        if not formatter:
            formatter = ('process_time_logger_level_msg'
                         if locking else
                         'time_logger_level_msg')
        self.add_handler(handler_name,
                         class_='logging.handlers.RotatingFileHandler',
                         filename=os.path.join(self.log_path, filename),
                         mode=mode,
                         level=level,
                         formatter=formatter,
                         delay=delay,
                         add_to_root=add_to_root,
                         maxBytes=max_bytes,
                         backupCount=backup_count,
                         **kwargs)
        if locking:
            del self.handlers[handler_name]['class']
            self.handlers[handler_name]['()'] = 'ext://lcd.LockingRotatingFileHandler'
            self.handlers[handler_name]['create_lock'] = True
        return self

    # TODO  Support for  ColorizedStreamHandler?
