import os
import urllib3
import logging
from core.settings import *
logging.basicConfig(filename=os.path.join(LOG_PATH, LOG_FILE),level=LOGGING_LEVEL)
logger = logging.getLogger(__name__)

def loadRoms(params=[]): #TODO launch emulationstation configurations by path
    menu = []
    folder = None
    if type(params) is list:
        logger.debug("list")
        for element in params:
            logger.debug("ele %s" % str(element))
            if "type" in element:
                folder = element["type"]
    if folder == None:
        logger.debug("not type")
        dir= os.listdir(ROMS_PATH)
        for directory in dir:
            if len(os.listdir(os.path.join(ROMS_PATH,directory))) == 0:
                logger.debug("Empty directory %s " % directory)
            else:
                logger.debug("Not empty directory %s, appending to list" % directory)
                element = {}
                element["title"] = "%s" % directory
                element["action"] = "function"
                element["external"] = "loadRoms"
                element["params"] = [{
                    'type' : directory
                }]
                menu.append(element)
        element = {}
        element["title"] = "Back"
        element["action"] = 'menu'
        element["external"] = 'main'
        menu.append(element)
    else:
        logger.debug("with type")
        logger.debug("selected directory is %s " % folder)
        if folder in ['gbc','gb','gba','megadrive','n64','amstradcpc','nes','snes']:
            if folder in ['gbc','gb']:
                logger.debug("selected gb/gbc...")
                config = CONFIG_GB
                lib = LIB_GB
            elif folder == 'gba':
                logger.debug("selected gba...")
                config = CONFIG_GBA
                lib = LIB_GBA
            elif folder == 'megadrive':
                logger.debug("selected megadrive...")
                config = CONFIG_MD
                lib = LIB_MD
            elif folder == 'n64':
                logger.debug("selected n64...")
                config = CONFIG_N64
                lib = LIB_N64
            elif folder == 'amstradcpc':
                logger.debug("selected amstrad...")
                config = CONFIG_AMSTRAD
                lib = LIB_AMSTRAD
            elif folder == 'nes':
                logger.debug("selected famicom/nes...")
                config = CONFIG_NES
                lib = LIB_NES
            elif folder == 'snes':
                logger.debug("selected super nintendo...")
                config = CONFIG_SNES
                lib = LIB_SNES_2010

            newPath = os.path.join(ROMS_PATH,folder)
            dir = os.listdir(newPath)
            #for directory in dir:
            for directory in sorted(dir):
                #if os.path.getsize(os.path.join(newPath,directory))>8192:
                if directory.lower().endswith('.zip') or directory.lower().endswith('.rar'):
                    element = {}
                    element["title"] = "%s" % directory[:directory.rfind(".")]
                    element["action"] = "function"
                    element["external"] = "loadZippedRom"
                    path = os.path.join(newPath,directory)
                    element["params"] = [{
                        'path' : path,
                        'lib': lib,
                        'config': config
                    }]
                    menu.append(element)
                elif not directory.lower().endswith('.srm') and not directory.lower().endswith('.state'):
                    logger.debug("Not empty directory %s, appending to list" % directory)
                    element = {}
                    element["title"] = "%s" % directory[:directory.rfind(".")]
                    element["action"] = "function"
                    element["external"] = "loadCommandRom"
                    command = '%s -L %s --config %s "%s/%s"' % (RETROARCH_BIN,lib,config,newPath,directory)
                    element["params"] = [{
                        'type' : directory,
                        'command' : command,
                        'game' : "%s/%s" % (newPath,directory)
                    }]
                    menu.append(element)
        elif folder == 'pico8':
            logger.debug("selected pico8")
            picoPath = os.path.join(ROMS_PATH,"pico8")
            for directory in sorted(os.listdir(picoPath)):
                element = {}
                element["title"] = "%s" % directory[:directory.rfind(".")]
                element["action"] = "command"
                element["external"] = '%s -run "%s/%s"' % (PICO8_BIN,picoPath,directory)
                menu.append(element)
        elif folder == 'tic80':
            logger.debug("selected tic80")
            ticPath = os.path.join(ROMS_PATH,"tic80")
            for directory in sorted(os.listdir(ticPath)):
                element = {}
                element["title"] = "%s" % directory[:directory.rfind(".")]
                element["action"] = "command"
                element["external"] = '%s "%s/%s"' % (TIC80_BIN,ticPath,directory)
                menu.append(element)
        element = {}
        element["title"] = "Back"
        element["action"] = "function"
        element["external"] = "loadRoms"
        menu.append(element)
    return menu

