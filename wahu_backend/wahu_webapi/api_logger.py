from aiohttp import web
import asyncio
from asyncio import StreamWriter
import logging
from ..root_logger import logger

class AppWebSocketLogStream(StreamWriter):
    """将 warning 信息发送到前端"""

    def __init__(self, app: web.Application):
        self.app = app

    def write(self, msg: str):
        if 'ws' in self.app.keys():
            ws: web.WebSocketResponse = self.app['ws']
            if not ws.closed:

                jdata = {'type': 'warning', 'return': msg}

                loop = asyncio.get_running_loop()
                loop.create_task(ws.send_json(jdata))

    def flush(self):
        pass

async def direct_warning_to_ws(app: web.Application):
    log_stream = AppWebSocketLogStream(app)
    hdlr = logging.StreamHandler(log_stream)
    hdlr.addFilter(lambda rec: rec.levelno == logging.WARNING)
    logger.addHandler(hdlr)

def register(app: web.Application):
    app.on_startup.append(direct_warning_to_ws)
