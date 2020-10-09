
import os
from core.settings import *
import logging
logging.basicConfig(filename=os.path.join(LOG_PATH, LOG_FILE),level=logging.DEBUG)
logger = logging.getLogger(__name__)

from core.decoder import Decoder
from core.downloader import Downloader

import urllib

try:
    import json
except:
    import simplejson as json

import sys

class Youtube(Downloader):

    MAIN_URL = "https://www.youtube.com"
    SEARCH_URL = "https://www.youtube.com/results?search_query=%s"

    @staticmethod
    def getChannels(page='0'):
        x = []
        if str(page) == '0':
            page=Youtube.MAIN_URL+"/"
            x = Youtube.extractMainChannels()
        elif '/channel/' in page or '/trending' in page or '/gaming' in page:
            headers = Youtube.buildHeaders()
            response = Youtube.getContentFromUrl(url=str(page+"?pbj=1"),headers=headers,launchLocation=True)
            try:
                jsonResponse = json.loads(response)
                logger.debug("parsed json from '"+page+"', continue...")
                logger.debug("json is: "+response)
                try:
                    logger.debug("using way 1...")
                    x = Youtube.extractVideosFromJSON(jsonResponse[1]["response"])
                except:
                    logger.debug("fails way 1, using way 2...")
                    x = Youtube.extractVideosFromSpecialChannelJSON(jsonResponse[1]["response"])
                    pass
            except Exception as ex:
                logger.error("Could not parse response: "+str(ex))
                pass
        else:
            logger.debug("else!!")
            element = Youtube.extractTargetVideoJSON(page)
            x.append(element)
        return x

    @staticmethod
    def search(text):
        start = 'window["ytInitialData"] = '
        end = ";"
        page = Youtube.SEARCH_URL % urllib.parse.quote_plus(text)
        logger.debug("search url is: %s" % page)
        html = Youtube.getContentFromUrl(page)
        logger.debug("now extracting json search results...")
        jsonString = Decoder.extract(start,end,html)
        logger.debug("done, loading json...")
        jsonList = json.loads(jsonString)
        with open('/tmp/data.json', 'w') as outfile:
            json.dump(jsonList, outfile)
        logger.debug("parsed and saved!")
        listed = Youtube.extractVideosSearchFromJSON(jsonList)
        logger.debug("json to lists done")
        return listed



    @staticmethod
    def extractTargetVideoJSON(page):
        title = ''
        link = ''
        thumbnail = ''
        headers = Youtube.buildHeaders()
        response = Youtube.getContentFromUrl(url=str(page + "?pbj=1"), headers=headers)
        logger.debug("response is: "+response)
        try:
            responseJ = Decoder.extract('ytplayer.config = ','};',response)+"}"
            #logger.debug("json extracted is: " + responseJ)
            jsonResponse = json.loads(responseJ)
            logger.debug("json loaded")
            bruteVideoInfo = jsonResponse["args"]
            logger.debug("obtained brute video info...")
            title = bruteVideoInfo["title"]
            url = bruteVideoInfo["adaptive_fmts"]
            url = Decoder.extract('url=',",",url)
            url = urllib.unquote(url)
            #url = url[:-1]
            thumbnail = bruteVideoInfo["thumbnail_url"]
            logger.debug("extracted final url: "+url)
        except:
            logger.error("error parsing video info")
            pass
        element = {}
        element["title"] = title
        element["link"] = link
        element["thumbnail"] = thumbnail
        element["finalLink"] = True
        return element


    @staticmethod
    def buildHeaders():
        headers = {}
        headers["accept-language"] = "es-ES,es;q=0.9"
        headers["x-youtube-client-version"] = "2.20171120"
        headers["user-agent"] = Downloader.USER_AGENT_CHROME
        headers["x-youtube-client-name"] = '1'
        return headers

    @staticmethod
    def extractMainChannels():
        x = [
            {'title':'Music','page':'https://www.youtube.com/channel/UC-9-kyTW8ZkZNDHQJ6FgpwQ','thumbnail':''},
            {'title':'Sports','page':'https://www.youtube.com/channel/UCEgdi0XIXXZ-qJOFPf4JSKw','thumbnail':''},
            {'title':'Gaming','page':'https://www.youtube.com/gaming','thumbnail':''},
            {'title':'News','page':'https://www.youtube.com/channel/UCYfdidRxbB8Qhf0Nx7ioOYw','thumbnail':''},
            {'title':'Live','page':'https://www.youtube.com/channel/UC4R8DWoMoI7CAwX8_LjQHig','thumbnail':''},
            {'title':'Learning','page':'https://www.youtube.com/channel/UCtFRv9O2AHqOZjjynzrv-xg','thumbnail':''},
            {'title':'360','page':'https://www.youtube.com/channel/UCzuqhhs6NWbgTzMuM09WKDQ','thumbnail':''}
        ]

        return x

    @staticmethod
    def extractVideosFromChannelJSON(jsonScript):
        x = []
        jsonList = json.loads(jsonScript)
        x = Youtube.extractVideosFromJSON(jsonList)
        return x

    @staticmethod
    def extractVideosFromJSON(jsonList):
        x = []
        for jsonElements in jsonList['contents']['twoColumnBrowseResultsRenderer']["tabs"][0]['tabRenderer']['content']['sectionListRenderer']['contents']:
            logger.debug("inside first for...")
            #-> itemSectionRenderer -> contents [0] -> shelfRenderer -> content -> horizontalListRenderer -> items [0-11] (4) -> gridVideoRenderer
            for jsonElement in jsonElements['itemSectionRenderer']['contents'][0]['shelfRenderer']['content']['horizontalListRenderer']['items']:
                logger.debug("inside second for...")
                try:
                    title = ''
                    url = ''
                    thumbnail = ''
                    try:
                        element2 = jsonElement["gridVideoRenderer"]
                    except:
                        logger.debug("fail!")
                        element2 = jsonElement["gridChannelRenderer"]
                        pass
                    logger.debug("inside element2...")
                    if 'title' in element2:
                        title = element2['title']['simpleText']
                    logger.debug("simple text: "+str(title))
                    if 'thumbnail' in element2:
                        thumbnail = element2['thumbnail']['thumbnails'][0]['url']
                        if 'https' not in thumbnail:
                            thumbnail = 'https:' + thumbnail
                    logger.debug("simple thumb: "+str(thumbnail))
                    if 'videoId' in element2:
                        url = element2['videoId']
                        url = 'https://youtube.com/watch?v='+url
                    logger.debug("simple url: "+str(url))
                    element = {}
                    element["title"] = title
                    element["page"] = url
                    element["thumbnail"] = thumbnail
                    element["finalLink"] = True
                    logger.debug("append: "+title+", page: "+url+", thumb: "+thumbnail)
                    x.append(element)
                except:
                    logger.debug("fail parser for: "+str(jsonElement))
                    pass
        return x

    @staticmethod
    def extractVideosSearchFromJSON(jsonList):
        x = []
        for jsonElements in jsonList['contents']['twoColumnSearchResultsRenderer']["primaryContents"]['sectionListRenderer']['contents']:
            if "itemSectionRenderer" in jsonElements:
                for jsonElement in jsonElements["itemSectionRenderer"]["contents"]:
                    logger.debug("inside first for...")
                    try:
                        title = ''
                        url = ''
                        thumbnail = ''
                        element2 = jsonElement["videoRenderer"]
                        logger.debug("inside element2...")
                        if 'title' in element2:
                            title = element2['title']['runs'][0]['text']
                        logger.debug("simple text: "+str(title))
                        if 'thumbnail' in element2:
                            thumbnail = element2['thumbnail']['thumbnails'][0]['url']
                            if 'https' not in thumbnail:
                                thumbnail = 'https:' + thumbnail
                        logger.debug("simple thumb: "+str(thumbnail))
                        if 'videoId' in element2:
                            url = element2['videoId']
                            url = 'https://youtube.com/watch?v='+url
                        logger.debug("simple url: "+str(url))
                        element = {}
                        element["title"] = title
                        element["page"] = url
                        element["thumbnail"] = thumbnail
                        element["finalLink"] = True
                        logger.debug("append: "+title+", page: "+url+", thumb: "+thumbnail)
                        x.append(element)
                    except Exception as ex:
                        logger.debug("fail parser for: "+str(ex))
                        pass
        return x

    @staticmethod
    def extractVideosFromSpecialChannelJSON(jsonList):
        x = []
        logger.debug("special....")
        if 'tabs' in jsonList['contents']['twoColumnBrowseResultsRenderer']:
            targets = jsonList['contents']['twoColumnBrowseResultsRenderer']['tabs'][0]['tabRenderer']['content']
        elif 'primaryContents' in jsonList['contents']['twoColumnBrowseResultsRenderer']:
            targets = jsonList['contents']['twoColumnBrowseResultsRenderer']['primaryContents']
        for jsonElements in targets['sectionListRenderer']['contents']:
            if 'tabs' in jsonList['contents']['twoColumnBrowseResultsRenderer'] and 'itemSectionRenderer' in jsonElements and 'shelfRenderer' in jsonElements['itemSectionRenderer']['contents'][0]:
                content = jsonElements['itemSectionRenderer']['contents'][0]['shelfRenderer']['content']
                if 'horizontalListRenderer' in content:
                    for jsonElement in content['horizontalListRenderer']['items']:
                        if 'gridVideoRenderer' in jsonElement:
                            element2 = jsonElement["gridVideoRenderer"]
                            element = Youtube.extractVideoElement(element2)
                            x.append(element)
                if 'expandedShelfContentsRenderer' in content:
                    for jsonElement in content['expandedShelfContentsRenderer']['items']:
                        element2 = jsonElement["videoRenderer"]
                        element = Youtube.extractVideoElement(element2)
                        x.append(element)
                if 'horizontalMovieListRenderer' in content:
                    for jsonElement in content['horizontalMovieListRenderer']['items']:
                        element2 = jsonElement["gridMovieRenderer"]
                        element = Youtube.extractVideoElement(element2)
                        x.append(element)
            elif 'itemSectionRenderer' in jsonElements: #search
                logger.debug("search....")
                content = jsonElements['itemSectionRenderer']['contents']
                for jsonElement in content:
                    try:
                        if "horizontalCardListRenderer" in jsonElement:
                            for element2 in  jsonElement["horizontalCardListRenderer"]['cards']:
                                #element2 = jsonElement["videoRenderer"]
                                element = Youtube.extractVideoElement(element2["videoCardRenderer"])
                                x.append(element)
                        else:
                            if "gridMovieRenderer" in jsonElement:
                                element2 = jsonElement["gridMovieRenderer"]
                            elif "videoRenderer" in jsonElement:
                                element2 = jsonElement["videoRenderer"]
                            #element2 = jsonElement["videoRenderer"]
                            element = Youtube.extractVideoElement(element2)
                            x.append(element)
                    except:
                        logger.debug("fails this way, so needs other new way...")

                        pass

        return x

    @staticmethod
    def extractVideoElement(element2):
        title = ''
        url = ''
        thumbnail = ''
        if 'title' in element2:
            try:
                title = element2['title']['simpleText']
            except:
                title = element2['title']['runs'][0]['text']
                pass
        if 'thumbnails' in element2:
            thumbnail = element2['thumbnail']['thumbnails'][0]['url']
            if 'https' not in thumbnail:
                thumbnail = 'https:' + thumbnail
        if 'videoId' in element2:
            url = element2['videoId']
            url = 'https://youtube.com/watch?v=' + url
        element = {}
        element["title"] = title
        element["page"] = url
        element["thumbnail"] = thumbnail
        element["finalLink"] = True
        return element
