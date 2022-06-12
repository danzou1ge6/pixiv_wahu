import asyncio
import logging
import os
from tkinter import *
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import webbrowser
from aiohttp import web

from wahu_backend.wahu_config import load_config, ConfigLoadError
from wahu_backend.wahu_core import WahuContext
from wahu_backend.wahu_webapi.server import create_app
from wahu_backend.root_logger import logger

from .log_window import LogWindow

DEFAULT_CONF_PATH = os.environ.get('PIXIVWAHU_CONFPATH', 'user/conf.toml')


class Launcher:

    def __init__(self):

        # -------------------------------------------------- root frames

        self.root = Tk()
        self.root.title('PixivWahu Launcher')

        varmainframe = ttk.Frame(self.root, padding="2 2 2 2")
        varmainframe.grid(column=0, row=0, sticky='nsw')

        ctlframe = ttk.Frame(self.root, padding='2 2 2 2')
        ctlframe.grid(column=1, row=0, sticky='nse')

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0 ,weight=1)

        # -------------------------------------------------- var frame

        # row 配置文件

        self.conf_path = StringVar(value=DEFAULT_CONF_PATH)

        ttk.Label(varmainframe, text='配置文件').grid(column=0, row=0, sticky='w')

        self.conf_path_lb = ttk.Label(
            varmainframe, textvariable=self.conf_path, width='5c')
        self.conf_path_lb.grid(column=1, row=0, sticky='nwes')

        ttk.Button(
            varmainframe, text='选择', width='1c',
            command=self.select_conf_file).grid(column=2, row=0, sticky='e')

        # row 主机

        self.host = StringVar()

        ttk.Label(varmainframe, text='主机').grid(column=0, row=1, sticky='wne')

        self.host_input = ttk.Entry(varmainframe, textvariable=self.host)
        self.host_input.grid(column=1, row=1, columnspan=2, sticky='wne')

        # row 端口

        self.port = StringVar()

        ttk.Label(varmainframe, text='端口').grid(column=0, row=2, sticky='wne')

        self.port_input = ttk.Entry(varmainframe, textvariable=self.port)
        self.port_input.grid(column=1, row=2, columnspan=2, sticky='wne')


        # -------------------------------------------------- ctl frame

        # button 启动

        self.launch_btn = ttk.Button(ctlframe, text='启动', command=self.launch)
        self.launch_btn.grid(column=0, row=0)

        # button 停止

        self.kill_btn = ttk.Button(
            ctlframe, text='停止', command=self.kill, state='disabled')
        self.kill_btn.grid(column=0, row=1)

        # button 浏览器

        self.browser_btn = ttk.Button(
            ctlframe, text='打开浏览器', command=self.browser, state='disabled'
        )
        self.browser_btn.grid(column=0, row=2)

        # button 帮助文件

        ttk.Button(ctlframe, text='帮助', command=self.help_file) \
            .grid(column=0, row=3)

        # -------------------------------------------------- misc

        self.loop = asyncio.new_event_loop()


    def select_conf_file(self, *args):

        p = filedialog.askopenfile('r', defaultextension='.toml')
        if p is None:
            return

        self.conf_path.set(p.name)

    def launch(self, *args):
        """
        - 加载配置文件
        - 创建日志窗口
        - 创建服务器
        - 启动服务器
        - 打开浏览器
        """

        try:
            conf_path = Path(self.conf_path.get())
            self.conf = load_config(conf_path)
        except FileNotFoundError:
            messagebox.showerror('配置文件错误', f'文件 {conf_path} 不存在')
            return
        except ConfigLoadError as e:
            messagebox.showerror('配置文件错误', f'{e}')
            return

        # 使用 conf.pylogging.formatters.standard 作为格式器配置
        self.log_window = LogWindow(self.root)
        hdlr = logging.StreamHandler(self.log_window)
        fmtr = logging.Formatter(
            fmt=self.conf.pylogging_cfg_dict['formatters']['standard']['format'],
            datefmt=self.conf.pylogging_cfg_dict['formatters']['standard']['datefmt']
        )
        hdlr.setFormatter(fmtr)
        hdlr.setLevel(logging.DEBUG)

        logger.addHandler(hdlr)

        self.wctx = WahuContext(self.conf)
        web_app = create_app(self.wctx)

        if self.host.get() != '':
            self.conf.server_host = self.host.get()
        if self.port.get() != '':
            self.conf.server_port = self.port.get()

        async def main():
            self.app_runner = web.AppRunner(web_app)
            await self.app_runner.setup()
            logger.info(f'后端在 {self.conf.server_host}:{self.conf.server_port} 上启动')
            site = web.TCPSite(
                self.app_runner, self.conf.server_host, self.conf.server_port)
            await site.start()

        self.loop.create_task(main())
        self.launch_btn.state(['disabled'])
        self.browser_btn.state(['!disabled'])
        self.kill_btn.state(['!disabled'])

        self.browser()

    def kill(self, *args):
        """
        - 调用 WahuContext.cleanup
        - 关闭日志窗口
        """

        async def main():
            await self.wctx.cleanup()
            await self.app_runner.cleanup()
            self.log_window.destroy()

        self.loop.create_task(main())

        self.launch_btn.state(['!disabled'])
        self.browser_btn.state(['disabled'])
        self.kill_btn.state(['disabled'])

    def browser(self, *args):
        hst = '127.0.0.1' if self.conf.server_host == '0.0.0.0' else self.conf.server_host
        webbrowser.open(
            f'http://{hst}:{self.conf.server_port}/index.html')

    def help_file(self, *args):
        p = Path('./README.html').resolve()
        webbrowser.open(f'file://{p}')

    async def mainloop(self):
        """使用 asyncio 循环代替 tk 的事件循环"""

        while True:
            self.root.update()
            await asyncio.sleep(0.05)

    def run_forever(self):
        self.loop.create_task(self.mainloop())
        self.loop.run_forever()

def main():
    launcher = Launcher()
    launcher.run_forever()

if __name__ == '__main__':
    main()
