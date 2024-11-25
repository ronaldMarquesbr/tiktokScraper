import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from wordcloud import WordCloud
from ast import literal_eval
from files import getStateFolder, getCandidatePostsBeforeElection
from partidos import getPartyAlignment, getCandidateParty
from candidatos import candidatos
from utils import (createDictWithZeros, convertTimestamp, convertStringToTimestamp,
                   nameAbbreviation, formatStateName)
from table import createTableFromDf
import numpy

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 0)
pd.set_option('display.colheader_justify', 'left')


def sortSideTimelines(sideTimelines):
    allDates = set()

    for sideTimeline in sideTimelines.values():
        allDates = allDates | set(sideTimeline.index.unique())

    for sideTimeline in sideTimelines.values():
        for date in allDates:
            sideTimeline[date] = sideTimeline.get(date, 0)

    for side in sideTimelines:
        sideTimelines[side].index = pd.to_datetime(sideTimelines[side].index, format="%d/%m/%Y")
        sideTimelines[side] = sideTimelines[side].sort_index()
        sideTimelines[side].index = sideTimelines[side].index.map(lambda dt: dt.strftime("%d/%m/%Y"))

    return sideTimelines


def getCandidateOverview(candidateName, state):
    candidateObject = getCandidatePostsBeforeElection(candidateName, state)
    candidateDf = candidateObject['df']
    candidateOverview = {
        'name': candidateName,
        'party': getCandidateParty(candidateName, state),
        'side': getPartyAlignment(getCandidateParty(candidateName, state)),
        'likes': candidateDf['likes'].sum(),
        'comments': candidateDf['comments'].sum(),
        'shares': candidateDf['shares'].sum(),
        'playCount': candidateDf['playCount'].sum(),
        'saves': candidateDf['saves'].sum(),
        'duration': candidateDf['duration'].sum(),
        'postsCount': len(candidateDf),
        'votes': [candidate['votos'] for candidate in candidatos[state] if candidate['nome'] == candidateName][0],
    }

    return candidateOverview


def getCandidateHashtags(candidateName, state):
    candidateObject = getCandidatePostsBeforeElection(candidateName, state)
    candidateDf = candidateObject['df']
    allTags = []
    candidateTags = candidateDf['tags'].tolist()

    for candidateTag in candidateTags:
        allTags.extend(literal_eval(f"{candidateTag}"))

    candidateOverview = {
        'name': candidateName,
        'party': getCandidateParty(candidateName, state),
        'side': getPartyAlignment(getCandidateParty(candidateName, state)),
        'tags': allTags
    }

    return candidateOverview


def getStateOverviewBySide(state):
    stateFolder = getStateFolder(state)
    stateCandidatesOverview = [getCandidateOverview(candidate[:-4], state) for candidate in stateFolder]
    keyStats = [key for key in stateCandidatesOverview[0].keys() if key not in ['name', 'party', 'side', 'votes']]
    stateOverview = {'esquerda': createDictWithZeros(keyStats),
                     'direita': createDictWithZeros(keyStats),
                     'centro': createDictWithZeros(keyStats)}

    for candidate in stateCandidatesOverview:
        for key in keyStats:
            stateOverview[candidate['side']][key] = candidate[key] + stateOverview[candidate['side']].setdefault(key, 0)

    return stateOverview


def getStateOverview(state):
    stateFolder = getStateFolder(state)
    stateCandidatesOverview = [getCandidateOverview(candidate[:-4], state) for candidate in stateFolder]
    return stateCandidatesOverview


def getOverviewFromCountry():
    states = candidatos.keys()
    countryOverview = {'direita': {}, 'esquerda': {}, 'centro': {}}

    for state in states:
        stateOverview = getStateOverviewBySide(state)
        for side in stateOverview:
            for key in stateOverview[side]:
                countryOverview[side][key] = stateOverview[side][key] + countryOverview[side].setdefault(key, 0)

    return countryOverview


def getTikTokUseFromState(state):
    tiktokUse = {'direita': {'yes': 0, 'no': 0},
                 'esquerda': {'yes': 0, 'no': 0},
                 'centro': {'yes': 0, 'no': 0}}

    for candidate in candidatos[state]:
        tiktokUse[getPartyAlignment(candidate['partido'])]['yes' if candidate['tiktok'] else 'no'] += 1

    return tiktokUse


def getCountryOverview():
    keys = ['likes', 'comments', 'shares', 'playCount', 'saves', 'duration', 'postsCount']
    overviewDf = pd.DataFrame(columns=keys)
    states = candidatos.keys()

    for state in states:
        stateOverview = {'estado': state}
        candidatesOverview = pd.DataFrame(getStateOverview(state))

        for key in keys:
            stateOverview[key] = candidatesOverview[key].sum()

        overviewDf = pd.concat([overviewDf, pd.Series(stateOverview).to_frame().T], ignore_index=True)

    orderedOverview = overviewDf.sort_values(by='playCount', ascending=False)
    return orderedOverview


