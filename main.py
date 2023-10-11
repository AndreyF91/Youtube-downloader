from pytube import YouTube
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from threading import *
from PIL import Image, ImageTk
from urllib.request import urlretrieve
import datetime
import re
import os

def finish():
    root.destroy()  # ручное закрытие окна и всего приложения
    os.remove('./thumb.jpg')
    print("Закрытие приложения")

def threading(yt, msgBox):
    # Call work function
    t1=Thread(target=download, args=(yt, msgBox))
    t1.start()

def download(n, msgBox):
    arr = []
    arr.append(varVideo.get())
    arr.append(varAudio.get())
    arr = list(filter(None, arr))
    if varAudio.get() or varVideo.get(): 
        msgBox.config(
            background="yellow",
            foreground="black",
            text="Загрузка началась. Ждите!",
            font=("Arial, 12")
        )
        msgBox.pack(side="left", expand=1)
        output_path = filedialog.askdirectory()
        for i in arr:
            stream = n.streams.get_by_itag(i[1:-1])
            stream_title = re.sub('[^a-zA-Zа-яА-Я0-9-_*. ()]', '', stream.title)
            if stream.type == "audio":
                stream.download(output_path, filename=f"{stream_title}.mp3" if audioMp3.get() == 1 else None)
            else:
                stream.download(output_path, filename=f"{stream_title}")
        msgBox.config(
            background="green",
            foreground="white",
            text="Загрузка завершена",
            font=("Arial, 12")
        )       
    else:  
        msgBox.config(
            background="red",
            foreground="white",
            text="Нужно выбрать файл",
            font=("Arial, 12")
        )
        msgBox.pack(side="left", expand=1)
    

def buildVideo(yt, videoWindow, var):
    arr = []
    for i in yt.streams.filter(type="video"):
        j = i.resolution[:-1]
        if int(j) > 360:
            arr.append(i)
    j = 0
    s = ttk.Style()
    s.configure("Wild.TRadiobutton", background="white", font=8)
    for i in arr:
        type = (i.mime_type).replace("video/", "")
        ttk.Radiobutton(
            videoWindow,
            style="Wild.TRadiobutton",
            text=f'{type} : {i.resolution} : {round(i.filesize_mb)}MB {"" if i.is_progressive else "(Без аудио)"}',
            variable=var,
            value={i.itag},
        ).grid(column=0, row=j, sticky="w", padx=4, pady=4, ipadx=5, ipady=5)
        j = j + 1


def buildAudio(yt, audioWindow, varAudio):
    j = 0
    s = ttk.Style()
    s.configure("Wild.TRadiobutton", background="white", font=8)
    for i in yt.streams.filter(only_audio=True):
        type = (i.mime_type).replace("audio/", "")
        ttk.Radiobutton(
            audioWindow,
            style="Wild.TRadiobutton",
            text=f"{type} : {i.abr} : {round(i.filesize_mb)}MB",
            value={i.itag},
            variable=varAudio,
        ).grid(column=0, row=j, sticky="w", padx=4, pady=4, ipadx=5, ipady=5)
        j = j + 1

