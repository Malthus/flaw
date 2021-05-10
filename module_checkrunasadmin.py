
from flaw_library import checkadministratorrole
from module import Parameter, Status, Error, Module


class CheckRunAsAdmin(Module):

    def __init__(self):
        super().__init__(
            name = "Check run as admin", 
            key = "checkadmin",
            function = self.checkrunasadmin,
            parameters = [
                Parameter('admin', required = False)
            ])


    def checkrunasadmin(self, arguments):
        runasadmin = arguments.get('admin', True)
    
        if checkadministratorrole() == runasadmin:
            return self.buildresult(Status.OK)
        else:
            return self.handleerror(Error.FailedCondition, f"Failed the expectation to {'DO' if runasadmin else 'NOT'} run as admin.")

