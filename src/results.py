import pandas as pd
from files import getCandidateDataFrame, getStateFolder
from partidos import getPartyAlignment, getCandidateParty
from candidatos import candidatos
from table import createTableFromDf
from utils import createDictWithZeros, convertDateToTimestamp

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 0)
pd.set_option('display.colheader_justify', 'left')


def getCandidateOverview(candidateName, state):
    candidateObject = getCandidateDataFrame(candidateName, state)
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
        'postsCount': len(candidateDf)
    }

    return candidateOverview


def getStateOverview(state):
    stateFolder = getStateFolder(state)
    stateCandidatesOverview = [getCandidateOverview(candidate[:-4], state) for candidate in stateFolder]
    keyStats = [key for key in stateCandidatesOverview[0].keys() if key not in ['name', 'party', 'side']]
    stateOverview = {'esquerda': createDictWithZeros(keyStats),
                     'direita': createDictWithZeros(keyStats),
                     'centro': createDictWithZeros(keyStats)}

    for candidate in stateCandidatesOverview:
        for key in keyStats:
            stateOverview[candidate['side']][key] = candidate[key] + stateOverview[candidate['side']].setdefault(key, 0)

    return stateOverview


def getOverviewFromCountry():
    states = candidatos.keys()
    countryOverview = {'direita': {}, 'esquerda': {}, 'centro': {}}

    for state in states:
        stateOverview = getStateOverview(state)
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
