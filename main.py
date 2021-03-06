# coding:utf-8

import json
import socket
import sys
from platform import platform

import requests
import yaml
from loguru import logger

from client_launcher.client_clash import Clash
from utils.check_port import check_port
from utils.cli import cli_opt
from utils.config import config
from utils.get_proxies import get_proxies
from utils.netflix import is_unlock
from utils.upload_gist import upload

try:
    cli_opt()
    logger.warning(f"StairUnlocker is staring. Version: {config['VERSION']}")
    check_port(config["mixPort"])
    logger.error(f"Port {config['mixPort']} already in use, " +
                 "please change the local port in stairunlock_config.json or terminate the application.")
    sys.exit(0)
except (ConnectionRefusedError, socket.timeout):
    pass

if __name__ == "__main__":
    logger.warning("localFile: on") if config['localFile'] else logger.warning("upload gist: on")
    logger.warning("fastMode: on") if config['fastMode'] else logger.warning("fastMode: off")
    logger.info(f"Platform Info : {platform()}")
    # 生成clash配置文件
    proxies = yaml.safe_load(get_proxies())
    cfg = {"mode": "global",
           "mixed-port": config["mixPort"],
           "bind-address": config["localAddress"],
           "external-controller": config["localAddress"] + ":" + str(config["controlPort"]),
           "proxy-groups": [{"name": "select", "type": "select",
                             "proxies": [_["name"] for _ in proxies["proxies"]]}]}
    cfg.update(proxies)
    with open("config.yaml", "w", encoding="utf-8") as _:
        yaml.safe_dump(cfg, _, allow_unicode=True)

    clash = Clash()
    clash.start_client()

    # 批量解锁测试
    try:
        unlock_server_list = []
        for idx, server in enumerate(proxies["proxies"]):
            params = json.dumps({"name": server['name']}, ensure_ascii=False)
            req_url = requests.put(f"http://127.0.0.1:{config['controlPort']}/proxies/GLOBAL",
                                   data=params.encode('utf-8'))
            if "Full" in is_unlock(server['name'], config['mixPort'], idx + 1, len(proxies['proxies'])):
                unlock_server_list.append(server)
        if config['localFile']:
            with open('list.yaml', 'w', encoding='utf-8') as _:
                yaml.safe_dump({'proxies': unlock_server_list}, _, allow_unicode=True)
            logger.info('Writing to list.yaml success!')
        else:
            # 上传到gist
            upload(yaml.safe_dump({'proxies': unlock_server_list}, allow_unicode=True))
    except Exception as e:
        logger.error(e.args[0])
    finally:
        clash.stop_client()
