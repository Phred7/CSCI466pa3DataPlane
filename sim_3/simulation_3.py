'''
Created on Oct 12, 2016

@author: mwittie

Editted on Nov 03, 2020

@author: Phred7
'''

import network_3 as network
import link_3 as link
import threading
from time import sleep
from rprint import print
import math

class Route:
        src = None
        dest = None
        hops = ''
        
        def __init__(self, src, dest, hops):
                self.src = src
                self.dest = dest
                self.hops = hops

        def __str__(self):
                return self.getHops()

        def __int__(self):
                return self.getNumHops()

        def equals(self, other):
                return((self.getSrc() == other.getSrc()) and (self.getDest() == other.getDest()) and (self.getHops() == other.getHops()))

        def __lt__(self, other):
                return self.getNumHops() < other.getNumHops()

        def getSrc(self):
                return self.src

        def getDest(self):
                return self.dest

        def getHops(self):
                return self.hops

        def getNumHops(self):
                return len(self.hops) - 1

        def getNext(self, curr):
                for char in range(self.getNumHops()):
                        if(str(curr) == str(self.hops[char])):
                                if(char == (self.getNumHops()-1)):
                                        return 0
                                else:
                                        return self.hops[char+1]
                return -1

                

class RoutingTable:
        noConnVal = -1
        table = None
        hosts = []
        routers = []
        routes = []
        node = None

        def __init__(self, hosts, routers):
                self.hosts = hosts
                self.routers = routers
                #self.routes = routes
                #self.node = currRouter
                self.table = self.createTable(len(self.hosts), len(self.routers), self.routes)

        def createTable(self, numHosts, numRouters, routes):
                table = [[-1 for g in range(numHosts)] for h in range(numHosts)]
                #print(table)
                for i in range(0, (numHosts)):
                        for j in range(0, (numHosts)):
                                table[i][j] = self.noConnVal
                                if(i == j):
                                        table[i][j] = Route(i, j, str(i)) 
                                else:
                                        pass

                return table
##                                       for path in routes:
##                                               if((path.getSrc() == i) and (path.getDest()) == j):
##                                                       table[i][j] = str(path)

        def putRoute(self, route):
                if(isinstance(route, list)):
                        for path in route:
                                self.putRoute(path)
                elif(isinstance(route, Route)):
                        if(self.table[route.getSrc()-1][route.getDest()-1] == -1):    
                                self.table[route.getSrc()-1][route.getDest()-1] = route
                        else:
                                if(isinstance((self.table[route.getSrc()-1][route.getDest()-1]), list)):
                                        self.table[route.getSrc()-1][route.getDest()-1].append(route)
                                else:
                                        x = []
                                        x = [self.table[route.getSrc()-1][route.getDest()-1], route]
                                        self.table[route.getSrc()-1][route.getDest()-1] = x

                                

        def rmvRoute(self, route, rpl = None):
                if(rpl == None):
                        rpl = None
                else:
                        rpl = rpl

                if(isinstance(route, list)):
                        for r in route:
                                self.rmvRoute(r)
                                
                elif(isinstance(route, Route)):       
                        if(isinstance((self.table[route.getSrc()-1][route.getDest()-1]), list)):
                                x = self.table[route.getSrc()-1][route.getDest()-1]
                                for i in range(len(x)):
                                        #print("i:" + str(i) + "; " + str(x) + "; rmv:" + str(route) + ";" , end='\n')
                                        if((x[i].equals(route))):
                                                if rpl is not None:
                                                        self.table[route.getSrc()-1][route.getDest()-1][i] = rpl
                                                else:
                                                        self.table[route.getSrc()-1][route.getDest()-1].pop(i)
                                                        if(len(self.table[route.getSrc()-1][route.getDest()-1]) == 1):
                                                                self.table[route.getSrc()-1][route.getDest()-1] = self.table[route.getSrc()-1][route.getDest()-1][0]
                                                                break 
                                                        

                        elif(isinstance((self.table[route.getSrc()-1][route.getDest()-1]), Route)):
                                if rpl is not None:
                                        self.table[route.getSrc()-1][route.getDest()-1] = rpl
                                else:
                                        self.table[route.getSrc()-1][route.getDest()-1] = -1
                        
                                               
        def getNextHop(self, src, dest, curr):
                route = self.getRoute(src, dest, curr)
                ret = -1 if route == -1 else route.getNext(curr)
                return ret
                

        def getRoute(self, src, dest, curr):
                routes = self.table[src-1][dest-1]
                if(isinstance(routes, list)):
                        minRoute = None
                        for item in routes:
                                if(item.getNext(curr) != -1):
                                        minRoute = item
                                        
                        if(minRoute == None):
                                return -1
                        
                        for item in routes:
                                if((item < minRoute) and (item.getNext(curr) != -1)):
                                        minRoute = item
                        return minRoute
                elif(isinstance(routes, Route)):
                        return routes

        def getTable(self):
                return self.table

        def __str__(self):
                ret_S = ''
                ret_S += "RT:\n"
                ret_S += "    "
                for i in range(0, 2):
                        for j in range(len(self.getTable()[0])):
                                if(i == 0):
                                        ret_S += (" " + str(j+1) + " ")
                                else:
                                        ret_S += ("___")
                                        
                        ret_S += '\n'
                        if(i == 0):
                                ret_S += "   "
                        
                for i in range(len(self.getTable())):
                        ret_S += str(i+1) + " | "
                        for j in range(len(self.getTable()[i])):
                                x = self.getTable()[i][j]
                                if(isinstance(x, list)):
                                        minVal = 99999
                                        for item in range(len(x)):
                                                if(int(x[item]) < minVal):
                                                        minVal = item
                                        x = x[minVal] if minVal < 100 else x[0]
                                if(int(x) < 0):
                                        ret_S += ("{s:2.2s} ").format(s = str(int(x)))
                                else:
                                        ret_S += (" " + str(int(x)) + " ")
                                if(j == (len(self.table[i])-1)):
                                        ret_S += '\n'
                return ret_S


