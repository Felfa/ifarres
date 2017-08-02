from polaris.utils import get_input
from subprocess import call
from random import randint


class plugin(object):
    # Loads the text strings from the bots language #
    def __init__(self, bot):
        self.bot = bot
        self.commands = self.bot.trans.plugins.mapgen.commands
        self.description = self.bot.trans.plugins.mapgen.description

    # Plugin action #
    def run(self, m):
        call(["python2", "polaris/mapscript.py", "-x",str(randint(-8192,8191)),"-y",str(randint(-8192,8191))])
        
        return self.bot.send_message(m, '/tmp/out.png', 'photo')
