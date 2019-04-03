# -*- coding: utf-8 -*-
"""
Created on Thu Jan  4 16:08:19 2018

@author: CIMlab徐孟維
"""

import tkinter as tk
from tkinter import StringVar, IntVar
from tkinter import ttk
import numpy as np
import copy

unit = 50
Hight = 10
Width = 10
Origin = [2, 1]



class FMS(tk.Tk, object):
    def __init__(self, env, Controller, unit, Hight, Width, Origin):
        super(FMS, self).__init__()
        self.Controller = Controller
        self.env = env
        self.unit = unit
        self.Hight = Hight
        self.Width = Width
        self.Origin = Origin
        #Window
        self.title("AGV Path")
        self.geometry("{1}x{1}".format((self.Width+5)*self.unit
                      , (self.Hight+5)*self.unit))
        self.BuildFloor()
        self.obstacle = []
        
        #Buttons
        
        self.tlist = tk.Text(width=30, height=30, font=("Helvetica", 14))
        self.tlist.place(x=650, y=0)
        
        tk.Label(text = "Obstacle Position", bg = "orange", font=('Arial', 12), width = 15, height = 1).place(x=230, y=580)
        tk.Label(text = "From:  x", font=('Arial', 12), width = 15, height = 1).place(x=150, y=610)
        self.fromx = tk.Entry(textvariable = StringVar(value = 3), width = 5)
        self.fromx.place(x=250, y=612)
        tk.Label(text = "y", font=('Arial', 12), height = 1).place(x=320, y=610)
        self.fromy = tk.Entry(textvariable = StringVar(value = 3), width = 5)
        self.fromy.place(x=332, y=612)
        
        tk.Label(text = "To:  x", font=('Arial', 12), width = 15, height = 1).place(x=159, y=630)
        self.tox = tk.Entry(textvariable = StringVar(value = 4), width = 5)
        self.tox.place(x=250, y=632)
        tk.Label(text = "y", font=('Arial', 12), height = 1).place(x=320, y=630)
        self.toy = tk.Entry(textvariable = StringVar(value = 4), width = 5)
        self.toy.place(x=332, y=632)
        
        self.create = tk.Button(text="Create", command = self.Create)
        self.create.place(x=270, y=660)
        self.clean = tk.Button(text="Clean", command = self.Clean)
        self.clean.place(x=272, y=690)
        
        
        
        tk.Label(text = "Training Epochs", bg = "orange", font=('Arial', 12), width = 15, height = 1).place(x=30, y=610)
        self.etrain = tk.Entry(textvariable = StringVar(value = 10), width = 10)
        self.etrain.place(x=60, y=635)
        self.btrain = tk.Button(text="Train", command = self.Train)
        self.btrain.place(x=80, y=655)
        
        self.btrain = tk.Button(text="Show EXP", command = self.EXP)
        self.btrain.place(x=80, y=695)
        self.btrain = tk.Button(text="Clean EXP", command = self.EXPclean)
        self.btrain.place(x=80, y=720)
        '''
        tk.Label(text = "Alpha/Beta/Gamma", bg = "orange", font=('Arial', 12), width = 15, height = 1).pack()
        self.ea = tk.Entry(textvariable = StringVar(value = 0.6))
        self.ea.pack()
        self.eb = tk.Entry(textvariable = StringVar(value = 0.3))
        self.eb.pack()
        self.ec = tk.Entry(textvariable = StringVar(value = 0.1))
        self.ec.pack()
        
        tk.Label(text = "Dist1/Dist2", bg = "orange", font=('Arial', 12), width = 8, height = 1).pack()
        self.e1 = tk.Entry(textvariable = StringVar(value = 3))
        self.e1.pack()
        self.e2 = tk.Entry(textvariable = StringVar(value = 7))
        self.e2.pack()
        
        b = tk.Button(text="Create Task",command = self.batchTask)
        b.pack()
        
        b = tk.Button(text="Create Task",command = self.Add)
        b.pack()
        
        tk.Label(text = "AGV number", bg = "orange", font=('Arial', 12), width = 10, height = 1).pack()
        
        
        v = StringVar(value = 1)
        self.Vnum = tk.Entry(textvariable = v)
        self.Vnum.pack()'''
        
        self.start = tk.Button(text="Start",command = self.Start, state = "normal")
        self.start.place(x=80, y=580)
        
        tk.Label(text = "Method", bg = "orange", font=('Arial', 12), width = 8, height = 1).place(x=458, y=585)
        method = StringVar(value = "Astar").get()
        self.CBox = ttk.Combobox(width=12, textvariable = method)
        self.CBox['values'] = ("Dijkstra's", "Astar", "Mod-Astar1", "Mod-Astar2", "Q-Learning")
        self.CBox.place(x=440, y=610)
        self.CBox.current(4)
        
        tk.Label(text = "Speed", bg = "orange", font=('Arial', 12), width = 8, height = 1).place(x=458, y=645)
        method = StringVar(value = "Moderate").get()
        self.CBox2 = ttk.Combobox(width=12, textvariable = method)
        self.CBox2['values'] = ("Real Time", "Moderate", "Fast", "Extremely Fast")
        self.CBox2.place(x=440, y=670)
        self.CBox2.current(2)
        
        self.CFree = IntVar()
        check = tk.Checkbutton(text="Conflict Free", variable = self.CFree, state = "normal")
        check.place(x=440, y=695)
        
        self.time = self.canvas.create_text(2.5*unit\
                                            , 0.5*unit, text = ""\
                                            , font = ("arial", 20)\
                                            , fill = "Blue")
        
        
    def EXP(self):
        table = copy.deepcopy(self.Controller.RL.Qtable[tuple([10, 8])])
        
        if hasattr (self, "expArrow"):
            self.EXPclean()
        else:
            self.expArrow = []
        
        for i in range(np.shape(table)[0]):
            expArrow = []
            for j in range(np.shape(table)[1]):
                if hasattr(self.Controller, "BLOCK"):
                    if [i, j] in self.Controller.BLOCK:
                        table[i][j][0] = 9999
                    elif [i, j+1] in self.Controller.BLOCK:
                        table[i][j][1] = -1
                    elif [i, j-1] in self.Controller.BLOCK:
                        table[i][j][2] = -1
                    elif [i-1, j] in self.Controller.BLOCK:
                        table[i][j][3] = -1
                    elif [i+1, j] in self.Controller.BLOCK:
                        table[i][j][4] = -1
                
                
                direct = table[i][j]
                
                indexes = []
                MAX = min(direct)
                for k in range(len(direct)):
                    if direct[k] == MAX:
                        indexes.append(k)
                    elif direct[k] > MAX:
                        MAX = direct[k]
                        indexes = [k]
                if 0 in indexes:
                    indexes = [0]
                    

                
                x = self.Origin[0]*self.unit + i*self.unit
                y = self.Origin[1]*self.unit - j*self.unit + self.Hight*self.unit
                
                for k in indexes:
                    item = []
                    if k == 2:
                        item.append(self.canvas.create_line(x, y+0.4*self.unit, x, y-0.4*self.unit, fill = "red", width = 5, arrow = tk.FIRST))
                    elif k == 1:
                        item.append(self.canvas.create_line(x, y-0.4*self.unit, x, y+0.4*self.unit, fill = "red", width = 5, arrow = tk.FIRST))
                    elif k == 3:
                        item.append(self.canvas.create_line(x-0.4*self.unit, y, x+0.4*self.unit, y, fill = "red", width = 5, arrow = tk.FIRST))
                    elif k == 4:
                        item.append(self.canvas.create_line(x+0.4*self.unit, y, x-0.4*self.unit, y, fill = "red", width = 5, arrow = tk.FIRST))
                    else:
                        item.append(0)
                    expArrow.append(item)
            
            self.expArrow.append(expArrow)
                
                
    def EXPclean(self):
        for i in range(len(self.expArrow)):
            for j in range(len(self.expArrow[i])):
                for k in self.expArrow[i][j]:
                    self.canvas.delete(k)
                
        self.expArrow = []
        
    def Create(self):
        fx = int(self.fromx.get())
        fy = int(self.fromy.get())
        tx = int(self.tox.get())
        ty = int(self.toy.get())
        
        if tx < fx:
            tx, fx = fx, tx
        if ty < fy:
            ty, fy = fy, ty
        

        
        p1 = [(self.Origin[0]+fx-0.2)*self.unit, (self.Origin[1]+self.Hight-fy+0.2)*self.unit]
        p2 = [(self.Origin[0]+tx+0.2)*self.unit, (self.Origin[1]+self.Hight-ty-0.2)*self.unit]
        self.obstacle.append(self.canvas.create_rectangle(p1[0], p1[1], p2[0], p2[1], fill = "blue"))
        
        for i in range(fx, tx+1):
            for j in range(fy, ty+1):
                self.Controller.BLOCK.append([i, j])
                
                
        
        
    def Clean(self):
        self.Controller.BLOCK = []
        for i in self.obstacle:
            self.canvas.delete(i)
            
        self.obstacle = []
        
        
    def Train(self):
        self.btrain.config(state = "disable")
        self.start.config(state = "disable")
        Epoch = int(self.etrain.get())
        for i in range(Epoch):
            self.Start(False)
        self.btrain.config(state = "normal")
        self.start.config(state = "normal")
        
    
    def Start(self, demo = True):
        self.Add()
        
        if demo:
            self.Controller.demo = True
            self.Controller.RL.Epsilon = 0.1
        else:
            self.Controller.demo = False
            self.Controller.RL.Epsilon = 0.8
        
        #self.start.config(state = "disable")
        #Get Routing Method
        if self.CBox.get() == "Dijkstra's":
            self.Controller.routRule = 0
        elif self.CBox.get() == "Astar":
            self.Controller.routRule = 1
        elif self.CBox.get() == "Mod-Astar1":
            self.Controller.routRule = 2
        elif self.CBox.get() == "Mod-Astar2":
            self.Controller.routRule = 3
        elif self.CBox.get() == "Q-Learning":
            self.Controller.routRule = 4
            
        #Get Simulation Speed
        if self.CBox2.get() == "Real Time":
            self.Controller.speed = 1
        elif self.CBox2.get() == "Moderate":
            self.Controller.speed = 5
        elif self.CBox2.get() == "Fast":
            self.Controller.speed = 10
        elif self.CBox2.get() == "Extremely Fast":
            self.Controller.speed = 100
        
        
        #Get Parameters
        Alpha = 0.6
        Beta = 0.3
        Gamma = 0.1
        Dist1 = 3
        Dist2 = 7
        '''
        Alpha = float(self.ea.get())
        Beta = float(self.eb.get())
        Gamma = float(self.ec.get())
        Dist1 = int(self.e1.get())
        Dist2 = int(self.e2.get())
        '''
        self.Controller.Parameter = [Alpha, Beta, Gamma, Dist1, Dist2]
        
        if self.CFree.get():
            #print("Free")
            self.Controller.mesh = self.Controller.create_path(self.env, self.Controller.x, self.Controller.y, 1)
        else:
            #print("Bang")
            self.Controller.mesh = self.Controller.create_path(self.env, self.Controller.x, self.Controller.y, 50)
        '''
        num = int(self.Vnum.get())'''
        num = 1
        for i in range(num):
            current = self.froms.pop(0)
            goal = self.tos.pop(0)
            self.Controller.create_task(current, goal)
        self.env.process(self.Controller.TimeCount())
        self.env.run()
        
    
    def Add(self):
        '''current = [int(self.ex.get()), int(self.ey.get())]
        goal = [int(self.tx.get()), int(self.ty.get())]
        '''
        current = [0, 1]
        goal = [10, 8]
        self.froms = []
        self.tos = []
        self.froms.append(current)
        self.tos.append(goal)
        #show = "Task" + str(len(self.froms)) + ": From " + str(current) + " To " + str(goal) + "\n"
        #self.tasklist.insert("insert", show)
        
        self.start.config(state = "normal")
        
    def clean(self):
        self.tasklist.delete(1.0, 50.0)
        self.froms = []
        self.tos = []
    
    
    def batchTask(self):
        '''
        self.tasklist.delete(1.0, 50.0)
        
        '''
        self.froms = []
        self.tos = []
        
        self.start.config(state = "normal")
        
        self.froms = [[7, 2], [5, 4], [6, 6], [4, 1], [6, 4], [5, 6]\
                      , [7, 5], [2, 3], [7, 7], [3, 6], [1, 3], [6, 1]\
                      ,[5, 5], [6, 7], [2, 7], [2, 1], [6, 2], [1, 7]\
                      , [4, 3], [4, 2], [4, 5], [5, 1], [7, 6], [3, 7]\
                      , [5, 2], [1, 2], [2, 4], [1, 1], [7, 3], [2, 6]\
                      , [3, 1], [7, 4], [6, 3], [5, 7], [7, 1], [1, 4]]
        self.tos = [[5, 5], [6, 7], [2, 7], [2, 1], [6, 2], [1, 7]\
                      , [4, 3], [4, 2], [4, 5], [5, 1], [7, 6], [3, 7]\
                      ,[7, 2], [5, 4], [6, 6], [4, 1], [6, 4], [5, 6]\
                      , [7, 5], [2, 3], [7, 7], [3, 6], [1, 3], [6, 1]\
                      , [2, 2], [2, 5], [3, 2], [1, 5], [4, 7], [4, 4]\
                      , [5, 3], [3, 4], [6, 5], [4, 6], [3, 3], [3, 5]]
        
        self.froms = []
        self.tos = []
        all_point = []
        for i in range(Hight+1):
            for j in range(Width+1):
                all_point.append([i, j])
                
        for i in range(30):
            index = np.random.choice(range(len(all_point)))
            self.froms.append(all_point.pop(index))
            index = np.random.choice(range(len(all_point)))
            self.tos.append(all_point.pop(index))
        '''
        self.froms = [[7, 2], [5, 4], [6, 6], [4, 1], [6, 4], [5, 6]\
                      , [7, 5], [2, 3], [7, 7], [3, 6], [1, 3], [6, 1]\
                      , [2, 2], [2, 5], [3, 2], [1, 5], [4, 7], [4, 4]\
                      , [5, 3], [3, 4], [6, 5], [4, 6], [3, 3], [3, 5]]
        self.tos = [[5, 5], [6, 7], [2, 7], [2, 1], [6, 2], [1, 7]\
                      , [4, 3], [4, 2], [4, 5], [5, 1], [7, 6], [3, 7]\
                      , [5, 2], [1, 2], [2, 4], [1, 1], [7, 3], [2, 6]\
                      , [3, 1], [7, 4], [6, 3], [5, 7], [7, 1], [1, 4]]
        
        for i in range(len(self.froms)):
            show = "Task" + str(i+1) + ": From " + str(self.froms[i]) + " To " + str(self.tos[i]) + "\n"
            self.tasklist.insert("insert", show)
        '''

    def BuildFloor(self):
        self.canvas = tk.Canvas(self, bg = "white", height = (self.Hight+1.5)\
                *self.unit, width = (self.Width+2)*self.unit)
        self.AGV = []
        self.agv = []

        #Grid Layout
        for c in range(0, (self.Width*self.unit+1), self.unit):
            x0, y0, x1, y1 = self.Origin[0]*self.unit+c, self.Origin[1]*unit\
                    , self.Origin[0]*self.unit+c, (self.Hight+self.Origin[1])\
                    *self.unit
            self.canvas.create_line(x0, y0, x1, y1)

        for r in range(0, (self.Hight*self.unit+1), self.unit):
            x0, y0, x1, y1 = self\
                    .Origin[0]*self.unit, self.Origin[1]*self.unit+r\
                    , (self.Width+self.Origin[0])*self.unit\
                    , self.Origin[1]*self.unit+r
            self.canvas.create_line(x0, y0, x1, y1)

        self.canvas.place(x=50, y=0)

    def render(self):
        self.update()
            


            
