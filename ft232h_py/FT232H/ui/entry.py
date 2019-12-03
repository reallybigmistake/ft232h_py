from tkinter import *


def uart_entry(frm):
    fields = 'port', 'baudrate', 'parity', 'datasize', 'stopbit'
    entries = []
    vals = {}
    variables = []
    for field in fields:
        row = Frame(frm)
        lab = Label(row, width=10, text=field)
        ent = Entry(row)
        row.pack(side=TOP, fill=X)
        lab.pack(side=LEFT)
        ent.pack(side=RIGHT, expand=YES, fill=X)
        var = StringVar()
        ent.config(textvariable=var)
        variables.append(var)
        entries.append(ent)

    def getvalue():
        for idex, field in enumerate(fields):
            vals[field] = variables[idex].get()
        print(vals)
        frm.destroy()
    Button(frm, text='OK', command=getvalue).pack(
        side=BOTTOM, expand=YES, fill=X)

if __name__ == '__main__':
    root = Tk()
    uart_entry(root)
    mainloop()
