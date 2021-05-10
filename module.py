
from datetime import datetime
from enum import IntEnum
from collections import Mapping


def donothing(parameters):
    return None


class Parameter(object):

    def __init__(self, key, required = True, masked = False):
        self.key = key
        self.required = required
        self.masked = masked


class Status(IntEnum):
    OK = 0,
    Changed = 1,
    Skipped = 8,
    Error = 9


class Error(IntEnum):
    OK = 0,
    MissingArgument = 1,
    BadArgument = 2,
    FailedCondition = 3,
    NotImplemented = 9,
    MissingDirectory = 20,
    MissingFile = 21,
    MissingExecutable = 22,
    MissingProfileDirectory = 24,
    NoValidDirectory = 25,
    DuplicateDirectory = 31,
    DuplicateFile = 32,
    FailedCopyFile = 71,
    FailedMakeDirectory = 72
    FailedDownloadFile = 73,
    

class Result(object):

    def __init__(self, status, returncode, start, end, cmd = None, message = None, payload = {}):
        self.status = status
        self.returncode = returncode
        self.start = start
        self.end = end
        self.delta = end - start

        self.cmd = cmd
        self.message = message
        self.payload = payload


class Module(object):

    def __init__(self, name, key, function = donothing, parameters = []):
        self.name = name
        self.key = key
        self.function = function
        self.parameters = parameters


    def getname(self):
        return self.name


    def getkey(self):
        return self.key


    def execute(self, arguments):
        self.starttime = datetime.now()
        result = self.checkarguments(arguments)
        arguments = self.parsearguments(arguments)

        if result is None:
#            self.printparameters(arguments)
            return self.function(arguments)
        else:
            return result


    def parsearguments(self, arguments):
        if len(self.parameters) == 1 and arguments is not None and not isinstance(arguments, Mapping):
            return {self.parameters[0]: arguments}
        else:
            return arguments


    def checkarguments(self, arguments):
        if len(self.parameters) > 1:
            for parameter in self.parameters:
                if parameter.key not in arguments and parameter.required:
                    return self.handleerror(Error.MissingArgument, f"The required parameter {parameter.key} is not present, but it is required for the '{self.name}' module.")
        elif len(self.parameters) == 1 and self.parameters[0].required:
            if arguments is None:
                return self.handleerror(Error.MissingArgument, f"The single required parameter is not present, but it is required for the '{self.name}' module.")

        return None


    def handleerror(self, returncode, message, payload = {}):
        self.printmessage(message)
        return Result(Status.Error, returncode, self.starttime, datetime.now(), message, payload)


    def buildresult(self, status, returncode = 0, cmd = None, message = None, payload = {}):
        return Result(status, returncode, self.starttime, datetime.now(), cmd, message, payload)


    def printparameters(self, arguments):
        if arguments is not None and isinstance(arguments, Mapping):
            for key in arguments:
                self.printmessage(f"- {key}: {arguments[key]}")
        elif arguments is not None:
                self.printmessage(f"- {arguments}")


    def printmessage(self, message):
        print(f"     {message}")


    def printdivider(self):
        print(f"----------------------------------------------------------------------")
    

