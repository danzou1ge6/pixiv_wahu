from pathlib import Path
import os
from zipfile import ZIP_DEFLATED, ZipFile as ZipFileOriginal

backend_src = Path('wahu_backend')
frontend_emit = Path('dist/wahu_frontend')
dist_base = Path('dist/package_base')
dist_stuff = Path('dist_stuff')
dist_bundle = Path('dist/PixivWahu.zip')

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
        zf.write_dir(dist_base, Path(''))

        zf.write_dir(backend_src, Path('wahu_backend'))

        zf.write(dist_stuff / 'PixivWahu.ps1', 'PixivWahu.ps1')

        zf.write(dist_stuff / 'conf.toml', 'conf.toml')

        zf.write('dev_stuff/databases/danzou1ge6.db', 'user/databases/danzou1ge6.db')

        zf.write_dir(dist_stuff / 'token_getter', Path('token_getter'))
        zf.write(dist_stuff / 'GetToken.ps1', 'GetToken.ps1')

        zf.writestr('README.html', create_readme_html())

        zf.write_dir(frontend_emit, Path('static'))

if __name__ == '__main__':
    main()
