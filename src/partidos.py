from candidatos import candidatos


def getPartyAlignment(party):
    if party in ['novo', 'pl', 'podemos', 'pmb', 'psd', 'prtb', 'pp', 'republicanos', 'união', 'dc']:
        return 'direita'
    elif party in ['pt', 'mobiliza', 'pdt', 'psb', 'psol', 'up', 'pco', 'pcb', 'cidadania', 'pstu']:
        return 'esquerda'
    else:  # psdb, solidariedade, mdb, avante
        return 'centro'


def getCandidateParty(candidateDict):
    return candidateDict["partido"]


def getPartiesFromCandidateList(candidateList):
    parties = set()

    for candidate in candidateList:
        parties.add(getCandidateParty(candidate))

    return list(parties)


def getAllPartiesFromCandidatesObject():
    allParties = []

    for estado in candidatos:
        allParties = allParties + getPartiesFromCandidateList(candidatos[estado])

    return set(allParties)