def loadCommandRom(params=[]):
    type = None
    command = None
    game = None
    if type(params) is list:
        logger.debug("list")
        for element in params:
            logger.debug("ele %s" % str(element))
            if "command" in element:
                command = element["command"]
            if "type" in element:
                type = element["type"]
            if "game" in element:
                game = element["game"]
    if command and type and game:
        os.system("sudo rm -Rf /home/pi/game")
        #do temp folder
        os.system("mkdir /home/pi/game/")

        #put states
        command2 = "cp %s/*.state* /home/pi/game/" % ( os.path.dirname(game) )
        os.system(command2)
        logger.debug(command2)

        launch = command[:command.find('"')] + " /home/pi/game/" + directory
        logger.debug(launch)
        os.system(launch)

        command = "cp /home/pi/game/*.state* '%s'" % ( os.path.dirname(path) )
        logger.debug(command)
        os.system(command)
        #last remove old one
        os.system("sudo rm -Rf /home/pi/game")


def loadZippedRom(params=[]):
    menu = []
    path = None
    lib = None
    config = None
    #read params
    if type(params) is list:
        logger.debug("list")
        for element in params:
            logger.debug("ele %s" % str(element))
            if "path" in element:
                path = element["path"]
            if "lib" in element:
                lib = element["lib"]
            if "config" in element:
                config = element["config"]
    #launch logic
    if path and lib:
        #remove old folder if exists
        os.system("sudo rm -Rf /home/pi/game")
        #do temp folder
        os.system("mkdir /home/pi/game/")
        if path.lower().endswith('.zip'):
            #now unzip
            command = 'unzip "%s" -d /home/pi/game' % path
        elif path.lower().endswith('.rar'):
            command = 'unrar x "%s" /home/pi/game' % path
        logger.debug(command)
        os.system(command)

        #last get gamePath
        gamePath = None
        for file in os.listdir("/home/pi/game"):
            logger.debug(str(file))
            if os.path.isfile(os.path.join("/home/pi/game",file)):
                logger.debug("found!")
                gamePath = os.path.join("/home/pi/game",file)
                logger.debug("get unzipped file: %s" % gamePath)

        #put states
        command = "cp %s/*.state* /home/pi/game/" % ( os.path.dirname(path) )
        os.system(command)
        logger.debug(command)

        #next launch command
        logger.debug("launching %s" % gamePath)
        command = '%s -L %s --config %s "%s"' % (RETROARCH_BIN,lib,config,gamePath)
        logger.debug(command)
        os.system(command)
        logger.debug("get saved file (if exists...)")
        #save files if exists in previews path
        command = "cp /home/pi/game/*.state* '%s'" % ( os.path.dirname(path) )
        logger.debug(command)
        os.system(command)
        #last remove old one
        os.system("sudo rm -Rf /home/pi/game")


