from pathlib import Path
import os
from zipfile import ZIP_DEFLATED, ZipFile as ZipFileOriginal

backend_src = Path('wahu_backend')
frontend_emit = Path('dist/wahu_frontend')
dist_base = Path('dist/package_base')
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

def main():
    with ZipFile(dist_bundle, 'w', compression=COMPRESSION_METHOD,
        compresslevel=COMPRESSION_LEVEL) as zf:

        print('写入 Python 可执行档')
        zf.write_dir(dist_base, Path(''))

        print('写入入口脚本及配置')
        zf.write(dist_stuff / 'PixivWahu.ps1', 'PixivWahu.ps1')
        zf.write(dist_stuff / 'conf.toml', 'conf.toml')
        zf.write(dist_stuff / 'GetToken.ps1', 'GetToken.ps1')

        print('写入预置数据库')
        zf.write(dist_stuff /' databases/danzou1ge6.db', 'user/databases/danzou1ge6.db')

        print('写入 README')
        zf.writestr('README.html', create_readme_html())


if __name__ == '__main__':
    main()
