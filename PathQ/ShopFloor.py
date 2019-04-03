"""
Created on Sat Nov 18 23:29:07 2017

@author: CIMlab徐孟維
"""
import simpy
from Routing import ShortestPath as sp
import time
from Qlearning import QLearning as RL

unit = 50
Hight = 10
Width = 10
Origin = [1, 1]

split = 10


class Vehicle(object):
    def __init__(self, fms, env, Controller, mesh, id, x, y, rule, Parameter, demo = False):
        self.fms = fms
        self.ID = id
        self.x = x
        self.y = y
        self.path = 0
        self.status = []
        self.nextpath = 0
        self.RL = Controller.RL
        
        self.demo = demo
        
        self.routRule = rule
        self.Parameter = Parameter
        
        self.env = env
        self.Controller = Controller
        self.mesh = mesh
        self.redet = self.env.event()
        self.Redet = False
        
        self.env.process(self.nevigation())
        
        self.Waiting = self.env.event()
        self.wait = self.env.process(self.redetect())
        
        
        
        
    def nevigation(self):
        if self.demo:
            self.Controller.RL.Epsilon = 1
        else:
            self.Controller.RL.Epsilon = 0.7
        if self.demo:
            self.create_show(self.fms)
        self.req_ori = self.mesh[self.x][self.y].request()
        yield self.req_ori
        #print("Vehicle ", self.ID, " now at ", [self.x, self.y], " (Time: ", self.env.now, ")")
        
        if self.routRule == 4:
            x = self.goal[0]
            y = self.goal[1]
        else:
            x = self.path.path[len(self.path.path)-1][0]
            y = self.path.path[len(self.path.path)-1][1]
        p1 = [(Origin[0]-0.2+x)*unit, (Origin[1]+Hight-0.2-y)*unit]
        p2 = [(Origin[0]+0.2+x)*unit, (Origin[1]+Hight+0.2-y)*unit]
        
        if self.demo:
            self.Goal = self.fms.canvas.create_oval(p1[0], p1[1], p2[0], p2[1], fill = "red")
        
        
        while self.routRule == 4:
            if [self.x, self.y] != [self.goal[0], self.goal[1]]:
                state = self.goal + [self.x, self.y]
                if hasattr(self, "ori_state"):
                    self.RL.Learning(self.ori_state, toward, state, 0)
                
                toward = self.RL.Choose_act(state)
                if toward == 1:
                    nextpos = [self.x, self.y+1]
                elif toward == 2:
                    nextpos = [self.x, self.y-1]
                elif toward == 3:
                    nextpos = [self.x-1, self.y]
                elif toward == 4:
                    nextpos = [self.x+1, self.y]
                else:
                    #yield self.env.timeout(1)
                    self.ori_state = state
                    continue
                    
                PASS = True
                if nextpos[0] < 0 or nextpos[0] >= self.Controller.x:
                    PASS = False
                elif nextpos[1] < 0 or nextpos[1] >= self.Controller.y:
                    PASS = False
                elif nextpos in self.Controller.BLOCK:
                    self.Controller.RL.Epsilon = 0.7
                    yield self.env.timeout(1)
                    self.ori_state = state
                    continue
                else:
                    PASS = not self.detect(self.mesh[nextpos[0]][nextpos[1]].users)
                    
                block = []
                if not PASS:
                    if self.y+1 >= self.Controller.y or self.detect(self.mesh[self.x][self.y+1].users) or [self.x, self.y+1] in self.Controller.BLOCK:
                        block.append(1)
                    if self.y-1 < 0 or self.detect(self.mesh[self.x][self.y-1].users) or [self.x, self.y-1] in self.Controller.BLOCK:
                        block.append(2)
                    if self.x-1 < 0 or self.detect(self.mesh[self.x-1][self.y].users) or [self.x-1, self.y] in self.Controller.BLOCK:
                        block.append(3)
                    if self.x+1 >= self.Controller.x or self.detect(self.mesh[self.x+1][self.y].users) or [self.x+1, self.y] in self.Controller.BLOCK:
                        block.append(4)
                    
                    if len(block) < 4:
                        toward = self.RL.Choose_act(state, block)
                    else:
                        yield self.env.timeout(1)
                        self.ori_state = state
                        continue
                
                if toward == 1:
                    nextpos = [self.x, self.y+1]
                elif toward == 2:
                    nextpos = [self.x, self.y-1]
                elif toward == 3:
                    nextpos = [self.x-1, self.y]
                elif toward == 4:
                    nextpos = [self.x+1, self.y]
                else:
                    yield self.env.timeout(1)
                    self.ori_state = state
                    continue
                    
                
                
                self.req_tar = self.mesh[nextpos[0]][nextpos[1]].request()
                
                
                #self.req_ori.append(req_tar)
                yield self.req_tar
                
                if self.demo:
                    for i in range(split):
                        
                        yield self.env.timeout(1/split)
                        self.moving(toward)
                    
                else:
                    yield self.env.timeout(1)
                    

                self.mesh[self.x][self.y].release(self.req_ori)
                    
                    
                #self.req_ori.pop(0)
                self.x = nextpos[0]
                self.y = nextpos[1]
                
                self.req_ori = self.req_tar
                #self.req_tar.pop(0)

                #print("Vehicle ", self.ID, " now at ", [self.x, self.y], " (Time: ", self.env.now, ")")
                self.ori_state = state
                
            else:
                state = self.goal + [self.x, self.y]
                self.RL.Learning(self.ori_state, toward, state, 100, True)
                
                
                self.mesh[self.x][self.y].release(self.req_ori)
                
                for i in self.Controller.AGVs:
                    if self == i:
                        self.Controller.AGVs.remove(i)
                        self.Controller.AGV_num -= 1
                
                print(self.Controller.Time)
                if self.demo:
                    self.fms.canvas.delete(self.Goal)
                    self.fms.canvas.delete(self.Show)
                    self.fms.canvas.delete(self.show)
                    self.fms.update()
                
                del self
                return 0
                    
                
        
        while self.routRule != 4:
            if self.status != []:
                if self.status[0] == 1:
                    nextpos = [self.x, self.y+1]
                elif self.status[0] == 2:
                    nextpos = [self.x, self.y-1]
                elif self.status[0] == 3:
                    nextpos = [self.x-1, self.y]
                elif self.status[0] == 4:
                    nextpos = [self.x+1, self.y]
                if self.detect(self.mesh[nextpos[0]][nextpos[1]].users):
                        
                    yield self.env.timeout(0)
                    if self.status[0] == 1:
                        nextpos = [self.x, self.y+1]
                    elif self.status[0] == 2:
                        nextpos = [self.x, self.y-1]
                    elif self.status[0] == 3:
                        nextpos = [self.x-1, self.y]
                    elif self.status[0] == 4:
                        nextpos = [self.x+1, self.y]


                        
                
                self.Redet = False
                
                
                self.req_tar = self.mesh[nextpos[0]][nextpos[1]].request()
                
                
                self.redet.succeed()
                
                #self.req_ori.append(req_tar)
                yield self.req_tar | self.Waiting
                self.Waiting = self.env.event()
                self.wait.interrupt()
                if self.Redet:
                    #self.Redet = False
                    
                    if self.req_tar in self.mesh[nextpos[0]][nextpos[1]].users:
                        self.mesh[nextpos[0]][nextpos[1]].release(self.req_tar)
                    if self.req_tar in self.mesh[nextpos[0]][nextpos[1]].queue:
                        self.mesh[nextpos[0]][nextpos[1]].queue.remove(self.req_tar)
                        #self.req_tar.pop(0)
                else:
                    self.Redet = False
                    for i in range(split):
                    
                        yield self.env.timeout(1/split)
                        self.moving(self.status[0])
                    

                    self.mesh[self.x][self.y].release(self.req_ori)
                    
                    
                    #self.req_ori.pop(0)
                    self.x = nextpos[0]
                    self.y = nextpos[1]
                    
                    self.req_ori = self.req_tar
                    #self.req_tar.pop(0)
                    
                    
                    
                    self.status.pop(0)
                    print("Vehicle ", self.ID, " now at ", [self.x, self.y], " (Time: ", self.env.now, ")")
            elif self.fms.froms != [] or self.nextpath != 0:
                #yield self.env.timeout(0)
                if self.nextpath == 0:
                    current = [self.x, self.y]
                    froms = self.fms.froms.pop(0)
                    tos = self.fms.tos.pop(0)
                    
                    self.path = sp(current, froms, self.routRule, self.Controller.x-1, self.Controller.y-1, [], self, self.Parameter)
                    self.status = self.path.direct
                    
                    self.nextpath = sp(froms, tos, self.routRule, self.Controller.x-1, self.Controller.y-1, [], self, self.Parameter)
                else:
                    self.path = self.nextpath
                    self.status = self.path.direct
                    self.nextpath = 0
                
                if self.path.path != []:
                    self.fms.canvas.delete(self.Goal)
                    x = self.path.path[len(self.path.path)-1][0]
                    y = self.path.path[len(self.path.path)-1][1]
                    p1 = [(Origin[0]-0.2+x)*unit, (Origin[1]+Hight-0.2-y)*unit]
                    p2 = [(Origin[0]+0.2+x)*unit, (Origin[1]+Hight+0.2-y)*unit]
            
                    self.Goal = self.fms.canvas.create_oval(p1[0], p1[1], p2[0], p2[1], fill = "red")
            else:
                self.fms.canvas.delete(self.Goal)
                
                self.mesh[self.x][self.y].release(self.req_ori)
                for i in self.Controller.AGVs:
                    if self == i:
                        self.Controller.AGVs.remove(i)
                        self.Controller.AGV_num -= 1
                self.fms.canvas.delete(self.Show)
                self.fms.canvas.delete(self.show)
                self.fms.update()
                del self
                break
                
    def detect(self, req):
        sensor = False
        if req != []:
            for i in range(self.Controller.AGV_num):
                if self.Controller.AGVs[i].req_ori == req[0]:
                     V1 = self
                     V2 = self.Controller.AGVs[i]
                     if self.routRule != 4:
                         self.deadlock_resolve(V1, V2)
                    
                '''
                for j in self.Controller.AGVs[i].req_ori:
                    if req[0] == j:
                        V1 = self
                        V2 = self.Controller.AGVs[i]
                        self.deadlock_resolve(V1, V2)
                '''
            sensor = True
            
        return sensor
    
    def create_show(self, fms):
        #AGVs
        p = [(Origin[0]+self.x)*unit, (Origin[1]+Hight-self.y)*unit]
        p1 = [(Origin[0]-0.4+self.x)*unit, (Origin[1]+Hight-0.4-self.y)*unit]
        p2 = [(Origin[0]+0.4+self.x)*unit, (Origin[1]+Hight+0.4-self.y)*unit]

        self.Show = fms.canvas.create_oval(p1[0], p1[1], p2[0], p2[1], fill = "purple")
        self.show = fms.canvas.create_text(p[0], p[1], text = "A" + str(self.ID), font = ("arial", 10), fill = "yellow")
        
    def moving(self, action):
        base_action = [0, 0]
        if action == 1:
            base_action = [0, -1]
        elif action == 2:
            base_action = [0, 1]
        elif action == 3:
            base_action = [-1, 0]
        elif action == 4:
            base_action = [1, 0]
        dist = unit/split
        self.fms.canvas.move(self.Show, base_action[0]*dist
                             , base_action[1]*dist)
        self.fms.canvas.move(self.show, base_action[0]*dist
                             , base_action[1]*dist)
        self.fms.update()
        
    def redetect(self):
        while True:
            try:
                yield self.redet
                self.redet = self.env.event()
                yield self.env.timeout(3)
                self.Redet = True
                self.Waiting.succeed()
            except simpy.Interrupt:
                self.redet = self.env.event()
        
    def deadlock_resolve(self, V1, V2):
        toward = V1.status[0]
        if toward == 1:
            anti = 2
            if V1.x-1>=0:
                swap = 3
            elif V1.x+1<V1.Controller.x:
                swap = 4
        elif toward == 2:
            anti = 1
            if V1.x+1<V1.Controller.x:
                swap = 4
            elif V1.x-1>=0:
                swap = 3
        elif toward == 3:
            anti = 4
            if V1.y+1<V1.Controller.y:
                swap = 1
            elif V1.y-1>=0:
                swap = 2
        elif toward == 4:
            anti = 3
            if V1.y-1>=0:
                swap = 2
            elif V1.y+1<V1.Controller.y:
                swap = 1
            
        checkpoint = [[V1.x, V1.y+1], [V1.x, V1.y-1], [V1.x-1, V1.y], [V1.x+1, V1.y]]
        block = []
        for i in checkpoint:
            if i[0] < self.Controller.x and i[1] < self.Controller.y and i[0]>=0 and i[1]>=0:
                if self.mesh[i[0]][i[1]].users != []:
                    block.append(i)
                    
        if V2.status != []:
            if V2.status[0] == anti or self.Redet:
            #if True:
                ori1 = sp([V1.x, V1.y], V1.path.path[len(V1.path.path)-1], self.routRule, self.Controller.x-1, self.Controller.y-1, [], V1, self.Parameter).distance
                ori2 = sp([V2.x, V2.y], V2.path.path[len(V2.path.path)-1], self.routRule, self.Controller.x-1, self.Controller.y-1, [], V2, self.Parameter).distance
                if V1.path.path[len(V1.path.path)-1] in block or len(block)>=3:
                    modi1 = 9999
                else:
                    modi1 = sp([V1.x, V1.y], V1.path.path[len(V1.path.path)-1], self.routRule, self.Controller.x-1, self.Controller.y-1, block, V1, self.Parameter).distance
                
                checkpoint = [[V2.x, V2.y+1], [V2.x, V2.y-1], [V2.x-1, V1.y], [V2.x+1, V2.y]]
                block2 = []
                for i in checkpoint:
                    if i[0] < self.Controller.x and i[1] < self.Controller.y and i[0] >= 0 and i[1] >= 0:
                        if self.mesh[i[0]][i[1]].users != []:
                            block2.append(i)
                
                if V2.path.path[len(V2.path.path)-1] in block2 or len(block2)>=3:
                    modi2 = 9999
                else:
                    modi2 = sp([V2.x, V2.y], V2.path.path[len(V2.path.path)-1], self.routRule, self.Controller.x-1, self.Controller.y-1, block2, V2, self.Parameter).distance
                
                
                
                diff1 = modi1-ori1
                diff2 = modi2-ori2
                
                
                if diff1 <= diff2 and V1.path.path[len(V1.path.path)-1] not in block and len(block)<3:
                #if True:
                    V1.path = sp([V1.x, V1.y], V1.path.path[len(V1.path.path)-1], self.routRule, self.Controller.x-1, self.Controller.y-1, block, V1, self.Parameter)
                    V1.status = V1.path.direct
                
                if self.Redet:
                    if V1.path.path[len(V1.path.path)-1] == [V2.x, V2.y] and V2.path.path[len(V2.path.path)-1] == [V1.x, V1.y]:
                        V1.status.insert(0, swap)
        else:
            if V1.path.path[len(V1.path.path)-1] not in block and len(block)<3:
                V1.path = sp([V1.x, V1.y], V1.path.path[len(V1.path.path)-1], self.routRule, self.Controller.x-1, self.Controller.y-1, block, V1, self.Parameter)
                V1.status = V1.path.direct
                

        
        
        
                
                
                
                
