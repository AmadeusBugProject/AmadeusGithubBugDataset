MAX_COMMITS = 10
MAX_LOC = 250
MAX_FILES = 20

DUMP_KEY_PROJECT_NAME = "projectName"
DUMP_KEY_BUG_LABELS = "bugLabels"
DUMP_KEY_CAPTURE_TIME = "captureTime"
DUMP_KEY_ISSUES = "issues"

DUMP_FILE_NAME = 'issues.json'
ISSUE_DATA_FILE_NAME = 'issuesData.json'
ISSUE_DATA_W_STATS_FILE_NAME = 'issuesDataWStats.json'
MANUAL_CLASSIFICATION_FILE = 'manualClassification.csv'

MANUAL_CLASSIFICATION_KEY_URL = "IssueUrl"
MANUAL_CLASSIFICATION_CONFIDENCE = "Confidence"
MANUAL_CLASSIFICATION_REMARKS = "Remarks"
MANUAL_CLASSIFICATION_MODE = "Mode"
MANUAL_CLASSIFICATION_ROOT_CAUSE_DETAIL = "RootCauseDetail"
MANUAL_CLASSIFICATION_ROOT_CAUSE = "RootCause"
MANUAL_CLASSIFICATION_IMPACT = "Impact"
MANUAL_CLASSIFICATION_COMPONENT = "SoftwareComponent"
MANUAL_CLASSIFICATION_INFO = "Info"
MANUAL_CLASSIFICATION_USE_COMMITS = "useCommit"

DUMP_KEY_MANUAL_CLASSIFICATION = "manualClassification"
DUMP_KEY_ISSUE_TITLE = "title"
DUMP_KEY_ISSUE_BODY = "body"
DUMP_KEY_ISSUE_URL = "url"
DUMP_KEY_ISSUE_HTML_URL = "htmlurl"
DUMP_KEY_ISSUE_USER = "user"
DUMP_KEY_ISSUE_LABELS = "labels"
DUMP_KEY_ISSUE_CREATE_TIME = "created"
DUMP_KEY_ISSUE_CLOSE_TIME = "closed"
DUMP_KEY_ISSUE_COMMITS = "commits"

DUMP_KEY_ISSUE_COMMIT_DETAILS_HASH = "commitHash"
DUMP_KEY_ISSUE_COMMIT_DETAILS_GH_EVENT_TYPE = "commitGHEventType"
DUMP_KEY_ISSUE_COMMIT_DETAILS_GH_USER = "commitUser"

DUMP_KEY_ISSUE_ID = "issueId"
DUMP_KEY_ISSUE_TTF = "ttf"
DUMP_KEY_ISSUE_MENTIONED_EXCEPTIONS = "exceptionsMentionedInIssue"
DUMP_KEY_ISSUE_STACKTRACE_FEATURES = "exceptionsStacktraceFeatures"

DUMP_KEY_ISSUE_FILTERED_COMMITS = "filteredCommits"
DUMP_KEY_ISSUE_FILTERED_COMMITS_REASON = "filteredCommitsReason"
DUMP_KEY_ISSUE_FILTERED_COMMITS_REASON_DUP = "duplicated"
DUMP_KEY_ISSUE_FILTERED_COMMITS_REASON_NOT_SINGLE_ISSUE = "multipleIssueFixes"
DUMP_KEY_ISSUE_FILTERED_COMMITS_REASON_MORE_THAN_ONE_PARENT = "moreThanOneParent"
DUMP_KEY_ISSUE_FILTERED_COMMITS_REASON_ALSO_FIXES_PHRASE = "alsoFixesPhrase"
DUMP_KEY_ISSUE_FILTERED_COMMITS_REASON_UNAVAILABLE = "unavailable"
DUMP_KEY_ISSUE_FILTERED_COMMITS_ONLY_USED_MERGE_COMMIT = "mergeCommitUsed"

