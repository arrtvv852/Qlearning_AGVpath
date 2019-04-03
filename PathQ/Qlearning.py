# -*- coding: utf-8 -*-
"""
Created on Thu Jan  4 17:57:16 2018

@author: CIMlab
"""

import numpy as np
import random as rd


class QLearning:
    def __init__(self, state_size, action_num, Alpha, Gamma, incre):
        tmp = state_size
        tmp.append(action_num)
        self.Qtable = np.zeros((tmp))
        self.actions = action_num
        self.Alpha = Alpha
        self.Gamma = Gamma
        self.Epsilon = 0.9
        self.incre = incre
        
        self.Rewards = []
        self.Actions = []
        for i in range(action_num):
            self.Actions.append(0)
        
    def Choose_act(self, state, block = []):
        if rd.random() < self.Epsilon:
            candidate = self.Qtable[tuple(state)].tolist()
            for i in block:
                candidate[i] = -1
            #candidate[0] = -0.5
                
                
            indexes = []
            MAX = min(candidate)
            for i in range(len(candidate)):
                if candidate[i] >= MAX:
                    MAX = candidate[i]
                    indexes.append(i)
                
            action = rd.choice(indexes)
            
            self.Actions[action] += 1
            return action
        else:
            #print("rand")
            action = rd.choices(range(1, self.actions))[0]
            while action in block:
                action = rd.choices(range(1, self.actions))[0]
            
            self.Actions[action] += 1
            return action
            
    def Learning(self, s, a, s_, r, Terminate = False):
        
        
        self.Rewards.append(r)
        
        p = s
        p.append(a)
        Predict = self.Qtable[tuple(p)]
        Target = np.max(self.Qtable[tuple(s_)])
        self.Qtable[tuple(p)] += self.Alpha*(r + self.Gamma*Target - Predict)
        '''
        if Terminate:
            if self.Epsilon + self.incre < 0.99:
                self.Epsilon += self.incre
            else:
                self.Epsilon = 0.999'''