def getTikTokUseFromCountry():
    states = candidatos.keys()
    tiktokUse = {'direita': {'yes': 0, 'no': 0},
                 'esquerda': {'yes': 0, 'no': 0},
                 'centro': {'yes': 0, 'no': 0}}

    for state in states:
        stateUse = getTikTokUseFromState(state)
        for side in tiktokUse:
            tiktokUse[side]['yes'] += stateUse[side]['yes']
            tiktokUse[side]['no'] += stateUse[side]['no']

    return tiktokUse


def createResultChart(state):
    stateDf = pd.DataFrame(getStateOverview(state)).sort_values('votes', ascending=False)
    categorias = stateDf['name']
    valores_barras = stateDf['votes']
    valores_linhas = stateDf['shares'] + stateDf['likes'] + stateDf['comments'] + stateDf['postsCount']

    fig, ax = plt.subplots(figsize=(10, 5))

    plt.bar(categorias, valores_barras, color='lightblue', label='Votos')

    plt.plot(categorias, valores_linhas, color='red', marker='o', label='Interações')

    plt.title(state)
    plt.xlabel('Candidato')
    plt.ylabel('Valores')
    ax.tick_params(axis='both',
                   labelsize=12,
                   left=False,
                   labelleft=False,
                   labelrotation=90)

    plt.legend()
    plt.tight_layout()

    plt.savefig(f"{state}.png", dpi=300, bbox_inches='tight')
    plt.close(fig)


def getPostsTimelineFromCandidate(candidateName, candidateState):
    candidateDf = getCandidatePostsBeforeElection(candidateName, candidateState)['df']
    dateCount = candidateDf['date'].value_counts()

    return dateCount


def getInfoTimelineFromCandidate(candidateName, candidateState, info):
    candidateDf = getCandidatePostsBeforeElection(candidateName, candidateState)['df']
    dates = candidateDf['date'].unique().tolist()
    candidateTimeline = pd.Series()

    for date in dates:
        candidateTimeline[date] = candidateDf[candidateDf['date'] == date][info].sum()

    return candidateTimeline


def getInfoTimelineFromStateBySide(stateName, info):
    candidatesWithTikTok = [candidate for candidate in candidatos[stateName] if candidate['tiktok']]
    candidatesTimelines = [(getInfoTimelineFromCandidate(candidate['nome'], stateName, info), candidate['nome'])
                           for candidate in candidatesWithTikTok]

    sideTimelines = {side: pd.Series() for side in ['esquerda', 'direita', 'centro']}

    for candidateTimeline in candidatesTimelines:
        timeline = candidateTimeline[0]
        candidateSide = getPartyAlignment(getCandidateParty(candidateTimeline[1], stateName))

        for date, count in timeline.items():
            sideTimelines[candidateSide][date] = sideTimelines[candidateSide].get(date, 0) + count

    return sortSideTimelines(sideTimelines)


def getInfoTimelineFromCountryBySide(info):
    states = candidatos.keys()
    statesTimelines = [(getInfoTimelineFromStateBySide(state, info), state) for state in states]

    countryTimelines = {side: pd.Series() for side in ['esquerda', 'direita', 'centro']}
    for group in statesTimelines:
        stateTimeline = group[0]

        for side in stateTimeline:
            timeline = stateTimeline[side]

            for date, count in timeline.items():
                countryTimelines[side][date] = countryTimelines[side].get(date, 0) + count

    return sortSideTimelines(countryTimelines)


def getPostsTimelineFromState(stateName):
    candidatesWithTikTok = [candidate for candidate in candidatos[stateName] if candidate['tiktok']]
    candidatesTimelines = [(getPostsTimelineFromCandidate(candidate['nome'], stateName), candidate['nome'])
                           for candidate in candidatesWithTikTok]

    postsOverview = pd.DataFrame(columns=['date', 'postsCount', 'side'])
    for candidateTimeline in candidatesTimelines:
        timeline = candidateTimeline[0]

        for date, count in timeline.items():
            postsOverview[date] = postsOverview.get(date, 0) + count

    return postsOverview


