from typing import Literal
from aiohttp import web
import asyncio
from asyncio import StreamWriter
import logging
from ..root_logger import logger

class AppWebSocketLogStream(StreamWriter):
    """将 warning 信息发送到前端"""

    def __init__(self, app: web.Application, rtype: Literal['warning', 'exception']):
        self.app = app
        self.rtype = rtype

    def write(self, msg: str):
        if 'ws' in self.app.keys():
            ws: web.WebSocketResponse = self.app['ws']
            if not ws.closed:

                jdata = {'type': self.rtype, 'return': msg}

                loop = asyncio.get_running_loop()
                loop.create_task(ws.send_json(jdata))

    def flush(self):
        pass

async def direct_warning_to_ws(app: web.Application):
    warning_log_stream = AppWebSocketLogStream(app, 'warning')
    warning_hdlr = logging.StreamHandler(warning_log_stream)
    warning_hdlr.addFilter(lambda rec: rec.levelno == logging.WARNING)

    except_log_stream = AppWebSocketLogStream(app, 'exception')
    except_hdlr = logging.StreamHandler(except_log_stream)
    except_hdlr.addFilter(lambda rec: rec.levelno >= logging.ERROR)

    logger.addHandler(warning_hdlr)
    logger.addHandler(except_hdlr)

def register(app: web.Application):
    app.on_startup.append(direct_warning_to_ws)
