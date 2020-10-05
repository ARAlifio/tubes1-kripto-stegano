from tkinter import *
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from src import stegano
from src import crypto
import os

class Application(Frame):
    def __init__(self, master=None):
        super().__init__(master)

        #Init global var
        self.master = master
        self.stegopath = None
        self.messagepath = None
        self.decryptpath = None
        self.stego_render = None
        self.message_render = None
        # self.stegofile = IntVar()
        self.encrypt = IntVar()
        self.method = IntVar()
        # self.eKey = IntVar()

        # Frames
        encryptMaster = Frame(master)
        encryptMaster.grid(row=0, column=0)

        decryptMaster = Frame(master)
        decryptMaster.grid(row=0, column=1)

        # A. Config Frame
        configFrame = Frame(encryptMaster)
        configFrame.grid(row=0)

        # A.1. Method Frame
        methodFrame = Frame(configFrame)
        methodFrame.grid(row=2, columnspan=4)

        # A.1.1. Different Method Type Frames
        imageMethodFrame = Frame(methodFrame, borderwidth = 1, relief="sunken")
        imageMethodFrame.grid(row=0,column=0, sticky="new", padx=5)
        videoMethodFrame = Frame(methodFrame, borderwidth = 1, relief="sunken")
        videoMethodFrame.grid(row=0,column=1, sticky="new", padx=5)
        audioMethodFrame = Frame(methodFrame, borderwidth = 1, relief="sunken")
        audioMethodFrame.grid(row=0,column=2, sticky="new", padx=5)

        # B. Input Frame
        inputFrame = Frame(encryptMaster, relief="sunken")
        inputFrame.grid(row=1)

        # C. Show Frame
        showFrame = Frame(encryptMaster)
        showFrame.grid(row=2)

        # Encrpytion
        label_encrypt = Label(configFrame, text="Encryption Type", font=("Helvetica", 12))
        label_encrypt.grid(row=1, column=0, sticky=W, pady=10)
        r_encrypt_1 = Radiobutton(configFrame, text="With Encrpytion", variable=self.encrypt, value=1)
        r_encrypt_1.grid(row=1, column=1)
        r_encrypt_2 = Radiobutton(configFrame, text="Without Encrpytion", variable=self.encrypt, value=0)
        r_encrypt_2.grid(row=1, column=2)

        # Image 
        label_image = Label(imageMethodFrame, text="Image Steganography Type", font=("Helvetica", 12))
        label_image.grid(row=0, column=0)
        r_image_1 = Radiobutton(imageMethodFrame, text="Sequential LSB", variable=self.method, value=111)
        r_image_1.grid(row=1, column=0, sticky=W)
        r_image_2 = Radiobutton(imageMethodFrame, text="Random LSB", variable=self.method, value=112)
        r_image_2.grid(row=2, column=0, sticky=W)
        r_image_3 = Radiobutton(imageMethodFrame, text="Sequential BPCS", variable=self.method, value=121)
        r_image_3.grid(row=3, column=0, sticky=W)
        r_image_4 = Radiobutton(imageMethodFrame, text="Random BPCS", variable=self.method, value=122)
        r_image_4.grid(row=4, column=0, sticky=W)

        # Video
        label_video = Label(videoMethodFrame, text="Video Steganography Type", font=("Helvetica", 12))
        label_video.grid(row=0, column=0)
        r_video_1 = Radiobutton(videoMethodFrame, text="Seq Frame Seq Px", variable=self.method, value=211)
        r_video_1.grid(row=1, column=0, sticky=W)
        r_video_2 = Radiobutton(videoMethodFrame, text="Seq Frame Rand Px", variable=self.method, value=212)
        r_video_2.grid(row=2, column=0, sticky=W)
        r_video_3 = Radiobutton(videoMethodFrame, text="Rand Frame Seq Px", variable=self.method, value=221)
        r_video_3.grid(row=3, column=0, sticky=W)
        r_video_4 = Radiobutton(videoMethodFrame, text="Rand Frame Rand Px", variable=self.method, value=222)
        r_video_4.grid(row=4, column=0, sticky=W)

        # Audio
        label_audio = Label(audioMethodFrame, text="Audio Steganography Type", font=("Helvetica", 12))
        label_audio.grid(row=0, column=0)
        r_audio_1 = Radiobutton(audioMethodFrame, text="Sequential Byte", variable=self.method, value=311)
        r_audio_1.grid(row=1, column=0, sticky=W)
        r_audio_2 = Radiobutton(audioMethodFrame, text="Random Byte", variable=self.method, value=312)
        r_audio_2.grid(row=2, column=0, sticky=W)

        # Show Image
        stego_image_show_label = Label(showFrame, relief='sunken')
        stego_image_show_label.grid(row=0, column=0)

        message_image_show_label = Label(showFrame, relief='sunken')
        message_image_show_label.grid(row=0, column=1)

        # Placeholder Image for Show Image
        load = Image.open("placeholder.png")
        resized = load.resize((300, 300), Image.ANTIALIAS)
        render = ImageTk.PhotoImage(resized)
        message_image_show_label.configure(image=render)
        stego_image_show_label.configure(image=render)

        # Open Media
        button_open_stego = Button(showFrame, text='Open Stego Media', command= lambda: self.playmedia(self.stegopath))
        button_open_stego.grid(row=1, column=0)
        
        button_open_message = Button(showFrame, text='Open Message Media', command= lambda: self.playmedia(self.messagepath))
        button_open_message.grid(row=1, column=1)

		# Input
        button_load_stego_file = Button(inputFrame, text='Load Stego File', command= lambda: self.askopenfile(self.stegopath, "stego", stego_image_show_label))
        button_load_stego_file.grid(row=0, column=0, sticky=N, pady=5, padx=5)

        button_load_message_file = Button(inputFrame, text='Load Message File', command= lambda: self.askopenfile(self.messagepath, "message", message_image_show_label))
        button_load_message_file.grid(row=0, column=1, sticky=N, pady=5, padx=5)

		# Key
        key_label = Label(encryptMaster, text="Key", font=("Helvetica", 10))
        key_label.grid(row=3, columnspan=2)

        self.eKey = Entry(encryptMaster)
        # self.eKey = Entry(encryptMaster, height=1, width=69, font=("Consolas", 12))
        self.eKey.grid(row=4, column=0, padx=10, pady=5)

        # Encrypt Button
        button_encrypt = Button(encryptMaster, text='Encrypt', command= self.callencrypt)
        button_encrypt.grid(row=5, columnspan=2)
        
        # Decrpyt File
        button_load_decrypt_file = Button(decryptMaster, text='Load Decryption File', command= lambda: self.askopenfile(self.decryptpath, "decrypt", message_image_show_label))
        button_load_decrypt_file.grid(row=0, column=1, sticky=N, pady=5, padx=5)

        # Decrypt Method
        decrypt_image = Radiobutton(decryptMaster, text="Decrypt Image", variable=self.method, value=91)
        decrypt_image.grid(row=1, column=0, sticky=N)
        decrypt_video = Radiobutton(decryptMaster, text="Decrypt Video", variable=self.method, value=92)
        decrypt_video.grid(row=1, column=1, sticky=N)
        decrpyt_audio = Radiobutton(decryptMaster, text="Decrypt Audio", variable=self.method, value=93)
        decrpyt_audio.grid(row=1, column=2, sticky=N)

        # Decrypt Button
        button_decrypt = Button(decryptMaster, text='Decrypt', command= self.calldecrypt)
        button_decrypt.grid(row=2, columnspan=2, sticky=N)

    def callencrypt(self):
        try:
            stringkey = self.eKey.get()
            key = int(stringkey)
        except:
            key = 0

        # stego_path = self.stegopath.get()
        # message_path = self.messagepath.get()
        methoda = self.method.get()
        enkrip = self.encrypt.get()
        print("method",methoda)
        print("enkr",enkrip)
        print("key",key)
        print("stegopath", self.stegopath)
        print("messagepath", self.messagepath)

        self.encrypt(self.stegopath, self.messagepath, self.method, self.encrypt, key)

    def calldecrypt(self):
        try:
            key = self.eKey.get()
        except:
            key = 0
        self.decrypt(self.stegopath, self.messagepath, self.method, self.encrypt, key)

    def playmedia(self, pathfile):
        print(pathfile)
        os.startfile(pathfile)

    def askopenfile(self, pathfile, filetype, label):

        filepath = filedialog.askopenfilename()
        if filepath != None:
            pathfile = filepath 
        else:
            print("File cannot be empty")

        if filetype == "stego":
            self.stegopath = filepath
        else:
            self.messagepath = filepath

        try:
            if filetype == "stego":
                load = Image.open(pathfile)
                resized = load.resize((300, 300), Image.ANTIALIAS)
                self.stego_render = ImageTk.PhotoImage(resized)
                label.configure(image=self.stego_render)
            elif filetype == "message":
                load = Image.open(pathfile)
                resized = load.resize((300, 300), Image.ANTIALIAS)
                self.message_render = ImageTk.PhotoImage(resized)
                label.configure(image=self.message_render)
            else:
                pass
        except:
            print("Not an Image")
            
                        
    def encrypt(stegopath, messagepath, method, encrypt_mode=0, key=0):
        X = Stegano()

        if encrypt_mode:
            print("encrypted")
    
        if method == 111 : # Image, seq LSB
            pass
            X.LSB_encrypt_image(stegopath, messagepath, 0)
        elif method == 112 : # Image, rand LSB
            pass
            X.LSB_encrypt_image(stegopath, messagepath, key)
        elif method == 121 : # Image, seq BPCS
            pass
        elif method == 122 : # Image, rand BPCS
            pass
        elif method == 211 : # Video, seq frame seq px
            pass
            X.LSB_encrypt_video(stegopath, messagepath, 0, False, False)
        elif method == 212 : # Video, seq frame rand px
            pass
            X.LSB_encrypt_video(stegopath, messagepath, key, False, True)
        elif method == 221 : # Video, rand frame seq px
            pass
            X.LSB_encrypt_video(stegopath, messagepath, key, True, False)
        elif method == 222 : # Video, rand frame rand px
            pass
            X.LSB_encrypt_video(stegopath, messagepath, key, True, True)
        elif method == 311 : # Audio, seq LSB
            pass
            X.LSB_encrypt_audio(stegopath, messagepath, 0)
        elif method == 312 : # Audio, rand LSB
            pass
            X.LSB_encrypt_audio(stegopath, messagepath, key)
        else:
            print("Error, Please choose a method")

    def decrypt(stegopath, stegotype, key):
        print("decrypt")

if __name__ == "__main__":
    gui = Tk()
    gui.title("Tubes 1 Kriptografi - Cryptosteganography")
    gui.geometry('{}x{}'.format(1000, 620))
    app = Application(master=gui)
    app.mainloop()
