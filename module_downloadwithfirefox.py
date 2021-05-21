
from os import system
from os.path import exists, isdir, join
from subprocess import run
from time import sleep
from configparser import ConfigParser

from flaw_library import createdirectory
from module import Parameter, Status, Error, Module


class DownloadWithFirefox(Module):

    def __init__(self):
        super().__init__(
            name = "Download file with Firefox", 
            key = "firefox",
            function = self.downloadwithfirefox,
            parameters = [
                Parameter('executable', required = True), 
                Parameter('url', required = True), 
                Parameter('targetdir', required = True), 
                Parameter('filename', required = True),
                Parameter('profiledir', required = True),
                Parameter('overwrite', required = False),
                Parameter('killprocess', required = False),
                Parameter('timeout', required = False)
            ])


    def downloadwithfirefox(self, arguments):
        firefoxexecutable = arguments['executable']
        directory = arguments['targetdir']
        filename = arguments['filename']
        profilebasedirectory = arguments['profiledir']
        url = arguments['url']
        overwrite = arguments.get('overwrite', False)
        killbrowser = arguments.get('killprocess', False)
        timeout = arguments.get('timeout', 30)

        if not exists(firefoxexecutable):
            return self.handleerror(Error.MissingExecutable, f"The Firefox executable {firefoxexecutable} cannot be found.")

        # Add additional checks

        result = self.createflawprofile(firefoxexecutable, profilebasedirectory, directory)
        if result.status == Status.Error:
            return result

        return self.downloadfile(firefoxexecutable, url, timeout, killbrowser)


    def createflawprofile(self, firefoxexecutable, profilebasedirectory, directory):
        profiledirectory = self.findflawprofiledirectory(profilebasedirectory)
        if profiledirectory is None:
            result = run([firefoxexecutable, "-CreateProfile", "flaw"], shell = False, capture_output = False, text = False)
            # Check result?
        
        profiledirectory = self.findflawprofiledirectory(profilebasedirectory)
        if profiledirectory is None:
            return self.handleerror(Error.MissingProfileDirectory, f"The profile directory {profiledirectory} could not be found, so the profile is probably not created.")
    
        downloaddirectory = directory.replace("/", "\\\\")
        lines = [
            "user_pref(\"browser.download.folderList\", 2);\n", 
            "user_pref(\"browser.download.dir\", \"" + downloaddirectory + "\");\n", 
            "user_pref(\"browser.download.useDownloadDir\", true);\n", 
            "user_pref(\"browser.download.viewableInternally.enabledTypes\", \"\");\n", 
            "user_pref(\"browser.helperApps.neverAsk.saveToDisk\", \"application/pdf;text/plain;application/text;text/xml;application/xml;application/octet-stream\");\n", 
            "user_pref(\"pdfjs.disabled\", true);\n"
        ]

        profilehandle = open(join(profiledirectory, "user.js"), "w")
        profilehandle.writelines(lines)
        profilehandle.close()

        return self.buildresult(Status.OK)


    def downloadfile(self, firefoxexecutable, url, timeout, killbrowser):
        result = run([firefoxexecutable, "-P", "flaw", url], shell = False, capture_output = False, text = False)
        # Run with -silent flag?
        sleep(timeout)

        if killbrowser:
            system("taskkill /im firefox.exe /f")
    
        if result.returncode != 0:
            return self.handleerror(result.returncode, f"The command exited with return code {result.returncode}.")
        else:
            return self.buildresult(Status.Changed)


    def findflawprofiledirectory(self, profilebasedirectory):
        profiledirectory = None
        config = ConfigParser()

        config.read(join(profilebasedirectory, "profiles.ini"))
        for section in config.sections():
            if section.startswith("Profile") and config[section]['Name'] == "flaw":
                profiledirectory = join(profilebasedirectory, config[section]['Path'])

        return profiledirectory

