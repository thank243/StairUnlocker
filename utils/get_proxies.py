import requests
from loguru import logger

from utils.config import config


def get_proxies():
    sub_convert_url = config['converterAPI'] + "/sub"
    ret = requests.get(sub_convert_url, params={"url": config['subURL'],
                                                "target": "clash",
                                                "list": "true",
                                                "include": config['include'],
                                                "exclude": config['exclude']})
    if ret.status_code > 300:
        logger.error(ret.text)
        raise Exception("Invalid link.")
    logger.info("Converted url to clash config file.")
    return ret.text
