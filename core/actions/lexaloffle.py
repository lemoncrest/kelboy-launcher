import os
import re
import urllib3
from core.decoder import Decoder
from core.settings import *
import logging
logging.basicConfig(filename=os.path.join(LOG_PATH, LOG_FILE),level=logging.DEBUG)
logger = logging.getLogger(__name__)

def getCatalogMenu(params=[]):
    page=1
    if type(params) is list:
        logger.debug("page")
        for element in params:
            logger.debug("page %s" % str(element))
            if "page" in element:
                page = element["page"]
    #/bbs/cposts/sc/
    http = urllib3.PoolManager()
    url = "https://www.lexaloffle.com/bbs/lister.php?use_hurl=1&cat=7&sub=2&page=%s&mode=carts&orderby=featured" % page
    logger.debug("lexaoffle url is: %s" % url)
    r = http.request('GET', url, preload_content=False)
    html = r.data.decode()
    bruteCards = Decoder.extract('pdat=[','];',html)
    cards = []
    if page>1:
        element = {}
        element["title"] = "next p. %s" % (int(page)-1)
        element["action"] = "function"
        element["external"] = 'getCatalogMenu'
        element["params"] = [{
            'page': int(page)-1
        }]
        cards.append(element)
    for bruteCardLine in bruteCards.split(",``],"):
        logger.debug("line is %s" % bruteCardLine)
        if '[' in bruteCardLine:
            element = {}
            bruteCardLine = bruteCardLine[:bruteCardLine.find('],')]
            name = Decoder.extract(', `','`,',bruteCardLine)
            id = Decoder.extract("['","'",bruteCardLine)
            link = 'https://www.lexaloffle.com/bbs/get_cart.php?cat=7&play_src=0&lid=%s' % id
            out = re.sub('[^A-Za-z0-9.\-,\ ]+', '', name)+".p8.png"
            out = ROMS_PATH + "/pico8/" + out
            command = 'curl "%s" --create-dirs --output "%s" \n' %(link,out)
            element["external"] = command
            element["action"] = 'command-exit'
            element["title"] = name
            cards.append(element)
    #next page
    if len(cards)>0:
        element = {}
        element["title"] = "next p. %s" % (int(page)+1)
        element["action"] = "function"
        element["external"] = 'getCatalogMenu'
        element["params"] = [{
            'page': int(page)+1
        }]
        cards.append(element)
    element = {}
    element["title"] = "Search"
    element["action"] = 'function-text'
    element["external"] = 'getCatalogSearchMenu'
    element["params"] = [{'webpage':link, 'final': False}]
    #TODO append getCatalogSearchMenu search
    cards.append(element)
    #back
    element = {}
    element["title"] = "Back"
    if int(page) != 1:
        element["action"] = 'function'
        element["external"] = 'getCatalogMenu'
    else:
        element["action"] = 'menu'
        element["external"] = 'webpages'
    cards.append(element)
    return cards

def getCatalogSearchMenu(params=[]):
    text = ""
    page=1
    if type(params) is list:
        logger.debug("text")
        for element in params:
            logger.debug("text %s" % str(element))
            if "text" in element:
                text = element["text"]
            if "page" in element:
                page = element["page"]
    url = 'https://www.lexaloffle.com/bbs/lister.php?use_hurl=1&cat=7&sub=2&page=%s&sub=2&mode=carts&orderby=featured&search=%s' % (page,text)
    http = urllib3.PoolManager()
    logger.debug("lexaoffle url is: %s" % url)
    r = http.request('GET', url, preload_content=False)
    html = r.data.decode()
    bruteCards = Decoder.extract('pdat=[','];',html)
    cards = []
    for bruteCardLine in bruteCards.split(",``],"):
        logger.debug("line is %s" % bruteCardLine)
        if '[' in bruteCardLine:
            element = {}
            bruteCardLine = bruteCardLine[:bruteCardLine.find('],')]
            name = Decoder.extract(', `','`,',bruteCardLine)
            id = Decoder.extract("['","'",bruteCardLine)
            link = 'https://www.lexaloffle.com/bbs/get_cart.php?cat=7&play_src=0&lid=%s' % id
            out = re.sub('[^A-Za-z0-9.\-,\ ]+', '', name)+".p8.png"
            out = ROMS_PATH + "/pico8/" + out
            command = 'curl "%s" --create-dirs --output "%s" \n' %(link,out)
            element["external"] = command
            element["action"] = 'command-exit'
            element["title"] = name
            cards.append(element)
    #back
    element = {}
    element["title"] = "Back"
    element["action"] = 'function'
    element["external"] = 'getCatalogMenu'
    cards.append(element)
    return cards
