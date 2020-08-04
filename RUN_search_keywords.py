import os

import pandas

from githubanalysis.common.DumpParser import DUMP_KEY_ISSUE_COMMIT_DETAILS_MESSAGE, \
    DUMP_KEY_ISSUE_COMMIT_DETAILS, DUMP_KEY_ISSUE_URL
from keywordSearch.constants import KEYWORDS_IMPACT_RE, KEYWORDS_CONCURRENCY_RE, KEYWORDS_MEMORY_RE, KEYWORD_PATH
from pandasMagic import BugDataFrames
from pandasMagic import Filters


def main():
    # write_keyword_search_results_to_file()
    keywords_described()


def write_keyword_search_results_to_file():
    df = BugDataFrames.get_all_issues_df()
    df = Filters.only_bugs_with_valid_commit_set(df)
    df = Filters.remove_pull_request_issues(df)

    df = df.explode(DUMP_KEY_ISSUE_COMMIT_DETAILS)
    df = pandas.concat([df.drop([DUMP_KEY_ISSUE_COMMIT_DETAILS], axis=1), df[DUMP_KEY_ISSUE_COMMIT_DETAILS].apply(pandas.Series)], axis=1)

    memory_df = df[df[DUMP_KEY_ISSUE_COMMIT_DETAILS_MESSAGE].str.contains('|'.join(KEYWORDS_MEMORY_RE), case=False)]
    memory_url_ser = memory_df[DUMP_KEY_ISSUE_URL].value_counts()

    concurrency_df = df[df[DUMP_KEY_ISSUE_COMMIT_DETAILS_MESSAGE].str.contains('|'.join(KEYWORDS_CONCURRENCY_RE), case=False)]
    concurrency_url_ser = concurrency_df[DUMP_KEY_ISSUE_URL].value_counts()

    impact_df = df[df[DUMP_KEY_ISSUE_COMMIT_DETAILS_MESSAGE].str.contains('|'.join(KEYWORDS_IMPACT_RE), case=False)]
    impact_url_ser = impact_df[DUMP_KEY_ISSUE_URL].value_counts()


    all_keywords = []
    all_keywords.extend(KEYWORDS_MEMORY_RE)
    all_keywords.extend(KEYWORDS_IMPACT_RE)
    all_keywords.extend(KEYWORDS_CONCURRENCY_RE)

    random_any_other_df = df[~df[DUMP_KEY_ISSUE_COMMIT_DETAILS_MESSAGE].str.contains('|'.join(all_keywords), case=False)]
    random_any_other_url_ser = random_any_other_df.sample(120)[DUMP_KEY_ISSUE_URL].value_counts()

    print('\nsearching in commit message:')
    print('memory ' + str(memory_df.shape[0]) + ' unique ' + str(memory_url_ser.shape[0]))
    print('concurrency ' + str(concurrency_df.shape[0]) + ' unique ' + str(concurrency_url_ser.shape[0]))
    print('suspicious impacts ' + str(impact_df.shape[0]) + ' unique ' + str(impact_url_ser.shape[0]))

    os.makedirs(KEYWORD_PATH, exist_ok=True)
    memory_url_ser.to_csv(KEYWORD_PATH + 'memory.csv')
    concurrency_url_ser.to_csv(KEYWORD_PATH + 'concurrency.csv')
    random_any_other_url_ser.to_csv(KEYWORD_PATH + 'random.csv')


def keywords_described():
    df_all = BugDataFrames.get_all_issues_df()
    df_all = Filters.only_bugs_with_valid_commit_set(df_all)
    df_all = Filters.remove_pull_request_issues(df_all)
    df_all = Filters.remove_reporter_is_committer_issues(df_all)

    df = df_all.explode(DUMP_KEY_ISSUE_COMMIT_DETAILS)
    df = pandas.concat([df.drop([DUMP_KEY_ISSUE_COMMIT_DETAILS], axis=1), df[DUMP_KEY_ISSUE_COMMIT_DETAILS].apply(pandas.Series)], axis=1)

    memory_df = df[df[DUMP_KEY_ISSUE_COMMIT_DETAILS_MESSAGE].str.contains('|'.join(KEYWORDS_MEMORY_RE), case=False)]
    memory_url_ser = memory_df[DUMP_KEY_ISSUE_URL].value_counts()

    concurrency_df = df[df[DUMP_KEY_ISSUE_COMMIT_DETAILS_MESSAGE].str.contains('|'.join(KEYWORDS_CONCURRENCY_RE), case=False)]
    concurrency_url_ser = concurrency_df[DUMP_KEY_ISSUE_URL].value_counts()

    random_any_other_df = df[(~df[DUMP_KEY_ISSUE_COMMIT_DETAILS_MESSAGE].str.contains('|'.join(KEYWORDS_MEMORY_RE), case=False) &
                              (~df[DUMP_KEY_ISSUE_COMMIT_DETAILS_MESSAGE].str.contains('|'.join(KEYWORDS_CONCURRENCY_RE), case=False)) &
                              (~df[DUMP_KEY_ISSUE_COMMIT_DETAILS_MESSAGE].str.contains('|'.join(KEYWORDS_IMPACT_RE), case=False)))]
    random_any_other_url_ser = random_any_other_df.sample(250)[DUMP_KEY_ISSUE_URL].value_counts()

    print('\n\nmemory:\n')
    print(describe_stats(df_all, memory_url_ser))
    print('\n\nconcurrency:\n')
    print(describe_stats(df_all, concurrency_url_ser))
    print('\n\n500 random all:\n')
    print(describe_stats(df_all, random_any_other_url_ser))


def describe_stats(df_all, url_series):
    return df_all[df_all['url'].isin(url_series.index)][['ttf', 'spoonStatsSummary.TOT', 'spoonStatsSummary.spoonFilesChanged']].describe()


if __name__ == "__main__":
    main()
