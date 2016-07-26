__author__ = 'brianoneill'

from .logging_config_dict_ex import LoggingConfigDictEx


class ConfiguratorABC():
    """
    A class for automatic multi-package / multi-module logging configuration.
    Every package/module that wants a say in the configuration of logging
    should define its own (sub*)subclass of ConfiguratorABC, which overrides
    the method

    .. code::

        @classmethod
        def add_to_lcd(lcd: LoggingConfigDict):
            pass

    Once and once only, the application should call ``configure_logging()``,
    a classmethod which

        * creates a "blank" ``LoggingConfigDict``, ``lcdx``, and then
        * calls ``subcls.add_to_lcd(lcdx)`` on every subclass ``subcls``
          that implements ``add_to_lcd``, in a breadth-first way.

    For example, given the following inheritance tree (where "<" means
    "is a superclass of"):

    .. code::

        ConfiguratorABC < MainConfigurator < ConfiguratorModuleA
                                           < ConfiguratorModuleB
                                           < ConfiguratorPackage < ConfiguratorSubPackage

    Assuming that all classes shown implement ``add_to_lcd``, that method
    will be called first on ``MainConfigurator``; then on
    ``ConfiguratorModuleA``, ``ConfiguratorModuleB``, and
    ``ConfiguratorPackage``, in some order; then on ``ConfiguratorSubPackage``.

    See the test ``test_configurator.py`` for a multi-module example
    of this facility.
    """

    @classmethod
    def add_to_lcd(cls, lcdx):          # pragma: no cover
        """(Virtual callout) Customize the passed ``LoggingConfigDictEx``.

        :param lcdx: a ``LoggingConfigDictEx``

        ``configure_logging`` calls this method
        on every ``ConfiguratorABC`` subclass that implements it.
        All implementations are passed the same object ``lcdx``.
        Implementations should call ``LoggingConfigDictEx`` methods
        on ``lcdx`` to further augment and customize it.
        """
        pass

    @classmethod
    def configure_logging(cls,
                   root_level='WARNING',
                   log_path='',
                   locking=False,
                   attach_handlers_to_root=False,
                   disable_existing_loggers=False):
        """A single method which creates a ``LoggingConfigDictEx``,
        calls all ``add_to_lcd`` methods with that object, and then
        configures logging using that object.

        This method creates a ``LoggingConfigDictEx`` ``lcdx``,
        and calls ``subcls.add_to_lcd(lcdx)`` on all subclasses ``subcls``
        of ``ConfiguratorABC`` *which implement the method*, in breadth-first
        order, passing the same ``LoggingConfigDictEx`` instance to each.

        After calling all the ``add_to_lcd`` implementations,
        this method calls ``lcdx.config()`` to configure logging.

        Parameters are as for ``LoggingConfigDictEx``.
        """
        lcdx = LoggingConfigDictEx(
                    root_level=root_level,
                    log_path=log_path,
                    locking=locking,
                    attach_handlers_to_root=attach_handlers_to_root,
                    disable_existing_loggers=disable_existing_loggers
        )
        derived_classes = ConfiguratorABC.__subclasses__()

        while derived_classes:
            subcls = derived_classes.pop()
            if 'add_to_lcd' in vars(subcls):    # i.e. in subcls.__dict__
                subcls.add_to_lcd(lcdx)
            derived_classes.extend(subcls.__subclasses__())

        lcdx.config()
