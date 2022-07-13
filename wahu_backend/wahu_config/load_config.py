import os
from pathlib import Path

import toml

from .config_exceptions import (ConfigLoadBadPath, ConfigLoadError,
                                ConfigLoadKeyError)
from .config_object import WahuConfig
from logging import config as log_cfg

from ..manual_dns.dns_resolve import set_doh_ssl, set_doh_url


class WPath:
    """
    `Path` 的工厂函数类，用于带入配置文件中指定的路径常量
    """

    def __init__(self, path_constants: dict[str, str]):
        self.path_constants = path_constants

    def __call__(self, p: str) -> Path:
        try:
            pth = Path(p.format(**self.path_constants))
            return pth

        except KeyError as ke:
            raise KeyError(f'找不到路径常量 {ke.args}')


def load_config(config_file: Path) -> WahuConfig:
    d = toml.load(config_file)

    try:

        # path
        path_constants = d.get('path', {})

        for k in path_constants.keys():
            if path_constants[k].startswith('$env:'):
                envvar_val = os.getenv(path_constants[k][4:])
                if envvar_val is None:
                    raise ConfigLoadBadPath(path_constants[k])
                path_constants[k] = envvar_val

        path_constants['$this'] = str(config_file.parent)

        wpath = WPath(path_constants)


        # local
        database_dir = wpath(d['local']['database_dir'])
        repos_file = wpath(d['local']['repos_file'])
        file_name_template = d['local']['file_name_template']
        temp_download_dir = wpath(d['local']['temp_download_dir'])
        cli_script_dir = wpath(d['local']['cli_script_dir'])
        tag_model_dir = wpath(d['local']['tag_model_dir'])

        # pixiv
        refresh_token_path = d['pixiv'].get('refresh_token_path', None)
        account_session_path = wpath(d['pixiv']['account_session_path'])

        if refresh_token_path is not None:
            refresh_token_path = wpath(refresh_token_path)
        else:
            refresh_token_path = None

        illust_detail_pool_size = d['app'].get('illust_detail_pool_size', 1000)

        api_timeout = d['pixiv']['timeout']

        api_host_ip = d['pixiv'].get('host_ip', None)

        tag_language = d['pixiv']['tag_language']
        api_connection_limit = d['pixiv'].get('connection_limit', 20)

        # image
        image_timeout = d['image']['timeout']

        image_host_ip = d['image'].get('host_ip', None)

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

        # network
        doh_urls = d['app'].get('dns_over_https_urls', None)
        doh_ssl = d['app'].get('dns_over_https_ssl', True)

        # logging
        log_rpc_ret_length = d['logging'].get('rpc_return_length', 1000)

        # pylogging
        pylogging_cfg_dict = d['pylogging']


    except KeyError as ke:
        raise ConfigLoadKeyError(ke.args[0]) from ke

    for p in (database_dir, cli_script_dir):
        if not p.exists():
            raise ConfigLoadBadPath(p)

    return WahuConfig(
        wpath=wpath,
        database_dir=database_dir,
        repos_file=repos_file,
        file_name_template=file_name_template,
        refresh_token_path=refresh_token_path,
        temp_download_dir=temp_download_dir,
        cli_script_dir=cli_script_dir,
        tag_model_dir=tag_model_dir,
        doh_urls=doh_urls,
        doh_ssl=doh_ssl,
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

def conf_side_effects(conf: WahuConfig):
    """
    设置日志，模块级配置
    """
    # pylogging
    log_cfg.dictConfig(conf.pylogging_cfg_dict)

    # 全局设定
    if conf.doh_urls is not None:
        set_doh_url(conf.doh_urls)
        set_doh_ssl(conf.doh_ssl)

