import logging
from typing import Any, MutableMapping

class IllustBookmarkDatabaseLogAdapter(logging.LoggerAdapter):

    def __init__(self, ibd_name: str, logger: logging.Logger):
        self.ibd_name = ibd_name
        self.logger = logger
    
    def process(
        self,
        msg: Any,
        kwargs: MutableMapping[str, Any]
    ) -> tuple[Any, MutableMapping[str, Any]]:

        return 'IlstBmDB[%s] %s' % (self.ibd_name, msg), kwargs
