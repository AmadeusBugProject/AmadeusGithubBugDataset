import io
import re
from pathlib import Path

from githubanalysis.common.ConfigFileParser import Config
from githubanalysis.common.collectionUtils import uniquify
from githubanalysis.common.constants import *
from githubanalysis.common.Logger import Logger

re_logcat_message = r"\bLog.(?:e|d|i|w)\(TAG,\s*\"(.*)\".*,\s*e\);"
re_exception_message = r"throw\s*new\s*\w*Exception\(\"(.*)\".*\);"
rec_logcat_message = re.compile(re_logcat_message)
rec_exception_message = re.compile(re_exception_message)

log = Logger()

class ExceptionMessageCollector:
    def __init__(self, config: Config):
        self.config = config
        self.logcat_exception_messages = self.get_logcat_exception_messages()
        self.thrown_exception_messages = self.get_thrown_exception_messages()

    def get_logcat_exception_messages(self):
        java_files = list(Path(self.config.local_git_repo).rglob('*.java'))
        logcat_message = []
        for file_path in java_files:
            if file_path.is_file():
                try:
                    with io.open(str(file_path), 'r', encoding="utf-8") as file:
                        logcat_message.extend(rec_logcat_message.findall(file.read()))
                except UnicodeDecodeError as e:
                    log.e('unicode error in exception message collection ' + str(e))
        return logcat_message

    def get_thrown_exception_messages(self):
        java_files = list(Path(self.config.local_git_repo).rglob('*.java'))
        logcat_message = []
        for file_path in java_files:
            if file_path.is_file():
                try:
                    with io.open(str(file_path), 'r', encoding="utf-8") as file:
                        logcat_message.extend(rec_exception_message.findall(file.read()))
                except UnicodeDecodeError as e:
                    log.e('unicode error in exception message collection ' + str(e))
        return logcat_message
