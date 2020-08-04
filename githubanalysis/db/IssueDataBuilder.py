import datetime

import githubanalysis.gitRepoAnalysis.GitRepo as GitRepo
from githubanalysis.codeAnalysis.JavaAwareDiffDistiller import JavaAwareDiffDistiller
from githubanalysis.common.ConfigFileParser import Config
from githubanalysis.common.Logger import Logger
from githubanalysis.common.constants import *
from githubanalysis.gitRepoAnalysis.ExceptionMessageCollector import ExceptionMessageCollector

log = Logger()


class IssueDataBuilder:
    def __init__(self, config: Config):
        self.config = config
        self.repo = GitRepo.GitRepo(config.local_git_repo)
        self.emc = ExceptionMessageCollector(config)
        self.differ = JavaAwareDiffDistiller(config)

    def build_time_to_fix(self, issue):
        try:
            created = datetime.datetime.strptime(issue[DUMP_KEY_ISSUE_CREATE_TIME], DATE_TIME_STR_FORMAT)
            closed = datetime.datetime.strptime(issue[DUMP_KEY_ISSUE_CLOSE_TIME], DATE_TIME_STR_FORMAT)
            time_diff = closed - created
            days = time_diff.days + time_diff.seconds / (3600 * time_diff.seconds)
        except (ValueError, ZeroDivisionError):
            days = None
        issue.update({DUMP_KEY_ISSUE_TTF: days})

    def build_detailed_commit_info(self, issue):
        commits_details = []
        for commit_hash, commit_info in issue[DUMP_KEY_ISSUE_COMMITS].items():
            if self.repo.is_commit_available(commit_hash):
                commits_details.append((commit_hash, commit_info))

        if len(commits_details) > MAX_COMMITS:
            issue.update({DUMP_KEY_ISSUE_COMMIT_DETAILS: []})
            issue.update({DUMP_KEY_ISSUE_STATS_SKIPPED_REASON: DUMP_KEY_ISSUE_STATS_SKIPPED_REASON_TOO_MANY_COMMITS})
            return

        commit_infos = []
        for commit_hash, commit_info in issue[DUMP_KEY_ISSUE_COMMITS].items():
            git_detailed_stats = self.repo.get_detailed_commit_stats(commit_hash)

            skipped_reason = self.is_big_change(git_detailed_stats)
            if skipped_reason:
                spoon_detailed_stats = []
                log.s(commit_hash + ' ' + skipped_reason)
            else:
                spoon_detailed_stats = self.get_spoon_ast_diff_stats(commit_hash)

            commit_info = {DUMP_KEY_ISSUE_COMMIT_DETAILS_HASH: commit_hash,
                                 DUMP_KEY_ISSUE_COMMIT_DETAILS_GH_EVENT_TYPE: commit_info[DUMP_KEY_ISSUE_COMMIT_DETAILS_GH_EVENT_TYPE],
                                 DUMP_KEY_ISSUE_COMMIT_DETAILS_GH_USER: commit_info[DUMP_KEY_ISSUE_COMMIT_DETAILS_GH_USER],
                                 DUMP_KEY_ISSUE_COMMIT_DETAILS_PARENTS: self.repo.get_commit_parents(commit_hash),
                                 DUMP_KEY_ISSUE_COMMIT_DETAILS_NAME_REV: self.repo.get_commit_name_rev(commit_hash),
                                 DUMP_KEY_ISSUE_COMMIT_DETAILS_MESSAGE: self.repo.get_commit_message(commit_hash),
                                 DUMP_KEY_ISSUE_COMMIT_DETAILS_COMMITED_DATE_TIME: self.repo.get_committed_date_time(commit_hash),
                                 DUMP_KEY_ISSUE_COMMIT_DETAILS_AUTHORED_DATE_TIME: self.repo.get_authored_date_time(commit_hash),
                                 DUMP_KEY_ISSUE_COMMIT_DETAILS_GIT_STATS: git_detailed_stats,
                                 DUMP_KEY_ISSUE_COMMIT_DETAILS_SPOON_AST_DIFF_STATS: spoon_detailed_stats,
                                 DUMP_KEY_ISSUE_SPOON_STATS_SKIPPED_REASON: skipped_reason}

            commit_infos.append(commit_info)

        issue.update({DUMP_KEY_ISSUE_COMMIT_DETAILS: commit_infos})

    def is_big_change(self, git_detailed_stats):
        java_git_stats = []
        for git_stat in git_detailed_stats:
            if git_stat['filePath'].endswith('.java'):
                java_git_stats.append(git_stat)

        if len(java_git_stats) > MAX_FILES:
            return DUMP_KEY_ISSUE_STATS_SKIPPED_REASON_TOO_MANY_FILES
        for git_stat in java_git_stats:
            if git_stat['lines'] > MAX_LOC:
                return DUMP_KEY_ISSUE_STATS_SKIPPED_REASON_TOO_MANY_CHANGES
        return ''

    def get_spoon_ast_diff_stats(self, commit_hash):
        if commit_hash:
            detailed_diff = self.differ.diff_commit(commit_hash)
            if not detailed_diff:
                return []
            return self.differ.get_stats(detailed_diff)
        else:
            return []

    def build_issue(self, issue):
        # time open
        self.build_time_to_fix(issue)
        self.build_detailed_commit_info(issue)

    def build_all_issues(self, issues):
        for i, issue in enumerate(issues):
            log.s("at issue " + str(i) + " of " + str(issues.__len__()))
            if '/issues/' in issue[DUMP_KEY_ISSUE_URL]:
                log.s("issue " + issue[DUMP_KEY_ISSUE_URL])
                self.build_issue(issue)
            else:
                log.s("pull request skipped " + issue[DUMP_KEY_ISSUE_URL])
