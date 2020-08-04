import pandas

from mlClassifier.isof1 import plot_isof1


def main():
    df = pandas.DataFrame()
    for k in range(0, 100):
        run_df = pandas.read_csv('mlClassifier/figures/ml_5_fold_cross_validation' + str(k) + '.csv', index_col=0)
        df = df.append(run_df)

    descriptions = pandas.DataFrame()
    for method in df['classifier'].value_counts().index:
        description = df[df['classifier'] == method].describe()
        description['classifier'] = method
        descriptions = descriptions.append(description)
        print(method)
        print(df[df['classifier'] == method]['F1 weighted average'].describe())
    descriptions.to_csv('description_all_experiments.csv')

    descriptions['metric'] = descriptions.index
    descriptions['index'] = 1
    descriptions = descriptions.set_index('index')
    descriptions.reset_index()

    plot_for_metric(descriptions, 'mean')
    plot_for_metric(descriptions, '50%')
    plot_for_metric(descriptions, 'min')
    plot_for_metric(descriptions, 'max')


def plot_for_metric(descriptions, metric):
    df = descriptions[descriptions['metric'] == metric].copy()
    df = df.drop(columns=['metric'])
    plot_isof1(df, metric, 0.4)


if __name__ == "__main__":
    main()
