from polaris.utils import get_input, is_command, first_word, all_but_first_word, is_mod, is_trusted, is_int, set_step, cancel_steps, get_plugin_name
from polaris.types import AutosaveDict
from re import findall

class plugin(object):
    # Loads the text strings from the bots language #

    def __init__(self, bot):
        self.bot = bot
        self.commands = self.bot.trans.plugins.administration.commands
        self.description = self.bot.trans.plugins.administration.description
        self.administration = AutosaveDict('polaris/data/%s.administration.json' % self.bot.name)
        self.groups = AutosaveDict('polaris/data/%s.groups.json' % self.bot.name)
        self.users = AutosaveDict('polaris/data/%s.users.json' % self.bot.name)

    # Plugin action #
    def run(self, m):
        input = get_input(m)
        uid = str(m.sender.id)
        gid = str(m.conversation.id)

        # List all administration commands. #
        if is_command(self, 1, m.content):
            text = self.bot.trans.plugins.administration.strings.commands
            for command in self.commands:
                # Adds the command and parameters#
                if command['command'] == '^new_chat_member$':
                    text += '\n • ' + self.bot.trans.plugins.administration.strings.new_chat_member
                else:
                    text += '\n • ' + command['command'].replace('/', self.bot.config.prefix)

                if 'parameters' in command:
                    for parameter in command['parameters']:
                        name, required = list(parameter.items())[0]
                        # Bold for required parameters, and italic for optional #
                        if required:
                            text += ' <b>&lt;%s&gt;</b>' % name
                        else:
                            text += ' [%s]' % name

                if 'description' in command:
                    text += '\n   <i>%s</i>' % command['description']
                else:
                    text += '\n   <i>?¿</i>'

            return self.bot.send_message(m, text, extra={'format': 'HTML'})

        # List all groups. #
        if is_command(self, 2, m.content):
            text = self.bot.trans.plugins.administration.strings.groups
            i = 1
            for gid, attr in self.administration.items():
                text += '\n %s. %s (%s)' % (i, self.groups[gid]['title'], attr['alias'])
                i += 1
            return self.bot.send_message(m, text, extra={'format': 'HTML'})
        
        # Send message to another group. #
        if is_command(self, 10, m.content):
            input = get_input(m, ignore_reply=False)
            if not input:
                return self.bot.send_message(m, self.bot.trans.errors.missing_parameter, extra={'format': 'HTML'})
                
            id_backup = m.conversation.id
            group_number = int(findall(r"(\w+)", m.content)[1])
            msg_offset = len(str(group_number)) + 1
            text = input[msg_offset:]
            
            if text and is_int(group_number):
                m.conversation.id = 0
                for gid, attr in self.administration.items():
                    if group_number == 1:
                        m.conversation.id = int(gid)
                    group_number -= 1
                        
                if m.conversation.id != id_backup and m.conversation.id != 0:
                    text = self.bot.trans.plugins.administration.strings.message_received % m.conversation.title + text
                    return self.bot.send_message(m, text, extra={'format': 'HTML'})
                    #return self.bot.send_message(m, self.bot.trans.plugins.administration.strings.sent, extra={'format': 'HTML'})
                elif m.conversation.id == id_backup:
                    return self.bot.send_message(m, self.bot.trans.plugins.administration.strings.no_echo, extra={'format': 'HTML'})
                else:
                    m.conversation.id = id_backup
                    return self.bot.send_message(m, self.bot.trans.errors.send_error, extra={'format': 'HTML'})
            else:
                return self.bot.send_message(m, self.bot.trans.plugins.administration.strings.invalid_syntax, extra={'format': 'HTML'})

        # Join a group. #
        elif is_command(self, 3, m.content):
            if not input:
                return self.bot.send_message(m, self.bot.trans.errors.missing_parameter, extra={'format': 'HTML'})

            for id in self.administration:
                if (input in self.administration or
                    input in self.administration[id]['alias'] or
                    input in self.groups[id]['title']):
                    gid_to_join = id
                    break

            if not gid_to_join in self.administration:
                return self.bot.send_message(m, self.bot.trans.plugins.administration.strings.not_added % m.conversation.title, extra={'format': 'HTML'})

            text = '<b>%s</b>\n<i>%s</i>\n\n%s' % (self.groups[gid_to_join]['title'], self.administration[gid_to_join]['description'], self.bot.trans.plugins.administration.strings.rules)
            i = 1
            for rule in self.administration[gid_to_join]['rules']:
                text += '\n %s. <i>%s</i>' % (i, rule)
                i += 1
            if not self.administration[gid_to_join]['rules']:
                text += '\n%s' % self.bot.trans.plugins.administration.strings.norules
            if not self.administration[gid_to_join]['link']:
                text += '\n\n%s' % self.bot.trans.plugins.administration.strings.nolink
            else:
                text += '\n\n<a href="%s">%s</a>' % (self.administration[gid_to_join]['link'], self.bot.trans.plugins.administration.strings.join)
            return self.bot.send_message(m, text, extra={'format': 'HTML', 'preview': False})

        # Information about a group. #
        elif is_command(self, 4, m.content) or is_command(self, 9, m.content):
            if m.conversation.id > 0:
                return self.bot.send_message(m, self.bot.trans.errors.group_only, extra={'format': 'HTML'})
            if not gid in self.administration:
                if is_command(self, 4, m.content):
                    return self.bot.send_message(m, self.bot.trans.plugins.administration.strings.not_added % m.conversation.title, extra={'format': 'HTML'})
                elif is_command(self, 9, m.content):
                    return

            text = '<b>%s</b>\n<i>%s</i>\n\n%s' % (self.groups[gid]['title'], self.administration[gid]['description'], self.bot.trans.plugins.administration.strings.rules)
            i = 1
            for rule in self.administration[gid]['rules']:
                text += '\n %s. <i>%s</i>' % (i, rule)
                i += 1

            if not self.administration[gid]['rules']:
                text += '\n%s' % self.bot.trans.plugins.administration.strings.norules
            if is_command(self, 4, m.content):
                if not self.administration[gid]['link']:
                    text += '\n\n%s' % self.bot.trans.plugins.administration.strings.nolink
                else:
                    text += '\n\n<a href="%s">%s</a>' % (self.bot.trans.plugins.administration.strings.join.self.administration[gid]['link'])
            return self.bot.send_message(m, text, extra={'format': 'HTML', 'preview': False})

        # Rules of a group. #
        elif is_command(self, 5, m.content):
            if m.conversation.id > 0:
                return self.bot.send_message(m, self.bot.trans.errors.group_only, extra={'format': 'HTML'})
            if not gid in self.administration:
                return self.bot.send_message(m, self.bot.trans.plugins.administration.strings.not_added % m.conversation.title, extra={'format': 'HTML'})

            if input and is_int(input):
                try:
                    i = int(input)
                    text = '%s. <i>%s</i>' % (i, self.administration[gid]['rules'][i - 1])
                except:
                    text = self.bot.trans.plugins.administration.strings.notfound

            else:
                text = self.bot.trans.plugins.administration.strings.rules
                i = 1
                for rule in self.administration[gid]['rules']:
                    text += '\n %s. <i>%s</i>' % (i, rule)
                    i += 1

            if not self.administration[gid]['rules']:
                text += '\n%s' % self.bot.trans.plugins.administration.strings.norules
            return self.bot.send_message(m, text, extra={'format': 'HTML', 'preview': False})

        # Kicks a user. #
        elif is_command(self, 6, m.content):
            if m.conversation.id > 0:
                return self.bot.send_message(m, self.bot.trans.errors.group_only, extra={'format': 'HTML'})

            if not is_mod(self.bot, m.sender.id, m.conversation.id):
                return self.bot.send_message(m, self.bot.trans.errors.permission_required, extra={'format': 'HTML'})

            if not input and not m.reply:
                return self.bot.send_message(m, self.bot.trans.errors.missing_parameter, extra={'format': 'HTML'})

            if m.reply:
                target = m.reply.sender.id
            elif input:
                target = input
            else:
                target = m.sender.id

            res = self.bot.kick_user(m, target)
            self.bot.unban_user(m, target)
            if res is None:
                return self.bot.send_message(m, self.bot.trans.errors.admin_required, extra={'format': 'HTML'})
            elif not res:
                return self.bot.send_message(m, self.bot.trans.errors.failed, extra={'format': 'HTML'})
            else:
                return self.bot.send_message(m, '<pre>An enemy has been slain.</pre>', extra={'format': 'HTML'})

            return self.bot.send_message(m, self.bot.trans.errors.unknown, extra={'format': 'HTML'})

        # Bans a user. #
        elif is_command(self, 7, m.content):
            if m.conversation.id > 0:
                return self.bot.send_message(m, self.bot.trans.errors.group_only, extra={'format': 'HTML'})

            if not is_mod(self.bot, m.sender.id, m.conversation.id):
                return self.bot.send_message(m, self.bot.trans.errors.permission_required, extra={'format': 'HTML'})

            if not input:
                return self.bot.send_message(m, self.bot.trans.errors.missing_parameter, extra={'format': 'HTML'})

            return self.bot.send_message(m, self.bot.trans.errors.unknown, extra={'format': 'HTML'})

        # Configures a group. #
        elif is_command(self, 8, m.content):
            if m.conversation.id > 0:
                return self.bot.send_message(m, self.bot.trans.errors.group_only, extra={'format': 'HTML'})

            if not is_mod(self.bot, m.sender.id, m.conversation.id):
                return self.bot.send_message(m, self.bot.trans.errors.permission_required, extra={'format': 'HTML'})

            if not input:
                self.bot.send_message(m, self.bot.trans.plugins.administration.strings.ask_to_add % m.conversation.title, extra={'format': 'HTML', 'force_reply': True})
                if not gid in self.administration:
                    self.administration[gid] = {
                        'alias': None,
                        'description': None,
                        'link': None,
                        'rules': []
                    }
                    self.administration.store_database()
                set_step(self.bot, m.conversation.id, get_plugin_name(self), 1)
            else:
                if first_word(input) == 'add':
                    if not gid in self.administration:
                        self.administration[gid] = {
                            'alias': None,
                            'description': None,
                            'link': None,
                            'rules': []
                        }
                        self.administration.store_database()
                        return self.bot.send_message(m, self.bot.trans.plugins.administration.strings.added % m.conversation.title, extra={'format': 'HTML'})
                    else:
                        return self.bot.send_message(m, self.bot.trans.plugins.administration.strings.already_added % m.conversation.title, extra={'format': 'HTML'})

                elif first_word(input) == 'remove':
                    if gid in self.administration:
                        del(self.administration[gid])
                        self.administration.store_database()
                        return self.bot.send_message(m, self.bot.trans.plugins.administration.strings.removed % m.conversation.title, extra={'format': 'HTML'})
                    else:
                        return self.bot.send_message(m, self.bot.trans.plugins.administration.strings.not_added % m.conversation.title, extra={'format': 'HTML'})

                elif first_word(input) == 'alias':
                    if gid in self.administration:
                        self.administration[gid]['alias'] = all_but_first_word(input)
                        self.administration.store_database()
                        return self.bot.send_message(m, self.bot.trans.plugins.administration.strings.set % m.conversation.title, extra={'format': 'HTML'})
                    else:
                        return self.bot.send_message(m, self.bot.trans.plugins.administration.strings.not_added % m.conversation.title, extra={'format': 'HTML'})

                elif first_word(input) == 'motd':
                    if gid in self.administration:
                        self.administration[gid]['description'] = all_but_first_word(input)
                        self.administration.store_database()
                        return self.bot.send_message(m, self.bot.trans.plugins.administration.strings.set % m.conversation.title, extra={'format': 'HTML'})
                    else:
                        return self.bot.send_message(m, self.bot.trans.plugins.administration.strings.not_added % m.conversation.title, extra={'format': 'HTML'})

                elif first_word(input) == 'link':
                    if gid in self.administration:
                        self.administration[gid]['link'] = all_but_first_word(input)
                        self.administration.store_database()
                        return self.bot.send_message(m, self.bot.trans.plugins.administration.strings.set % m.conversation.title, extra={'format': 'HTML'})
                    else:
                        return self.bot.send_message(m, self.bot.trans.plugins.administration.strings.not_added % m.conversation.title, extra={'format': 'HTML'})

                elif first_word(input) == 'rules':
                    if gid in self.administration:
                        self.administration[gid]['rules'] = all_but_first_word(input).split('\n')[0:]
                        self.administration.store_database()
                        return self.bot.send_message(m, self.bot.trans.plugins.administration.strings.set % m.conversation.title, extra={'format': 'HTML'})
                    else:
                        return self.bot.send_message(m, self.bot.trans.plugins.administration.strings.not_added % m.conversation.title, extra={'format': 'HTML'})

                elif first_word(input) == 'rule':
                    if gid in self.administration:
                        try:
                            i = int(first_word(all_but_first_word(input)))-1
                            if i > len(self.administration[gid]['rules']):
                                i = len(self.administration[gid]['rules'])
                            elif i < 1:
                                i = 0
                        except:
                            return self.bot.send_message(m, self.bot.trans.errors.unknown, extra={'format': 'HTML'})
                        self.administration[gid]['rules'].insert(i, all_but_first_word(all_but_first_word(input)))
                        self.administration.store_database()
                        return self.bot.send_message(m, self.bot.trans.plugins.administration.strings.set % m.conversation.title, extra={'format': 'HTML'})
                    else:
                        return self.bot.send_message(m, self.bot.trans.plugins.administration.strings.not_added % m.conversation.title, extra={'format': 'HTML'})


                else:
                    return self.bot.send_message(m, self.bot.trans.errors.no_results, extra={'format': 'HTML'})


    def always(self, m):
        if str(m.sender.id).startswith('-100'):
            return

        # Update group data #
        gid = str(m.conversation.id)
        if m.conversation.id < 0:
            if gid in self.groups:
                self.groups[gid].title = m.conversation.title
                self.groups[gid].messages += 1

            else:
                self.groups[gid] = {
                    "title": m.conversation.title,
                    "messages": 1
                }

        # Update user data #
        uid = str(m.sender.id)
        if uid in self.users:
            self.users[uid].first_name = m.sender.first_name
            if hasattr(m.sender, 'last_name'):
                self.users[uid].last_name = m.sender.last_name
            if hasattr(m.sender, 'username'):
                self.users[uid].username = m.sender.username
            self.users[uid].messages += 1

        else:
            self.users[uid] = {
                "first_name": m.sender.first_name,
                "last_name": m.sender.last_name,
                "username": m.sender.username,
                "messages": 1
            }

        # Update group id when upgraded to supergroup #
        if m.type == 'notification' and m.content == 'upgrade_to_supergroup':
            to_id = str(m.extra['chat_id'])
            from_id = str(m.extra['from_chat_id'])
            if from_id in self.administration:
                self.administration[to_id] = self.administration.pop(from_id)
            self.groups[to_id] = self.groups.pop(from_id)

        self.administration.store_database()
        self.groups.store_database()
        self.users.store_database()


    def steps(self, m, step):
        gid = str(m.conversation.id)

        if step == -1:
            self.bot.send_message(m, self.bot.trans.plugins.administration.strings.cancel % m.conversation.title, extra={'format': 'HTML'})
            cancel_steps(self.bot, m.conversation.id)

        if step == 0:
            self.bot.send_message(m, self.bot.trans.plugins.administration.strings.done % m.conversation.title, extra={'format': 'HTML'})
            cancel_steps(self.bot, m.conversation.id)

        elif step == 1:
            if self.bot.trans.plugins.administration.strings.yes.lower() in m.content.lower():
                set_step(self.bot, m.conversation.id, get_plugin_name(self), 2)
                if not m.content.startswith('/cancelar') and not m.content.startswith('/aceptar'):
                    self.bot.send_message(m, self.bot.trans.plugins.administration.strings.ask_link % m.conversation.title, extra={'format': 'HTML', 'force_reply': True})

            else:
                cancel_steps(self.bot, m.conversation.id)
                self.bot.send_message(m, self.bot.trans.errors.unknown, extra={'format': 'HTML'})

        elif step == 2:
            set_step(self.bot, m.conversation.id, get_plugin_name(self), 3)
            if not m.content.startswith('/cancelar') and not m.content.startswith('/aceptar'):
                self.administration[gid]['link'] = m.content
                self.bot.send_message(m, self.bot.trans.plugins.administration.strings.ask_alias % m.conversation.title, extra={'format': 'HTML', 'force_reply': True})

        elif step == 3:
            set_step(self.bot, m.conversation.id, get_plugin_name(self), 4)
            if not m.content.startswith('/cancelar') and not m.content.startswith('/aceptar'):
                self.administration[gid]['alias'] = m.content.lower()
                self.bot.send_message(m, self.bot.trans.plugins.administration.strings.ask_rules % m.conversation.title, extra={'format': 'HTML', 'force_reply': True})

        elif step == 4:
            set_step(self.bot, m.conversation.id, get_plugin_name(self), 5)
            if not m.content.startswith('/cancelar') and not m.content.startswith('/aceptar'):
                self.administration[gid]['rules'] = m.content.split('\n')
                self.bot.send_message(m, self.bot.trans.plugins.administration.strings.ask_motd % m.conversation.title, extra={'format': 'HTML', 'force_reply': True})

        elif step == 5:
            set_step(self.bot, m.conversation.id, get_plugin_name(self), -1)
            if not m.content.startswith('/cancelar') and not m.content.startswith('/aceptar'):
                self.administration[gid]['motd'] = m.content
