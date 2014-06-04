import os
import imp
import re
import requests


USER = 'sawboo'
# A dictionary of commands and their functions
COMMANDS = {}

# START PLUGIN BULLSHIT
#######################

def getPlugins():
    """
    Find all plugin modules from the ./plugins and add them to [plugins]

    """
    plugins = []
    possibleplugins = os.listdir('./plugins')
    for i in possibleplugins:
        location = os.path.join('./plugins', i)
        if not os.path.isdir(location) or not "plugin.py" in os.listdir(location):
            continue
        info = imp.find_module('plugin', [location])
        plugins.append({"name": i, "info": info})
    return plugins

def loadPlugin(plugin):
    """ Use imp to load a plugin module. """
    return imp.load_module('plugin', *plugin["info"])

# Loop through the list of found plugins, add their commands to the COMMANDS
# dictionary and load each plugin.
for i in getPlugins():
    print("Loading plugin " + i["name"])
    plugin = loadPlugin(i)
    p = plugin.setup()
    # build a dictionary of commands
    for c in p.commands:
        COMMANDS[c] = p.commands[c]

command_regex = re.compile(r'\!(([A-Za-z0-9_-]+)\w?.*$)')
url_regex = re.compile(r"(?:^|\s)((?:https?://)?(?:[a-z0-9.\-]+[.][a-z]{2,4}/?)(?:[^\s()<>]*|\((?:[^\s()<>]+|(?:\([^\s()<>]+\)))*\))+(?:\((?:[^\s()<>]+|(?:\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'\".,<>?]))", flags=re.IGNORECASE|re.DOTALL)
title_regex = re.compile(r'<title(\s+.*?)?>(.*?)</title>', flags=re.IGNORECASE|re.DOTALL)

def check_message(USER, MESSAGE):
    """
    This is where we handle incoming messages and decide what to do with them.

    """
    print '%s: %s' % (USER, MESSAGE)

    # Check if the message contains a url.
    urls = re.findall(url_regex, MESSAGE)

    # If a url is found, append the custom !url command to the message.
    if urls:
        MESSAGE = '!url ' + MESSAGE

    # Check if the sent message was a command.
    get_command = re.match(command_regex, MESSAGE)
    if get_command:
        # A command was found, lets send the message to the proper plugin.
        command = re.findall(command_regex, MESSAGE)
        c = command[0][1]
        COMMANDS[c](USER, MESSAGE)

check_message('sawboo', '!random 1000')
check_message('sawboo', '!random 10')
check_message('sawboo', 'https://stackoverflow.com/ there you go')
check_message('sawboo', '!weather')