def internetBrowser(params=[]):
    menu = []
    url = ""
    text = ""
    final = False
    if len(params)>0:
        for key in params:
            logger.debug("str %s" % str(key))
            if 'webpage' in key:
                url = key["webpage"]
            if 'final' in key:
                final = key["final"]
            if 'text' in key:
                text = key["text"]
    logger.debug("using url: '%s' " % url)
    if len(url)>0:
        http = urllib3.PoolManager()
        if final:
            logger.debug("transforming link %s to final link..." % (url))
            url = url.replace('/roms/','/download/roms/')
            logger.debug("final url is '%s'" % url)
        elif len(text)>0 and '%' in url:
            logger.debug("search detected")
            url = url % text
            logger.debug("new url is: %s" % url)
        r = http.request('GET', url, preload_content=False)
        exit = False
        html = r.data.decode()
        r.release_conn()
        if len(html)>0:
            if not final:
                if '<form class="filter" action="/roms/platforms-search">' in html:

                    logger.debug("consoles wrap")
                    container = html[html.find('<form class="filter" action="/roms/platforms-search">')+len('<form class="filter" action="/roms/platforms-search">'):]
                    container = container[:container.find('</table>')]
                    i = 0

                    #first search
                    element = {}
                    link = url[0:url.rfind('/')+1]
                    logger.debug("link %s " % link)
                    link = link+'search?name=%s'
                    logger.debug("link2 %s " % link)
                    element["title"] = "Search"
                    element["action"] = 'function-text'
                    element["external"] = 'internetBrowser'
                    element["params"] = [{'webpage':link, 'final': False}]
                    menu.append(element)

                    for line in container.split('<a href="'):
                        if i > 0:
                            link = line[:line.find('"')]
                            name = line[line.find('">')+len('">'):]
                            name = name[:name.find('<')]
                            element = {}
                            element["title"] = name
                            element["action"] = 'function'
                            element["external"] = 'internetBrowser'
                            element["params"] = [{'webpage':link, 'final': False}]
                            if len(name)>0:
                                menu.append(element)
                                logger.debug("%s, %s" % (name,link) )
                        i+=1
                elif '<div class="results">' in html or '<h1 class="is-medium i-mb-15">Search Result for ' in html:
                    if '<h1 class="is-medium i-mb-15">Search Result for ' in html:
                        container = html[html.find('<table class="table">')+len('<table class="table">'):]
                        splitter = '<tr>'
                    else:
                        logger.debug('<div class="results">')
                        container = html[html.find('<div class="results">')+len('<div class="results">'):]
                        splitter = '<a href="'

                    container = container[:container.find('</table>')]
                    i = 0
                    for line in container.split(splitter):
                        if i > 1:
                            logger.debug("inside2...")
                            link = line[line.find('"')+1:line.find('">')]
                            if len(link)==0:
                                logger.debug("line is: '%s'" % (line))
                                link = line[:line.find('">')]
                                logger.debug("new link is %s" % (link))
                            if 'https:' not in link and '//' in link:
                                link = 'https:'+link
                            logger.debug("inside3...")
                            name = line[line.find('">')+len('">'):]
                            logger.debug("inside4...")
                            name = name[:name.find('<')]
                            logger.debug("extracted info...")
                            platform = line[line.find('<td><a href="')+len('<td><a href="'):]
                            platform = platform[platform.find('>')+1:platform.find('<')]
                            element = {}
                            element["title"] = name.replace('&#039;',"'").replace('&amp;','&')
                            if len(splitter) < 5:
                                element["title"] += " - "+platform
                            element["action"] = 'function'
                            element["external"] = 'internetBrowser'
                            element["params"] = [{'webpage':link, 'final': True}]
                            logger.debug("appending...")
                            if len(name)>0:
                                menu.append(element)
                                logger.debug("%s, %s" % (link,name) )
                            else:
                                logger.debug("discarting one...")
                        i+=1
                        logger.debug(i)
                else:
                    logger.debug("ELSE result...")

                element = {}
                element["title"] = "Back"
                element["action"] = 'menu'
                element["external"] = 'webpages'
                menu.append(element)
            else:
                logger.debug("final link...")
                link = html[html.find('<a class="wait__link" href="')+len('<a class="wait__link" href="'):]
                link = link[:link.find('"')]
                logger.debug("final url is: %s" % (link) )
                url2 = url.lower()
                if 'gameboy-advance' in url2:
                    subtype = 'gba'
                elif 'super-nintendo' in url2:
                    subtype = 'snes'
                elif 'nintendo-ds' in url2:
                    subtype = 'nds'
                elif 'gameboy-color' in url2:
                    subtype = 'gbc'
                elif 'gameboy' in url2:
                    subtype = 'gb'
                elif 'nintendo-64' in url2:
                    subtype = 'n64'
                elif 'nintendo' in url2:
                    subtype = 'nes'
                elif 'playstation' in url2 and 'portable' in url2:
                    subtype = 'psp'
                elif 'playstation-2' in url2:
                    subtype = 'ps2'
                elif 'playstation' in url2:
                    subtype = 'psx'
                elif 'gamecube' in url2:
                    subtype = 'gc'
                elif 'nintendo-wii' in url2:
                    subtype = 'wii'
                elif 'mame' in url2 or 'acorn' in url2:
                    subtype = 'arcade/mame2003'
                    #subtype = 'mame-libretro/mame2003'
                elif 'dreamcast' in url2:
                    subtype = 'dreamcast'
                elif 'sega-genesis' in url2:
                    subtype = 'genesis'
                elif 'neo-geo' in url2:
                    subtype = 'neogeo'
                elif 'microsoft-xbox' in url2:
                    subtype = 'xbox'
                elif 'amiga' in url2:
                    subtype = 'amiga'
                elif 'amstrad' in url2:
                    subtype = 'amstradcpc'
                elif 'apple2' in url:
                    subtype = 'apple2'
                elif 'atari' in url:
                    if '2600' in url:
                        subtype = 'atari2600'
                    elif '7800' in url:
                        subtype = 'atari7800'
                    elif '800' in url:
                        subtype = 'atari800'
                    elif '5200' in url:
                        subtype = 'atari5200'
                    elif 'jaguar' in url:
                        subtype = 'atarijaguar'
                    elif 'lynx' in url:
                        subtype = 'atarilynx'
                    elif 'st' in url:
                        subtype = 'atarist'
                elif 'tsr-80' in url:
                    subtype = 'coco'
                elif 'colecovision' in url:
                    subtype = 'coleco'
                elif 'commodore' in url:
                    subtype = 'c64'
                elif 'dragon' in url:
                    subtype = 'dragon32'
                elif 'famicom' in url:
                    subtype = 'fds'
                elif 'gamegear' in url:
                    subtype = 'gamegear'
                elif 'gameandwatch' in url:
                    subtype = 'gameandwatch'
                elif 'megadrive' in url:
                    subtype = 'megadrive'
                elif 'intellivision' in url:
                    subtype = 'intellivision'
                elif 'love' in url:
                    subtype = 'love'
                elif 'macintosh' in url:
                    subtype = 'macintosh'
                elif 'mastersystem' in url:
                    subtype = 'mastersystem'
                elif 'msx' in url:
                    subtype = 'msx'
                elif 'necpc' in url:
                    subtype = 'pc88'
                elif 'neogeo' in url:
                    if 'pocket' in url:
                        if 'color' in url:
                            subtype = 'ngpc'
                        else:
                            subtype = 'ngp'
                elif 'nds' in url:
                    subtype = 'nds'
                elif 'openbor' in url:
                    subtype = 'openbor'
                elif 'oric' in url:
                    subtype = 'oric'
                elif 'pcengine' in url:
                    subtype = 'pcengine'
                elif 'samcoupe' in url:
                    subtype = 'samcoupe'
                elif 'saturn' in url:
                    subtype = 'saturn'
                elif 'scummvm' in url:
                    subtype = 'scummvm'
                elif 'sega32x' in url:
                    subtype = 'sega32x'
                elif 'segacd' in url:
                    subtype = 'segacd'
                elif 'sharp' in url:
                    subtype = 'x1'
                elif 'sg-1000' in url:
                    subtype = 'sg-1000'
                elif 'thomson' in url:
                    subtype = 'moto'
                elif 'ti99' in url:
                    subtype = 'ti99'
                elif 'trs-80' in url:
                    subtype = 'trs-80'
                elif 'vectrex' in url:
                    subtype = 'vectrex'
                elif 'videopac' in url:
                    subtype = 'videopac'
                elif 'virtualboy' in url:
                    subtype = 'virtualboy'
                elif 'wii' in url:
                    subtype = 'wii'
                elif 'wonderswan' in url:
                    subtype = 'wonderswancolor'
                    if 'wonderswan' in url:
                        subtype = 'wonderswan'
                elif 'zmachine' in url:
                    subtype = 'zmachine'
                elif 'spectrum' in url:
                    subtype = 'zxspectrum'

                out = ROMS_PATH+"/"+subtype+"/"
                element = {}
                element["title"] = "Back"
                element["action"] = 'command-exit'
                command = 'wget -N %s -P %s \n' %(link,out)
                #download unzipped is commented because some platforms needs to be in .zip format
#                if link.endswith('.zip'):
#                    command = 'mkdir -p "%s" \n' % (out)
                    #command += 'curl -L %s | bsdtar -xvf - -C %s\n' % (link,out)
#                    command += 'wget -qO- %s | bsdtar -xvf - -C %s\n' % (link,out)
                    #file = link[link.rfind('/')+1:].replace('%20','\ ').replace('%28','\(').replace('%29','\)')#.replace('%20',' ').replace('%28','(').replace('%29',')')
                    #command += 'unzip %s -d %s \n' % (file,out)
                    #command += 'rm -Rf %s%s \n' % (out,file)
                element["external"] = command
                return element
        else:
            logger.debug("empty html")
    logger.debug("returning menu...")
    return menu
