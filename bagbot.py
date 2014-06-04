import sys
import re
import os
import imp
from settings import HOST, PORT, CHANNEL, NICKNAME, REALNAME, PASSWORD, PLUGINS
from twisted.words.protocols import irc
from twisted.internet import defer
from twisted.internet import protocol
from twisted.internet import reactor
from twisted.internet import task
from twisted.python import log

path = os.path.dirname(os.path.realpath(sys.argv[0])) + '\plugins'

log.startLogging(sys.stdout)

class BagBot(irc.IRCClient):

    password = PASSWORD
    # This is a regex to split the user nick, ident, and hostname
    user_regex = re.compile(r'^(.*?)!(.*?)@(.*?)$')

    command_regex = re.compile(r'\!(([A-Za-z0-9_-]+)\w?.*$)')
    url_regex = re.compile(r"(?:^|\s)((?:https?://)?(?:[a-z0-9.\-]+[.][a-z]{2,4}/?)(?:[^\s()<>]*|\((?:[^\s()<>]+|(?:\([^\s()<>]+\)))*\))+(?:\((?:[^\s()<>]+|(?:\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'\".,<>?]))", flags=re.IGNORECASE|re.DOTALL)

    def __init__(self, *args, **kwargs):
        self._namescallback = {}

    # Get the current nickname
    def _get_nickname(self):
        return self.factory.nickname
    nickname = property(_get_nickname)

    COMMANDS = {}
    plugins = []

    def getPlugins(self):
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

    def loadPlugin(self, plugin):
        """ Use imp to load a plugin module. """
        return imp.load_module('plugin', *plugin["info"])

    def signedOn(self):
        """ This is called when connecting to a channel. """
        self.join(self.factory.channel)
        log.msg("> Signed on as %s." % (self.nickname,))
        # Loop through the list of found plugins, add their commands to the COMMANDS
        # dictionary and load each plugin.
        for i in self.getPlugins():
            print("Loading plugin " + i["name"])
            plugin = self.loadPlugin(i)
            p = plugin.setup()
            # build a dictionary of commands
            for c in p.commands:
                self.COMMANDS[c] = p.commands[c]

    def joined(self, channel):
        """This is called when connecting to a channel."""
        log.msg("> %s has joined %s" % (self.nickname, self.factory.channel))
        # Let's see who is connected to the chat currently.
        # self.names(self.factory.channel).addCallback(self.got_names)


    def privmsg(self, user, channel, msg):
        """ This is called when a message is sent in the channel. """

        # Break the user up into usable groups.
        user = re.match(self.user_regex, user)
        # print user.group(1)

        # Log the message.
        log.msg("%s: %s" % (user.group(1), msg))

        # Check if the message contains a url.
        urls = re.findall(self.url_regex, msg)

        # If a url is found, append the custom !url command to the message.
        if urls:
            msg = '!url ' + msg

        # Check if the sent message was a command.
        get_command = re.match(self.command_regex, msg)
        if get_command:
            # A command was found, lets send the message to the proper plugin.
            command = re.findall(self.command_regex, msg)
            c = command[0][1]
            self.COMMANDS[c](self, user.group(1), msg)


    def names(self, channel):
        channel = channel.lower()
        d = defer.Deferred()

        if channel not in self._namescallback:
            self._namescallback[channel] = ([], [])

        self._namescallback[channel][0].append(d)
        self.sendLine("NAMES %s" % channel)
        return d

    def irc_RPL_NAMREPLY(self, prefix, params):
        """ This method handles the reply from the /NAMES command. """
        channel = params[2].lower()
        nicklist = params[3].split(' ')

        if channel not in self._namescallback:
            return

        log.msg('> Querying /NAMES')
        n = self._namescallback[channel][1]
        n += nicklist

    def irc_RPL_ENDOFNAMES(self, prefix, params):
        """This method is called after running the /NAMES command."""
        channel = params[1].lower()
        if channel not in self._namescallback:
            return
        callbacks, namelist = self._namescallback[channel]
        for cb in callbacks:
            cb.callback(namelist)
        log.msg('> viewers.txt successfully updated.')
        del self._namescallback[channel]


    def got_names(self, nicklist):
        """This is just some bullshit"""
        log.msg(nicklist)
        f = open('viewers.txt', 'r+')
        f.seek(0)
        for i in nicklist:
            f.write(i + '\n')
        f.close()


class BagBotFactory(protocol.ClientFactory):
    protocol = BagBot
    plugins = []

    def __init__(self, channel, plugins=[]):
        self.host = HOST
        self.password = PASSWORD
        self.channel = CHANNEL
        self.nickname = NICKNAME
        self.realname = REALNAME
        self.viewers = []
        self.plugins = plugins

    def clientConnectionLost(self, connector, reason):
        """Handle dropped connections to the irc server."""
        log.msg("Lost connection (%s), reconnecting." % (reason,))
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        log.msg("Could not connect: %s" % (reason,))


if __name__ == "__main__":
    reactor.connectTCP(HOST, PORT, BagBotFactory(CHANNEL, PLUGINS))
    reactor.run()