## configuration parameters
router_queue_size = 0  # 0 means unlimited
simulation_time = 3 # give the network sufficient time to transfer all packets before quitting

if __name__ == '__main__':
        object_L = []  # keeps track of objects, so we can kill their threads

        # create routing table
        path1 = Route(1, 3, "1ABD3")
        path2 = Route(1, 4, "1ABD4")
        path3 = Route(1, 3, "1ACD3")
        path4 = Route(1, 4, "1ACD4")
        path5 = Route(2, 3, "2ABD3")
        path6 = Route(2, 4, "2ABD4")
        path7 = Route(2, 3, "2ACD3")
        path8 = Route(2, 4, "2ACD4")
        paths = [path1, path2, path3, path4, path5, path6, path7, path8]
        table = RoutingTable([1, 2, 3, 4], ['A', 'B', 'C', 'D'])
        table.putRoute(paths)
        rmv = [path3, path4, path5, path6]
        table.rmvRoute(rmv)
        print()
        print(str(table))
        print()
        
        # create network nodes
        client1 = network.Host(1)
        object_L.append(client1)
        client2 = network.Host(2)
        object_L.append(client2)
        server1 = network.Host(3)
        object_L.append(server1)
        server2 = network.Host(4)
        object_L.append(server2)
        router_a = network.Router(name='A', intf_count=2, max_queue_size=router_queue_size, routingTable=table)
        object_L.append(router_a)
        router_b = network.Router(name='B', intf_count=1, max_queue_size=router_queue_size, routingTable=table)
        object_L.append(router_b)
        router_c = network.Router(name='C', intf_count=1, max_queue_size=router_queue_size, routingTable=table)
        object_L.append(router_c)
        router_d = network.Router(name='D', intf_count=2, max_queue_size=router_queue_size, routingTable=table)
        object_L.append(router_d)
        
        
        # create a Link Layer to keep track of links between network nodes
        link_layer = link.LinkLayer()
        object_L.append(link_layer)
        
        # add all the links
        # link parameters: from_node, from_intf_num, to_node, to_intf_num, mtu
        link_layer.add_link(link.Link(client1, 0, router_a, 0, 50))
        link_layer.add_link(link.Link(client2, 0, router_a, 1, 50))
        
        link_layer.add_link(link.Link(router_a, 0, router_b, 0, 50))
        link_layer.add_link(link.Link(router_a, 1, router_c, 0, 50))
        
        link_layer.add_link(link.Link(router_b, 0, router_d, 0, 50))
        link_layer.add_link(link.Link(router_c, 0, router_d, 1, 50))

        link_layer.add_link(link.Link(router_d, 0, server1, 0, 50))
        link_layer.add_link(link.Link(router_d, 1, server2, 0, 50))

        for link in link_layer.link_L:
                print(str(link))
        
        # start all the objects
        thread_L = [threading.Thread(name=object.__str__(), target=object.run) for object in object_L]
        for t in thread_L:
                t.start()

        try:
                #client1.udt_send(3, "DATA")
                sleep(0.5)
                #client2.udt_send(3, "DATA")
                
                #client1.udt_send(3, 'We the People of the United States, in Order to form a more perfect Union, establish Justice, insure domestic Tranquility, provide for the common defense, promote the general Welfare, and secure the Blessings of Liberty to ourselves and our Posterity, do ordain and establish this Constitution for the United States of America.')
                sleep(simulation_time)
                for o in object_L:
                        o.stop = True
                for t in thread_L:
                        t.join()
        except Exception as err:
                print("\nError Running:")
                print(str(err) + "\n")
                for o in object_L:
                        o.stop = True
                for t in thread_L:
                        t.join()
        
        print("All simulation threads joined")
