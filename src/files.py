import os
import pandas

pandas.set_option('display.max_columns', None)
pandas.set_option('display.width', 0)
pandas.set_option('display.colheader_justify', 'left')
rootPath = '/Users/ronaldmarques/Documents/amaisnova'


def getStateFolder(state):
    stateFolder = os.listdir(os.path.join(rootPath, state))
    stateFolder = [file for file in stateFolder if file != '.DS_Store']

    return stateFolder


def getCandidateDataFrame(candidateName, state):
    candidateFilePath = os.path.join(rootPath, state, f'{candidateName}.csv')
    candidateDf = pandas.read_csv(candidateFilePath, delimiter=';')

    return {'nome': candidateName, 'df': candidateDf}
