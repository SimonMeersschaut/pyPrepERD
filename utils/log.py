import tkinter.messagebox



class Log:
    def log(msg: str):
        print(msg)

    def info(msg: str):
        tkinter.messagebox.showinfo("Application log", msg)
    
    def info(title:str, msg: str):
        tkinter.messagebox.showinfo(title, msg)

    def warn(msg: str):
        tkinter.messagebox.showwarning("Application log", msg)
    
    def warn(title:str, msg: str):
        tkinter.messagebox.showwarning(title, msg)

    def error(msg: str):
        tkinter.messagebox.showerror("Application log", msg)
    
    def error(title:str, msg: str):
        tkinter.messagebox.showerror(title, msg)