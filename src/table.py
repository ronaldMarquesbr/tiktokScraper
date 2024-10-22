import matplotlib.pyplot as plt
from utils import formatNumber, changeLabelName


def createTableFromDict(filename, contentList):
    with open(f'{filename}.csv', 'w', encoding='utf-8') as file:
        header = list(contentList[0].keys())
        for column in header:
            file.write(column)
            if header[-1] != column:
                file.write(';')

        file.write('\n')

        for row in contentList:
            for key in row:
                file.write(str(row[key]))
                if header[-1] != key:
                    file.write(';')

            file.write('\n')


def createRow(data):
    with open(f"{data['link'].split('/')[3][1:]}.csv", 'a', encoding='utf-8') as file:
        for v in data.values():
            file.write(str(v))
            file.write(';')
        file.write('\n')


def createTableFromDf(df, title):
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.axis('tight')
    ax.axis('off')
    values = [[formatNumber(value) for value in row] for row in df.values]
    columns = [col.capitalize() for col in df.columns]
    labels = [changeLabelName(label) for label in df.index]

    ax.table(cellText=values, colLabels=columns, rowLabels=labels, loc='center', cellLoc='center')
    ax.set_title(title, fontsize=16, fontweight='bold', loc='center', pad=20, x=0.375)
    plt.tight_layout()
    plt.savefig(f"table.pdf", format='pdf', dpi=300)
    plt.close(fig)
