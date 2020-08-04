from pandasMagic import BugDataFrames
from pandasMagic import Filters


def main():
    df = BugDataFrames.get_all_issues_df()
    print(df.shape)

    df = Filters.only_bugs_with_valid_commit_set(df)
    df = Filters.remove_pull_request_issues(df)
    print(df.shape)


if __name__ == "__main__":
    main()
