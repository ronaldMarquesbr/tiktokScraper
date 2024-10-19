def createHeader(url):
    with open(f'{url.split('/')[3][1:]}.csv', 'w', encoding='utf-8') as file:
        data = ['author', 'timestamp', 'date', 'likes', 'comments', 'shares', 'playCount', 'saves', 'duration', 'tags', 'link']
        for k in data:
            file.write(k)
            file.write(';')
        file.write('\n')


def createRow(data):
    with open(f"{data['link'].split('/')[3][1:]}.csv", 'a', encoding='utf-8') as file:
        for v in data.values():
            file.write(str(v))
            file.write(';')
        file.write('\n')
