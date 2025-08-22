import tkinter.messagebox



class Log:
    @staticmethod
    def log(cls, msg: str):
        print(msg)

    @staticmethod
    def info(cls, msg: str):
        tkinter.messagebox.showinfo("Application log", msg)
    
    @staticmethod
    def info(cls, title:str, msg: str):
        tkinter.messagebox.showinfo(title, msg)

    @staticmethod
    def warn(cls, msg: str):
        tkinter.messagebox.showwarning("Application log", msg)
    
    @staticmethod
    def warn(cls, title:str, msg: str):
        tkinter.messagebox.showwarning(title, msg)

    @staticmethod
    def error(cls, msg: str):
        tkinter.messagebox.showerror("Application log", msg)
    
    @staticmethod
    def error(cls, title:str, msg: str):
        tkinter.messagebox.showerror(title, msg)