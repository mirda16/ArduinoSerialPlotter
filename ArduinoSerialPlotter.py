import os
import sys
import serial
import serial.tools.list_ports
import PySimpleGUI as sg
import matplotlib
import matplotlib.backends.backend_tkagg as tkagg
import tkinter as Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import NullFormatter
import re
#import time
matplotlib.use('TkAgg')

rates = [50, 75, 110, 134, 150, 200, 300, 600, 1200, 1800, 2400, 4800, 9600, 19200, 38400, 57600, 115200]  # available baud rates

# seatchPorts creates list of available COM ports
def searchPorts():
    ports = serial.tools.list_ports.comports(include_links=False)
    return ports

# setSerial opens chosed COM port
def setSerial(comPort,bspeed):
    try:
        ser = serial.Serial(comPort, bspeed)
        return ser
    except:
        print("Serial port opening error.") 
    
# getData gets data from open COM port. The data must be eneded by new line mark
def getData(ser):
    try:
        data = ser.readline()  # TODO: data must be send like println (ended by NL or CR?)
    except:
        print("Bad data or timeout.")
    return data


ports = searchPorts()  # list of connected ports

fig = plt.gcf()      # if using Pyplot then get the figure from the plot
figure_x, figure_y, figure_w, figure_h = fig.bbox.bounds

#------------------------------- Beginning of Matplotlib helper code -----------------------
def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    figure_canvas_agg._idle
    return figure_canvas_agg

justification = 'l'
# pySimpleGUI window layout
layout = [[sg.Text('COM port:'), sg.Text('', key='_seat_', size = (10, None))],
         [sg.Combo(ports,default_value = ports[-1]), sg.Text("Baud Rate: "), sg.Combo(rates, default_value=rates[12]), sg.Button('Read')],
         [sg.Canvas(size=(figure_w, figure_h), key='-CANVAS-'), sg.Multiline(size=(40,30), key='-MLINE-', justification=justification, enable_events=True, autoscroll=True, focus=True)],
         [sg.Checkbox(text='Autoscrool',default=True,key='autoScrChange',enable_events=True)],              
         [sg.Button('Exit')]]
window = sg.Window('Arduino serial plotter', layout, finalize=True)

# canvas element for ploting
canvas_elem = window['-CANVAS-']
canvas = canvas_elem.TKCanvas

fig, ax = plt.subplots()  # subplot figure definition
ax.grid(False)  # disabling grid
#fig, ax = plt.subplots(figsize=(5, 5))
fig_agg = draw_figure(canvas, fig)

i = 0
run_ = 0
#arr2 = np.array([0])
arr3 = np.array([[0,0],[0],[0],[0],[0],[0],[0],[0]])
first_run = 1
decoded_messages =''
colours = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']

while True:  # Event Loop
    event, values = window.Read(timeout=10)
    if event == sg.WIN_CLOSED:
        break
    if event == 'Read':
        openPort = setSerial(values[0].device, values[1])
        event = ''
        while True:
            dataInBytes = getData(openPort)
            decoded_bytes = str(dataInBytes[0:len(dataInBytes)-2])
            decoded_bytes = decoded_bytes[2:len(decoded_bytes)-1]
            decoded_messages = decoded_messages + decoded_bytes + '\n'

            #strings = decoded_bytes.split(',')
            strings = re.split(r'[,|;"]+', decoded_bytes)
            #temp = {'_IN_': decoded_bytes}
            #window.FindElement('_data_').Update(temp['_IN_']
            for j in range(len(strings)):
                #print(float(strings[j]))
                if strings[j] != '':
                    arr3[j] = np.append(arr3[j], np.array([float(strings[j])]),axis=0)
                else:
                    strings[j] = '0'
                    arr3[j] = np.append(arr3[j], np.array([float(strings[j])]),axis=0)
            if first_run == 1:
                arr3[0] = np.delete(arr3[0], [0,1])
                arr3[1] = np.delete(arr3[1], [1])
                arr3[2] = np.delete(arr3[1], [1])
                arr3[3] = np.delete(arr3[1], [1])
                arr3[4] = np.delete(arr3[1], [1])
                arr3[5] = np.delete(arr3[1], [1])
                first_run = 0
            #arr3[0] = np.append(arr3[0], np.array([float(strings[0])]),axis=0)
            run_ = run_+1
            # show last 200 values in graph
            if run_ > 200:
                arr3 = arr3[-200:]
            
            window.FindElement('-MLINE-').Update(decoded_messages)
            # plot all data
            ax.clear()
            for i in range(arr3.size):
                ax.plot(arr3[i], color = colours[i])

            # show the plot

            #do some stuff
            fig_agg.draw()

            
            # print(decoded_bytes)
            #del(z)
            ax.clear()
            event, values = window.Read(timeout=10)
            if event == 'Read':
                openPort.close()  # close opened port
                break
            if event == sg.WIN_CLOSED:
                break
            if event == 'autoScrChange':
                #if element 
                if window.FindElement('-MLINE-').autoscroll == True:
                    window.FindElement('-MLINE-').Update(autoscroll = False)
    if values:
        # change the "output" element to be the value of "input" element  
        print(event, values)

window.Close()
