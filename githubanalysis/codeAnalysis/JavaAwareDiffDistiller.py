import os
from io import StringIO
from pathlib import Path

from githubanalysis.codeAnalysis.spoonAstDiffer.PyWrapperSpoonAstDiff import PyWrapperSpoonAstDiff
from githubanalysis.common.ConfigFileParser import Config, GlobalConfig
from githubanalysis.common import Logger
from githubanalysis.common.collectionUtils import uniquify
from githubanalysis.common.constants import *
from githubanalysis.common.Logger import Logger
from githubanalysis.gitRepoAnalysis.GitRepo import GitRepo

log = Logger()

global_config = GlobalConfig()
os.environ['JAVA_HOME'] = global_config.java_home
os.environ['CLASSPATH'] = global_config.gumtree_spoon_jar_path

DISTILLER_CHANGED_ENTITY_KEY = "changedEntity"
DISTILLER_CHANGE_TYPE_KEY = "changeType"


class JavaAwareDiffDistiller:
    def __init__(self, config: Config):
        self.config = config
        #self.java_aware_differ = PyWrapperChangeDistiller()
        self.java_aware_differ = PyWrapperSpoonAstDiff()
        self.detailed_stats = {}
        self.condensed_stats = {}
        self.repo = GitRepo(config.local_git_repo)

    def diff_commit(self, commit_hash):
        commit_distillant = {}

        try:
            commit = self.repo.repo.commit(commit_hash)
        except ValueError:
            log.e(commit_hash + " not found!\n")
            return
        unfiltered_diffs = commit.parents[0].diff(commit)
        if commit.parents.__len__() > 1:
            log.w(commit_hash + " has more than 1 parent")

        diffs = self.__filter_diffs_for_java_files(unfiltered_diffs)
        diffs = self.__filter_duplicate_files(diffs)

        for diff in diffs:
            a_filename = self.__filename_from_path(diff.a_path)
            b_filename = self.__filename_from_path(diff.b_path)
            if a_filename or b_filename:
                a_stream = ''
                b_stream = ''
                filename = ''
                if diff.a_blob:
                    a_stream = diff.a_blob.data_stream.read().decode("utf-8", errors='ignore')
                    filename = a_filename
                if diff.b_blob:
                    b_stream = diff.b_blob.data_stream.read().decode("utf-8", errors='ignore')
                    filename = b_filename
                commit_distillant.update({filename: self.java_aware_differ.diff_java(a_stream, b_stream)})
        return commit_distillant

    def __filter_diffs_for_java_files(self, diffs):
        filtered = []
        for diff in diffs:
            if diff.a_path.endswith('.java') or diff.b_path.endswith('.java'):
                filtered.append(diff)
        return filtered

    def __filter_duplicate_files(self, diffs):
        filtered = {}
        for diff in diffs:
            if diff.a_path:
                filename = diff.a_path
            if diff.b_path:
                filename = diff.b_path
            filtered.update({filename: diff})
        return filtered.values()

    def __filename_from_path(self, path):
        return path.split("/")[-1]

    def get_stats(self, detailed_diff):
        stats = []
        for file_name, diff_value in detailed_diff.items():
            file_stats = {SPOON_AST_DIFF_FILE: file_name, SPOON_AST_DIFF_METHODS: []}

            if SPOON_AST_DIFF_EXCEPTION_DURING_DIFF in diff_value.keys():
                method_stats = {SPOON_AST_DIFF_METHOD_NAME: SPOON_AST_DIFF_EXCEPTION_DURING_DIFF}
                file_stats[SPOON_AST_DIFF_METHODS].append(method_stats)
            else:
                for method_name, method in diff_value.items():
                    method_stats = {
                              SPOON_AST_DIFF_METHOD_NAME: method_name,
                              SPOON_AST_DIFF_TOTAL_OPERATIONS: 0,
                              SPOON_AST_DIFF_UPD: 0,
                              SPOON_AST_DIFF_INS: 0,
                              SPOON_AST_DIFF_MOV: 0,
                              SPOON_AST_DIFF_DEL: 0}
                    for change in method:
                        change_type = change[DISTILLER_CHANGE_TYPE_KEY]
                        method_stats[change_type] += 1
                        method_stats[SPOON_AST_DIFF_TOTAL_OPERATIONS] += 1
                    file_stats[SPOON_AST_DIFF_METHODS].append(method_stats)
            stats.append(file_stats)
        return stats
