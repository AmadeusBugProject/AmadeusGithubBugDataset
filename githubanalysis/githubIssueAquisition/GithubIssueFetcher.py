import io
import json
import os
import time

from github import Github  # pygithub
from github import RateLimitExceededException
from githubanalysis.common.constants import *


def rate_limit_handler(function):
    def wrapper(*args, **kwargs):
        while True:
            try:
                return function(*args, **kwargs)
            except RateLimitExceededException:
                print("RateLimitExceeded - waiting")
                print("Currently at: " + function.__name__)
                print("Current time: " + time.ctime())
                time.sleep(4000)
    return wrapper


class GithubIssueFetcher:

    def __init__(self, config):
        self.config = config
        self.already_handeled_issues = []
        if config.github_api_key:
            self.github = Github(config.github_api_key)
        else:
            self.github = Github()
        self.project = self.__get_github_project()
        self.bug_labels = self.__get_matching_bug_labels()
        self.dump = {DUMP_KEY_PROJECT_NAME: self.config.project_name,
                     DUMP_KEY_BUG_LABELS: self.__get_bug_labels_as_strings(self.bug_labels),
                     DUMP_KEY_CAPTURE_TIME: time.ctime(),
                     DUMP_KEY_ISSUES: []}

    def save_dump(self):
        os.makedirs(self.config.storage_path, exist_ok=True)
        with io.open(self.config.storage_path + DUMP_FILE_NAME, 'w', encoding="utf-8") as file:
            file.write(json.dumps(self.dump))

    @rate_limit_handler
    def __get_matching_bug_labels(self):
        bug_labels = []
        for label in self.project.get_labels():
            label_name = label.name.lower()
            for defect_label in self.config.defect_key_words:
                if defect_label in label_name:
                    bug_labels.append(label)
        return bug_labels

    @rate_limit_handler
    def __get_github_project(self):
        return self.github.get_repo(self.config.project_name)

    def __get_bug_labels_as_strings(self, labels):
        bug_labels_array = []
        for label in labels:
            bug_labels_array.append(label.name)
        return bug_labels_array

    def fetch_all(self):
        for label in self.bug_labels:
            issues = self.__get_issues_list([label])
            issues_count = issues.totalCount
            print('Issues for label=' + label.name + ' total: ' + str(issues_count))

            for issueIndex in range(0, issues_count):
                issue_url = self.__get_issue_html_url(issues[issueIndex])
                if '/issues/' in issue_url and not self.__get_issue_numer(issues[issueIndex]) in self.already_handeled_issues:
                    issue_dict = self.__issue_to_dict(issues[issueIndex])
                    self.dump[DUMP_KEY_ISSUES].append(issue_dict)

                    print(issue_url + " , nr. " + str(issueIndex) + " done! " + str(
                        issues_count - issueIndex - 1) + " issues to go...")
                else:
                    print(issue_url + " , nr. " + str(issueIndex) + " skipped! " + str(
                        issues_count - issueIndex - 1) + " issues to go...")

    @rate_limit_handler
    def __get_issue_html_url(self, issue):
        return issue.html_url

    @rate_limit_handler
    def __get_issue_numer(self, issue):
        return issue.number

    def fetch_issues_from_list(self, issues_ids: []):
        for i, issue_id in enumerate(issues_ids):
            issue = self.__get_issue(issue_id)
            if issue:
                issue_dict = self.__issue_to_dict(issue)
                self.dump[DUMP_KEY_ISSUES].append(issue_dict)

                print("issue id: " + str(issue_id) + " , nr. " + str(i) + " done! " + str(
                    issues_ids.__len__() - i - 1) + " issues to go...")
            else:
                print("issue id: " + str(issue_id) + " , nr. " + str(i) + " skipped! " + str(
                    issues_ids.__len__() - i - 1) + " issues to go...")

    @rate_limit_handler
    def __get_issue(self, issue_id):
        return self.project.get_issue(issue_id)

    @rate_limit_handler
    def __get_issues_list(self, label):
        return self.project.get_issues(state="closed", labels=label)

    @rate_limit_handler
    def __issue_to_dict(self, issue):
        issue_dict = {DUMP_KEY_ISSUE_TITLE: issue.title,
                      DUMP_KEY_ISSUE_BODY: issue.body,
                      DUMP_KEY_ISSUE_URL: issue.html_url,
                      DUMP_KEY_ISSUE_USER: issue.user.login,
                      DUMP_KEY_ISSUE_LABELS: self.__get_bug_labels_as_strings(issue.labels),
                      DUMP_KEY_ISSUE_CREATE_TIME: str(issue.created_at),
                      DUMP_KEY_ISSUE_CLOSE_TIME: str(issue.closed_at),
                      DUMP_KEY_ISSUE_COMMITS: self.__find_commit_in_issue(issue)}
        return issue_dict

    @rate_limit_handler
    def __find_commit_in_issue(self, issue):
        commits = {}
        for event in issue.get_events():
            if event.commit_id and event.event and event.actor \
                    and ('referenced' in event.event.lower() or 'closed' in event.event.lower() or 'merged' in event.event.lower()) \
                    and issue.repository.url + "/commits/" in event.commit_url:  # to remove commits pointing to forked repos, eg. https://github.com/skylot/jadx/issues/830
                commits.update({event.commit_id: {DUMP_KEY_ISSUE_COMMIT_DETAILS_GH_EVENT_TYPE: event.event.lower(),
                                                  DUMP_KEY_ISSUE_COMMIT_DETAILS_GH_USER: event.actor.login}})
        return commits
