from pynput import keyboard
import pytz
from datetime import datetime


def pressCombination():
    controller = keyboard.Controller()
    controller.press(keyboard.Key.cmd)
    controller.press('r')
    controller.release('r')
    controller.release(keyboard.Key.cmd)


def convertTimestamp(ts):
    dt = datetime.fromtimestamp(int(ts))
    brt = pytz.timezone('America/Sao_Paulo')
    dt_br = dt.astimezone(brt)
    data_formatada = dt_br.strftime('%d/%m/%Y')
    return data_formatada


def isMoreRecent(tsX, tsY):
    return int(tsX) >= int(tsY)
