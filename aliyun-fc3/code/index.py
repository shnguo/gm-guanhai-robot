# -*- coding: utf-8 -*-

import logging
from emoji import emojize
import datetime
# import sys
# sys.path.append('..')

def handler(event, context):
    logger = logging.getLogger()
    logger.info(event)
    return event

def emoji_handler(event, context):
    logger = logging.getLogger()
    logger.info(event)
    return datetime.datetime.now()

