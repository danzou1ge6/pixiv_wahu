import click


from .illust_database import WahuIllustDatabaseMethods
from .illust_repo import IllustRepoMethods
from .misc import WahuMiscMethods
from .pixiv import WahuPixivMethods
from .wahu_config import WahuConfigMethods
from .wahu_generator import WahuGeneratorMethods


class WahuMetdodsWithCli(
    WahuIllustDatabaseMethods, WahuPixivMethods, WahuGeneratorMethods,
    WahuConfigMethods, IllustRepoMethods, WahuMiscMethods):
    """还没实现（逃"""

