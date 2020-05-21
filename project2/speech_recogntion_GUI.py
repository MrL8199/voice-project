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

class RecAUD:
    def __init__(self,chunk=3024, frmat=pyaudio.paInt16, channels=1, rate=44100, py=pyaudio.PyAudio()):
        # Start Tkinter and set Title
        self.main = tk.Tk()
        self.collections = []
        self.main.geometry('800x300')
        self.main.title('Project 2 - NguyenLinhUET - MSSV: 17021195')
        self.CHUNK = chunk
        self.FORMAT = frmat
        self.CHANNELS = channels
        self.RATE = rate
        self.p = py
        self.frames = []
        self.st = 0
        self.is_playing = False
        self.playing_theard = None
        with open("multinomial_hmm.pkl", "rb") as file:
            self.models = pickle.load(file)
        self.kmeans = pickle.load(open("kmeans.pkl", 'rb'))
        
        self.stream = self.p.open(format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE, input=True, frames_per_buffer=self.CHUNK)
        # Set Frames
        self.TopFrame = tk.Frame(self.main)
        self.MidFrame1 = tk.Frame(self.main)
        self.MidFrame2 = tk.Frame(self.main)
        self.BottomFrame = tk.Frame(self.main)

        # Pack Frame
        self.TopFrame.pack()
        self.BottomFrame.pack()

        # Các phím record
        self.strt_rec = tk.Button(self.TopFrame, width=10, text='Start Record', command=lambda: self.start_record())
        self.stop_rec = tk.Button(self.TopFrame, width=10, text='Stop Record', command=lambda: self.stop_record())
        self.play_au = tk.Button(self.TopFrame, width=10, text='Play', command=lambda: self.play_record())
        self.stop_au = tk.Button(self.TopFrame, width=10, text="Stop", command=lambda: self.stop_play())
        self.detect_au = tk.Button(self.TopFrame, width=10, text="Detect", command=lambda: self.detect())

        self.strt_rec.grid(row=1, column=0, pady = 5)
        self.stop_rec.grid(row=1, column=1, pady = 5)
        self.play_au.grid(row=1, column=3, pady = 5)
        self.stop_au.grid(row=1, column=4, pady = 5)
        self.detect_au.grid(row=1, column=5, pady = 5)

        # status
        self.status_title = tk.Label(self.BottomFrame, text = "Trạng thái:")
        self.status_label = tk.Label(self.BottomFrame, text = "")
        self.status_title.grid(row = 0, column = 0)
        self.status_label.grid(row = 1, column = 0)

        tk.mainloop()
    
    def get_mfcc(self,file_path):
        y, sr = librosa.load(file_path)  # read .wav file
        hop_length = math.floor(sr*0.010)  # 10ms hop
        win_length = math.floor(sr*0.025)  # 25ms frame
        # mfcc is 12 x T matrix
        mfcc = librosa.feature.mfcc(
            y, sr, n_mfcc=12, n_fft=1024,
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
    
    def detect(self):
        if self.is_playing == True:
            self.stop_play()
        O = self.get_mfcc("record.wav")
        O = self.kmeans.predict(O).reshape(-1, 1)

        score = {cname: model.score(O, [len(O)]) for cname, model in self.models.items()}
        print(score)
        inverse = [(value, key) for key, value in score.items()]
        predict = max(inverse)[1]
        self.status_label['text'] = "Kết quả: " + predict

    def start_record(self):
        self.is_playing = False
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
            self.status_label['text'] = "Dừng phát"
            self.is_playing = False
            self.playing_theard.join()

    def play_record(self):
        if not self.is_playing:
            self.status_label['text'] = "Đang phát"
            self.is_playing = True
            filename = "record.wav"
            self.playing_theard = threading.Thread(target=self.play_audio,args=(filename,))
            self.playing_theard.start()

guiAUD = RecAUD()