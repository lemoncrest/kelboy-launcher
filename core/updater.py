import os
from core.settings import *
from core.downloadtools import downloadfile
from core.ziptools import Ziptools

import logging
logging.basicConfig(filename=os.path.join(LOG_PATH, LOG_FILE),level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Updater():

    def __init__(self):
        pass

    def update(self,url=UPLOAD_SITE,filename='update.zip'):
        logger.debug("launching update process...")
        downloadfile(url=url,fileName=filename)
        logger.debug("extracting...")
        unzipper = Ziptools()
        unzipper.extract(filename,"/tmp") #github issues
        logger.debug("cleaning process...")
        os.remove(filename)
        logger.info("update DONE!")
