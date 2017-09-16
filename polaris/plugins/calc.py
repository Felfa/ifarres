from polaris.utils import get_input, send_request

class plugin(object):
    # Loads the text strings from the bots language #
    def __init__(self, bot):
        self.bot = bot
        self.commands = self.bot.trans.plugins.calc.commands
        self.description = self.bot.trans.plugins.calc.description

    # Plugin action #
    def run(self, m):
        input = get_input(m, ignore_reply=False)
        if not input:
            return self.bot.send_message(m, self.bot.trans.errors.missing_parameter, extra={'format': 'HTML'})

        baseurl = 'http://api.mathjs.org/v1/'
        params = {
            'expr': input
        }

        result = send_request(baseurl, params, None, None, None, False, False, True)
        
        print(result)

        if 'Error' in result:
            return self.bot.send_message(m, self.bot.trans.errors.invalid_syntax)
        elif 'Infinity' in result:
            return self.bot.send_message(m, self.bot.trans.plugins.calc.strings.overflow)

        try:
            self.bot.send_message(m, result)

        except Exception as e:
            self.bot.send_alert(e)
