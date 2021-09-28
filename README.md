# ELL890 Assignment 1

## Installing requirements

The code runs without any problems in Python version 3.8.10. However, in principle, the Psychopy module supports Python version 3.6.6 and later. So first install a valid Python version. Then

Either run

```shell
pip install -r requirements.txt
```

OR

```shell
pip install psychopy
```

Both work equivalently, the second one being known to install all the required dependencies for the current version of code. This may change in future, however.

## Some general in-code settings

The following settings can be modified with ease in code:

1. `DATA_DIR`: Name of the directory for storing the experiment data for various subjects.
2. `isiRange`: Range of Inter-Stimulus Interval in which it is randomized during run time for each iteration.
3. `onT`: Fixed onset time for each stimulus alphabet on the screen. Note: always keep this value less than the minimum value of the `isiRange`.
4. `percentageSamples`: Percentage of samples in % you want the target alphabet to occur.
5. `percentageFollowed`: If the experiment is chosen to be probabilistic (selected from the dialog box during runtime), this is the percentage of the times the target is presented, that it will follow the particular selected preceeding alphabet denoted by `pAlpha` in code.
6. `removeMissed`: A boolean value that decides whether the times corresponding to missed targets should be saved and be used for the immediate plot after the experiment. Though this is provided for ease of code modification, but it is recommended to keep it at its default `False` so that those missed keypress times are saved along with the valid sample. This is because if once this is lost, it can not be recovered. Instead, it is recommended to keep this values saved and process the data accordingly, later, as per the requirements for the plots or any other purpose.

There may be other possible modifications as well, but those are not purposed to decide the experiment's core functional parameters.
