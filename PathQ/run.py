# -*- coding: utf-8 -*-
"""
Created on Thu Jan  4 16:51:17 2018

@author: CIMlab
"""
from Env import FMS
import simpy
from ShopFloor import Center


unit = 50
Hight = 10
Width = 10
Origin = [1, 1]

routeRule = 1




#Main
env = simpy.Environment()

#env = simpy.rt.RealtimeEnvironment(factor = 0.5, strict=False)
Controller = Center(env, Hight+1, Width+1, routeRule)

fms = FMS(env, Controller, unit, Hight, Width, Origin)

Controller.fms = fms

fms.mainloop()
'''
for i in range(1000):
    fms.Start(False)
    print(Controller.Time)
    '''



'''
Controller = Center(Hight, Width, 1)
env = FMS(unit, Hight, Width, Origin, Controller)
env.after(0, demo)
env.mainloop()
'''
