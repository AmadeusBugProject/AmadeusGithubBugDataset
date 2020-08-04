import io
import json
import os
import sys

import pandas

from githubanalysis.common.Logger import Logger
from githubanalysis.common.constants import DUMP_KEY_ISSUE_COMMIT_DETAILS
from pandasMagic import BugDataFrames, Filters

# log = Logger()
log = Logger(log_file='mlClassifier/data/dataset_composition.txt')

class InputDataCreator:
    def __init__(self):
        all_bugs_df = BugDataFrames.get_all_issues_df()
        all_bugs_df = Filters.only_bugs_with_valid_commit_set(all_bugs_df)
        self.all_bugs_df = Filters.remove_pull_request_issues(all_bugs_df)

    def load_csv(self, path):
        df = pandas.read_csv(path)
        df['RootCauseDetail'] = df['RootCauseDetail'].str.lower()
        df['RootCauseDetail'] = df['RootCauseDetail'].str.strip()
        df['RootCause'] = df['RootCause'].str.lower()
        df['RootCause'] = df['RootCause'].str.strip()
        df['ConfidenceNumeric'] = pandas.to_numeric(df['Confidence'])
        return df

    def get_memory_df(self):
        csv_df = self.load_csv('mlClassifier/data/keyword_memory_concurrency_bugs.csv')
        mem_df = csv_df[csv_df['RootCause'] == 'memory']
        log.s('keyword search memory: ' + str(mem_df.shape))

        rand_df = self.load_csv('mlClassifier/data/randomly_selected_bugs.csv')
        rand_df = rand_df[rand_df['RootCause'] == 'memory']
        log.s('random selected memory: ' + str(rand_df.shape))

        mem_df = mem_df.append(rand_df, ignore_index=True)
        log.s('full memory training set: ' + str(mem_df.shape))
        return self.all_bugs_df[self.all_bugs_df['url'].isin(mem_df['url'].values)].copy()

    def get_concurrency_df(self):
        csv_df = self.load_csv('mlClassifier/data/keyword_memory_concurrency_bugs.csv')
        con_df = csv_df[csv_df['RootCause'] == 'concurrency']
        log.s('keyword search concurrency: ' + str(con_df.shape))

        rand_df = self.load_csv('mlClassifier/data/randomly_selected_bugs.csv')
        rand_df = rand_df[rand_df['RootCause'] == 'concurrency']
        log.s('random selected concurrency: ' + str(rand_df.shape))

        con_df = con_df.append(rand_df, ignore_index=True)
        log.s('full concurrency training set: ' + str(con_df.shape))
        return self.all_bugs_df[self.all_bugs_df['url'].isin(con_df['url'].values)].copy()

    def get_semantic_KW_bias_scaled_df(self):
        keyw_df = self.load_csv('mlClassifier/data/keyword_memory_concurrency_bugs.csv')
        log.s('keyword search totals: ' + str(keyw_df.shape))
        log.s('keyword search manually classified: ' + str(keyw_df[keyw_df['ConfidenceNumeric'] > 0].shape))
        keyw_df = keyw_df[keyw_df['RootCause'] == 'semantic']
        log.s('keyword search semantic: ' + str(keyw_df.shape))
        keyw_df = keyw_df[keyw_df['ConfidenceNumeric'] > 7]
        log.s('keyword search semantic with confidence above 7: ' + str(keyw_df.shape))
        keyw_df = keyw_df.sample(int(keyw_df.shape[0]*0.05))
        log.s('keyword search semantic sample size: ' + str(keyw_df.shape))

        rand_df = self.load_csv('mlClassifier/data/randomly_selected_bugs.csv')
        log.s('random selected totals: ' + str(rand_df.shape))
        rand_df = rand_df[rand_df['RootCause'] == 'semantic']
        log.s('random selected semantic: ' + str(rand_df.shape))
        rand_df = rand_df[rand_df['ConfidenceNumeric'] > 7]
        log.s('random selected semantic with confidence above 7: ' + str(rand_df.shape))

        sem_df = pandas.DataFrame()
        sem_df = sem_df.append(keyw_df, ignore_index=True)
        sem_df = sem_df.append(rand_df, ignore_index=True)
        log.s('full semantic training set: ' + str(sem_df.shape))
        return self.all_bugs_df[self.all_bugs_df['url'].isin(sem_df['url'].values)].copy()

    def write_bug_report_files(self, df, category):
        df.to_csv('mlClassifier/data/trainingset_' + category + '.csv')
        category_path = 'mlClassifier/data/bugreports/' + category + '/'
        os.makedirs(category_path, exist_ok=True)
        for index, row in df.iterrows():
            file_name = row['url'].replace('https://github.com/', '').replace('/', '_')
            with io.open(category_path + file_name, 'w',  encoding="utf-8") as file:
                file.write(row["title"] + "\n" + row["body"])

    def write_commit_message_files(self, df, category):
        df = df.explode('commitsDetails')
        df = pandas.concat(
            [df.drop(['commitsDetails'], axis=1), df['commitsDetails'].apply(pandas.Series)],
            axis=1)
        df['commitMessage'] = df[['url', 'commitMessage']].groupby(['url'])['commitMessage'].transform(lambda x: '\n'.join(x))
        df[['url', 'commitMessage']].drop_duplicates()

        category_path = 'mlClassifier/data/commitmessages/' + category + '/'
        os.makedirs(category_path, exist_ok=True)
        for index, row in df.iterrows():
            file_name = row['url'].replace('https://github.com/', '').replace('/', '_')
            with io.open(category_path + file_name, 'w',  encoding="utf-8") as file:
                file.write(row["commitMessage"])

    def setup_bug_report_files(self):
        print('\nMEMORY')
        mem_df = self.get_memory_df()#.sample(120)
        self.write_bug_report_files(mem_df, 'memory')

        print('\nCONCURRENCY')
        con_df = self.get_concurrency_df()#.sample(120)
        self.write_bug_report_files(con_df, 'concurrency')

        print('\nSEMANTIC')
        sem_df = self.get_semantic_KW_bias_scaled_df()#.sample(120)
        self.write_bug_report_files(sem_df, 'semantic')

    def setup_commit_message_files(self):
        mem_df = self.get_memory_df()
        self.write_commit_message_files(mem_df, 'memory')
        con_df = self.get_concurrency_df()
        self.write_commit_message_files(con_df, 'concurrency')
        sem_df = self.get_semantic_df()
        self.write_commit_message_files(sem_df, 'semantic')
