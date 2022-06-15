from pathlib import Path
import os
import shutil
import sys
from zipfile import ZIP_DEFLATED, ZipFile as ZipFileOriginal

backend_src = Path('wahu_backend')
frontend_emit = Path('dist/wahu_frontend')
dist_base = Path('dist/package_base')
dist_stuff = Path('dist_stuff')

COMPRESSION_METHOD = ZIP_DEFLATED
COMPRESSION_LEVEL = 9

if len(sys.argv) > 1 and sys.argv[1] == 'gui':
    gui_launcher = True
    dist_bundle = Path('dist/PixivWahu-win64-guilauncher.zip')
else:
    gui_launcher = False
    dist_bundle = Path('dist/PixivWahu-win64.zip')

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
              f' {dist_stuff}/launcher.c "{pypath}/python310.dll"')

def write_tkinter(zf: ZipFile):
        print('Write Tkinter stuff')

        pypath = Path(sys.executable).parent

        zf.write_dir(pypath / 'tcl', Path('tcl'))
        zf.write_dir(pypath / 'Lib' / 'tkinter', Path('tkinter'))
        zf.write(pypath / 'DLLs' / '_tkinter.pyd', '_tkinter.pyd')
        zf.write(pypath / 'DLLs' / 'tcl86t.dll', 'tcl86t.dll')
        zf.write(pypath / 'DLLs' / 'tk86t.dll', 'tk86t.dll')

def edit__path():
    with open(dist_base / 'python310._pth', 'a', encoding='utf-8') as wf:
        wf.write('\n./Lib/site-packages\n')

def remove_useless():
    try:
        shutil.rmtree(str(dist_base / 'Lib' / 'site-packages' / 'setuptools'))
        shutil.rmtree(str(dist_base / 'Lib' / 'site-packages' / 'setuptools'))
        shutil.rmtree(str(dist_base / 'Scripts'))
    except FileNotFoundError:
        pass

def main():

    remove_useless()

    edit__path()

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

        print('Write subscrip')
        zf.write(dist_stuff / 'ibd_subscrip.toml', 'user/ibd_subscrip.toml')

        if gui_launcher:
            print('Write Tkinter')
            write_tkinter(zf)

            print('Write GUI launcher script')
            zf.write(dist_stuff / 'WahuLauncher.ps1', 'WahuLauncher.ps1')


if __name__ == '__main__':
    main()