DUMP_KEY_ISSUE_COMMIT_DETAILS = "commitsDetails"
DUMP_KEY_ISSUE_COMMIT_DETAILS_PARENTS = "commitParents"
DUMP_KEY_ISSUE_COMMIT_DETAILS_NAME_REV = "nameRev"
DUMP_KEY_ISSUE_COMMIT_DETAILS_MESSAGE = "commitMessage"
DUMP_KEY_ISSUE_COMMIT_DETAILS_COMMITED_DATE_TIME = "commitDateTime"
DUMP_KEY_ISSUE_COMMIT_DETAILS_AUTHORED_DATE_TIME = "authoredDateTime"
DUMP_KEY_ISSUE_COMMIT_DETAILS_GIT_STATS = "commitGitStats"
DUMP_KEY_ISSUE_COMMIT_DETAILS_SPOON_AST_DIFF_STATS = "commitSpoonAstDiffStats"

DUMP_KEY_ISSUE_STATS_SKIPPED_REASON = "statsSkippedReason"
DUMP_KEY_ISSUE_SPOON_STATS_SKIPPED_REASON = "spoonStatsSkippedReason"
DUMP_KEY_ISSUE_STATS_SKIPPED_REASON_TOO_MANY_COMMITS = "tooManyCommits"
DUMP_KEY_ISSUE_STATS_SKIPPED_REASON_TOO_MANY_FILES = "tooManyFiles"
DUMP_KEY_ISSUE_STATS_SKIPPED_REASON_TOO_MANY_CHANGES = "tooManyChanges"

DUMP_KEY_ISSUE_CHANGES_IN_PACKAGE_FROM_GIT_INFO = "changesInPackagesGIT"
DUMP_KEY_ISSUE_CHANGES_IN_PACKAGE_FROM_SPOON_INFO = "changesInPackagesSPOON"
DUMP_KEY_ISSUE_GIT_STATS_SUMMARY = "gitStatsSummary"
DUMP_KEY_ISSUE_SPOON_STATS_SUMMARY = "spoonStatsSummary"

SPOON_AST_DIFF_FILE = "spoonFilePath"
SPOON_AST_DIFF_METHOD_NAME = "spoonMethodName"
SPOON_AST_DIFF_METHODS = "spoonMethods"
SPOON_AST_DIFF_TOTAL_OPERATIONS = "TOT"
SPOON_AST_DIFF_UPD = "UPD"
SPOON_AST_DIFF_INS = "INS"
SPOON_AST_DIFF_MOV = "MOV"
SPOON_AST_DIFF_DEL = "DEL"
SPOON_AST_DIFF_EXCEPTION_DURING_DIFF = "SPOON_EXCEPTION"
SPOON_AST_DIFF_FILES_CHANGED = "spoonFilesChanged"
SPOON_AST_DIFF_METHODS_CHANGED = "spoonMethodsChanged"

DATE_TIME_STR_FORMAT ="%Y-%m-%d %H:%M:%S"

API_LINK_BASE_URL = "https://api.github.com"
WEB_LINK_BASE_URL = "https://github.com"

COMMIT_STATS_KEY_NUM_COMMITS = 'numCommits'
COMMIT_STATS_KEY_FILE_PATH = 'filePath'
COMMIT_STATS_KEY_INSERTIONS= 'insertions'
COMMIT_STATS_KEY_LINES = 'lines'
COMMIT_STATS_KEY_DELETIONS = 'deletions'
COMMIT_STATS_KEY_FILES_CHANGED = 'gitFilesChange'

ISSUE_DISTILLED_FILENAME = "issuesDistilled.csv"
ISSUE_DISTILLED_NUM_COMMITS = 'commits'
ISSUE_DISTILLED_KEYWORD_ISSUE_MESSAGE = "keywordIssueMessage"
ISSUE_DISTILLED_KEYWORD_COMMIT_MESSAGE = "keywordCommitMessage"
ISSUE_DISTILLED_CONTAINS_KNOWN_LOGCAT_ERROR_MESSAGE = "containsKnownLogcatErrorMessage"
ISSUE_DISTILLED_CONTAINS_KNOWN_EXCEPTION_MESSAGE = "containsKnownExceptionMessage"
ISSUE_DISTILLED_ALL_MENTIONED_EXCEPTIONS = "allMentionedExceptions"
