from tkinter import *
from widgets import *
root = Tk()
root.title('download')
parent = Frame(root)
parent.config(bd=8, relief=FLAT)
parent.config(height=500, width=1000)
parent.pack()


mainleft = Frame(parent)
mainleft.config(bd=8, relief=SUNKEN, bg='#ecffcc')
mainleft.config(height=500, width=500)
mainleft.pack(side=LEFT, fill=Y)


mainright = Frame(parent)
mainright.config(bd=8, relief=SUNKEN, bg='#ecffcc')
mainright.config(height=500, width=500)
mainright.pack(side=LEFT, fill=Y)


left1 = Filebrower(mainleft)
left1.config(bd=5, relief=RIDGE, pady=10)
left1.pack()


left2 = InterfaceSlector(mainleft)
left2.pack(fill=BOTH)

def getval():
    img = left1.val
    interface_para = left2.para_input.vals
    print(img)
    print(interface_para)


left3 = Frame(mainleft)
left3.config(bd=5, relief=RIDGE)
# StartButton(left3).pack(pady=20)
Button(left3, text='start', command=getval).pack(pady=20)
left3.pack(side=TOP, fill=X)



mainloop()
