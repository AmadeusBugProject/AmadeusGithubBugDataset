# AmadeusGithubBugDataset

This repo contains everything required to reproduce what is described in "Root cause prediction based on bug reports" by T. Hirsch and B. Hofer.
Including the full dataset, all code for dataset creation and automated ML bug classification.
As our work is ongoing this dataset is subject to change.

## The dataset
### Using the dataset:
Create a python script, or console and run the following:
```python
from pandasMagic import BugDataFrames, Filters
df = BugDataFrames.get_all_issues_df() # loads all available issues (including PRs, without commits, etc)
df = Filters.only_bugs_with_valid_commit_set(df)  # filter for issues where fixes are available
df = Filters.remove_pull_request_issues(df) # remove all PRs
```
Have a look at [RUN_example_load_dataset.py](RUN_example_load_dataset.py) for an example.

## Machine learning experiment
### Plots and Performance reports:
Plots for all individual experiment runs, as well as textual information on performance and selected hyperparameters can be found here: [mlClassifier/figures](mlClassifier/figures)

### Textual data
The trainingset can be found in [mlClassifier/data](mlClassifier/data)

### Running the experiment
To start the experiment, run the following script: [RUN_ml_experiment.py](RUN_ml_experiment.py) (this will run the experiment 10 times, this can be changed in line 81 in main())

### Creating your own trainingset
Create your own manual classification or mapping in a csv, and add modify the training set creation in [mlClassifier/InputDataCreator.py](mlClassifier/InputDataCreator.py).

accordingly.
Remove the existing trainingset in [mlClassifier/data](mlClassifier/data).

Run this script: [RUN_create_trainingset.py](RUN_create_trainingset.py).

## Extending the dataset
### File locations
Collected issue tickets for all projects can be found in [githubanalysis/data](githubanalysis/data).

### File structure
Please have a look at [exampleIssue.json](exampleIssue.json) for an example on the structure of the dataset files.

### Extending the dataset 
Download the newest version of the gumtree-spoon-ast-diff jar library here:
https://github.com/SpoonLabs/gumtree-spoon-ast-diff
Update the [config.json](config.json) file with your java sdk location, the path to the spoon library, and a github API key.

The list of github projects are stored in the CONFIG_PATHS field in [common/constants.py](common/constants.py).

To re-build the full dataset run [RUN_build_dataset.py](RUN_build_dataset.py) (be aware this will take a long time, create quite some traffic, and will overwrite the existing dataset).

To add new projects, create config files in [githubanalysis/data](githubanalysis/data).

Modify line 15 in [RUN_build_dataset.py](RUN_build_dataset.py) to include only new config paths, and then run the script. 

Finally, add the new configs to the CONFIG_PATHS to use them in keyword search and ML experiments.

Creating a Github API key and adding it to the config files is strongly recommended.

## Python requirements

### Conda
The conda environment can be found in [conda.yml](conda.yml).

### Python 3.5+

* Cython
* GitPython
* PyGithub
* matplotlib
* numpy
* packaging
* pandas
* pyjnius
* tabulate
* beautifulsoup4
* google-api-core
* google-api-python-client
* google-auth
* google-auth-oauthlib
* gspread
* oauth2client
* oauthlib
* plotly
* psutil
* scikit-learn
* scipy
* nltk

## Other scripts and structure of this repo

* [githubanalysis/githubIssueAquisition](githubanalysis/githubIssueAquisition) - Contains everything for fetching issues from github.
* [githubanalysis/codeAnalysis](githubanalysis/codeAnalysis) - Contains java aware differ.
* [githubanalysis/gitRepoAnalysis](githubanalysis/gitRepoAnalysis) - Contains all code for performing operations on local git repos.
* [githubanalysis/data](githubanalysis/data) - tThe data and config files for all projects.
* [githubanalysis/db](githubanalysis/db) - Scripts for creating the code stats and other metadata based on fetched issues.

* [keywordSearch](keywordSearch) - Should be self explanatory.

* [mlClassifier](mlClassifier) - The trainingset, scripts for creation them, as well as ouptut folder for the experiments.

* [pandasMagic](pandasMagic) - Scripts for combining the raw data of all fetched projects, and applying filters to them.

## Acknowledgement
The work has been funded by the Austrian Science Fund (FWF): P 32653 (Automated Debugging in Use).
