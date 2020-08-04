import pandas

from common.constants import CONFIG_PATHS
from githubanalysis.common.ConfigFileParser import Config
from githubanalysis.common.DumpParser import DumpParser, ISSUE_DATA_W_STATS_FILE_NAME, DUMP_KEY_PROJECT_NAME
from pandasMagic import Filters
from githubanalysis.common.Logger import Logger

log = Logger()

def get_all_issues_df():
    all_issues = pandas.DataFrame()
    print(str(len(CONFIG_PATHS)) + " projects")
    for config_path in CONFIG_PATHS:
        log.s(config_path)
        config = Config(config_path)
        issues_df = get_issues_df(config)
        all_issues = all_issues.append(issues_df, ignore_index=True)
    return all_issues


def get_issues_df(config):
    dump_parser = DumpParser(config, ISSUE_DATA_W_STATS_FILE_NAME)
    issues = dump_parser.get_all_issues()
    issues_red = Filters.drop_keys(issues, ['commits'])
    issues_df = pandas.io.json.json_normalize(issues_red)
    issues_df['projectName'] = config.github_repo_name
    return issues_df