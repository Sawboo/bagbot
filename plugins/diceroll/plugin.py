import random

class DiceRollPlugin(object):
    title = 'Dice Roll'

    def roll_dice(user, message):
        n = message.split()
        try:
            roll = random.randrange(1, int(n[1]))
        except:
            roll = random.randrange(1, 100)
        print "> %s rolled %s!" % (user, roll)

    commands = {
        "random": roll_dice,
        "roll": roll_dice,
        "r": roll_dice
        }



def setup():
    return DiceRollPlugin()