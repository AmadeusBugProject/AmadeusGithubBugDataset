import csv
import io
import json
import os

from githubanalysis.common.collectionUtils import get_value_robust
from githubanalysis.common.constants import *
from githubanalysis.common.Logger import Logger

log = Logger()


class DumpParser:
    def __init__(self, config, dump_file_name=DUMP_FILE_NAME):
        self.config = config
        self.dump = ""
        with io.open(config.storage_path + dump_file_name, 'r', encoding="utf-8") as file:
            self.dump = json.loads(file.read())

    def get_all_issues(self):
        return get_value_robust(self.dump, DUMP_KEY_ISSUES, [])

    def get_issue_by_url(self, url):
        url = url.replace('https://github.com/', 'https://api.github.com/repos/').replace('https://www.github.com/', 'https://api.github.com/repos/')
        for issue in self.dump[DUMP_KEY_ISSUES]:
            issue_url = issue[DUMP_KEY_ISSUE_URL].replace('https://github.com/', 'https://api.github.com/repos/').replace('https://www.github.com/', 'https://api.github.com/repos/')
            if issue_url == url:
                return issue
        return {}

    def get_web_link_list(self):
        links = []
        for issue in self.dump[DUMP_KEY_ISSUES]:
            link = self.get_web_link(issue)
            commit_available = "N" if not issue[DUMP_KEY_ISSUE_COMMITS] else "Y"
            links.append(link + "," + commit_available)
        return links

    def get_web_link(self, issue):
        if DUMP_KEY_ISSUE_URL in issue.keys():
            return issue[DUMP_KEY_ISSUE_URL].replace(API_LINK_BASE_URL, WEB_LINK_BASE_URL).replace("/repos/", "/")
        else:
            return ""

    def save_dump_to(self, file_name):
        os.makedirs(self.config.storage_path, exist_ok=True)
        with io.open(self.config.storage_path + file_name, 'w', encoding="utf-8") as file:
            file.write(json.dumps(self.dump))

    fieldnames = [MANUAL_CLASSIFICATION_KEY_URL,
                  MANUAL_CLASSIFICATION_CONFIDENCE,
                  MANUAL_CLASSIFICATION_REMARKS,
                  MANUAL_CLASSIFICATION_MODE,
                  MANUAL_CLASSIFICATION_ROOT_CAUSE_DETAIL,
                  MANUAL_CLASSIFICATION_ROOT_CAUSE,
                  MANUAL_CLASSIFICATION_IMPACT,
                  MANUAL_CLASSIFICATION_COMPONENT,
                  MANUAL_CLASSIFICATION_INFO,
                  MANUAL_CLASSIFICATION_USE_COMMITS,
                  ISSUE_DISTILLED_NUM_COMMITS,
                  ISSUE_DISTILLED_KEYWORD_ISSUE_MESSAGE,
                  ISSUE_DISTILLED_KEYWORD_COMMIT_MESSAGE,
                  ISSUE_DISTILLED_CONTAINS_KNOWN_LOGCAT_ERROR_MESSAGE,
                  ISSUE_DISTILLED_CONTAINS_KNOWN_EXCEPTION_MESSAGE,
                  ISSUE_DISTILLED_ALL_MENTIONED_EXCEPTIONS]

    def write_csv_for_manual_classification(self):
        os.makedirs(self.config.storage_path, exist_ok=True)
        with io.open(self.config.storage_path + ISSUE_DISTILLED_FILENAME, 'w', encoding="utf-8",
                     newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=self.fieldnames)
            writer.writeheader()
            for i, issue in enumerate(self.get_all_issues()):
                try:
                    writer.writerow(self.__issue_to_csv(issue))
                except KeyError:
                    log.e("key error issue no " + str(i) + " , skipping")

    def __issue_to_csv(self, issue):
        stats = {MANUAL_CLASSIFICATION_KEY_URL: issue[DUMP_KEY_ISSUE_URL]}
        stats.update({ISSUE_DISTILLED_NUM_COMMITS: issue[DUMP_KEY_ISSUE_COMMITS].__len__()})
        stats.update({ISSUE_DISTILLED_ALL_MENTIONED_EXCEPTIONS: issue[DUMP_KEY_ISSUE_MENTIONED_EXCEPTIONS]})
        return stats

    def get_issue_id(self, issue):
        if DUMP_KEY_ISSUE_URL in issue.keys():
            spl = issue[DUMP_KEY_ISSUE_URL].split("/")
            return spl[-1]
        else:
            return ""
