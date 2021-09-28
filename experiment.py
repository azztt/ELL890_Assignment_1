from __future__ import with_statement
import threading
# from types import FunctionType
from typing import Sequence
from numpy import ceil
from psychopy import core, gui, visual, data, event
from psychopy.hardware.keyboard import Keyboard
import numpy.random as nrand
import matplotlib.pyplot as plt
from os import makedirs

# =====================SETUP=========================

DATA_DIR = 'experiment_data'

# 1) prepare the letter to be tested and the preceding
#    letter randomly

# list of alphabets in sequence
alpha = [chr(i) for i in range(65, 65+26)]
# picking random alphabet to be the target
tAlpha = nrand.choice(alpha)
# remove the target letter
alpha.remove(tAlpha)
# picking random alphabet to always preceed
# the target from remaining alphabets
pAlpha = nrand.choice(alpha)
# remove that as well
alpha.remove(pAlpha)

# 2) initialize preceeding variable letter to empty
#    (there is no preceeding letter for the first trial)
#    set variable to represent if experiment is on for
#    listening to relevant key presses or not and other
#    logic related variables
prevLet = ''
expOn = False
targetPresentedTimes = []
keyPressedTimes = []
# Inter-Stimulus Interval range and initial value
isiRange = (0.700,0.900)
isi = 0.800
# Onset time (fixed)
# onTRange = (0.400,0.600)
onT = 0.200
# final list of choices to choose next stimuli with bias for
# the preceding letter
percentageSamples = 50 # samples percentage needed in %
frSample = percentageSamples/100.0
numSample = int(ceil(24*frSample/(1-frSample)))
alphaChoices = [pAlpha]*numSample
alphaChoices += alpha

# 3) Set experiment parameters (to be entered by setter again)
expData = {
    'Date of Experiment': data.getDateStr(),
    'Name of Subject': 'Subject_1',
    'Duration of Experiment': 300
}
# dataLabels = [
#     'Date of Experiment', 
#     'Name of Subject', 
#     'Duration of Experiment'
# ]

# 4) methods to:
#        return random ISI  within range upto 2 decimal places
#        return unique filename from experiment parameters
def getISI() -> float:
    '''
    Return ISI time within range with upto 2 decimal places of precision
    '''
    return round(isiRange[0] + nrand.random()*(isiRange[1]-isiRange[0]), 2)

# def getOnsetTime() -> float:
#     '''
#     Return Onset time within range with upto 2 decimal places of precision
#     '''
#     return round(onTRange[0] + nrand.random()*(onTRange[1]-onTRange[0]), 2)

makedirs(DATA_DIR, exist_ok=True)

def getFileName(name: str, date: str) -> str:
    '''
    Return unique filename from given subject name and date of experiment
    '''
    return '{}_Pr_{}_Tr_{}_{}'.format(name, pAlpha, tAlpha, date)

# 5) method to return random next letter to be displayed
def getNextLetter(old: str, fixedOld: str, fixedNew: str, choices: Sequence[str]) -> str:
    '''
        Inputs\n
            old (string of length 1): last letter used\n
            fixedOld (string of length 1): trigger letter for target\n
            fixedNew (string of length 1): value to return if
                old == fixedOld\n
            choices (list of single character strings):
                list choices to choose from\n
        Output
            newChar (string of length 1): next character.
                If old == fixedNew returns fixedNew, otherwise\n
                a random one from choices
    '''
    if old == fixedOld:
        return fixedNew

    return nrand.choice(choices)

# 6) method to listen to keypress and log timestamps accordingly,
#   also provide feedback of registered keypress to use subject
#   as a beep sound
# feedback = [False]

# class FeedbackThread(threading.Thread):
#     def __init__(self):
#         threading.Thread.__init__(self)
    
#     def run(self) -> None:
#         while expOn:
#             while (not feedback[0]) and expOn:
#                 pass
#             if expOn:
#                 Beep(500, 200)
#             feedback[0] = False

def listenKeyPredict(key: str, clk: core.Clock) -> None:
    kb = Keyboard(clock=clk)
    while expOn:
        keypress = kb.waitKeys(keyList=[key])
        if keypress[0].name == 'enter':
            break
        ts = keypress[0].rt
        diff = len(targetPresentedTimes)-len(keyPressedTimes)

        if diff > 1:
            keyPressedTimes.extend([-1]*(diff-1))
            diff = 1

        if diff == 1:
            tdiff = ts-targetPresentedTimes[-1]
            if tdiff < (onT+0.1):
                keyPressedTimes.append(ts)
                # feedback[0] = True
            else:
                keyPressedTimes.append(-1)
                diff = 0
        if diff == 0:
            if len(targetPresentedTimes) > 0:
                if ts > (targetPresentedTimes[-1]+onT+0.1):
                    keyPressedTimes.append(ts)
                    # feedback[0] = True
            else:
                keyPressedTimes.append(ts)
                # feedback[0] = True
    kb.stop()

# 7) Custom class to run separate thread to listen to key presses
class KeyThread(threading.Thread):
    def __init__(self, key: str, clk: core.Clock):
        threading.Thread.__init__(self)
        self.key = key
        self.clk = clk

    def run(self) -> None:
        listenKeyPredict(self.key, self.clk)
        
# ===================SETUP DONE======================
#////////////////////////////////////////////////////
# ===============STARTING EXPERIMENT=================

