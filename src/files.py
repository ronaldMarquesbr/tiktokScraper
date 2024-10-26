import os
import pandas
from utils import convertDateToTimestamp, convertStringToDatetimeFromSeries

pandas.set_option('display.max_columns', None)
pandas.set_option('display.width', 0)
pandas.set_option('display.colheader_justify', 'left')
rootPath = '/Users/ronaldmarques/Documents/novos'


def getStateFolder(state):
    stateFolder = os.listdir(os.path.join(rootPath, state))
    stateFolder = [file for file in stateFolder if file != '.DS_Store']

    return stateFolder


def getCandidateDataFrame(candidateName, state):
    candidateFilePath = os.path.join(rootPath, state, f'{candidateName}.csv')
    candidateDf = pandas.read_csv(candidateFilePath, delimiter=';')

    return {'nome': candidateName, 'df': candidateDf}


def getCandidatePostsBeforeElection(candidateName, state):
    candidate = getCandidateDataFrame(candidateName, state)
    candidateDf = candidate['df']

    candidatePostsBeforeElection = candidateDf[
        convertStringToDatetimeFromSeries(candidateDf['date']) <=
        convertDateToTimestamp('06/10/2024')].copy()

    return {'nome': candidateName, 'df': candidatePostsBeforeElection}
