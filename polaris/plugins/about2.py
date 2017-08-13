from polaris.utils import get_input
from polaris.types import AutosaveDict
import subprocess


class plugin(object):
    # Loads the text strings from the bots language #
    def __init__(self, bot):
        self.bot = bot
        self.commands = self.bot.trans.plugins.start.commands

    # Plugin action #
    def run(self, m):
        greeting = self.bot.trans.plugins.start.strings.greeting % self.bot.info.first_name
        self.bot.send_message(m, greeting, extra={'format': 'HTML'})
