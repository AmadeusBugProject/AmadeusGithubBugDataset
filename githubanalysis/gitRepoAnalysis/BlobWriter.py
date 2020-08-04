import io
import os

from githubanalysis.common.ConfigFileParser import Config
from githubanalysis.common.collectionUtils import uniquify
from githubanalysis.common.constants import *
from githubanalysis.common.Logger import Logger
from githubanalysis.gitRepoAnalysis.GitRepo import GitRepo

log = Logger()
# breakpoint import pdb; pdb.set_trace()


class BlobWriter:
    def __init__(self, config: Config):
        self.config = config
        self.repo = GitRepo(config.local_git_repo)

    def get_ab_blobs(self, commit_hash):
        try:
            commit = self.repo.repo.commit(commit_hash)
        except ValueError:
            log.e(commit_hash + " not found!\n")
            return
        unfiltered_diffs = commit.parents[0].diff(commit)
        if commit.parents.__len__() > 1:
            log.w(commit_hash + " has more than 1 parent")

        diffs = self.__filter_diffs_for_java_files(unfiltered_diffs)
        #
        # for diff in diffs:
        #     a_filename = self.__filename_from_path(diff.a_path)
        #     b_filename = self.__filename_from_path(diff.b_path)
        #     if a_filename and (a_filename == b_filename):
        #         with io.open(commit_folder + BLOB_BEFORE_FILE_PREFIX + a_filename, 'wb') as file:
        #             if diff.a_blob:
        #                 file.write(diff.a_blob.data_stream.read())
        #         with io.open(commit_folder + BLOB_AFTER_FILE_PREFIX + b_filename, 'wb') as file:
        #             if diff.b_blob:
        #                 file.write(diff.b_blob.data_stream.read())

    def __filter_diffs_for_java_files(self, diffs):
        filtered = []
        for diff in diffs:
            if diff.a_path.endswith('.java') or diff.b_path.endswith('.java'):
                filtered.append(diff)
        return filtered

    def __filename_from_path(self, path):
        return path.split("/")[-1]
