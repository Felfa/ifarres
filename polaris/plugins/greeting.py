from random import randint

class plugin(object):
    # Loads the text strings from the bots language #
    def __init__(self, bot):
        self.bot = bot
        self.commands = self.bot.trans.plugins.greeting.commands
        self.strings = self.bot.trans.plugins.greeting.strings

    # Plugin action #
    def run(self, m):
        i = randint(0, len(self.strings) - 1)
        
        # NOTE: Only for Arate translation #
        if i < 2:
            text = self.strings[i] % self.bot.info.first_name
            if not i:
                # If it's the first quote, reverse and capitalize
                text = text[::-1].capitalize()
        elif i < 4:
            text = self.strings[i] % (self.bot.info.first_name, self.bot.info.first_name)
        else:
            text = self.strings[i]
        #                                  #

        self.bot.send_message(m, text)