# 1) Get experiment data in seconds from experiment setter and initialize parameters
expDuration = 0
expDialog = gui.DlgFromDict(expData,
                            title='ELL890 Assignment 1',
                            fixed=['Date of Experiment'],
                            tip=['', 'Enter a number if you want to be anonymous',
                             'Enter experiment duration in seconds'])

if expDialog.OK:
    expData['filename'] = getFileName(expData['Name of Subject'], expData['Date of Experiment'])
    expDuration = expData['Duration of Experiment']
else:
    print('Experiment cancelled before starting. Exiting...')
    core.quit()

# 2) start stimulus window and present introduction screen
listenKey = 'space'
introMessage = 'Hello {} ! You will be presented a series of capital english alphabets '.format(expData['Name of Subject'])
introMessage += 'one by one, for a total of {} seconds.\nYour target is to press the "spacebar" on the keyboard '.format(expDuration)
introMessage += 'AT the moment the letter "{}" is shown.\nTry your best to match the timing. The duration '.format(tAlpha)
introMessage += 'for which each letter is shown is short, so be vigilent.\nOnly a single key press of yours will be considered between '
introMessage += 'different instances of the letter "{}".\n DO NOT press the key more than once between each "{}".\n'.format(tAlpha, tAlpha)
introMessage += 'Press "{}" whenever you are ready.\nGOOD LUCK!'.format(listenKey)

win = visual.Window(monitor='testMonitor', size=(1920, 1080))

# show welcome screen
welcomeScreen = visual.TextStim(win,text=introMessage, color=-1, wrapWidth=2.0, height=0.07)
welcomeScreen.draw()
win.flip()
# wait to press space to start experiment
event.waitKeys(keyList=[listenKey])
# set flag and start experiment clock
expOn = True
expClock = core.Clock()

# 3) setup keypress thread object
listenObj = KeyThread(key=listenKey, clk=expClock)
# setup feedback thread
# feedObj = FeedbackThread()

# static periods to time stimulus appearance independent of code execution time
ISI = core.StaticPeriod(screenHz=144, win=win, name='Inter Stimulus Interval')
ONS = core.StaticPeriod(screenHz=144, win=win, name='Onset Time')

# Prepare stimulus for letter presentation
let = visual.TextStim(win, text='', bold=True, height=1.0, color=-1)

# reset clock to start stimulus presentation
# expClock.reset()
# feedObj.start()
listenObj.start()
ISI.start(0.3)
expClock.reset()

while expClock.getTime() <= expDuration:
    # get data for next stimulus
    stim = getNextLetter(old=prevLet, fixedOld=pAlpha, fixedNew=tAlpha, choices=alphaChoices)
    prevLet = stim
    let.text = stim
    let.draw()

    # first let the previous stimulus time end
    ISI.complete()

    # show stimulus
    win.flip()
    # start onset time
    ONS.start(onT)
    # log presented time when target letter is presented
    if stim == tAlpha:
        targetPresentedTimes.append(expClock.getTime())
    # onset complete in fixed time
    ONS.complete()
    # starting stimulus time
    ISI.start(getISI())
    # blank screen
    win.flip()

# end all static periods
ISI.complete()

# stop all threads
expOn = False
listenObj.join()

# keyPressedTimes = keyPressedTimes[:-1]

# 3) Display thank you message
tyMess = 'That was awesome! Thank you very much for your precious time, {}. We appreciate your '.format(expData['Name of Subject'])
tyMess += 'effort to be a part of this experiment. Have a great day ahead!\n'
tyMess += 'One last time, press "{}" to exit.'.format(listenKey)
# show thank you message
welcomeScreen.text = tyMess
welcomeScreen.draw()
win.flip()

print('Key presented times: ')
print(targetPresentedTimes)

print('Key pressed times:')
print(keyPressedTimes)

event.waitKeys(keyList=[listenKey])

win.close()

# ===============ENDING EXPERIMENT=================
# /////////////////////////////////////////////////
# ==================PROCESS DATA===================

diffs = []

for i in range(len(targetPresentedTimes)):
    if keyPressedTimes[i] == -1: # missed this one
        keyPressedTimes[i] = 0
        targetPresentedTimes[i]=7
    diffs.append(round(abs(targetPresentedTimes[i]-keyPressedTimes[i]), 3))

titles = 'Presented time(s),Pressed time(s),Difference(s)\n'

with open(DATA_DIR+'/'+getFileName(expData['Name of Subject'], expData['Date of Experiment'])+'.csv', 'w') as df:
    df.write(titles)
    for i in range(len(targetPresentedTimes)):
        df.write(str(targetPresentedTimes[i])+','+str(keyPressedTimes[i])+','+str(diffs[i])+'\n')

try:
    plt.figure()
    plt.scatter([i for i in range(1, len(targetPresentedTimes)+1)], diffs)
    # plt.plot([i for i in range(1, len(targetPresentedTimes)+1)], diffs, '-')
    plt.ylabel('Difference between keypress and\nactual presentation of stimuli (seconds)')
    plt.xlabel('Trial Number')
    plt.title('Subject response times vs trial number', fontweight='bold')
    plt.grid()
    ax = plt.gca()
    ax.set_xticks([i for i in range(len(targetPresentedTimes)+1)])
    plt.show()
except Exception as e:
    print('An unexpected error occured while plotting! Try plotting manually\n')
    print(e)