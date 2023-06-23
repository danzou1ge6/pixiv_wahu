from .aiopixivpy.api_base import AccountSession
from .aiopixivpy.datastructure_comment import PixivComment
from .aiopixivpy.datastructure_illust import (IllustDetail, IllustTag,
                                              PixivUserSummery,
                                              TrendingTagIllusts)
from .aiopixivpy.datastructure_user import PixivUserDetail, PixivUserPreview
from .aiopixivpy.pixivpy_typing import (PixivRecomMode, PixivSearchTarget,
                                        PixivSort)
from .file_tracing import FileEntry, FileTracingConfig
from .illust_bookmarking import IllustBookmark, IllustBookmarkingConfig
from .pixiv_image import DownloadProgress
from .wahu_methods.cli import CliScriptInfo
from .wahu_methods.illust_repo import FileEntryWithURL, RepoSyncAddReport
from .wahu_methods.lib_tag_utils import WeighedIllustTag, TagRegressionModel
from .wahu_methods.tag_statistic import CountedIllustTag

"""
暴露给前端的 dataclass
"""

exports = [PixivComment, PixivUserSummery, IllustTag, IllustDetail, PixivUserDetail,
           PixivUserPreview, IllustBookmark, FileEntry, TrendingTagIllusts,
           FileTracingConfig, RepoSyncAddReport, AccountSession,
           FileEntryWithURL, DownloadProgress, CliScriptInfo, WeighedIllustTag,
           CountedIllustTag, TagRegressionModel, IllustBookmarkingConfig]

exports_type = {
    'PixivRecomMode': PixivRecomMode,
    'PixivSearchTarget': PixivSearchTarget,
    'PixivSort': PixivSort}
