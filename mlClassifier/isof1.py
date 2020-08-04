import pandas
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

plots_dir = "mlClassifier/figures/"

def plot_isof1(df, file_appendix, scale=None):
    # df = pandas.read_csv('ml_5_fold_cross_validation.csv', index_col=0)
    df = df.copy().rename(columns={'classifier': 'Classifier'})
    df = df.drop(columns=['F1 macro average',
                          'F1 weighted average',
                          'accuracy',
                          'precision macro average',
                          'recall macro average'])

    df = df.rename(columns={'precision weighted average': 'Precision',
                            'recall weighted average': 'Recall'})
    df = df.reset_index()
    plot_precision_recall_comparison_with_iso_f1(df, file_appendix, scale)


def plot_precision_recall_comparison_with_iso_f1(df, file_appendix, min_show):
    plt.figure(figsize=(7, 8))
    f_scores = np.linspace(0.1, 0.9, num=9)
    lines = []
    labels = []
    for f_score in f_scores:
        x = np.linspace(0.01, 1, num=500)
        y = f_score * x / (2 * x - f_score)
        l, = plt.plot(x[y >= 0], y[y >= 0], color='gray', alpha=0.2)
        plt.annotate('f1={0:0.1f}'.format(f_score), xy=(0.9, y[450] + 0.02),color='gray')

    lines.append(l)
    labels.append('iso-f1 curves')

    markers = ['bo', 'ro', 'go', 'bx', 'rx', 'gx', 'b+', 'r+', 'g+', 'bs', 'rs', 'gs']

    for index, row in df.iterrows():
        l, = plt.plot(row['Recall'], row['Precision'], markers.pop(0))
        lines.append(l)
        labels.append(row['Classifier'])

    # fig = plt.gcf()
    # fig.subplots_adjust(bottom=0.25)
    if min_show:
        plt.xlim([min_show, 1.0])
        plt.ylim([min_show, 1.0])
    else:
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.0])
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    # plt.title('Precision-Recall comparison')
    plt.legend(lines, labels, loc=(0.05, 0.65), prop=dict(size=14))
    plt.tight_layout(rect=[0, 0.95, 1, 1])

    file_name = "isof1_" + file_appendix + ".png"

    plt.savefig(plots_dir + file_name)
    # plt.show()
