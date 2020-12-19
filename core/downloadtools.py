import sys, os.path
import re
import urllib
try:
    import urllib2
    from urllib2 import Request, HTTPHandler, build_opener, install_opener
except:
    import urllib3 as urllib2
    from urllib.request import HTTPHandler, Request, build_opener, install_opener
    pass
import time
import socket
import traceback # for download problems
import gzip

from core.settings import LOG_PATH

import logging
logging.basicConfig(filename=os.path.join(LOG_PATH, LOG_FILE),level=LOGGING_LEVEL)
logger = logging.getLogger(__name__)

def sec_to_hms(seconds):
    m,s = divmod(int(seconds), 60)
    h,m = divmod(m, 60)
    return ("%02d:%02d:%02d" % ( h , m ,s ))

def downloadfile(url,fileName,headers=[],silent=False,notStop=False):
    logger.debug("downloadfile: url="+str(url))
    logger.debug("downloadfile: fileName="+fileName)
    try:
        logger.debug("downloadfile with fileName="+fileName)
        if os.path.exists(fileName) and notStop:
            f = open(fileName, 'r+b')
            existSize = os.path.getsize(fileName)

            logger.info("downloadfile: file exists, size=%d" % existSize)
            recordedSize = existSize
            f.seek(existSize)
        elif os.path.exists(fileName) and not notStop:
            logger.info("downloadfile: file exists, dont re-download")
            return
        else:
            existSize = 0
            logger.info("downloadfile: file doesn't exists")
            f = open(fileName, 'wb')
            recordedSize = 0

        socket.setdefaulttimeout(30) #Timeout
        h=HTTPHandler(debuglevel=0)
        remoteFile = url
        params = None

        request = Request(url)

        logger.debug("checking headers... type: "+str(type(headers)))
        if len(headers)>0:
            logger.debug("adding headers...")
            for key in headers.keys():
                logger.debug("Header="+key+": "+headers.get(key))
                request.add_header(key,headers.get(key))
        else:
            logger.debug("headers figure are 0")

        logger.debug("checking resume status...")
        if existSize > 0: #restart
            logger.info("resume is launched!")
            request.add_header('Range', 'bytes=%d-' % (existSize, ))

        opener = build_opener(h)
        install_opener(opener)
        try:
            logger.debug("opening request...")
            connection = opener.open(request)
        except: # End
            logger.error("ERROR: "+traceback.format_exc())
            f.close()
        logger.debug("detecting download size...")

        try:
            totalFileSize = int(connection.headers["Content-Length"])
        except:
            totalFileSize = 1

        logger.debug("total file size: "+str(totalFileSize))

        if existSize > 0:
            totalFileSize = totalFileSize + existSize

        logger.debug("Content-Length=%s" % totalFileSize)

        blockSize = 100*1024 #Buffer size

        bufferReadedSize = connection.read(blockSize)
        logger.info("Starting download, readed=%s" % len(bufferReadedSize))

        maxRetries = 5

        while len(bufferReadedSize)>0:
            try:
                f.write(bufferReadedSize)
                recordedSize = recordedSize + len(bufferReadedSize)
                percent = int(float(recordedSize)*100/float(totalFileSize))
                totalMB = float(float(totalFileSize)/(1024*1024))
                downloadedMB = float(float(recordedSize)/(1024*1024))

                retries = 0
                while retries <= maxRetries:
                    try:
                        before = time.time()
                        bufferReadedSize = connection.read(blockSize)
                        after = time.time()
                        if (after - before) > 0:
                            speed=len(bufferReadedSize)/((after - before))
                            remainingSize=totalFileSize-recordedSize
                            if speed>0:
                                remainingTime=remainingSize/speed
                            else:
                                remainingTime=0 #infinite

                            if not silent:
                                logger.debug( percent ,"downloading %s %s %s %s %s" % ( downloadedMB , totalMB , percent , speed/1024 , sec_to_hms(remainingTime)))
                        break
                    except:
                        retries = retries + 1
                        logger.info("ERROR downloading buffer, retry %d" % retries)
                        logger.error( traceback.print_exc() )

                # Something wrong happened
                if retries > maxRetries:
                    logger.error("ERROR, something happened in download proccess")
                    f.close()
                    return -2
            except:
                logger.error( traceback.print_exc() )
                f.close()
                return -2

    except Exception as ex:
        logger.error(str(ex))
        pass

    try:
        f.close()
    except:
        pass

    logger.info("Finished download proccess")