def getPostsTimelineFromStateBySide(stateName):
    candidatesWithTikTok = [candidate for candidate in candidatos[stateName] if candidate['tiktok']]
    candidatesTimelines = [(getPostsTimelineFromCandidate(candidate['nome'], stateName), candidate['nome'])
                           for candidate in candidatesWithTikTok]
    sideTimelines = {side: pd.Series(dtype=pd.Int64Dtype()) for side in ['esquerda', 'direita', 'centro']}

    for candidateTimeline in candidatesTimelines:
        timeline = candidateTimeline[0]
        candidateSide = getPartyAlignment(getCandidateParty(candidateTimeline[1], stateName))

        for date, count in timeline.items():
            sideTimelines[candidateSide][date] = sideTimelines[candidateSide].get(date, 0) + count

    allDates = set()

    for side in sideTimelines:
        allDates = allDates | set(sideTimelines[side].index)

    for side in sideTimelines:
        for date in allDates:
            sideTimelines[side][date] = sideTimelines[side].get(date, 0)

    return sideTimelines


def getCountryPostsTimeline():
    countryTimelines = {side: pd.Series(dtype=pd.Int64Dtype()) for side in ['esquerda', 'direita', 'centro']}

    states = list(candidatos.keys())
    for state in states:
        stateTimeline = getPostsTimelineFromStateBySide(state)

        for side in stateTimeline:
            for date, count in stateTimeline[side].items():
                countryTimelines[side][date] = countryTimelines[side].get(date, 0) + count

    return sortSideTimelines(countryTimelines)


def createPostsTimeline(sideTimelines, title):
    fig, ax = plt.subplots(figsize=(8, 6))

    for side in sideTimelines:
        if side == 'esquerda':
            color = 'red'
        elif side == 'direita':
            color = 'orange'
        else:
            color = 'blue'

        xAxis = sideTimelines[side].index
        ax.plot(xAxis, sideTimelines[side].values, color=color, marker='.', label=f"{side.capitalize()}")

    plt.grid(True, which='major', axis='y', linestyle='--')
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    ax.xaxis.set_major_locator(plt.MaxNLocator(5))
    plt.legend(fontsize=15)


    fig.supxlabel("Data", fontweight='bold', fontsize=16)
    fig.supylabel(title.capitalize(), fontweight='bold', fontsize=15)

    ax.tick_params(axis='x', labelsize=15)
    ax.tick_params(axis='y', labelsize=16)

    plt.tight_layout()

    plt.savefig(f"{title.capitalize()}.png", dpi=300, bbox_inches='tight')
    plt.close(fig)


def getInfoTimelineFromCountryConcise(info):
    infoTimeline = pd.Series()
    res = getInfoTimelineFromCountryBySide(info)
    for sid in res.values():
        for date, count in sid.items():
            infoTimeline[date] = infoTimeline.get(date, 0) + count

    return infoTimeline.sort_values(ascending=False)


def getInfoTimelineFromCountry(info):
    states = candidatos.keys()
    statesObj = [(getInfoTimelineFromState(state, info), state) for state in states]
    statesTimelines = [stateObj[0] for stateObj in statesObj]

    allDates = set()

    for stateTimeline in statesTimelines:
        allDates = allDates | set(stateTimeline.index)

    allDates = list(allDates)
    allDates = [convertStringToTimestamp(date) for date in allDates]
    allDates.sort()
    allDates = [convertTimestamp(date) for date in allDates]

    for stateTimeline in statesTimelines:
        for date in allDates:
            stateTimeline[date] = stateTimeline.get(date, 0)

    timeline = pd.DataFrame(columns=states)

    for date in allDates:
        tempTimeline = {'date': date}
        for stateObj in statesObj:
            tempTimeline[stateObj[1]] = [stateObj[0][date]]

        timeline = pd.concat([timeline, pd.DataFrame(tempTimeline)], ignore_index=True)

    timeline.set_index('date', inplace=True)
    totais = []
    for date in timeline.index:
        total = timeline.loc[date].sum()
        totais.append(total)

    timeline['total'] = totais

    return timeline


def getInfoTimelineFromState(stateName, info):
    candidatesWithTikTok = [candidate for candidate in candidatos[stateName] if candidate['tiktok']]
    candidatesTimelines = [getInfoTimelineFromCandidate(candidate['nome'], stateName, info)
                           for candidate in candidatesWithTikTok]

    stateTimeline = pd.Series()

    for candidateTimeline in candidatesTimelines:
        for date, count in candidateTimeline.items():
            stateTimeline[date] = stateTimeline.get(date, 0) + count

    return stateTimeline.sort_values(ascending=False)


def getAllCandidatesWithTikTok():
    states = candidatos.keys()

    allCandidates = pd.DataFrame()

    for state in states:
        stateOverview = pd.DataFrame(getStateOverview(state))
        stateOverview['state'] = state
        allCandidates = pd.concat([allCandidates, stateOverview], ignore_index=True)

    return allCandidates


def getAllCandidatesBySide():
    allCandidates = getAllCandidatesWithTikTok()
    return {
        side: allCandidates[allCandidates['side'] == side]
        .sort_values(by='playCount', ascending=False)
        .reset_index(drop=True)
        for side in ['esquerda', 'direita', 'centro']
    }


