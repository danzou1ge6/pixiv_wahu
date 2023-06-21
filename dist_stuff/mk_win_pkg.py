from pathlib import Path
import os
import shutil
import sys
from zipfile import ZIP_DEFLATED, ZipFile as ZipFileOriginal

backend_src = Path('wahu_backend')
frontend_emit = Path('dist/wahu_frontend')
dist_base = Path('dist/package_base')
dist_dir = Path('dist')
dist_stuff = Path('dist_stuff')
dist_bundle = Path('dist/PixivWahu-win64.zip')

COMPRESSION_METHOD = ZIP_DEFLATED
COMPRESSION_LEVEL = 9


class ZipFile(ZipFileOriginal):
    def write_dir(self, p: Path, arcname: Path):
        for item in p.iterdir():
            if item.is_file():
                self.write(item, arcname / item.relative_to(p))
            else:
                self.write_dir(item, arcname / item.relative_to(p))

def create_readme_html():
    with open('README.md', 'r', encoding='utf-8') as rf:
        mkd = '\n' + rf.read()
    with open(dist_stuff / 'README_template.html', 'r', encoding='utf-8') as rf:
        html = rf.read()
    html = html.replace('[% markdown %]', mkd)
    return html

def compile_launcher():

    print('Compiling CLI launcher')
    pypath = str(Path(sys.executable).parent).replace('\\', '/')

    cli_launcher_path = str(dist_base / 'PixivWahu.exe').replace('\\', '/')

    os.system(f'gcc -o "{cli_launcher_path}" -I "{pypath}/include"'
              f' {dist_stuff}/launcher.c "{pypath}/python310.dll" -municode')

def edit__path():
    with open(dist_base / 'python310._pth', 'a', encoding='utf-8') as wf:
        wf.write('\n./Lib/site-packages\n')

def download_embed_python():
    print(f'Downloading Python Embed to {dist_dir / "python.zip"}')
    os.system(f'curl -o {dist_dir / "python.zip"} https://www.python.org/ftp/python/3.10.4/python-3.10.4-embed-amd64.zip')

    print(f'Decompressing to {dist_base}')
    with ZipFile(dist_dir / 'python.zip', 'r') as zf:
        zf.extractall(dist_base)

def install_wheel():
    from os import listdir, system
    whl = [f for f in listdir(dist_dir) if f.endswith('.whl')][0]
    os.system(f'pipenv run pip install dist/{whl}[accelerate_fuzzywuzzy] --prefix dist/package_base -I')

def remove_useless():
    try:
        shutil.rmtree(str(dist_base / 'Lib' / 'site-packages' / 'setuptools'))
        shutil.rmtree(str(dist_base / 'Lib' / 'site-packages' / 'pkg_resources'))
        shutil.rmtree(str(dist_base / 'Scripts'))

        for package in ('aiohttp', 'wahu_backend.logistic_regression'):

            for item in (dist_base / 'Lib' / 'site-packages' / package).iterdir():
                if item.is_file() and item.suffix == '.c':
                    item.unlink()

    except FileNotFoundError:
        pass

def main():
    if dist_bundle.exists():
        dist_bundle.unlink()

    download_embed_python()

    install_wheel()  # from dist_dir / *.whl

    remove_useless()

    edit__path()

    compile_launcher()

    with ZipFile(dist_bundle, 'w', compression=COMPRESSION_METHOD,
        compresslevel=COMPRESSION_LEVEL) as zf:

        print('Write Python executables')
        zf.write_dir(dist_base, Path(''))

        print('Write entrance script and configuration')
        zf.write(dist_stuff / 'conf.toml', 'conf.toml')

        print('Write pre-built database')
        zf.write(dist_stuff / 'danzou1ge6.db', 'user/databases/danzou1ge6.db')
        zf.write(dist_stuff / 'my_favourite.db', 'user/databases/my_favourite.db')

        print('Write scripts')
        zf.write_dir(dist_stuff / 'cli_script', Path('user/scripts'))

        print('Write README')
        zf.writestr('README.html', create_readme_html())

        print('Write subscrip')
        zf.write(dist_stuff / 'ibd_subscrip.toml', 'user/ibd_subscrip.toml')


if __name__ == '__main__':
    main()
