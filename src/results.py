import pandas as pd
import matplotlib.pyplot as plt
from files import getStateFolder, getCandidatePostsBeforeElection
from partidos import getPartyAlignment, getCandidateParty
from candidatos import candidatos
from utils import createDictWithZeros

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 0)
pd.set_option('display.colheader_justify', 'left')


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

    orderedOverview = overviewDf.sort_values(by='likes', ascending=False)
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
