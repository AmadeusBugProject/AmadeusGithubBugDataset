import git  # pip3 install gitphyton

from githubanalysis.common.ConfigFileParser import Config
from githubanalysis.common.constants import *

# breakpoint import pdb; pdb.set_trace()


class GitRepo:
    def __init__(self, repo_path):
        self.repo = git.Repo(repo_path)

    def get_changed_files_via_stats(self, commit_hash):
        file_paths = []
        try:
            commit = self.repo.commit(commit_hash)
            file_paths.extend(commit.stats.files.keys())
            return file_paths
        except ValueError:
            return file_paths

    def get_commit_message(self, commit_hash):
        try:
            commit = self.repo.commit(commit_hash)
            return commit.message
        except ValueError:
            return ""

    def get_committed_date_time(self, commit_hash):
        try:
            commit = self.repo.commit(commit_hash)
            return commit.committed_datetime.strftime(DATE_TIME_STR_FORMAT)
        except ValueError:
            return ""

    def get_authored_date_time(self, commit_hash):
        try:
            commit = self.repo.commit(commit_hash)
            return commit.authored_datetime.strftime(DATE_TIME_STR_FORMAT)
        except ValueError:
            return ""

    def get_commit_name_rev(self, commit_hash):
        try:
            commit = self.repo.commit(commit_hash)
            return commit.name_rev
        except ValueError:
            return ""

    def get_commit_parents(self, commit_hash):
        try:
            commit = self.repo.commit(commit_hash)
            return list(map(lambda x: x.hexsha, commit.parents))
        except ValueError:
            return []

    def get_detailed_commit_stats(self, commit_hash):
        try:
            commit = self.repo.commit(commit_hash)
        except ValueError:
            return []
        file_stats = []
        commit_stats = commit.stats.files
        for file_name in commit_stats.keys():
            single_file = {"filePath": file_name}
            single_file.update(commit_stats[file_name])
            file_stats.append(single_file)
        return file_stats

    def is_commit_available(self, commit_hash):
        try:
            commit = self.repo.commit(commit_hash)
            return True
        except ValueError:
            return False