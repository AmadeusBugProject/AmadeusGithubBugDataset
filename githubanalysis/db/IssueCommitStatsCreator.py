import re

import pandas
from packaging import version

from githubanalysis.common.ConfigFileParser import Config
from githubanalysis.common.collectionUtils import uniquify
from githubanalysis.common.constants import *
from githubanalysis.common.Logger import Logger

log = Logger()


class IssueCommitStatsCreator:
    def __init__(self, config: Config):
        self.config = config

    def create_stats_for_all_issues(self, issues):
        for i, issue in enumerate(issues):
            log.s("at issue " + str(i) + " of " + str(issues.__len__()))
            self.create_stats_for_issue(issue)

    def create_stats_for_issue(self, issue):
        if not issue[DUMP_KEY_ISSUE_COMMITS]:
            return
        if DUMP_KEY_ISSUE_COMMIT_DETAILS not in issue.keys():
            return

        # step 1 - filter commits
        total_commits = issue[DUMP_KEY_ISSUE_COMMIT_DETAILS]
        filtered_hashes, filter_summary = self.filter_commits(issue)

        # # step 2 - take manual selected commits into consideration
        # manual_classification = issue[DUMP_KEY_MANUAL_CLASSIFICATION]
        # if manual_classification and manual_classification[MANUAL_CLASSIFICATION_USE_COMMITS]:
        #     filtered_hashes = manual_classification[MANUAL_CLASSIFICATION_USE_COMMITS]
        #     filter_summary = {DUMP_KEY_ISSUE_FILTERED_COMMITS_REASON_DUP: 0,
        #               DUMP_KEY_ISSUE_FILTERED_COMMITS_REASON_ALSO_FIXES_PHRASE: 0,
        #               DUMP_KEY_ISSUE_FILTERED_COMMITS_REASON_MORE_THAN_ONE_PARENT: 0,
        #               DUMP_KEY_ISSUE_FILTERED_COMMITS_REASON_NOT_SINGLE_ISSUE: 0,
        #               DUMP_KEY_ISSUE_FILTERED_COMMITS_REASON_UNAVAILABLE: 0}

        issue.update({DUMP_KEY_ISSUE_FILTERED_COMMITS: filtered_hashes})
        issue.update({DUMP_KEY_ISSUE_FILTERED_COMMITS_REASON: filter_summary})

        # step 3.1 - filter ignored file paths # done in each __get_single_..._commit_stats_df
        # step 3.2 - sum up filtered change stats for every file in spoon and git stats
        # step 4 - sum up filtered change stats for every commit
        issue.update(self.sum_git_issue_stats(issue))
        issue.update(self.sum_spoon_issue_stats(issue))

        # step 5 - create package path information
        issue.update(self.create_package_from_git_information(issue))
        issue.update(self.create_package_from_spoon_information(issue))

    def flatten_spoon_stats(self, issue):
        commits = issue[DUMP_KEY_ISSUE_COMMIT_DETAILS]
        all_spoon_df = pandas.DataFrame()
        for commit in commits:
            commit_spoon_df = pandas.DataFrame()
            for spoon_file in commit[DUMP_KEY_ISSUE_COMMIT_DETAILS_SPOON_AST_DIFF_STATS]:
                spoon_file_name = spoon_file[SPOON_AST_DIFF_FILE]
                spoon_methods_df = pandas.io.json.json_normalize(spoon_file[SPOON_AST_DIFF_METHODS])
                if spoon_methods_df.shape[0] != 0:
                    spoon_methods_df[SPOON_AST_DIFF_FILE] = spoon_file_name
                    commit_spoon_df = commit_spoon_df.append(spoon_methods_df)
            commit_spoon_df[DUMP_KEY_ISSUE_COMMIT_DETAILS_HASH] = commit[DUMP_KEY_ISSUE_COMMIT_DETAILS_HASH]
            commit_spoon_df[DUMP_KEY_ISSUE_SPOON_STATS_SKIPPED_REASON] = commit[DUMP_KEY_ISSUE_SPOON_STATS_SKIPPED_REASON]
            all_spoon_df = all_spoon_df.append(commit_spoon_df)
        return all_spoon_df

    def sum_spoon_issue_stats(self, issue):
        # filter commits
        filtered_commit_hashes = issue[DUMP_KEY_ISSUE_FILTERED_COMMITS]

        git_stats_df = self.flatten_spoon_stats(issue)

        if git_stats_df.shape[0] == 0:
            return {DUMP_KEY_ISSUE_SPOON_STATS_SUMMARY: {}, DUMP_KEY_ISSUE_STATS_SKIPPED_REASON: ''}

        # only look at filtered commits
        git_stats_df = git_stats_df[git_stats_df[DUMP_KEY_ISSUE_COMMIT_DETAILS_HASH].isin(filtered_commit_hashes)]

        # only look at filtered files
        file_filter = list(map(lambda x: x.replace('.', '\.'), self.config.ignore_file_paths))
        git_stats_df = git_stats_df[~git_stats_df[SPOON_AST_DIFF_FILE].str.contains('|'.join(file_filter))]

        # sum change stats
        git_stats_sums = git_stats_df.sum(0, numeric_only=True)
        git_sums_d = git_stats_sums.to_dict()

        # get files, methods and commit count
        git_file_count = git_stats_df[SPOON_AST_DIFF_FILE].value_counts().size
        git_method_count = git_stats_df[SPOON_AST_DIFF_METHOD_NAME].value_counts().size

        git_sums_d.update({SPOON_AST_DIFF_FILES_CHANGED: git_file_count})
        git_sums_d.update({SPOON_AST_DIFF_METHODS_CHANGED: git_method_count})

        stats_skipped_reason = ''
        if SPOON_AST_DIFF_EXCEPTION_DURING_DIFF in git_stats_df[SPOON_AST_DIFF_METHOD_NAME]:
            stats_skipped_reason = SPOON_AST_DIFF_EXCEPTION_DURING_DIFF
            git_sums_d = {}
        if DUMP_KEY_ISSUE_STATS_SKIPPED_REASON_TOO_MANY_CHANGES in git_stats_df[DUMP_KEY_ISSUE_SPOON_STATS_SKIPPED_REASON]:
            stats_skipped_reason = DUMP_KEY_ISSUE_STATS_SKIPPED_REASON_TOO_MANY_CHANGES
            git_sums_d = {}
        if DUMP_KEY_ISSUE_STATS_SKIPPED_REASON_TOO_MANY_FILES in git_stats_df[DUMP_KEY_ISSUE_SPOON_STATS_SKIPPED_REASON]:
            stats_skipped_reason = DUMP_KEY_ISSUE_STATS_SKIPPED_REASON_TOO_MANY_FILES
            git_sums_d = {}

        return {DUMP_KEY_ISSUE_SPOON_STATS_SUMMARY: git_sums_d, DUMP_KEY_ISSUE_STATS_SKIPPED_REASON: stats_skipped_reason}


    def create_package_from_git_information(self, issue):
        # filter commits
        filtered_commit_hashes = issue[DUMP_KEY_ISSUE_FILTERED_COMMITS]

        git_stats_df = self.flatten_git_stats(issue)

        if git_stats_df.shape[0] == 0:
            return {}

        # only look at filtered commits
        git_stats_df = git_stats_df[git_stats_df[DUMP_KEY_ISSUE_COMMIT_DETAILS_HASH].isin(filtered_commit_hashes)]

        # only look ad filtered files
        file_filter = list(map(lambda x: x.replace('.', '\.'), self.config.ignore_file_paths))
        git_stats_df = git_stats_df[~git_stats_df[COMMIT_STATS_KEY_FILE_PATH].str.contains('|'.join(file_filter))]

        file_paths = list(git_stats_df[COMMIT_STATS_KEY_FILE_PATH].value_counts().index)

        packages = []
        for file_path in file_paths:
            path = file_path.split("/")[:self.config.package_depth]
            if ".java" in path[-1] or ".gradle" in path[-1] or ".cc" in path[-1]:
                path.pop()
            packages.append("/".join(path))

        return {DUMP_KEY_ISSUE_CHANGES_IN_PACKAGE_FROM_GIT_INFO: uniquify(packages)}

    def create_package_from_spoon_information(self, issue):
        # filter commits
        filtered_commit_hashes = issue[DUMP_KEY_ISSUE_FILTERED_COMMITS]

        spoon_stats_df = self.flatten_spoon_stats(issue)

        if spoon_stats_df.shape[0] == 0:
            return {}

        # only look at filtered commits
        spoon_stats_df = spoon_stats_df[spoon_stats_df[DUMP_KEY_ISSUE_COMMIT_DETAILS_HASH].isin(filtered_commit_hashes)]

        # only look ad filtered files
        file_filter = list(map(lambda x: x.replace('.', '\.'), self.config.ignore_file_paths))
        spoon_stats_df = spoon_stats_df[~spoon_stats_df[SPOON_AST_DIFF_FILE].str.contains('|'.join(file_filter))]


        method_paths = list(spoon_stats_df[SPOON_AST_DIFF_METHOD_NAME].value_counts().index)

        # for method_path in method_paths:
        #     path = method_path.split(".")[:self.config.package_depth]
        #     packages.append(".".join(path))

        return {DUMP_KEY_ISSUE_CHANGES_IN_PACKAGE_FROM_SPOON_INFO: uniquify(method_paths)}

    def flatten_git_stats(self, issue):
        commits = issue[DUMP_KEY_ISSUE_COMMIT_DETAILS]
        all_git_df = pandas.DataFrame()
        for commit in commits:
            commit_hash = commit[DUMP_KEY_ISSUE_COMMIT_DETAILS_HASH]
            commit_git_df = pandas.io.json.json_normalize(commit[DUMP_KEY_ISSUE_COMMIT_DETAILS_GIT_STATS])
            commit_git_df[DUMP_KEY_ISSUE_COMMIT_DETAILS_HASH] = commit_hash
            all_git_df = all_git_df.append(commit_git_df)
        return all_git_df

    def sum_git_issue_stats(self, issue):
        # filter commits
        filtered_commit_hashes = issue[DUMP_KEY_ISSUE_FILTERED_COMMITS]

        git_stats_df = self.flatten_git_stats(issue)

        if git_stats_df.shape[0] == 0:
            return {}

        # only look at filtered commits
        git_stats_df = git_stats_df[git_stats_df[DUMP_KEY_ISSUE_COMMIT_DETAILS_HASH].isin(filtered_commit_hashes)]

        # only look ad filtered files
        file_filter = list(map(lambda x: x.replace('.', '\.'), self.config.ignore_file_paths))
        git_stats_df = git_stats_df[~git_stats_df[COMMIT_STATS_KEY_FILE_PATH].str.contains('|'.join(file_filter))]

        # sum change stats
        git_stats_sums = git_stats_df.sum(0, numeric_only=True)
        git_sums_d = git_stats_sums.to_dict()

        # get files and commit count
        git_file_count = git_stats_df[COMMIT_STATS_KEY_FILE_PATH].value_counts().size
        git_sums_d.update({COMMIT_STATS_KEY_FILES_CHANGED: git_file_count})

        git_commit_count = git_stats_df[DUMP_KEY_ISSUE_COMMIT_DETAILS_HASH].value_counts().size

        # save to issue
        return {COMMIT_STATS_KEY_NUM_COMMITS: git_commit_count,
                DUMP_KEY_ISSUE_GIT_STATS_SUMMARY: git_sums_d}

    def filter_commits(self, issue):
        commits_details = issue[DUMP_KEY_ISSUE_COMMIT_DETAILS]
        filter_sum = {DUMP_KEY_ISSUE_FILTERED_COMMITS_REASON_DUP: 0,
                      DUMP_KEY_ISSUE_FILTERED_COMMITS_REASON_ALSO_FIXES_PHRASE: 0,
                      DUMP_KEY_ISSUE_FILTERED_COMMITS_REASON_MORE_THAN_ONE_PARENT: 0,
                      DUMP_KEY_ISSUE_FILTERED_COMMITS_REASON_NOT_SINGLE_ISSUE: 0,
                      DUMP_KEY_ISSUE_FILTERED_COMMITS_REASON_UNAVAILABLE: 0,
                      DUMP_KEY_ISSUE_FILTERED_COMMITS_ONLY_USED_MERGE_COMMIT: 0}
        num_commits = commits_details.__len__()

        commits = self.__prefer_pr_merge_commit(commits_details)
        filter_sum[DUMP_KEY_ISSUE_FILTERED_COMMITS_ONLY_USED_MERGE_COMMIT] = num_commits - commits.__len__()
        num_commits = commits.__len__()

        commits = self.__remove_duplicate_commits(commits)
        filter_sum[DUMP_KEY_ISSUE_FILTERED_COMMITS_REASON_DUP] = num_commits - commits.__len__()
        num_commits = commits.__len__()

        commits = self.__remove_commits_containing_more_than_one_issue(commits)
        filter_sum[DUMP_KEY_ISSUE_FILTERED_COMMITS_REASON_NOT_SINGLE_ISSUE] = num_commits - commits.__len__()
        num_commits = commits.__len__()

        commits = self.__remove_commits_containing_also_fix_phrase(commits)
        filter_sum[DUMP_KEY_ISSUE_FILTERED_COMMITS_REASON_ALSO_FIXES_PHRASE] = num_commits - commits.__len__()
        num_commits = commits.__len__()

        commits = self.__remove_commits_with_more_than_one_parent(commits)
        filter_sum[DUMP_KEY_ISSUE_FILTERED_COMMITS_REASON_MORE_THAN_ONE_PARENT] = num_commits - commits.__len__()
        num_commits = commits.__len__()

        commits = self.__remove_unavailable_commits(commits)
        filter_sum[DUMP_KEY_ISSUE_FILTERED_COMMITS_REASON_UNAVAILABLE] = num_commits - commits.__len__()

        return list(map(lambda x: x[DUMP_KEY_ISSUE_COMMIT_DETAILS_HASH], commits)), filter_sum

    def __prefer_pr_merge_commit(self, commits_details_list):
        for commit in commits_details_list:
            try:
                if commit[DUMP_KEY_ISSUE_COMMIT_DETAILS_GH_EVENT_TYPE] == 'merged':
                    return [commit]
            except ValueError:
                pass
        return commits_details_list

    def __remove_duplicate_commits(self, commits_details_list):
        commits_dict = {}
        for commit in commits_details_list:
            try:
                commit_summary = commit[DUMP_KEY_ISSUE_COMMIT_DETAILS_MESSAGE].splitlines()[0]
                # only use commit.summary and not full message to prevent false negatives because of small differences
                # like the autogenerated migration id, eg. https://github.com/google/ExoPlayer/issues/1336
                if commit_summary in list(commits_dict.keys()):
                    commits_dict[commit_summary].append(commit)
                else:
                    commits_dict.update({commit_summary: [commit]})
            except (ValueError, IndexError):
                log.e("commit message empty")

        # select one from duplicates based on newer reference
        filtered_commits = []
        for duplicate_commits in commits_dict.values():
            filtered_commits.append(self.__select_newest_commits(duplicate_commits))

        return filtered_commits

    def __remove_commits_containing_more_than_one_issue(self, commits_details_list):
        re_issue_id = r"#\d+"
        rec_issue_id = re.compile(re_issue_id)
        filtered_commits = []
        for commit in commits_details_list:
            try:
                linked_issues = rec_issue_id.findall(commit[DUMP_KEY_ISSUE_COMMIT_DETAILS_MESSAGE])
                if uniquify(linked_issues).__len__() <= 1:
                    filtered_commits.append(commit)
            except ValueError:
                pass
        return filtered_commits

    def __remove_commits_containing_also_fix_phrase(self, commits_details_list):
        re_also_fix = r"also\s+fix(?:es)?(?:\s+issue)?\s+#\d+"
        rec_also_fix = re.compile(re_also_fix, re.IGNORECASE)
        filtered_commits = []
        for commit in commits_details_list:
            try:
                linked_issues = rec_also_fix.findall(commit[DUMP_KEY_ISSUE_COMMIT_DETAILS_MESSAGE])
                if uniquify(linked_issues).__len__() == 0:
                    filtered_commits.append(commit)
            except ValueError:
                pass
        return filtered_commits

    def __remove_commits_with_more_than_one_parent(self, commits_details_list):
        filtered_commits = []
        for commit in commits_details_list:
            if commit[DUMP_KEY_ISSUE_COMMIT_DETAILS_PARENTS].__len__() == 1:
                filtered_commits.append(commit)
        return filtered_commits

    def __remove_unavailable_commits(self, commits_details_list):
        filtered_commits = []
        for commit in commits_details_list:
            if commit[DUMP_KEY_ISSUE_COMMIT_DETAILS_COMMITED_DATE_TIME] != "":
                filtered_commits.append(commit)
        return filtered_commits

    def __select_newest_commits(self, duplicate_commits):
        selected_commit = duplicate_commits[0]
        for commit in duplicate_commits:
            if "tags/r" in commit[DUMP_KEY_ISSUE_COMMIT_DETAILS_NAME_REV]:
                if "tags/r" not in selected_commit[DUMP_KEY_ISSUE_COMMIT_DETAILS_NAME_REV]:
                    selected_commit = commit
                    continue
                elif version.parse(
                        selected_commit[DUMP_KEY_ISSUE_COMMIT_DETAILS_NAME_REV].split("tags/r")[1]) < version.parse(
                        commit[DUMP_KEY_ISSUE_COMMIT_DETAILS_NAME_REV].split("tags/r")[1]):
                    selected_commit = commit
        return selected_commit
