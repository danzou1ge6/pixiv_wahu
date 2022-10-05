from .api_illust import IllustPixivAPI
from .api_user import UserPixivAPI
from .api_account_control import AccountControlPixivAPI
from .api_misc import MiscPixivAPI


class PixivAPI(IllustPixivAPI, UserPixivAPI, AccountControlPixivAPI, MiscPixivAPI):
    """
    基于异步 http 框架重构的 pixivpy \n
    为了使逻辑简洁（其实是因为懒）默认使用 ip 地址访问 pixiv 服务器
        （为什么要用 ip 而不是域名呢，你懂我意思吧 [doge] ）
    漫画、小说相关的 API 也没有实现（还是因为懒）

    相比 pixivpy ，这个 PixivAPI 的优点在于
        - 支持异步（当然似乎异步 Pixiv API 早就有了）
        - 优雅的接口：所有的 pixiv 服务器返回的**屎**一样的字典被转换成了 Python 对象
                     （ `DataClass` 或者 `NamedTuple` ，前者是因为对数据库操作有更好的支持）
                     因而可以使用类型注记
        - 使用了异步生成器，不用纠结 pixivpy 中 `parse_qs` 的逻辑
    """

