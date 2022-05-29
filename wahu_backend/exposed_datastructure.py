from .aiopixivpy.datastructure_comment import PixivComment
from .aiopixivpy.datastructure_illust import PixivUserSummery, IllustDetail, IllustTag
from .aiopixivpy.datastructure_user import PixivUserDetail, PixivUserPreview
from .aiopixivpy.api_base import AccountSession

from .aiopixivpy.pixivpy_typing import PixivRecomMode, PixivSearchTarget, PixivSort


from .illust_bookmarking import IllustBookmark, IllustBookmarkingConfig
from .file_tracing import FileEntry, FileTracingConfig

from .wahu_methods.illust_repo import RepoSyncAddReport, FileEntryWithURL
from .wahu_methods.cli import CliScriptInfo

from .pixiv_image import DownloadProgress

"""
暴露给前端的 dataclass
"""

exports = [PixivComment, PixivUserSummery, IllustTag, IllustDetail, PixivUserDetail,
           PixivUserPreview, IllustBookmark, IllustBookmarkingConfig, FileEntry,
           FileTracingConfig, RepoSyncAddReport, AccountSession,
           FileEntryWithURL, DownloadProgress, CliScriptInfo]

exports_type = {
    'PixivRecomMode': PixivRecomMode,
    'PixivSearchTarget': PixivSearchTarget,
    'PixivSort': PixivSort}
