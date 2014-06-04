import re
import requests

url_regex = re.compile(r"(?:^|\s)((?:https?://)?(?:[a-z0-9.\-]+[.][a-z]{2,4}/?)(?:[^\s()<>]*|\((?:[^\s()<>]+|(?:\([^\s()<>]+\)))*\))+(?:\((?:[^\s()<>]+|(?:\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'\".,<>?]))", flags=re.IGNORECASE|re.DOTALL)
title_regex = re.compile(r'<title(\s+.*?)?>(.*?)</title>', flags=re.IGNORECASE|re.DOTALL)

class UrlPlugin(object):
    title = 'Url Plugin'

    def get_url_title(bagbot, user, message):
        # Check if the message is a url.
        # Find every URL within the message.
        urls = re.findall(url_regex, message)

        # Loop through the URLs, and make them valid.
        for url in urls:
            if url[:7].lower() != "http://" and url[:8].lower() != "https://":
                url = "http://" + url
                # Use requests to get the page content.
            try:
                r = requests.get(url)
                # check for a valid response
                if r.status_code:
                    title = re.search(title_regex, r.content)
                    if title:
                        if len(title.group(2).strip()) > 0:
                            title = re.sub('\s+', ' ', title.group(2)).strip()
                        # Send the page title to the chat.
                        bagbot.msg(bagbot.factory.channel, '%s' % title)
            except: pass

    commands = {
        "url": get_url_title,
        }



def setup():
    return UrlPlugin()
