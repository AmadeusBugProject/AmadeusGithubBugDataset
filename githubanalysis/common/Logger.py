import time

class Logger:
    VERBOSE = 0
    DEBUG = 1
    WARN = 2
    ERROR = 3
    STATUS = 4
    OFF = 5

    def __init__(self, level=2, log_file=None):
        self.level = level
        self.log_file = log_file

    def __out(self, message, level):
        if level >= self.level:
            print(time.ctime() + " " + message)
        if self.log_file:
            with open(self.log_file, "a") as fd:
                fd.write(time.ctime() + " " + message + "\n")

    def v(self, message):
        self.__out(message, Logger.VERBOSE)

    def d(self, message):
        self.__out(message, Logger.DEBUG)

    def w(self, message):
        self.__out(message, Logger.WARN)

    def e(self, message):
        self.__out(message, Logger.ERROR)

    def s(self, message):
        self.__out(message, Logger.STATUS)
