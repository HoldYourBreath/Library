import os
import configparser


class ConfigError(IOError):
    pass


if not os.path.isfile('library.cfg'):
    raise ConfigError("Config file not found!")

config = configparser.ConfigParser()
config.read('library.cfg')
