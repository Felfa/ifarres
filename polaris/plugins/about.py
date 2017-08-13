from polaris.utils import get_input
from polaris.types import AutosaveDict
import subprocess


class plugin(object):
    # Loads the text strings from the bots language #
    def __init__(self, bot):
        self.bot = bot
        self.commands = self.bot.trans.plugins.about.commands
        self.description = self.bot.trans.plugins.about.description

    # Plugin action #
    def run(self, m):
        groups = AutosaveDict('polaris/data/%s.groups.json' % self.bot.name)
        users = AutosaveDict('polaris/data/%s.users.json' % self.bot.name)

        tag = subprocess.check_output(['git', 'describe', '--tags']).decode('ascii').rstrip('\n')

        greeting = self.bot.trans.plugins.about.strings.greeting % self.bot.info.first_name
        version = self.bot.trans.plugins.about.strings.version % (tag)
        # license = self.bot.trans.plugins.about.strings.license
        help = self.bot.trans.plugins.about.strings.help % self.bot.config.prefix
        stats = self.bot.trans.plugins.about.strings.stats % (len(users), len(groups))

        text = '%s\n\n%s\n\n%s\n\n%s' % (greeting, help, version, stats)

        self.bot.send_message(m, text, extra={'format': 'HTML'})
