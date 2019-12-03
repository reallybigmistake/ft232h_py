# coding=utf-8
from download.dloader import Dloader
from download.serdloader import serDloader
from download.interface import I2C_downloader
from download.interface import SPI_downloader
from download.interface import UART_downloader
from download.pyser import UART_downloader as ser_downloader
from tkinter import *
from tkinter.filedialog import askopenfilename
from tkinter.scrolledtext import ScrolledText
from tkinter import ttk
import _thread as thread
import queue
import time
import os
import sys
from download.serdloader import serDloader
from list_com import listCom
import logging


class IOTextQueue:

    def __init__(self, queue):
        self.queue = queue

    def write(self, text):
        self.queue.put(text)

    def writelines(self, lines):
        for line in lines:
            self.write(line)

    def flush(self):
        print('flush')


class Browerframe(Frame):

    def __init__(self, parent=None, **options):
        Frame.__init__(self, parent, **options)
        self.var = StringVar()
        self.makeWidgets()

    def makeWidgets(self):
        self.lab = Label(self, text='select bin file')
        self.lab.pack(side=LEFT)
        self.ent = Entry(self, textvariable=self.var, width=40)
        self.ent.pack(side=LEFT, expand=YES, fill=X)
        self.but = Button(
            self, text='Browse...', command=self.onPress)
        self.but.pack(side=LEFT)
        self.pack()

    def get(self):
        return self.var.get()

    def onPress(self):
        self.var.set(askopenfilename())


class progressFrame(Frame):

    def __init__(self, parent=None, **options):
        Frame.__init__(self, parent, **options)
        self.labvar = StringVar()
        self.provar = IntVar()
        self.makeWidgets()

    def makeWidgets(self):
        self.lab = Label(self, text='downloading', textvariable=self.labvar)
        self.pro_bar = ttk.Progressbar(self, orient="horizontal", length=500,
                                       mode="determinate", maximum=100, value=0, variable=self.provar)
        self.pro_bar.pack()
        self.lab.pack()
        self.pack()

    def set(self, num):
        self.provar.set(num)

    def get(self):
        return self.provar.get()

    def setText(self, text):
        self.labvar.set(text)


class UartSetFrame(Frame):

    def __init__(self, parent=None, **options):
        Frame.__init__(self, parent, **options)
        self.com = StringVar()
        self.speed = StringVar()
        self.comlist = []
        self.settings = dict()
        self.speeds = ['115200', '1000000', '3000000']
        self.makeWidgets()
        self.onRefresh()

    def makeWidgets(self):
        self.com_lab = Label(self, text='COM')
        self.speed_lab = Label(self, text='SPEED')
        self.com_box = ttk.Combobox(
            self, justify='left', state='readonly', textvariable=self.com, values=self.comlist)
        self.speed_box = ttk.Combobox(
            self, justify='left', state='normal', textvariable=self.speed, values=self.speeds)
        self.img = PhotoImage(file='refresh.png')
        self.img = self.img.subsample(5)
        self.refresh_btn = Button(self, image=self.img, command=self.onRefresh)
        self.refresh_btn.grid(row=1, column=0, padx=10)
        self.com_lab.grid(row=0, column=1, padx=10)
        self.speed_lab.grid(row=0, column=2, padx=10)
        self.com_box.grid(row=1, column=1, padx=10)
        self.speed_box.grid(row=1, column=2, padx=10)
        self.speed.set(self.speeds[0])
        self.pack()

    def updateCom(self, comlist):
        self.comlist = comlist

    def onRefresh(self):
        com_state = listCom()
        self.comlist = []
        coms = com_state.keys()
        for com in coms:
            self.comlist.append(
                com + (' (busy)' if not com_state[com] else ''))
        self.com.set(self.comlist[0])
        self.com_box.config(values=self.comlist)

    def getSetting(self):
        self.settings['com'] = self.com.get()
        self.settings['baud'] = self.speed.get()
        return self.settings


class AutoDownload(Frame):

    def __init__(self, parent=None, **options):
        Frame.__init__(self, parent, **options)
        self.chk_var = IntVar()
        self.lab_var = StringVar()
        self.txt_var = StringVar()
        self.makeWidgets()

    def makeWidgets(self):
        self.lab_var.set('(0/0)')
        self.btn = Button(self, text='Download')
        self.chkbtn = Checkbutton(
            self, text='Auto', variable=self.chk_var, command=self.onCheck)
        self.lab = Label(self, textvariable=self.lab_var)
        self.ent = Entry(self, textvariable=self.txt_var, width=5)
        self.btn.grid(row=0, column=0, padx=10)
        self.chkbtn.grid(row=0, column=1, padx=10)
        self.pack()

    def setDownload(self, callback):
        self.btn.config(command=callback)

    def onCheck(self):
        if self.chk_var.get():
            self.lab.grid(row=0, column=2, padx=10)
            self.ent.grid(row=0, column=3, padx=10)
        else:
            self.lab.grid_forget()
            self.ent.grid_forget()

    def setCount(self, num, total):
        self.lab_var.set('(%d/%d)' % (num, total))

    def getCount(self):
        try:
            count = int(self.txt_var.get())
        except ValueError:
            logging.error('not digital')
            return 1
        else:
            return count

    def isAuto(self):
        return self.chk_var.get()

    def responsible(self, value):
        if value:
            state = NORMAL
        else:
            state = DISABLED
        self.btn.config(state=state)
        if self.isAuto():
            self.ent.config(state=state)


