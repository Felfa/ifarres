from polaris.utils import set_step, cancel_steps, get_plugin_name


class plugin(object):
    # Loads the text strings from the bots language #
    def __init__(self, bot):
        self.bot = bot
        self.commands = [
            {
                'command': '/test',
                'description': 'test',
                'parameters': [],
            }
        ]
        self.description = "Test"


    # Plugin action #
    def run(self, m):
        self.bot.send_message(m, '¿Cómo te llamas?', extra={'format': 'HTML'})
        set_step(self.bot, m.conversation.id, get_plugin_name(self), 1)


    def steps(self, m, step):
        if step == -1:
            self.bot.send_message(m, 'Vale... :(', extra={'format': 'HTML'})
            cancel_steps(self.bot, m.conversation.id)
        if step == 0:
            self.bot.send_message(m, 'Guay', extra={'format': 'HTML'})
            cancel_steps(self.bot, m.conversation.id)

        elif step == 1:
            self.bot.send_message(m, 'Vale, ahora send nudes, o /cancelar', extra={'format': 'HTML'})
            set_step(self.bot, m.conversation.id, get_plugin_name(self), 2)

        elif step == 2:
            self.bot.send_message(m, '( ͡° ͜ʖ ͡°)', extra={'format': 'HTML'})
            cancel_steps(self.bot, m.conversation.id)
