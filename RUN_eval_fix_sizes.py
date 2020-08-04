import pandas

from common.constants import CONFIG_PATHS
from githubanalysis.common.ConfigFileParser import Config
from githubanalysis.common.DumpParser import DumpParser
from githubanalysis.common.constants import ISSUE_DATA_W_STATS_FILE_NAME, COMMIT_STATS_KEY_LINES
from mlClassifier.InputDataCreator import InputDataCreator
from pandasMagic import Filters
from pandasMagic import BugDataFrames


def main():
    print('\n\nFilter stats\n')
    filter_stats()

    print('\n\nFix size git stats\n')
    commits()
    files_changed()
    lines_changed()

    print('\n\nSample set desription\n')
    testset_described()

    
def filter_stats():
    project_stats_df = pandas.DataFrame()
    for config_path in CONFIG_PATHS:
        print(config_path)
        config = Config(config_path)
        issues_df = BugDataFrames.get_issues_df(config)
        valid_commits_df = Filters.only_bugs_with_valid_commit_set(issues_df)
        no_pr_df = Filters.remove_pull_request_issues(valid_commits_df)
        stats_df = pandas.DataFrame({'Project': [config.github_repo_name],
                                     'Issues': [issues_df.shape[0]],
                                     'alsoFixesPhrase': [issues_df[issues_df['filteredCommitsReason.alsoFixesPhrase'] == 0].shape[0]],
                                     'moreThanOneParent': [issues_df[issues_df['filteredCommitsReason.moreThanOneParent'] == 0].shape[0]],
                                     'multipleIssueFixes': [issues_df[issues_df['filteredCommitsReason.multipleIssueFixes'] == 0].shape[0]],
                                     'unavailable': [issues_df[issues_df['filteredCommitsReason.unavailable'] == 0].shape[0]],
                                     'TOT': [issues_df[issues_df['spoonStatsSummary.TOT'] != 0].shape[0]],
                                     'TOT': [issues_df[issues_df['spoonStatsSummary.TOT'].astype(str) != 'nan'].shape[0]],
                                     'mergeCommitUsed': [issues_df[issues_df['filteredCommitsReason.mergeCommitUsed'] != 0].shape[0]],
                                     'ValidCommitSet': [valid_commits_df.shape[0]],
                                     'ValidCommitSet and not PR': [no_pr_df.shape[0]],
                                     'stats Skipped reason': [issues_df[issues_df['statsSkippedReason'].astype(str) == ''].shape[0]]})

        project_stats_df = project_stats_df.append(stats_df, ignore_index=True)

    with pandas.option_context('display.max_rows', None, 'display.max_columns', None, 'display.max_colwidth', -1):
        print('\nTotals\n')
        print(project_stats_df.sum(axis=0, numeric_only=True))

    project_stats_df.to_csv('filteredIssues.csv')


def lines_changed():
    changes_per_file = []

    for config_path in CONFIG_PATHS:
        print(config_path)
        config = Config(config_path)
        dump_parser = DumpParser(config, ISSUE_DATA_W_STATS_FILE_NAME)

        for issue in dump_parser.get_all_issues():
            commits_details = issue["commitsDetails"]

            for commit_details in issue["commitsDetails"]:
                java_files = []
                for file_stats in commit_details["commitGitStats"]:
                    if file_stats['filePath'].endswith('.java'):
                        changes_per_file.append(file_stats[COMMIT_STATS_KEY_LINES])
                # if len(java_git_stats) > MAX_FILES:
                #     return DUMP_KEY_ISSUE_STATS_SKIPPED_REASON_TOO_MANY_FILES
                # for git_stat in java_git_stats:
                #     if git_stat['lines'] > MAX_LOC:
                #         return DUMP_KEY_ISSUE_STATS_SKIPPED_REASON_TOO_MANY_CHANGES

    df = pandas.DataFrame(changes_per_file)
    print("Lines changed")
    print(df.describe())
    print(df.quantile([0.75, 0.8, 0.90, 0.95, 0.96, 0.97, 0.98, 0.99]))


def files_changed():
    files_per_commit = []

    for config_path in CONFIG_PATHS:
        print(config_path)
        config = Config(config_path)
        dump_parser = DumpParser(config, ISSUE_DATA_W_STATS_FILE_NAME)

        for issue in dump_parser.get_all_issues():
            commits_details = issue["commitsDetails"]

            for commit_details in issue["commitsDetails"]:
                java_files = []
                for file_stats in commit_details["commitGitStats"]:
                    if file_stats['filePath'].endswith('.java'):
                        java_files.append(file_stats)
                if len(java_files) > 0:
                    files_per_commit.append(len(java_files))
                # if len(java_git_stats) > MAX_FILES:
                #     return DUMP_KEY_ISSUE_STATS_SKIPPED_REASON_TOO_MANY_FILES
                # for git_stat in java_git_stats:
                #     if git_stat['lines'] > MAX_LOC:
                #         return DUMP_KEY_ISSUE_STATS_SKIPPED_REASON_TOO_MANY_CHANGES

    df = pandas.DataFrame(files_per_commit)
    print("Files changed")
    print(df.describe())
    print(df.quantile([0.75, 0.8, 0.90, 0.95, 0.96, 0.97, 0.98, 0.99]))


def commits():
    num_commits = []

    for config_path in CONFIG_PATHS:
        print(config_path)
        config = Config(config_path)
        dump_parser = DumpParser(config, ISSUE_DATA_W_STATS_FILE_NAME)

        for issue in dump_parser.get_all_issues():
            num_commits.append(len(issue['commits']))

    df = pandas.DataFrame(num_commits)
    print("Commits")
    print(df.describe())
    print(df.quantile([0.75, 0.8, 0.90, 0.95, 0.96, 0.97, 0.98, 0.99]))


def testset_described():
    idc = InputDataCreator()
    print('\n\nmemory:\n')
    print(idc.get_memory_df()[['ttf', 'spoonStatsSummary.TOT', 'spoonStatsSummary.spoonFilesChanged']].describe())
    print('\n\nconcurrency:\n')
    print(idc.get_concurrency_df()[['ttf', 'spoonStatsSummary.TOT', 'spoonStatsSummary.spoonFilesChanged']].describe())
    print('\n\nall:\n')
    print(idc.all_bugs_df[['ttf', 'spoonStatsSummary.TOT', 'spoonStatsSummary.spoonFilesChanged']].describe())


if __name__ == "__main__":
    main()
