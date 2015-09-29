from __main__ import *
from utilies import *

triggers = {
	'^/run ',
	'^/reload',
	'^/msg ',
	'^/stop',
}

def action(msg):			
	input = get_input(msg.text)
	
	message = config.locale.errors['argument']
	
	if msg.from_user.id not in config.admins:
		return core.send_message(msg.chat.id, config.locale.errors['permission'])
	
	if msg.text.startswith('/run'):
		message = subprocess.check_output(input, shell=True)
		
	elif msg.text.startswith('/reload'):
		reload(config)
		bot_init()
		
		message = 'Bot reloaded!'
		
	elif msg.text.startswith('/msg'):
		chat_id = first_word(input)
		text = get_input(input)
		
		if not core.send_message(chat_id, text):
			return core.send_message(msg.chat.id, config.locale.errors['argument'], parse_mode="Markdown")
		return
			
	elif msg.text.startswith('/stop'):
		is_started = False
		message = 'Shutting down...'
		
	core.send_message(msg.chat.id, message, parse_mode="Markdown")

plugin = {
    'triggers': triggers,
    'action': action,
    'typing': None,
}