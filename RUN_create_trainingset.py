from mlClassifier.InputDataCreator import InputDataCreator


def main():
    idc = InputDataCreator()
    idc.setup_bug_report_files()
    # idc.setup_commit_message_files()


if __name__ == "__main__":
    main()


