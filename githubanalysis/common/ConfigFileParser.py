import io
import json

from githubanalysis.common.collectionUtils import get_value_robust

CONFIG_PATH = "githubanalysis/config.json"

KEY_USER = "github_user"
KEY_REPO_NAME = "github_repo_name"
KEY_LOCAL_REPO = "local_git_repo"
KEY_API_KEY = "github_api_key"
KEY_DEFECT_KEY_WORDS = "defect_key_words"
KEY_IGNORE_FILE_PATHS = "ignore_file_paths"
KEY_PACKAGE_DEPTH = "package_depth"


class Config:
    def __init__(self, config_file_path=CONFIG_PATH):
        try:
            with io.open(config_file_path, 'r', encoding="utf-8") as file:
                config = json.loads(file.read())
                self.github_user = get_value_robust(config, KEY_USER, "")
                self.github_repo_name = get_value_robust(config, KEY_REPO_NAME, "")
                self.local_git_repo = get_value_robust(config, KEY_LOCAL_REPO, "")
                self.github_api_key = get_value_robust(config, KEY_API_KEY, "")
                self.defect_key_words = get_value_robust(config, KEY_DEFECT_KEY_WORDS, [])
                self.ignore_file_paths = get_value_robust(config, KEY_IGNORE_FILE_PATHS, [])
                self.package_depth = get_value_robust(config, KEY_PACKAGE_DEPTH, 1)

                self.storage_path = ""
                self.blob_path = ""
                self.project_name = ""
                self.plot_path = ""
                self.set_paths()
        except FileNotFoundError:
            self.github_user = ""
            self.github_repo_name = ""
            self.local_git_repo = ""
            self.github_api_key = ""
            self.defect_key_words = ["bug"]
            self.ignore_file_paths = []
            self.package_depth = 1
            self.plot_path = "githubanalysis/data/default/plots/"
            self.storage_path = "githubanalysis/data/default/"
            self.blob_path = "githubanalysis/data/default/blobs/"
            self.project_name = ""
        if not self.github_api_key:
            global_config = GlobalConfig()
            self.github_api_key = global_config.github_api_key

    def set_paths(self):
        self.storage_path = "githubanalysis/data/" + self.github_user + "_" + self.github_repo_name + "/"
        self.blob_path = "githubanalysis/data/" + self.github_user + "_" + self.github_repo_name + "/blobs/"
        self.plot_path = "githubanalysis/data/" + self.github_user + "_" + self.github_repo_name + "/plots/"
        self.project_name = self.github_user + "/" + self.github_repo_name

    def save_to_file(self, config_file_path=CONFIG_PATH):
        with io.open(config_file_path, 'w', encoding="utf-8") as file:
            config = {KEY_USER: self.github_user,
                      KEY_REPO_NAME: self.github_repo_name,
                      KEY_LOCAL_REPO: self.local_git_repo,
                      KEY_API_KEY: self.github_api_key,
                      KEY_DEFECT_KEY_WORDS: self.defect_key_words,
                      KEY_IGNORE_FILE_PATHS: self.ignore_file_paths,
                      KEY_PACKAGE_DEPTH: self.package_depth}
            file.write(json.dumps(config))


class GlobalConfig:
    def __init__(self):
        try:
            with io.open('config.json', 'r', encoding="utf-8") as file:
                global_config = json.loads(file.read())
                self.github_api_key = get_value_robust(global_config, KEY_API_KEY, "")
                self.gumtree_spoon_jar_path = get_value_robust(global_config, 'SPOON_CLASSPATH', "")
                self.java_home = get_value_robust(global_config, 'JAVA_HOME', "")
        except FileNotFoundError:
            self.github_api_key = ""
            self.gumtree_spoon_jar_path = ""
            self.java_home = ""

