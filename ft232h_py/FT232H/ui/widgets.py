from tkinter import *
from tkinter.filedialog import askopenfilename, askdirectory
from entry import uart_entry


class Browerframe(Frame):

    def __init__(self, parent, **options):
        Frame.__init__(self, parent, **options)
        self.lab = Label(self, width=20)
        self.lab.pack(side=LEFT)
        self.ent = Entry(self)
        self.ent.pack(side=LEFT, expand=YES, fill=X)
        self.ent.config(width=40)
        self.but = Button(
            self, width=20, command=self.get_button_result)
        self.but.pack(side=LEFT)

    def settext(self, labeltext, buttontext):
        self.lab.config(text=labeltext)
        self.but.config(text=buttontext)

    def get_button_result(self):
        pass

    def getentry(self):
        return self.ent.get()


class Filebrower(Browerframe):

    def __init__(self, parent, **options):
        Browerframe.__init__(self, parent, **options)
        self.settext('Select image', 'Browse...')

    def get_button_result(self):
        self.val = askopenfilename()
        self.ent.delete(0, END)
        self.ent.insert(0, self.val)


class InterfaceSlector(Frame):

    def __init__(self, parent, **options):
        Frame.__init__(self, parent, **options)
        self.interfaces = ['UART', 'SPI', 'I2C']
        self.frm_left = Frame(self)
        Label(self.frm_left, text='downloaders').pack(side=TOP)
        self.var = StringVar()
        for i in self.interfaces:
            Radiobutton(self.frm_left, text=i, command=self.onPress,
                        variable=self.var, value=i).pack(anchor=NW)
        self.var.set(self.interfaces[0])
        self.frm_left.config(bd=5, relief=RIDGE)
        self.frm_left.pack(side=LEFT, expand=YES, fill=BOTH, padx=20, pady=30)

        self.frm_right = Frame(self)
        self.para_input = Interface_set(self.frm_right, 'UART')
        self.para_input.pack(fill=BOTH)
        self.frm_right.config(bd=5, relief=RIDGE)
        self.frm_right.pack(side=RIGHT)

    def onPress(self):
        pick = self.var.get()
        self.frm_right.destroy()
        self.frm_right = Frame(self)
        self.para_input = Interface_set(self.frm_right, pick)
        self.para_input.pack(fill=BOTH)
        self.frm_right.config(bd=5, relief=RIDGE)
        self.frm_right.pack(side=RIGHT)


class StartButton(Frame):

    def __init__(self, parent, **options):
        Frame.__init__(self, parent, **options)
        Button(self, text='Start', command=None,
               width=20).pack(expand=YES, fill=BOTH)
        # self.config(width=20)

    def onPress(self):
        pass


class Interface_set(Frame):

    def __init__(self, parent, interface,  **options):
        Frame.__init__(self, parent, **options)
        if interface == 'UART':
            self.fields = 'port', 'baudrate', 'parity', 'datasize', 'stopbit'
        elif interface == 'SPI':
            self.fields = 'speed', 'mode'
        elif interface == 'I2C':
            self.fields = 'speed', 'Addr', 'Reg'
        self.entries = []
        self.vals = {}
        self.variables = []
        self.make_input_fields()

    def make_input_fields(self):
        for field in self.fields:
            row = Frame(self)
            lab = Label(row, width=10, text=field)
            ent = Entry(row)
            row.pack(side=TOP, fill=X)
            lab.pack(side=LEFT)
            ent.pack(side=RIGHT, expand=YES, fill=X)
            var = StringVar()
            ent.config(textvariable=var)
            self.variables.append(var)
            self.entries.append(ent)
        Button(self, text='OK', command=self.getvalue).pack(
            side=BOTTOM, expand=YES, fill=X)

    def getvalue(self):
        for idex, field in enumerate(self.fields):
            self.vals[field] = self.variables[idex].get()
        print(self.vals)
        # self.destroy()


if __name__ == '__main__':
    root = Tk()
    InterfaceSlector(root).pack()
    mainloop()
