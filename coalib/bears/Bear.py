import traceback

from coalib.misc.i18n import _
from coalib.output.printers.LOG_LEVEL import LOG_LEVEL
from coalib.processes.communication.LogMessage import LogMessage
from coalib.settings.FunctionMetadata import FunctionMetadata
from coalib.settings.Section import Section


class Bear:
    """
    A bear contains the actual subroutine that is responsible for checking source code for certain specifications.
    However it can actually do whatever it wants with the files it gets. If you are missing some Result type, feel free
    to contact us and/or help us extending the coalib.

    This is the base class for every bear. If you want to write an bear, you will probably want to look at the
    GlobalBear and LocalBear classes that inherit from this class. In any case you'll want to overwrite at least the
    run_bear method. You can send debug/warning/error messages through the debug_msg(), warn_msg(), fail_msg()
    functions. These will send the appropriate messages so that they are outputted. Be aware that if you use fail_msg(),
    you are expected to also terminate the bear run-through immediately.

    If you need some setup or teardown for your bear, feel free to overwrite the set_up() and tear_down() functions.
    They will be invoked before/after every run_bear invocation.

    Settings are available at all times through self.section. You can access coalas translation database with the _()
    from coalib.misc.i18n. Be aware that the strings you use are probably not in the database, especially if your bear
    is not shipped with coala. Feel free to use your own translation database in this case or consider make your bear
    available to the coala project.
    """

    def __init__(self,
                 section,
                 message_queue,
                 TIMEOUT=0):
        if not isinstance(section, Section):
            raise TypeError("section has to be of type Section.")
        if not hasattr(message_queue, "put") and message_queue is not None:
            raise TypeError("message_queue has to be a Queue or None.")

        self.section = section
        self.message_queue = message_queue
        self.TIMEOUT = TIMEOUT

    def set_up(self):
        pass

    def tear_down(self):
        pass

    def debug_msg(self, *args, delimiter=' '):
        self.__send_msg(LOG_LEVEL.DEBUG, delimiter, *args)

    def warn_msg(self, *args, delimiter=' '):
        self.__send_msg(LOG_LEVEL.WARNING, delimiter, *args)

    def fail_msg(self, *args, delimiter=' '):
        self.__send_msg(LOG_LEVEL.ERROR, delimiter, *args)

    def __send_msg(self, log_level, delimiter, *args):
        if self.message_queue is None:
            return

        if len(args) == 0:
            return

        self.message_queue.put(LogMessage(log_level,
                                          str(delimiter).join(args)),
                               timeout=self.TIMEOUT)

    def run_bear(self, *args, dependency_results=None, **kwargs):
        raise NotImplementedError

    def run_bear_from_section(self, args, kwargs):
        kwargs.update(self.get_metadata().create_params_from_section(self.section))

        return self.run_bear(*args,
                             **kwargs)

    def run(self, *args, **kwargs):
        name = self.__class__.__name__
        try:
            self.debug_msg(_("Setting up bear {}...").format(name))
            self.set_up()

            self.debug_msg(_("Running bear {}...").format(name))
            retval = self.run_bear_from_section(args, kwargs)

            self.debug_msg(_("Tearing down bear {}...").format(name))
            self.tear_down()

            return retval
        except:
            self.warn_msg(
                _("Bear {} failed to run").format(name))
            self.debug_msg(_("The bear {bear} raised an exception. If you are "
                             "the writer of this bear, please make sure "
                             "to catch all exceptions. If not and this error "
                             "annoys you, you might want to get in contact "
                             "with the writer of this bear.\n\n"
                             "Traceback information is provided below:\n\n"
                             "{traceback}\n")
                           .format(bear=name,
                                   traceback=traceback.format_exc()))

    @staticmethod
    def kind():
        """
        :return: The kind of the bear
        """
        raise NotImplementedError

    @classmethod
    def get_metadata(cls):
        """
        :return: Metadata for the run_bear function. However parameters like
        self or parameters implicitly used by coala (e.g. filename for local
        bears) are already removed.
        """
        return FunctionMetadata.from_function(
            cls.run_bear,
            omit=["self", "dependency_results"])

    @classmethod
    def missing_dependencies(cls, lst):
        """
        Checks if the given list contains all dependencies.

        :param lst: A list of all already resolved bear classes (not
        instances).
        :return A list of missing dependencies.
        """
        dep_classes = cls.get_dependencies()

        for item in lst:
            if item in dep_classes:
                dep_classes.remove(item)

        return dep_classes

    @staticmethod
    def get_dependencies():
        """
        Retrieves bear classes that are to be executed before this bear gets
        executed. The results of these bears will then be passed to the
        run_bear method as a dict via the dependency_results argument. The dict
        will have the name of the Bear as key and the list of its results as
        results.

        :return A list of bear classes.
        """
        return []

    @classmethod
    def get_non_optional_settings(cls):
        """
        This method has to determine which settings are needed by this bear.
        The user will be prompted for needed settings that are not available
        in the settings file so don't include settings where a default value
        would do.

        :return: a dictionary of needed settings as keys and a tuple of help
        text and annotation as values
        """
        return cls.get_metadata().non_optional_params
