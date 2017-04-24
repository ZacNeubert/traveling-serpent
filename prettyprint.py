class bcolors:
        HEADER = '\033[95m'
        OKBLUE = '\033[94m'
        OKGREEN = '\033[92m'
        WARNING = '\033[93m'
        FAIL = '\033[91m'
        ENDC = '\033[0m'
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'

def printRed(string):
        print(bcolors.FAIL + string + bcolors.ENDC)

def printYellow(string):
        print(bcolors.WARNING + string + bcolors.ENDC)

def printGreen(string):
        print(bcolors.OKGREEN + string + bcolors.ENDC)

def asRed(string):
        return bcolors.FAIL + string + bcolors.ENDC

def asYellow(string):
        return bcolors.WARNING + string + bcolors.ENDC

def asGreen(string):
        return bcolors.OKGREEN + string + bcolors.ENDC

def asBlue(string):
        return bcolors.OKBLUE + string + bcolors.ENDC

def printhl(string, val):
        if val > 0.0:
                printGreen(string)
        else:
                printRed(string)
