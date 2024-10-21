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
