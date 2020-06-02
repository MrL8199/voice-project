# Import the necessary modules.
import pickle
import librosa
import numpy as np
import math
import tkinter as tk
import tkinter.messagebox
import pyaudio
import wave
import os
import threading
import soundfile as sf
import scipy as sp

class RecAUD:
    def __init__(self,model_names,chunk=3024, frmat=pyaudio.paInt16, channels=1, rate=44100, py=pyaudio.PyAudio()):
        # Start Tkinter and set Title
        self.modelName = model_names
        self.main = tk.Tk()
        self.collections = []
        self.main.geometry('800x300')
        self.main.title('Project 2')
        self.CHUNK = chunk
        self.FORMAT = frmat
        self.CHANNELS = channels
        self.RATE = rate
        self.p = py
        self.frames = []
        self.st = 0
        self.is_playing = False
        self.is_recording = False
        self.playing_theard = None
        self.modelPath = self.modelName[0]
        with open(self.modelPath, "rb") as file:
            self.models = pickle.load(file)
        
        self.stream = self.p.open(format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE, input=True, frames_per_buffer=self.CHUNK)
        # Set Frames
        self.TopFrame = tk.Frame(self.main)
        self.MidFrame = tk.Frame(self.main)
        self.BottomFrame = tk.Frame(self.main)

        # Pack Frame
        self.TopFrame.pack()
        self.MidFrame.pack()
        self.BottomFrame.pack()

        # chọn model
        self.model_var = tk.StringVar(self.main)
        self.model_var.set('Chọn model')
        self.model_var.trace('w', self.change_model)
        self.modelPopup = tk.OptionMenu(self.TopFrame, self.model_var, *self.modelName)
        self.modelPopup.grid(row=0,column=0, padx=50, pady=5)

        # Các phím record
        self.record_btn = tk.Button(self.MidFrame, width=10, text='Start Record', command=lambda: self._onClickRecord())
        self.play_btn = tk.Button(self.MidFrame, width=10, text='Play', command=lambda: self._onClickPlay())
        self.rmv_noise = tk.Button(self.MidFrame, width=10, text="Rmv Noise", command=lambda: self.remove_noise())
        self.detect_au = tk.Button(self.MidFrame, width=10, text="Predict", command=lambda: self.detect())
        self.record_btn.grid(row=1, column=0, padx = 2 , pady = 5)
        self.play_btn.grid(row=1, column=1, padx = 2, pady = 5)
        self.rmv_noise.grid(row=1, column=2, padx = 2, pady = 5)
        self.detect_au.grid(row=1, column=3, padx = 2 , pady = 5)

        # status
        self.status_title = tk.Label(self.BottomFrame, text = "Trạng thái:")
        self.status_label = tk.Label(self.BottomFrame, text = f"Đang sử dụng model {self.modelPath}")
        self.status_title.grid(row = 0, column = 0)
        self.status_label.grid(row = 1, column = 0)
        self.main.bind_all('<Key>', self.on_key_press)
        self.main.bind('<Return>', self.detect)
        tk.mainloop()
    
    def on_key_press(self,event):
        char = event.char
        if char == ' ':
            self._onClickRecord()
        if char == 'p':
            self._onClickPlay()
        if char == 'r':
            self.remove_noise()

    def get_mfcc(self,file_path):
        y, sr = librosa.load(file_path)  # read .wav file
        hop_length = math.floor(sr*0.010)  # 10ms hop
        win_length = math.floor(sr*0.025)  # 25ms frame
        # mfcc is 12 x T matrix
        mfcc = librosa.feature.mfcc(
            y=y, sr=sr, n_mfcc=12, n_fft=1024,
            hop_length=hop_length, win_length=win_length)
        # substract mean from mfcc --> normalize mfcc
        mfcc = mfcc - np.mean(mfcc, axis=1).reshape((-1, 1))
        # delta feature 1st order and 2nd order
        delta1 = librosa.feature.delta(mfcc, order=1)
        delta2 = librosa.feature.delta(mfcc, order=2)
        # X is 36 x T
        X = np.concatenate([mfcc, delta1, delta2], axis=0)  # O^r
        # return T x 36 (transpose of X)
        return X.T  # hmmlearn use T x N matrix
    
    def detect(self,event=None):
        if self.is_playing == True:
            self.is_playing = False
            self.stop_play()
            return
        
        O = self.get_mfcc("record.wav")
        if self.modelPath == "multinomial_hmm.pkl":
            O = self.kmeans.predict(O).reshape(-1, 1)

        score = {cname: model.score(O, [len(O)]) for cname, model in self.models.items()}
        print(f"Result: {score}")
        inverse = [(value, key) for key, value in score.items()]
        predict = max(inverse)[1]
        self.status_label['text'] = "Kết quả: " + predict
    
    def change_model(self,*args):
        self.modelPath = self.model_var.get()
        with open(self.modelPath, "rb") as file:
            self.models = pickle.load(file)
        if self.modelPath == "multinomial_hmm.pkl":
            self.kmeans = pickle.load(open("kmeans.pkl", 'rb'))
        self.status_label['text'] = f"Đang sử dụng model {self.modelPath}"

    def _onClickRecord(self):
        if self.is_recording == False:
            if self.is_playing:
                return
            self.record_btn['text'] = "Stop record"
            self.record_btn['bg'] = "red"
            self.is_recording = True
            self.start_record()
        else:
            self.record_btn['text'] = "Start record"
            self.record_btn['bg'] = "SystemButtonFace"
            self.is_recording = False
            self.stop_record()

    def _onClickPlay(self):
        if self.is_playing == False:
            if self.is_recording == True:
                return
            self.play_btn['text'] = "Stop"
            self.play_btn['bg'] = "red"
            self.is_playing = True
            self.play_record()
        else:
            self.play_btn['text'] = "Play"
            self.play_btn['bg'] = "SystemButtonFace"
            self.is_playing = False
            self.stop_play()

    def start_record(self):
        self.status_label['text'] = 'Đang ghi âm'
        self.st = 1
        self.frames = []
        stream = self.p.open(format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE, input=True, frames_per_buffer=self.CHUNK)
        while self.st == 1:
            data = stream.read(self.CHUNK)
            self.frames.append(data)
            self.main.update()
        stream.close()
        # get topic name
        # open wav file
        wf = wave.open("record.wav", 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(self.p.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(self.frames))
        wf.close()

    def stop_record(self):
        if self.st == 0:
            return
        self.st = 0
        self.status_label['text'] = 'Đã ghi âm'

    def trim_silence(self,y):
        y_trimmed, index = librosa.effects.trim(y, top_db=25, frame_length=2, hop_length=500) 
        trimmed_length = librosa.get_duration(y) - librosa.get_duration(y_trimmed)
        return y_trimmed, trimmed_length

    def remove_noise(self):
        if self.is_recording == True:
            return
        y,sr = librosa.load("record.wav")
        y_reduced_median = sp.signal.medfilt(y,3) # lọc trung vị
        y_reduced_median, time_trimmed = self.trim_silence(y_reduced_median)
        sf.write('record.wav',y_reduced_median, sr, 'PCM_24')
        print(f"Remove noise: {librosa.get_duration(y)} (s) -> {librosa.get_duration(y_reduced_median)} (s)")
        self.status_label['text'] = 'Đã remove noise'
    
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
        self.play_btn['text'] = "Play"
        self.play_btn['bg'] = "SystemButtonFace"
        self.status_label['text'] = "Dừng phát"

    def stop_play(self):
        if self.is_playing:
            self.status_label['text'] = "Dừng phát"
            self.playing_theard.join()

    def play_record(self):
        self.status_label['text'] = "Đang phát"
        self.playing_theard = threading.Thread(target=self.play_audio,args=("record.wav",))
        self.playing_theard.start()

model_names = []
for (paths, dirs, files) in os.walk("./"):
    for filename in files:
        if filename.endswith(".pkl") and filename != "kmeans.pkl":
            model_names.append(filename)
guiAUD = RecAUD(model_names)