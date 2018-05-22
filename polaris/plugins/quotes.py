from polaris.utils import get_input, is_command, is_mod, is_trusted
from polaris.types import AutosaveDict
from re import findall, sub, match
from random import randint

class plugin(object):
    # Loads the text strings from the bots language #

    def __init__(self, bot):
        self.bot = bot
        self.commands = self.bot.trans.plugins.pins.commands
        self.description = self.bot.trans.plugins.pins.description
        self.pins = AutosaveDict('polaris/data/%s.pins.json' % self.bot.name)
        self.update_triggers()

    # Plugin action #
    def run(self, m):
        input = get_input(m)

        # List all pins #
        if is_command(self, 1, m.content):
            pins = []
            for pin in self.pins:
                if self.pins[pin].creator == m.sender.id:
                    pins.append(pin)

            if len(pins) > 0:
                text = self.bot.trans.plugins.pins.strings.pins % len(pins)
                for pin in pins:
                    text += '\n • %s' % pin

            else:
                text = self.bot.trans.plugins.pins.strings.no_pins

            # If the message is too long send an error message instead #
            if len(text) < 4096:
                return self.bot.send_message(m, text, extra={'format': 'HTML'})
            else:
                return self.bot.send_message(m, self.bot.trans.errors.unknown, extra={'format': 'HTML'})

        # Add a pin #
        elif is_command(self, 2, m.content):
            if not input:
                return self.bot.send_message(m, self.bot.trans.errors.missing_parameter, extra={'format': 'HTML'})

            input = input.lower()
            input = sub(r'[^\w\ ]','',input)  # Removes every special character.
            input = " ".join(input.split())   # Removes any duplicated whitespace.
            #input = input.split(' ', 1)[0]
            #input = sub(r'[^\w]','',input)

            if not m.reply:
                return self.bot.send_message(m, self.bot.trans.errors.needs_reply, extra={'format': 'HTML'})
                
            if not input:
                return self.bot.send_message(m, self.bot.trans.errors.invalid_parameter, extra={'format': 'HTML'})

            if input in self.pins:
                return self.bot.send_message(m, self.bot.trans.plugins.pins.strings.already_pinned % input, extra={'format': 'HTML'})
                
            if len(input) < 4:
                return self.bot.send_message(m, self.bot.trans.plugins.pins.strings.too_short, extra={'format': 'HTML'})
            
            if input == self.bot.info.first_name.lower():
                return self.bot.send_message(m, self.bot.trans.plugins.pins.strings.illegal_pinname, extra={'format': 'HTML'})

            self.pins[input] = {
                'content': m.reply.content.replace('<','&lt;').replace('>','&gt;'),
                'creator': m.sender.id,
                'type': m.reply.type
            }
            
            self.pins.store_database()
            self.update_triggers()

            return self.bot.send_message(m, self.bot.trans.plugins.pins.strings.pinned % input, extra={'format': 'HTML'})

        # Remove a pin #
        elif is_command(self, 3, m.content):
            if not input:
                return self.bot.send_message(m, self.bot.trans.errors.missing_parameter, extra={'format': 'HTML'})

            input = input.lower()
            input = sub(r'[^\w\ ]','',input)
            input = " ".join(input.split())
            #input = input.split(' ', 1)[0]
            
            print(input)

            if not input in self.pins:
                return self.bot.send_message(m, self.bot.trans.plugins.pins.strings.not_found % input, extra={'format': 'HTML'})

            if not m.sender.id == self.pins[input]['creator']:
                if not is_mod(self.bot, m.sender.id, m.conversation.id):
                    return self.bot.send_message(m, self.bot.trans.plugins.pins.strings.not_creator % input, extra={'format': 'HTML'})
            try:
                del(self.pins[input])
            except KeyErrorException:
                return self.bot.send_message(m, self.bot.trans.errors.unknown, extra={'format': 'HTML'})

            self.pins.store_database()
            self.update_triggers()

            return self.bot.send_message(m, self.bot.trans.plugins.pins.strings.unpinned % input, extra={'format': 'HTML'})

        # Check what pin was triggered #
        else:
            # Finds the first 3 pins of the message and sends them. #
            #pins = findall(r"(\w+)", m.content.lower())
            if  randint(0,4):
                replymessage = False
                pins = m.content.lower()
                #count = 3
                
                # Checks if the message contains a saved pin
                for pin in self.pins:
                    if pins.find(pin) > -1:
                        pinlength = len(pin)
                        textlength = len(pins)
                        foundpin = pins.find(pin)
                        
                        # Found at first position of sent text and checks if it has a non-alphanumerical char next to the matching word
                        if foundpin == 0:
                            if textlength == pinlength:
                                replymessage = True
                            elif textlength > pinlength and match('\W',pins[foundpin + pinlength]):
                                replymessage = True
                                
                        # Ensures that the keyword is between spaces.
                        elif foundpin > 0 and match('\W',pins[foundpin-1]):
                            if foundpin + pinlength == textlength or match('\W',pins[foundpin + pinlength]): # Last or middle word
                                replymessage = True
                            
                        # You can reply with a pin and the message will reply too. #
                        if m.reply:
                            reply = m.reply.id
                        else:
                            reply = m.id

                        if replymessage:
                            self.bot.send_message(m, self.pins[pin]['content'], self.pins[pin]['type'], extra={'format': 'HTML'}) #, reply = reply)
                        #count -= 1

                    #if count == 0:
                    #    return


    def update_triggers(self):
        # Add new triggers #
        for pin, attributes in self.pins.items():
            if not next((i for i,d in enumerate(self.commands) if 'command' in d and d.command == pin), None):
                self.commands.append({
                    'command': pin,
                    'hidden': True
                })

        # Remove unused triggers #
        for command in self.commands:
            if 'hidden' in command and command.hidden and not command.command.lstrip('#') in self.pins:
                self.commands.remove(command)
