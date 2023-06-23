from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, Optional


if TYPE_CHECKING:
    from ..wahu_config.load_config import WPath


@dataclass(slots=True)
class WahuConfig:
    wpath: 'WPath'
    # local
    database_dir: Path
    repos_file: Path
    file_name_template: str
    temp_download_dir: Path
    cli_script_dir: Path
    tag_model_dir: Path
    # network
    doh_urls: Optional[list[str]]
    doh_ssl: bool
    # pixiv
    refresh_token_path: Optional[Path]
    account_session_path: Path
    illust_detail_pool_size: int
    api_timeout: float
    api_host_ip: Optional[str]
    tag_language: Literal['en-us', 'zh-cn']
    api_connection_limit: int
    # image
    image_timeout: float
    image_host_ip: Optional[str]
    fallback_image_size: Literal['original', 'medium', 'large', 'square_medium']
    image_connection_limit: int
    image_num_parallel: int
    image_download_record_size: int
    # app
    server_host: str
    server_port: int
    agenerator_pool_size: int
    image_pool_size: int
    default_fuzzy_cutoff: int
    # log
    log_rpc_ret_length: int
    # pylogging
    pylogging_cfg_dict: dict[str, Any]

    original_dict: dict[str, Any]