class DownloadFrame(Frame):

    def __init__(self, parent=None, **options):
        Frame.__init__(self, parent, **options)
        self.makeWidgets()
        self.threadQueue = queue.Queue()
        self.textQueue = queue.Queue()
        self.textIO = IOTextQueue(self.textQueue)
        self.savestreams = sys.stdout
        sys.stdout = self.textIO
        self.threadChecker()
        sys.stdout = self.savestreams

    def makeWidgets(self):
        self.browerframe = Browerframe(self)
        self.progressframe = progressFrame(self)
        self.uartsetframe = UartSetFrame(self)
        self.downloadframe = AutoDownload(self)
        self.browerframe.pack()
        self.progressframe.pack()
        self.uartsetframe.pack()
        self.downloadframe.pack()
        self.pack(fill=BOTH, expand=YES)
        self.dloadbtn = Button(self, text='Downlaod', command=self.onPress)
        # self.dloadbtn.pack()
        self.downloadframe.setDownload(self.onPress)
        self.text = ScrolledText(self)
        self.text.pack(fill=BOTH, expand=YES)

    def updateInProgress(self, stage, progress):
        self.threadQueue.put((self.progressframe.setText, (stage,)))
        self.threadQueue.put((self.progressframe.set, (progress,)))

    def onPress(self):
        self.timer_start = time.time()
        self.com_setting = self.uartsetframe.getSetting()
        self.infile = self.browerframe.get()
        self.dev = ser_downloader(COM=self.com_setting['com'])
        if self.downloadframe.isAuto():
            self.totalcycle = self.downloadframe.getCount()
            self.currentcycle = 1
            self.downloadframe.setCount(self.currentcycle, self.totalcycle)
        self.dl = serDloader(self.infile, self.dev,
                             int(self.com_setting['baud']))
        self.dl.configProgFunc(self.updateInProgress)

        self.downloadframe.responsible(False)

        thread.start_new_thread(
            self.threaded, (self.dl.boot, (), (), self.onExit, self.onFail, None))

    def totext(self, i):
        binname = os.path.split(self.browerframe.get())[1]
        com = self.uartsetframe.getSetting()['com']
        self.progressframe.set(i / 100 * 100)
        self.text.insert('end', binname + '\t%s\n' % (com))
        self.text.see('end')

    def fakedata(self):
        for i in range(101):
            self.threadQueue.put((self.totext, (i,)))
            time.sleep(0.05)

    def threadChecker(self, delayMsecs=100, perEvent=10):
        self.text.update()
        for i in range(perEvent):
            try:
                (callback, args) = self.threadQueue.get(block=False)

            except queue.Empty:
                break
            else:
                callback(*args)
        logs = []
        for i in range(self.textQueue.qsize()):
            logs.append(self.textQueue.get(block=False))
        if logs:
            logtext = ''.join(logs)
            self.text.insert('end', logtext + '\n')
            self.text.see('end')

        self.after(delayMsecs, lambda: self.threadChecker(
            delayMsecs, perEvent))

    def threaded(self, action, args, context, onExit, onFail, onProgress):
        try:
            if not onProgress:
                action(*args)
            else:
                def progress(*any):
                    self.threadQueue.put((onProgress, any + context))
                action(*args, progress=progress)
        except Exception:
            self.threadQueue.put((onFail, (sys.exc_info(),) + context))
        else:
            self.threadQueue.put((onExit, context))

    def onExit(self):
        self.time_end = time.time()
        self.text.insert('end', 'Download finish %0.2fs\n' %
                         (self.timer_start - self.time_end))
        self.text.see('end')
        self.text.update()
        self.downloadframe.responsible(True)
        if self.downloadframe.isAuto() and self.currentcycle < self.totalcycle:
            thread.start_new_thread(self.delayThread, (3000,))
            self.downloadframe.responsible(False)

    def onFail(self, exc_info):
        self.text.insert('end', 'Download fail\t%s\n' % (exc_info[0]))
        self.text.see('end')

    def onProgress(self):
        pass

    def delayThread(self, msecs):
        time.sleep(msecs / 1000)
        self.currentcycle += 1
        self.threadQueue.put((self.downloadframe.setCount,
                              (self.currentcycle, self.totalcycle)))
        self.timer_start = time.time()
        self.threadQueue.put((thread.start_new_thread, (self.threaded,
                                                        (self.dl.boot, (), (), self.onExit, self.onFail, None))))

if __name__ == '__main__':
    root = Tk()
    DownloadFrame(root)
    mainloop()
