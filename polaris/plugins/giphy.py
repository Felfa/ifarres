from polaris.utils import get_input, send_request, download
from random import randint

class plugin(object):
    # Loads the text strings from the bots language #
    def __init__(self, bot):
        self.bot = bot
        self.commands = self.bot.trans.plugins.giphy.commands
        self.description = self.bot.trans.plugins.giphy.description

    # Plugin action #
    def run(self, m):
        input = get_input(m, ignore_reply=False)
        if not input:
            return self.bot.send_message(m, self.bot.trans.errors.missing_parameter, extra={'format': 'HTML'})

        baseurl = 'http://api.giphy.com/v1/gifs/search'
        params = {
            'api_key': self.bot.config.api_keys.giphy,
            'q': input
        }

        data = send_request(baseurl, params)

        if not data or 'error' in data:
            return self.bot.send_message(m, self.bot.trans.errors.connection_error)

        if data.pagination.total_count == 0:
            return self.bot.send_message(m, self.bot.trans.errors.no_results)

        try:
            i = randint(0, len(data['data']) - 1)
            gif_url = data['data'][i]['images']['original']['url']

        except Exception as e:
            self.bot.send_alert(e)
            gif_url = None

        if gif_url:
            return self.bot.send_message(m, gif_url, 'document')
        else:
            return self.bot.send_message(m, self.bot.trans.errors.download_failed)
