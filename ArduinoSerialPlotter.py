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
matplotlib.use('TkAgg')

rates = [50, 75, 110, 134, 150, 200, 300, 600, 1200, 1800, 2400, 4800, 9600, 19200, 38400, 57600, 115200]

def searchPorts():
    ports = serial.tools.list_ports.comports(include_links=False)
    return ports

def setSerial(comPort,bspeed):
    try:
        ser = serial.Serial(comPort, bspeed)
        return ser
    except:
        print("Serial nejde precist") 
    

def getData(ser):
    try:
        data = ser.readline()  # TODO: data must be send like println
    except:
        print("Nemam data")
    return data


porty = searchPorts()

fig = plt.gcf()      # if using Pyplot then get the figure from the plot
figure_x, figure_y, figure_w, figure_h = fig.bbox.bounds

#------------------------------- Beginning of Matplotlib helper code -----------------------
def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    figure_canvas_agg._idle
    return figure_canvas_agg

layout = [[sg.Text('COM port:'), sg.Text('', key='_seat_', size = (10, None))],
         [sg.Combo(porty,default_value = porty[-1]), sg.Text("Baud Rate: "), sg.Combo(rates, default_value=rates[12]), sg.Button('Read')],
         [sg.Canvas(size=(figure_w, figure_h), key='-CANVAS-')],
         [sg.Text('Last data: '), sg.Text('',key = '_data_', size = (20, None))],
         [sg.Button('Exit')]]
window = sg.Window('Arduino serial plotter', layout, finalize=True)

canvas_elem = window['-CANVAS-']
canvas = canvas_elem.TKCanvas

fig, ax = plt.subplots()
ax.grid(False)
fig, ax = plt.subplots(figsize=(5, 5))

fig_agg = draw_figure(canvas, fig)

i = 0
kplotu = 0
arr2 = np.array([0])
a = 1

while True:  # Event Loop
    event, values = window.Read(timeout=10)
    if event is None or event == 'Exit':  
        break
    if event == 'Read':
        openPort = setSerial(values[0].device, values[1])
        event = ''
        while True:
            dataInBytes = getData(openPort)
            decoded_bytes = str(dataInBytes[0:len(dataInBytes)-2])
            decoded_bytes = decoded_bytes[2:len(decoded_bytes)-2]
            temp = {'_IN_': decoded_bytes}
            window.FindElement('_data_').Update(temp['_IN_'])

            arr2 = np.append(arr2, np.array(int(decoded_bytes)))
            i = i+1
            if i > 200:
                #    i = 0
                arr2 = arr2[-200:]
            a=a+1

            # plot all data
            ax.clear()
            ax.plot(arr2, color='r')
            #ax.set_xticks([i,i+1,i+2,i+3,])

            # show the plot
            #plt.show()
            fig_agg.draw()
            print(decoded_bytes)
            event, values = window.Read(timeout=10)
            if event == 'Read':
                openPort.close()  # close opened port
                break
            if event is None or event == 'Exit':  
                break
    if values:
        # change the "output" element to be the value of "input" element  
        print(event, values)

    #arr2 = np.append(arr2, np.array(a))
    #i = i+1
    #if i > 200:
    #    #    i = 0
    #    arr2 = arr2[-200:]
    #a=a+1
#
    ## plot all data
    #ax.clear()
    #ax.plot(arr2, arr2, color='r')
    ##ax.set_xticks([i,i+1,i+2,i+3,])
#
    ## show the plot
    ##plt.show()
    #fig_agg.draw()
    

    
    #plt.pause(0.0001) # <-- sets the current plot until refreshed

    # be nice to the cpu :)
    #time.sleep(.1)


window.Close()
