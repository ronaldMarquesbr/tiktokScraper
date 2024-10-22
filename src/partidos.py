from candidatos import candidatos


def getPartyAlignment(party):
    if party in ['novo', 'pl', 'podemos', 'pmb', 'psd', 'prtb', 'pp', 'republicanos', 'união', 'dc']:
        return 'direita'
    elif party in ['pt', 'mobiliza', 'pdt', 'psb', 'psol', 'up', 'pco', 'pcb', 'cidadania', 'pstu']:
        return 'esquerda'
    else:  # psdb, solidariedade, mdb, avante
        return 'centro'


def getCandidateParty(candidateName, state):
    candidateObject = [candidate for candidate in candidatos[state]
                       if candidate['nome'] == candidateName][0]

    return candidateObject["partido"]


def getCandidatePartyFromCandidatesObj(candidateObj):
    return candidateObj["partido"]


def getPartiesFromCandidateList(candidateList):
    parties = set()

    for candidate in candidateList:
        parties.add(getCandidatePartyFromCandidatesObj(candidate))

    return list(parties)


def getAllPartiesFromCandidatesObject():
    allParties = []

    for estado in candidatos:
        allParties = allParties + getPartiesFromCandidateList(candidatos[estado])

    return set(allParties)
