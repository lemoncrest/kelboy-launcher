import os
import re
import urllib3
from core.decoder import Decoder
from core.settings import *
import logging
logging.basicConfig(filename=os.path.join(LOG_PATH, LOG_FILE),level=LOGGING_LEVEL)
logger = logging.getLogger(__name__)

def getCatalogTic80Menu(params=[]):
    page=0
    if type(params) is list:
        logger.debug("page")
        for element in params:
            logger.debug("page %s" % str(element))
            if "page" in element:
                page = element["page"]
    #/bbs/cposts/sc/
    http = urllib3.PoolManager()
    url = "https://tic80.com/play?cat=%s&sort=1" % page
    logger.debug("tic-80 url is: %s" % url)
    r = http.request('GET', url, preload_content=False)
    html = r.data.decode()
    bruteCards = Decoder.extract('<div class="row">','<footer class="footer">',html)
    cards = []
    if False and page>1: #TODO for future include pagination (if exists) from API
        element = {}
        element["title"] = "next p. %s" % (int(page)-1)
        element["action"] = "function"
        element["external"] = 'getCatalogTic80Menu'
        element["params"] = [{
            'page': int(page)-1
        }]
        cards.append(element)
    for bruteCardLine in bruteCards.split('<div class="row">'):
        logger.debug("line is %s" % bruteCardLine)
        element = {}
        name = Decoder.extract('<h2>','</h2>',bruteCardLine)
        id = Decoder.extract('<a href="','"',bruteCardLine)
        link = 'https://tic80.com%s' % id
        #https://tic80.com/cart/29cc9f8d67d415db38176168719cf139/cover.gif
        #https://tic80.com/cart/29cc9f8d67d415db38176168719cf139/cart.tic
        cartUrl = 'https://tic80.com%s' % Decoder.extract('<img class="pixelated" width="100%" src="','"',bruteCardLine).replace('cover.gif','cart.tic')

        out = re.sub('[^A-Za-z0-9.\-,\ ]+', '', name)+".tic"
        out = ROMS_PATH + "/tic80/" + out
        command = 'curl "%s" --create-dirs --output "%s" \n' %(cartUrl,out)
        element["external"] = command
        element["action"] = 'command-exit'
        element["title"] = name
        cards.append(element)
    #next page
    if False and len(cards)>0: #TODO in future (if exists in API)
        element = {}
        element["title"] = "next p. %s" % (int(page)+1)
        element["action"] = "function"
        element["external"] = 'getCatalogTic80Menu'
        element["params"] = [{
            'page': int(page)+1
        }]
        cards.append(element)
    if False: #TODO in future (if exists in API)
        element = {}
        element["title"] = "Search"
        element["action"] = 'function-text'
        element["external"] = 'getCatalogTic80SearchMenu'
        element["params"] = [{'webpage':link, 'final': False}]
        #TODO append getCatalogTic80SearchMenu search
        #cards.append(element) #TODO commented because we don't find where is search in official webpage and apparently needs to query to API
    #back
    element = {}
    element["title"] = "Back"
    if int(page) != 1:
        element["action"] = 'function'
        element["external"] = 'getCatalogTic80Menu'
    else:
        element["action"] = 'menu'
        element["external"] = 'webpages'
    cards.append(element)
    return cards

def getCatalogTic80SearchMenu(params=[]):
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
    logger.debug("tic-80 url is: %s" % url)
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
    element["external"] = 'getCatalogTic80Menu'
    cards.append(element)
    return cards
