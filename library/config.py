import os
import ConfigParser

class ConfigError(IOError):
    pass

if not os.path.isfile('library.cfg'):
    raise ConfigError("Config file not found!")

config = ConfigParser.ConfigParser()
config.read('library.cfg')