def showInfo():
    print("Начало запроса")
    yt = YouTube(txt.get())
    print("Конец запроса")
    logoLbl.pack_forget()
    dWindow.pack_forget()
    txt.delete(0, END)

    frame_top = Frame(root, background="white", padx=10, width=850)
    frame_top.config(highlightbackground="black", highlightthickness=2)
    frame_top.grid(column=0, row=0, padx=5, sticky="we")
    frame_bot = Frame(root, background="white", width=850)
    frame_bot.grid(column=0, row=2, sticky="we", padx=2)
    frame_bot.columnconfigure(index=0, weight=1)
    frame_bot.columnconfigure(index=2, weight=1)
    frame_btns = Frame(root, background="white", borderwidth=1, relief=SOLID)
    frame_btns.config(borderwidth=0, highlightthickness=0)
    frame_btns.grid(
        column=0,
        row=1,
        sticky="we",
        pady=15,
        padx=3
    )

    urlretrieve(yt.thumbnail_url, "thumb.jpg")
    img = Image.open("thumb.jpg")
    img = img.resize((200, 150), Image.LANCZOS)
    res = ImageTk.PhotoImage(img)

    thumb = Label(frame_top, image=res, width=195, height=160, background="white")
    thumb.image = res
    thumb.grid(row=0, column=0, rowspan=4)

    title = Label(
        frame_top,
        text=yt.title,
        height=3,
        font="Arial 20 bold",
        width=36,
        wraplength="145m",
        background="white",
    )
    title.grid(row=0, column=2, sticky="wens")
    author = Label(
        frame_top,
        text=f"Автор: {yt.author}",
        justify=RIGHT,
        anchor="e",
        background="white",
        font="Arial 9 bold",
    )
    author.grid(row=1, column=2, sticky="wens")
    time = Label(
        frame_top,
        text=f"Длительность: {str(datetime.timedelta(seconds=yt.length))}",
        justify=RIGHT,
        background="white",
        anchor="e",
        font="Arial 9 bold",
    )
    time.grid(row=2, column=2, sticky="wens")
    viewers = Label(
        frame_top,
        text=f"Просмотров: {yt.views}",
        justify=RIGHT,
        background="white",
        anchor="e",
        font="Arial 9 bold",
    )
    viewers.grid(row=3, column=2, sticky="wens")

    videoWindow = LabelFrame(frame_bot, text="Видео", background="white")
    videoWindow.grid(column=0, row=0, sticky="nswe", padx=2, columnspan=2)
    audioWindow = LabelFrame(frame_bot, text="Аудио", background="white")
    audioWindow.grid(column=2, row=0, sticky="nswe", padx=2, columnspan=2)

    buildVideo(yt, videoWindow, varVideo)
    buildAudio(yt, audioWindow, varAudio)

    audioCheckbox = Checkbutton(frame_btns, text="Сохранять аудио в mp3-формате?", variable=audioMp3, background='white')
    resetBtn = Button(frame_btns, text="Заново", width=13, font=8, command=lambda : reset(frame_top, frame_bot, frame_btns))
    msgBox = Label(frame_btns, text="Test")
    downloadBtn = Button(
        frame_btns, text="Скачать", width=13, font="8", command=lambda: threading(yt, msgBox), state=['normal']
    )
    audioCheckbox.pack(side="left")
    downloadBtn.pack(side="right", padx=5)
    resetBtn.pack(side="right")

def validateEntry():
    input_data = txt.get()
    if input_data:
        if re.match(
            "^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube(-nocookie)?\.com|youtu\.be))(\/(?:[\w\-]+\?v=|embed\/|live\/|v\/)?)([\w\-]+)(\S+)?$",
            input_data,
        ):
            valMes.grid_forget()
            showInfo()
        else:
            valMes.grid(column=0, row=1)
            valMes.config(
                text="Некорректная ссылка на Youtube-видео", foreground="red", font="8"
            )
    else:
        valMes.grid(column=1, row=1)
        valMes.config(text="Введите ссылку в поле ввода", foreground="red", font="8")


def _onKeyRelease(event):
    ctrl = (event.state & 0x4) != 0
    if event.keycode == 88 and ctrl and event.keysym.lower() != "x":
        event.widget.event_generate("<<Cut>>")

    if event.keycode == 86 and ctrl and event.keysym.lower() != "v":
        event.widget.event_generate("<<Paste>>")

    if event.keycode == 67 and ctrl and event.keysym.lower() != "c":
        event.widget.event_generate("<<Copy>>")

def reset(fr1, fr2, fr3):
    fr1.grid_forget()
    fr2.grid_forget()
    fr3.grid_forget()
    initFirst()

def initFirst():
    logoLbl.pack(pady=50)    
    dWindow.pack()    
    txt.grid(column=0, row=0, padx=5, ipady=2)
    txt.focus()
    btn.grid(column=3, row=0, padx=10, pady=15)

root = Tk()
root.title("YouTube Downloader")
root.geometry("850x650+580+250")
root.resizable(0,0)
root.configure(bg="white")
root.bind_all("<Key>", _onKeyRelease, "+")

logo = ImageTk.PhotoImage(Image.open("logo.png"))
logoLbl = Label(
    root,
    image=logo,
    background="white",
    )
dWindow = LabelFrame(
    root,
    text="Вставьте ссылку",
    background="white",
    font="9",
    borderwidth=0,
    highlightthickness=0,
    )
txt = Entry(dWindow, width=45, font=("10"))   
valMes = Label(dWindow, text="", background="white")
btn = Button(dWindow, text="Далее", width=13, command=validateEntry, font="8")
varVideo = StringVar()
varAudio = StringVar()
audioMp3 = IntVar()

initFirst()

root.protocol("WM_DELETE_WINDOW", finish)
root.mainloop()