def getHashtagsFromStateBySide(state):
    stateCandidates = [candidate for candidate in candidatos[state] if candidate['tiktok']]

    hashtags = {side: [] for side in ['esquerda', 'direita', 'centro']}

    for candidate in stateCandidates:
        candidateHashtags = getCandidateHashtags(candidate['nome'], state)
        hashtags[candidateHashtags['side']].extend(candidateHashtags['tags'])

    return hashtags


def getHashtagsFromCountryBySide():
    states = candidatos.keys()
    countryHashtags = {side: [] for side in ['esquerda', 'direita', 'centro']}

    for state in states:
        stateHashtags = getHashtagsFromStateBySide(state)
        for side in countryHashtags:
            countryHashtags[side].extend(stateHashtags[side])

    return countryHashtags


def getHashtagsFromCountry():
    sideHashTags = getHashtagsFromCountryBySide()
    countryHashtags = []

    for side in sideHashTags:
        countryHashtags.extend(sideHashTags[side])

    return countryHashtags


def generateWordCloud(stringList):
    wordList = ' '.join(stringList)
    wordcloud = WordCloud(width=800, height=400, background_color='white', collocations=False).generate(wordList)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.savefig("nuvem.png", dpi=300)


def getAllCandidatesFromState(stateName):
    candidatesOverview = pd.DataFrame(getStateOverview(stateName))
    candidatesOverview['interactions'] = (candidatesOverview['likes'] +
                                          candidatesOverview['shares'] +
                                          candidatesOverview['saves'])

    stateCandidatesWithoutTikTok = [candidate for candidate in candidatos[stateName]
                                    if candidate['nome'] not in candidatesOverview['name'].tolist()]

    for candidate in stateCandidatesWithoutTikTok:
        candidateSeries = pd.DataFrame({
            'name': [candidate['nome']],
            'party': [candidate['partido']],
            'side': [getPartyAlignment(candidate['partido'])],
            'votes': [candidate['votos']],
            'likes': [0],
            'comments': [0],
            'shares': [0],
            'playCount': [0],
            'saves': [0],
            'duration': [0],
            'postsCount': [0],
            'interactions': [0]
        })

        candidatesOverview = pd.concat([candidatesOverview, candidateSeries], ignore_index=True)

    candidatesOverview.sort_values(by='votes', inplace=True)

    return candidatesOverview


def createVotesAndInteractionsPlot(stateName):
    candidatesOverview = getAllCandidatesFromState(stateName)

    fig, ax = plt.subplots(figsize=(8, 6))

    names = candidatesOverview['name'].tolist()
    names = [nameAbbreviation(name) for name in names]

    interactionsAmount = candidatesOverview['interactions'].sum()
    votesAmount = candidatesOverview['votes'].sum()

    ax.bar(names, candidatesOverview['votes'] / votesAmount, color='skyblue', label='Votos')
    ax.plot(names, candidatesOverview['interactions'] / interactionsAmount,
            color='red', marker='.', label='Interações')

    ax.set_xlabel('Candidatos', fontweight='bold', fontsize=16)
    ax.set_ylabel('Apoio recebido', fontweight='bold', fontsize=16)

    ax.tick_params(axis='x', labelsize=15)
    ax.tick_params(axis='y', labelsize=16)

    ax.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1.0))
    ax.legend()
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    plt.savefig(f'{stateName}.png', format='png', dpi=300)
    plt.close(fig)


def votesAndInteractionsCorrelationFromState(stateName):
    candidatesOverview = getAllCandidatesFromState(stateName)

    correlation = candidatesOverview['votes'].corr(candidatesOverview['interactions'])

    return correlation


def getCorrelationVotesFromCountry():
    correlations = pd.Series()
    states = candidatos.keys()
    for state in states:
        correlations[state] = votesAndInteractionsCorrelationFromState(state)

    return correlations

def createBarPlotFromCorrelations():
    correlations = getCorrelationVotesFromCountry()
    statesNames = [formatStateName(state) for state in correlations.index]
    # Plotando o gráfico de barras
    plt.figure(figsize=(10, 6))
    plt.bar(statesNames, correlations.values, color='green', alpha=0.5)
    plt.xlabel('Município', fontsize=16, fontweight='bold')
    plt.ylabel('Coeficiente de Correlação (Pearson)', fontsize=16, fontweight='bold')
    plt.ylim(-0.25, 1)
    plt.xticks(rotation=24, fontsize=16)
    plt.yticks(fontsize=16)
    plt.tight_layout()
    plt.savefig('correlations.png', format='png', dpi=300)


createPostsTimeline(getInfoTimelineFromCountryBySide('playCount'), 'Visualizações (em dezenas de milhões)')
