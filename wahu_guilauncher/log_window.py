from tkinter import *
from tkinter import ttk


class LogWindow:

    def __init__(self, parent, log_lines=100):

        self.log_lines = log_lines

        self.root = Toplevel(parent)
        self.root.title('PixivWahu Logging')
        self.root.geometry('400x250')

        self.root.protocol('WM_DELETE_WINDOW', lambda : None)

        mainframe = ttk.Frame(self.root, padding="2 2 2 2")
        mainframe.grid(column=0, row=0, sticky='nwes')
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0 ,weight=1)

        self.text = Text(mainframe)
        self.text.grid(column=0, row=0, sticky='new')
        mainframe.columnconfigure(0, weight=1)
        mainframe.rowconfigure(0, weight=1)

        scrollbar = ttk.Scrollbar(mainframe, orient='vertical', command=self.text.yview)
        scrollbar.grid(column=1, row=0, sticky='nes')
        self.text['yscrollcommand'] = scrollbar.set

    def write(self, msg):

        numlines = int(self.text.index('end -1 line').split('.')[0])
        self.text['state'] = 'normal'
        if numlines == self.log_lines:
            self.text.delete('1.0', '2.0')
        self.text.insert('end', msg)
        self.text.yview_moveto(1.0)
        self.text['state'] = 'disabled'

    def flush(self):
        pass

    def destroy(self):
        self.root.destroy()

