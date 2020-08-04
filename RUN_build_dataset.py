import os
import shutil

from common.constants import GIT_REPOS_DIRECTORY, CONFIG_PATHS
from githubanalysis.common.ConfigFileParser import Config
from githubanalysis.common.DumpParser import DumpParser
from githubanalysis.db.IssueCommitStatsCreator import IssueCommitStatsCreator
from githubanalysis.db.IssueDataBuilder import IssueDataBuilder
from githubanalysis.githubIssueAquisition.GithubIssueFetcher import GithubIssueFetcher
from githubanalysis.common.constants import ISSUE_DATA_FILE_NAME, ISSUE_DATA_W_STATS_FILE_NAME
from subprocess import call


def main():
    for config_path in CONFIG_PATHS:
        config = Config(config_path)
        clone_repo(config)
        fetch_issues(config)
        create_commit_stats(config)
        build_commit_stats_summary(config)
        # delete_repo()


def fetch_issues(config):
    fetcher = GithubIssueFetcher(config)
    fetcher.fetch_all()
    fetcher.save_dump()


def create_commit_stats(config):
    dump_parser = DumpParser(config)
    idb = IssueDataBuilder(config)
    idb.build_all_issues(dump_parser.get_all_issues())
    dump_parser.save_dump_to(ISSUE_DATA_FILE_NAME)


def build_commit_stats_summary(config):
    dump_parser = DumpParser(config, ISSUE_DATA_FILE_NAME)
    csc = IssueCommitStatsCreator(config)
    csc.create_stats_for_all_issues(dump_parser.get_all_issues())
    dump_parser.save_dump_to(ISSUE_DATA_W_STATS_FILE_NAME)


def clone_repo(config):
    config.local_git_repo = GIT_REPOS_DIRECTORY + config.github_repo_name
    config.save_to_file('githubanalysis/data/' + config.github_repo_name + '.json')
    os.makedirs(GIT_REPOS_DIRECTORY, exist_ok=True)
    command = "git clone https://github.com/" + config.github_user + '/' + config.github_repo_name + ".git"
    call(command, cwd=str(GIT_REPOS_DIRECTORY), shell=True)


def delete_repo():
    shutil.rmtree(GIT_REPOS_DIRECTORY)


if __name__ == "__main__":
    main()
