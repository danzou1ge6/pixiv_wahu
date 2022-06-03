from pathlib import Path

import toml

from .config_exceptions import (ConfigLoadBadPath, ConfigLoadError,
                                ConfigLoadKeyError)
from .config_object import WahuConfig

from ..manual_dns.dns_resolve import set_doh_url


def load_config(config_file: Path) -> WahuConfig:
    d = toml.load(config_file)

    try:
        # local
        database_dir = Path(d['local']['database_dir'])
        repos_file = Path(d['local']['repos_file'])
        file_name_template = d['local']['file_name_template']
        temp_download_dir = Path(d['local']['temp_download_dir'])
        cli_script_dir = Path(d['local']['cli_script_dir'])

        # pixiv
        refresh_token_path = d['pixiv'].get('refresh_token_path', None)
        account_session_path = Path(d['pixiv']['account_session_path'])

        if refresh_token_path is not None:
            refresh_token_path = Path(refresh_token_path)
        else:
            refresh_token_path = None

        illust_detail_pool_size = d['app'].get('illust_detail_pool_size', 1000)

        api_timeout = d['pixiv']['timeout']

        api_host_ip = d['pixiv'].get('host_ip', None)
        api_host_ip = None if api_host_ip == -1 else api_host_ip

        tag_language = d['pixiv']['tag_language']
        api_connection_limit = d['pixiv'].get('connection_limit', 20)

        # image
        image_timeout = d['image']['timeout']

        image_host_ip = d['image'].get('host_ip', None)
        image_host_ip = None if image_host_ip == -1 else image_host_ip

        fallback_image_size = d['image']['fallback_size']
        if fallback_image_size not in {'original', 'medium', 'large', 'square_medium'}:
            raise ConfigLoadError(f'不支持的图片大小 {fallback_image_size}')

        image_connection_limit = d['image'].get('connection_limit', 7)
        image_num_parallel = d['image'].get('num_parallel', 2)
        image_download_record_size = d['image'].get('download_record_size', 100)

        # app
        server_host = d['app']['server_host']
        server_port = d['app']['server_port']
        agenerator_pool_size = d['app'].get('agenerator_pool_size', 200)
        image_pool_size = d['app'].get('image_pool_size', 100)
        default_fuzzy_cutoff = d['app'].get('default_fuzzy_cutoff', 80)
        doh_urls = d['app'].get('dns_over_https_urls', None)

        # logging
        log_rpc_ret_length = d['logging'].get('rpc_return_length', 1000)

        # pylogging
        pylogging_cfg_dict = d['pylogging']

        # 全局设定
        if doh_urls is not None:
            set_doh_url(doh_urls)

    except KeyError as ke:
        raise ConfigLoadKeyError(ke.args[0]) from ke

    for p in (database_dir, cli_script_dir):
        if not p.exists():
            raise ConfigLoadBadPath(p)

    return WahuConfig(
        database_dir=database_dir,
        repos_file=repos_file,
        file_name_template=file_name_template,
        refresh_token_path=refresh_token_path,
        temp_download_dir=temp_download_dir,
        cli_script_dir=cli_script_dir,
        account_session_path=account_session_path,
        illust_detail_pool_size=illust_detail_pool_size,
        api_timeout=api_timeout,
        api_host_ip=api_host_ip,
        tag_language=tag_language,
        api_connection_limit=api_connection_limit,
        image_timeout=image_timeout,
        image_host_ip=image_host_ip,
        fallback_image_size=fallback_image_size,
        image_connection_limit=image_connection_limit,
        image_num_parallel=image_num_parallel,
        image_download_record_size=image_download_record_size,
        server_host=server_host,
        server_port=server_port,
        agenerator_pool_size=agenerator_pool_size,
        image_pool_size=image_pool_size,
        default_fuzzy_cutoff=default_fuzzy_cutoff,
        log_rpc_ret_length=log_rpc_ret_length,
        pylogging_cfg_dict=pylogging_cfg_dict,
        original_dict=d
    )
