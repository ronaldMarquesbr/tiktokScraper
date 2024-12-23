import pytz
from datetime import datetime


def convertTimestamp(ts):
    dt = datetime.fromtimestamp(int(ts))
    brt = pytz.timezone('America/Sao_Paulo')
    dt_br = dt.astimezone(brt)
    data_formatada = dt_br.strftime('%d/%m/%Y')
    return data_formatada


def convertStringToTimestamp(date):
    dt = datetime.strptime(date, '%d/%m/%Y')
    timestamp = int(dt.timestamp())
    return timestamp


def convertDateToTimestamp(date):
    return datetime.strptime(date, '%d/%m/%Y')


def isMoreRecent(tsX, tsY):
    return int(tsX) >= int(tsY)


def formatNumber(numero):
    numero_str = str(numero)

    if numero < 0:
        parte_negativa = '-'
        numero_str = numero_str[1:]
    else:
        parte_negativa = ''

    partes = []
    while len(numero_str) > 3:
        partes.append(numero_str[-3:])
        numero_str = numero_str[:-3]
    partes.append(numero_str)

    numero_formatado = parte_negativa + '.'.join(reversed(partes))

    return numero_formatado


def changeLabelName(labelName):
    if labelName == 'likes':
        return 'Curtidas'
    elif labelName == 'comments':
        return 'Comentários'
    elif labelName == 'shares':
        return 'Compartilhamentos'
    elif labelName == 'playCount':
        return 'Visualizações'
    elif labelName == 'saves':
        return 'Salvamentos'
    elif labelName == 'duration':
        return 'Duração'
    elif labelName == 'postsCount':
        return 'Postagens'
    elif labelName == 'yes':
        return 'Usam'
    elif labelName == 'no':
        return 'Não usam'
    else:
        return labelName.capitalize()


def createDictWithZeros(keysList):
    newObj = {}
    for key in keysList:
        newObj[key] = 0

    return newObj


def convertStringToDatetimeFromSeries(dateSeries):
    convertedDateSeries = dateSeries.map(lambda x: convertDateToTimestamp(x)).copy()

    return convertedDateSeries


def nameAbbreviation(name):
    return ''.join([phrase[0] for phrase in name.split()])


def formatStateName(stateName):
    formattedName = ''

    if stateName == 'saoPaulo':
        return 'São Paulo'

    if stateName == 'goiania':
        return 'Goiânia'

    for position, letter in enumerate(stateName):
        if letter.upper() == letter:
            formattedName += ' ' + letter

        elif position == 0:
            formattedName += letter.upper()

        else:
            formattedName += letter

    return formattedName
