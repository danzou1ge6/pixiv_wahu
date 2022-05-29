from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, Optional


@dataclass
class WahuConfig:
    # local
    database_dir: Path
    repos_file: Path
    file_name_template: str
    temp_download_dir: Path
    cli_script_dir: Path
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

    original_dict: dict[str, Any]
