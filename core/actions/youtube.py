import os
from core.settings import *
import logging
logging.basicConfig(filename=os.path.join(LOG_PATH, LOG_FILE),level=logging.DEBUG)
logger = logging.getLogger(__name__)

from core.providers.youtube import Youtube

def youtubeMenu(params=[]):
    page = "0"
    text = ""
    logger.debug("params: %s" % str(params))
    if type(params) is list:
        for element in params:
            logger.debug("ele %s" % str(element))
            if "page" in element:
                logger.debug("%s" % str(element))
                page = element["page"]
                logger.debug("target page %s" % (page))
            if "text" in element:
                logger.debug("%s" % str(element))
                text = element["text"]
                logger.debug("target search text is %s" % (text))
    if len(text) == 0:
        channels = Youtube.getChannels(page)
    else: #search
        channels = Youtube.search(text)
    logger.debug("found %s channels" % str(len(channels)))
    menu = []
    #now put in a list...
    for channel in channels:
        name = channel["title"]
        element = {}
        if 'finalLink' not in channel:
            element["title"] = "%s" % (name)
            element["action"] = "function"
            element["external"] = 'youtubeMenu'
            element["params"] = [{
                'page': channel["page"]
            }]
            menu.append(element)
        else:
            element["title"] = "%s" % (name)
            element["action"] = "command"
            element["external"] =  "youtube-dl -o - '%s' | mplayer -vf scale=320:240 -" % channel["page"]
            #element["external"] =  "omxplayer -o alsa $(youtube-dl -g -f 'best[height<=360]' %s)" % channel["page"]
            menu.append(element)

    #search
    if page == "0":
        element = {}
        element["title"] = "Search"
        element["action"] = 'function-text'
        element["external"] = 'youtubeMenu'
        menu.append(element)

    #back
    element = {}
    element["title"] = "Back"
    element["action"] = 'menu'
    element["external"] = 'program'
    menu.append(element)
    return menu