class Center(object):
    def __init__(self, env, x, y, routRule, demo = False):
        self.env = env
        self.Time = 0
        self.AGVs = []
        self.x = x
        self.y = y
        self.AGV_num = 0
        self.routRule = routRule
        self.Parameter = [0.6, 0.3, 0.1, 3, 7]
        
        self.demo = demo
        
        self.BLOCK = []
        
        
        self.V1 = 0 #The Vehicle found conflict
        self.V2 = 0 #The Vehicle V1 encounter
        
        
        #self.mesh = self.create_path(self.env, x, y, 1)
        self.speed = 3
        #self.env.process(self.Conflict_Controll())
        #self.env.process(self.TimeCount())
        
        self.RL = RL([self.x, self.y, self.x, self.y], 5, 0.9, 0.1, 0.01)
        
            
    def create_AGV(self, id, x, y):
        
        vehicle = Vehicle(self.fms, self.env, self, self.mesh, id, x, y, self.routRule, self.Parameter, self.demo)
        self.AGVs.append(vehicle)
        self.AGV_num += 1
                        
    def create_path(self, env, x, y, Capacity):
        mesh = []
        for i in range(y):
            temp = []
            for j in range(x):
                temp.append(simpy.Resource(env, Capacity))
            mesh.append(temp)
        return mesh
    
    def create_task(self, origin, goal):
        ID = self.AGV_num+1
        self.create_AGV(ID, origin[0], origin[1])
        if self.routRule != 4:
            self.AGVs[ID-1].path = sp(origin, goal, self.routRule, self.x-1, self.y-1, [], self.AGVs[ID-1], self.Parameter)
            self.AGVs[ID-1].status = self.AGVs[ID-1].path.direct
        else:
            self.AGVs[ID-1].goal = goal
        
            
        
        
    def TimeCount(self):
        yield self.env.timeout(0)
        self.Time = 0
        while self.AGVs != []:
            self.fms.tlist.delete(1.0, 20.0)
            
            self.Goal = []
            
            for i in range(len(self.AGVs)):
                #show = "AGV" + str(self.AGVs[i].ID) + ": ( ->" + str(self.AGVs[i].path.path[len(self.AGVs[i].path.path)-1]) + ") " + str(self.AGVs[i].status) + "\n"
                #self.fms.tlist.insert("insert", show)
                '''
                x = self.AGVs[i].path.path[len(self.AGVs[i].path.path)-1][0]
                y = self.AGVs[i].path.path[len(self.AGVs[i].path.path)-1][1]
                p = [(Origin[0]+x)*unit, (Origin[1]+Hight-y)*unit]
                p1 = [(Origin[0]-0.2+x)*unit, (Origin[1]+Hight-0.2-y)*unit]
                p2 = [(Origin[0]+0.2+x)*unit, (Origin[1]+Hight+0.2-y)*unit]

                self.Goal.append(self.fms.canvas.create_oval(p1[0], p1[1], p2[0], p2[1], fill = "red"))
                '''
            
            if self.demo:
            
                self.fms.canvas.delete(self.fms.time)
                    
                self.fms.TIME = self.fms.canvas.create_text(unit\
                                                , 0.5*unit, text = "Time:"\
                                                , font = ("arial", 20)\
                                                , fill = "Blue")
                self.fms.time = self.fms.canvas.create_text(2.5*unit\
                                                , 0.5*unit, text = str(round(self.Time))\
                                                , font = ("arial", 20)\
                                                , fill = "Blue")
                
                
                
                
                for i in range(split):
                        
                    yield self.env.timeout(1/split)
                    self.Time += 1/split
                    if self.speed < 50:
                        time.sleep(1/(split*self.speed))
            else:
                    
                yield self.env.timeout(1)
                self.Time += 1
            
            
            for i in range(len(self.Goal)):
                self.fms.canvas.delete(self.Goal.pop(0))
                
            
            
        
'''
env = simpy.rt.RealtimeEnvironment(factor = 0.5, strict=False)
Controller = Center(env, Hight+1, Width+1, 1)
Controller.fms = 0
Controller.create_task([1, 7], [1, 1])
Controller.create_task([6, 2], [0, 2])
Controller.create_task([1, 1], [1, 7])
        
env.run()
'''
