from pathlib import Path
import os
import sys
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

def compile_launcher():
    pypath = str(Path(sys.executable).parent).replace('\\', '/')

    output_path = str(dist_base / "PixivWahu.exe").replace('\\', '/')

    os.system(f'gcc -o "{output_path}" -I "{pypath}/include"'
              f' dist_stuff/launcher.c "{pypath}/python310.dll"')

def main():

    compile_launcher()

    with ZipFile(dist_bundle, 'w', compression=COMPRESSION_METHOD,
        compresslevel=COMPRESSION_LEVEL) as zf:

        print('Write Python executables')
        zf.write_dir(dist_base, Path(''))

        print('Write entrance script and configuration')
        zf.write(dist_stuff / 'conf.toml', 'conf.toml')
        zf.write(dist_stuff / 'GetToken.ps1', 'GetToken.ps1')

        print('Write pre-built database')
        zf.write(dist_stuff / 'danzou1ge6.db', 'user/databases/danzou1ge6.db')

        print('Write scripts')
        zf.write_dir(dist_stuff / 'cli_script', Path('user/scripts'))

        print('Write README')
        zf.writestr('README.html', create_readme_html())


if __name__ == '__main__':
    main()
