from tkinter import *
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

class Application(Frame):
    def __init__(self, master=None):
        super().__init__(master)

        #Init global var
        self.master = master
        self.stegopath = None
        self.messagepath = None
        self.stego_render = None
        self.message_render = None
        # self.stegofile = IntVar()
        self.encrypt = IntVar()
        self.method = IntVar()

        # Frames
        # A. Config Frame
        configFrame = Frame(master)
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
        inputFrame = Frame(master, relief="sunken")
        inputFrame.grid(row=1)

        # C. Show Frame
        showFrame = Frame(master)
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

		# Input
        button_load_stego_file = Button(inputFrame, text='Load Stego File', command= lambda: self.askopenfile(self.stegopath, "stego", stego_image_show_label))
        button_load_stego_file.grid(row=0, column=0, sticky=N, pady=5, padx=5)

        button_load_message_file = Button(inputFrame, text='Load Message File', command= lambda: self.askopenfile(self.messagepath, "message", message_image_show_label))
        button_load_message_file.grid(row=0, column=1, sticky=N, pady=5, padx=5)

		# Key
        key_label = Label(master, text="Key", font=("Helvetica", 10))
        key_label.grid(row=3, columnspan=2)

        self.eKey = Text(master, height=1, width=69, font=("Consolas", 12))
        self.eKey.grid(row=4, column=0, padx=10)

		# Opsi
        # actionFrame = Frame()
        # Label(master, text="Cipher Select", font=("Helvetica", 16)).grid(row=4)
        # self.cipherOption = CipherOptions(master=actionFrame)
        # self.cipherOption.grid(row=4, pady=(0,25))
        # Label(actionFrame, text="Output Format", font=("Helvetica", 16)).grid(row=5)
        # self.outputChoice = OutputChoices(master=actionFrame)
        # self.outputChoice.grid(row=6, pady=(0,25))
        # selectionFrame = Frame(master=actionFrame)
        # Button(selectionFrame, text='Encrypt', command=self.encrypt).grid(row=2, column=0, padx=5, pady=4)
        # Button(selectionFrame, text='Decrypt', command=self.decrypt).grid(row=2, column=1, padx=5, pady=4)
        # selectionFrame.grid(row=7)
        # actionFrame.grid(row=8, column=0, columnspan=2, pady=(0,25))

		# Output
        # outputFrame = Frame()
        # Label(outputFrame, text="Processed Text", font=("Helvetica", 16)).grid(column=0)
        # outputFrame.grid(row=9)
        # self.eOutput = Text(master, height=4, width=90, font=("Consolas", 12))
        # self.eOutput.grid(row=10, padx=10)
        # saveFrame = Frame()
        # Button(saveFrame, text='Save File', command=self.savefile).grid(column=1)
        # saveFrame.grid(row=11)

    def askopenfile(self, pathfile, filetype, label):

        filepath = filedialog.askopenfilename()
        if filepath != None:
            pathfile = filepath 
        else:
            print("File cannot be empty")

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
                        

    # def savefile(self):
    #     if (type(self.cipherOption.getCipher()) is cp.VigenereExtended):
    #         messagebox.showwarning("Warning", "Tidak bisa menyimpan file untuk Extenede Vigenere Cipher")
    #     elif (len(self.eOutput.get("1.0", "end-1c")) == 0):
    #         messagebox.showwarning("Warning", "Output masih kosong!")
    #     else:
    #         filename =  filedialog.asksaveasfilename(title = "Save As",filetypes = (("Text Files","*.txt"),("All Files","*.*")))
    #         f = open(filename,"w")
    #         f.write(self.eOutput.get("1.0", "end-1c"))
    #         f.close()

    # def validate(self):
    #     if (len(self.eInput.get("1.0", "end-1c")) == 0):
    #         messagebox.showwarning("Warning", "Input tidak boleh kosong!")
    #     else:
    #         return True

if __name__ == "__main__":
    gui = Tk()
    gui.title("Tubes 1 Kriptografi - Cryptosteganography")
    gui.geometry('{}x{}'.format(645, 600))
    app = Application(master=gui)
    app.mainloop()
