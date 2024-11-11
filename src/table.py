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
    values = [[value for value in row] for row in df.values]
    # values = [[formatNumber(value) for value in row] for row in df.values]
    columns = [col.capitalize() for col in df.columns]
    # labels = [changeLabelName(label) for label in df.index]

    ax.table(cellText=values, colLabels=columns, loc='center', cellLoc='center')
    # ax.table(cellText=values, colLabels=columns, rowLabels=labels, loc='center', cellLoc='center')
    ax.set_title(title, fontsize=16, fontweight='bold', loc='center', pad=20, x=0.375)
    plt.tight_layout()
    # plt.savefig(f"table.pdf", format='pdf', dpi=300)
    plt.savefig(f"table.png", format='png', dpi=300)
    plt.close(fig)


def createBarPlot(stateDf):
    fs = 16
    x = list(range(len(stateDf)))
    y = stateDf['likes'].to_list()
    labels = stateDf['name'].to_list()

    fig, ax = plt.subplots(figsize=(10, 5))
    barv = ax.bar(x, y, width=.5,
                  color='red',
                  tick_label=labels,
                  edgecolor='blue',
                  linewidth=2)

    # barh = ax.barh(range(1, len(stateDf) + 1), stateDf['likes'],
    #                height=.5,
    #                color='blue',
    #                edgecolor='red',
    #                tick_label=stateDf['name'],
    #                )
    #
    #
    # for rect in barh:
    #     h = rect.get_width()
    #     t = rect.get_y() + rect.get_height() / 2.
    #     ax.text(h, t, f'                     {h}',
    #             ha='center', va='center', fontsize=fs)

    ax.tick_params(axis='both',
                   labelsize=fs,
                   left=False,
                   labelleft=False,
                   labelrotation=90)

    plt.tight_layout()
    plt.show()
