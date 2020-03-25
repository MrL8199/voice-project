# Import the necessary modules.
import tkinter as tk
import tkinter.messagebox
import pyaudio
import wave
import os
import threading

class RecAUD:
    def __init__(self,topic_names ,chunk=3024, frmat=pyaudio.paInt16, channels=2, rate=44100, py=pyaudio.PyAudio()):
        # Start Tkinter and set Title
        self.topic_names = topic_names
        self.sentences = []
        self.audio_name = None
        self.file_output = None
        self.cur_sentence = -1
        self.main = tk.Tk()
        self.collections = []
        self.main.geometry('1000x300')
        self.main.title('Project 1 - NguyenLinhUET - MSSV: 17021195')
        self.CHUNK = chunk
        self.FORMAT = frmat
        self.CHANNELS = channels
        self.RATE = rate
        self.p = py
        self.frames = []
        self.st = 0
        self.is_playing = False
        self.playing_theard = None
        self.stream = self.p.open(format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE, input=True, frames_per_buffer=self.CHUNK)
        # Set Frames
        self.TopFrame = tk.Frame(self.main)
        self.MidFrame1 = tk.Frame(self.main)
        self.MidFrame2 = tk.Frame(self.main)
        self.BottomFrame = tk.Frame(self.main)


        # Pack Frame
        self.TopFrame.pack()
        self.MidFrame1.pack()
        self.MidFrame2.pack()
        self.BottomFrame.pack()

        # chọn chủ đề
        self.topic_var = tk.StringVar(self.main)
        self.topic_var.set('Chọn chủ đề')
        self.topic_var.trace('w', self.changetopic)
        self.topicPopup = tk.OptionMenu(self.TopFrame, self.topic_var, *topic_names)
        
        # sentence label
        self.sentence_title = tk.Label(self.TopFrame, text= "Văn bản cần đọc:")
        self.sentence_label = tk.Label(self.TopFrame, text= "(Văn bản cần đọc sẽ hiện ở đây)")
        self.topicPopup.grid(row=0,column=0, padx=50, pady=5)
        self.sentence_title.grid(row=1, column = 0 , columnspan =1)
        self.sentence_label.grid(row=2, column = 0 , columnspan =1, pady=5)

        # các phím chuyển câu
        self.next = tk.Button(self.MidFrame1, width=10, text='Câu sau >', command=lambda: self.nextSentence())
        self.pre = tk.Button(self.MidFrame1, width=10, text='< Câu trước', command=lambda: self.preSentence())

        # Các phím record
        self.strt_rec = tk.Button(self.MidFrame2, width=10, text='Start Record', command=lambda: self.start_record())
        self.stop_rec = tk.Button(self.MidFrame2, width=10, text='Stop Record', command=lambda: self.stop_record())
        self.play_au = tk.Button(self.MidFrame2, width=10, text='Play', command=lambda: self.play_record())
        self.stop_au = tk.Button(self.MidFrame2, width=10, text="Stop", command=lambda: self.stop_play())

        self.pre.grid(row=0, column=0)
        self.next.grid(row=0, column=1, padx = 5)

        self.strt_rec.grid(row=1, column=0, pady = 5)
        self.stop_rec.grid(row=1, column=1, pady = 5 ,padx = 5)
        
        self.play_au.grid(row=1, column=3, pady = 5)
        self.stop_au.grid(row=1, column=4, pady = 5 ,padx = 5)
        
        # status
        self.status_title = tk.Label(self.BottomFrame, text = "Trạng thái:")
        self.status_label = tk.Label(self.BottomFrame, text = "")
        self.status_title.grid(row = 0, column = 0, pady = 5)
        self.status_label.grid(row = 1, column = 0, pady = 5)

        tk.mainloop()

    def changetopic(self, *args):
        self.is_playing = False
        # get topic name
        topic_name = self.topic_var.get()
        # read file
        fin = open("/".join(["data",topic_name ,"data.txt"]), "r", encoding="utf-8")

        self.sentences = fin.readlines()

        # khởi tạo array ghi lại trạng thái câu đã được gh âm?
        self.record_tags = [False for i in range(len(self.sentences))]

        
        self.cur_sentence = -1
        fin.close()
        # nếu đang mở file output thì đóng file
        if self.file_output:
            self.file_output.close()
        # mở file output
        self.file_output = open("/".join(["data",topic_name ,"output.txt"]), "w" , encoding="utf-8")
        self.status_label['text'] = 'Đã chọn chủ đề ' + topic_name + ', bấm câu sau để bắt đầu ghi âm chủ đề này'
    
    def nextSentence(self):
        topic_name = self.topic_var.get()
        if topic_name == 'Chọn chủ đề':
            return
        if self.cur_sentence >= len(self.sentences) - 1:
            if self.file_output.closed:
                return
            # duyệt tất cả các câu
            for sentence in self.sentences:
                # lấy index câu
                index = self.sentences.index(sentence)
                # write câu ở dòng 1
                self.file_output.write(sentence)
                # nếu câu đã được record thì ghi stt + .wav
                if self.record_tags[index]:
                    audio_name = str(index) + ".wav"
                # nếu không thì ghi NULL
                else:
                    audio_name = "NULL"    
                self.file_output.write(audio_name + "\n")
            # đóng file
            self.file_output.close()
            self.status_label['text'] = 'Đã ghi xong chủ đề ' + topic_name
            return
        # chuyển sang câu tiếp theo
        self.is_playing = False # chuyển câu thì dừng play
        self.cur_sentence += 1
        file_path = "/".join(["data",topic_name , str(self.cur_sentence) +".wav"])
        status = 'Câu thứ: ' + str(self.cur_sentence) + "/" + str(len(self.sentences))
        if os.path.exists(file_path):
            self.record_tags[self.cur_sentence] = True
            status += " (đã ghi âm, bạn có thể nhấn nút play để nghe)"
        self.status_label['text'] = status
        self.sentence_label['text']= self.sentences[self.cur_sentence]
    
    def preSentence(self):
        if self.topic_var.get() == 'Chọn chủ đề':
            return
        if self.cur_sentence > 0:
            self.is_playing = False # chuyển câu thì dừng play
            self.cur_sentence -= 1
            self.sentence_label['text']= self.sentences[self.cur_sentence]
            topic_name = self.topic_var.get()
            file_path = "/".join(["data",topic_name , str(self.cur_sentence) +".wav"])
            status = 'Câu thứ: ' + str(self.cur_sentence) + "/" + str(len(self.sentences))
            if os.path.exists(file_path):
                self.record_tags[self.cur_sentence] = True
                status += " (đã ghi âm, bạn có thể nhấn nút play để nghe)"
            self.status_label['text'] = status
            self.sentence_label['text']= self.sentences[self.cur_sentence]


    def start_record(self):
        if self.cur_sentence == -1:
            return
        self.is_playing = False
        self.status_label['text'] = 'Đang ghi câu: ' + str(self.cur_sentence) + "/" + str(len(self.sentences))
        self.st = 1
        self.frames = []
        stream = self.p.open(format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE, input=True, frames_per_buffer=self.CHUNK)
        while self.st == 1:
            data = stream.read(self.CHUNK)
            self.frames.append(data)
            self.main.update()
        stream.close()
        self.p.terminate()
        # get topic name
        topic_name = self.topic_var.get()
        # open wav file
        wf = wave.open("/".join(["data",topic_name , str(self.cur_sentence) +".wav"]), 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(self.p.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(self.frames))
        wf.close()

    def stop_record(self):
        if self.st == 0:
            return
        self.st = 0
        self.record_tags[self.cur_sentence] = True
        self.status_label['text'] = 'Đã ghi câu: ' + str(self.cur_sentence) + "/" + str(len(self.sentences))
    
    def play_audio(self, filename):
        chunk = 1024
        wf = wave.open(filename, 'rb')
        p = pyaudio.PyAudio()

        stream = p.open(
            format = p.get_format_from_width(wf.getsampwidth()),
            channels = wf.getnchannels(),
            rate = wf.getframerate(),
            output = True)

        data = wf.readframes(chunk)

        while len(data) > 0 and self.is_playing: # is_playing to stop playing
            stream.write(data)
            data = wf.readframes(chunk)
        stream.stop_stream()
        stream.close()
        p.terminate()
        self.is_playing = False

    def stop_play(self):
        if self.is_playing:
            self.is_playing = False
            self.playing_theard.join()

    def play_record(self):
        if self.cur_sentence == -1:
            return
        if self.record_tags[self.cur_sentence] == False:
            return
        if not self.is_playing :
            self.is_playing = True
            topic_name = self.topic_var.get()
            filename = "/".join(["data",topic_name , str(self.cur_sentence) +".wav"])
            self.playing_theard = threading.Thread(target=self.play_audio,args=(filename,))
            self.playing_theard.start()

topic_names = []
for (paths, dirs, files) in os.walk("data/."):
    for dirname in dirs:
        topic_names.append(dirname)

guiAUD = RecAUD(topic_names)