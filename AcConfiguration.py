import ConfigParser, os

class AcConfiguration:

    class __impl:

        config = ''
        settings = {}

        def __init__(self, code_dir = None):

            if not self.config:

                self.init(code_dir)
            
        def init(self, code_dir = None):

            self.config = ConfigParser.ConfigParser()
            
            # Use relative path to this classes current directory
            if code_dir is None:
                code_dir = os.path.dirname(os.path.abspath(__file__))
            self.config.read(["{0}/config/config.cfg".format(code_dir), "{0}/../config.cfg".format(code_dir)])

            for section in self.config.sections():

                self.settings[section] = {}

                for name, value in self.config.items(section):

                    self.settings[section][name] = value

    # storage for the instance reference
    __instance = None

    def __init__(self, code_dir = None):
        """ Create singleton instance """
        # Check whether we already have an instance
        if AcConfiguration.__instance is None:
            # Create and remember instance
            AcConfiguration.__instance = AcConfiguration.__impl(code_dir)

        # Store instance reference as the only member in the handle
        self.__dict__['_AcConfiguration__instance'] = AcConfiguration.__instance

    def __getattr__(self, attr):
        """ Delegate access to implementation """
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        """ Delegate access to implementation """
        return setattr(self.__instance, attr, value)
