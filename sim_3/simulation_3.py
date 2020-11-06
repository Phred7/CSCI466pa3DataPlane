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
        links = []
        mtu = 0
        hops = ''
        
        def __init__(self, src, dest, hops, table):
                self.src = src
                self.dest = dest
                self.hops = hops
                if(src != dest):
                        self.getLinks(table)
                        

        def __str__(self):
                return self.getHops()

        def __int__(self):
                return self.getNumHops()

        def equals(self, other):
                return((self.getSrc() == other.getSrc()) and (self.getDest() == other.getDest()) and (self.getHops() == other.getHops()))

        def __lt__(self, other):
                return self.getMTU() > other.getMTU()

        def compHops(self, other):
                return self.getNumHops() < other.getNumHops()

        def getLinks(self, table):
                l = ''
                self.links = []
                for i in range(0, len(self.hops)-1):
                        link = -1
                        #print(str(i) + ": ", end='')
                        #print(self.hops[i] + "; ", end='')
                        if(i == 0):
                                link = table.getLink(int(self.hops[i]), str(self.hops[i+1]))
                                self.links.append(link)
                                l += str(link.from_node) + "->"
                        elif(i == (len(self.hops)-2)):
                                link = table.getLink(str(self.hops[i]), int(self.hops[i+1]))
                                self.links.append(link)
                                l += str(self.links[-1].to_node)
                        else:
                                link = table.getLink(str(self.hops[i]), str(self.hops[i+1]))
                                if(link != -1):
                                        self.links.append(link)
                                        l += str(link.to_node) + "->"
                        if(link != -1):
                                mtu = link.in_intf.mtu
                                self.mtu = mtu if mtu < self.mtu else (self.mtu if self.mtu != 0 else mtu)
                        #print(link)
                print("Route: " + str(self) + " initialized with links: " + l + " with MTU=" + str(self.mtu))

        def getSrc(self):
                return self.src

        def getDest(self):
                return self.dest

        def getHops(self):
                return self.hops

        def getMTU(self):
                return self.mtu

        def getNumHops(self):
                return len(self.hops) - 1

        def getNext(self, curr):
##                if(self.hops == "2ACD3" and curr == 'D'):
##                        for link in self.links:
##                                print(link)
                for char in range(self.getNumHops()):
                        if(str(curr) == str(self.hops[char])):
                                if(char == (self.getNumHops()-1)):
                                        return 0
                                else:
                                        return self.hops[char+1]
                return -1
        

class RoutingTable:

        table = None
        node = None
        links = None
        hosts = []
        routers = []
        formalRouters = None
        formalHosts = None
        routes = []
        noConnVal = -1
        

        def __init__(self, LinkLayer, hosts, routers):
                self.links = LinkLayer.link_L
                self.formalHosts = hosts
                self.formalRouters = routers
                
                for host in self.formalHosts:
                        self.hosts.append(host.addr)
                        
                for router in self.formalRouters:
                        self.routers.append(router.name)
                        
                self.table = self.createTable(len(self.hosts), len(self.routers))


        def createTable(self, numHosts, numRouters):
                table = [[-1 for g in range(numHosts)] for h in range(numHosts)]
                #print(table)
                for i in range(0, (numHosts)):
                        for j in range(0, (numHosts)):
                                table[i][j] = self.noConnVal
                                if(i == j):
                                        table[i][j] = Route(i, j, str(i), self) 
                                else:
                                        pass
                return table


        def getTable(self):
                return self.table
        


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
                                                        print("Route " + str(route) + " replaced with " + str(rpl))
                                                else:
                                                        self.table[route.getSrc()-1][route.getDest()-1].pop(i)
                                                        if(len(self.table[route.getSrc()-1][route.getDest()-1]) == 1):
                                                                self.table[route.getSrc()-1][route.getDest()-1] = self.table[route.getSrc()-1][route.getDest()-1][0]
                                                                print("Route removed: " + str(route))
                                                                break 
                                                        

                        elif(isinstance((self.table[route.getSrc()-1][route.getDest()-1]), Route)):
                                if rpl is not None:
                                        self.table[route.getSrc()-1][route.getDest()-1] = rpl
                                        print("Route " + str(route) + " replaced with " + str(rpl))
                                else:
                                        self.table[route.getSrc()-1][route.getDest()-1] = -1
                                        print("Route removed: " + str(route))


        def getNode(self, nodeName): #if a host use the int address as nodeName
                if(isinstance(nodeName, int)):
                        for host in self.hosts:
                                if(nodeName == host):
                                        return self.formalHosts[self.hosts.index(host)]
                elif(isinstance(nodeName, str)):
                        for router in self.routers:
                                if(nodeName == router):
                                        return self.formalRouters[self.routers.index(router)]
                else:
                        return False
                        


        def getLink(self, fromNodeName, toNodeName): #if a host use the int address as nodeName
                fNode = self.getNode(fromNodeName)
                tNode = self.getNode(toNodeName)
                if fNode is False:
                        return -1
                if tNode is False:
                        return -1
                
                for link in self.links:
                        if((link.from_node == fNode) and (link.to_node == tNode)):
                                return link
                return -1

        def getLinkByRoute(self, fromNodeName, toNodeName, srcInterface, route): #if a host use the int address as nodeName
                fNode = self.getNode(fromNodeName)
                tNode = self.getNode(toNodeName)
##                if(fromNodeName == 'D'):
##                        print(fNode)
##                        print(tNode)
##                        print(srcInterface)
##                        #print(self.links[-1])
##                        #print(route.links[-1])
                if fNode is False:
                        return -1
                if tNode is False:
                        return -1
                if srcInterface is None:
                        return -1
                
                for link in route.links:
##                        if(fromNodeName == 'D'): 
##                                print(link)
                        #if(link == route.links[-1]):
                                #print("link: " + str(link) + "; From: " + str(link.from_node) + "; To: " + str(link.to_node) + "; intf: " + str(link.from_intf_num))
                        if((link.from_node == fNode) and (link.to_node == tNode)): #and(link.from_intf_num == srcInterface)
                                #print("link: " + str(link))
                                return link
                return -1


        def getNextLink(self, dest, curr, src, srcInterface):
                #print("src: " + str(src))
                route = self.getRoute(dest, curr, src)
                hop = route.getNext(curr)
                #print("hop:" + str(hop))
                nxt =  hop if route != 0 else 0
                dest = nxt if nxt != 0 else dest
                return -1 if route == -1 else self.getLinkByRoute(curr, dest, srcInterface, route)
                        
        def getRoute(self, dest, curr, src):                        
                ret = []
                routes = self.table[src-1][dest-1]
                #print("routes: " + str(routes))
                if(isinstance(routes, list)):
                        bestRoute = routes[0]
                        for item in routes:
                                bestRoute = item if ((bestRoute < item) and (item.getMTU() != 0))  else bestRoute
                        ret.append(bestRoute)
                elif(isinstance(routes, Route)):
                        ret.append(routes)

                if(len(ret) == 0):
                        return 0
                        
                if(isinstance(ret, list)):
                        bestRoute = ret[0]
                        for item in ret:
                                bestRoute = item if ((bestRoute < item) and (item.getMTU() != 0))  else bestRoute
                        ret = bestRoute
                        return ret
                #print("return route: " + str(routes))
                return ret

        def getOutIntfNum(self, dest, curr, src, srcInterface):
                out = self.getNextLink(dest, curr, src, srcInterface)
                output_intf_num =  self.getFromIntfNum(out) if out != -1 else -1
                return output_intf_num
        

        def getFromIntfNum(self, link):
                return link.from_intf_num

        

        def __str__(self):
                ret_S = ''
                ret_S += "RT:\n"
                ret_S += "    "
                for i in range(0, 2):
                        for j in range(len(self.getTable()[0])):
                                if(i == 0):
                                        ret_S += ("  " + str(j+1) + "  ")
                                else:
                                        ret_S += ("_____")
                                        
                        ret_S += '\n'
                        if(i == 0):
                                ret_S += "   "
                        
                for i in range(len(self.getTable())):
                        ret_S += str(i+1) + " | "
                        for j in range(len(self.getTable()[i])):
                                entry = self.getTable()[i][j]
                                if(isinstance(entry, list)):
                                        mtu = entry[0].getMTU()
                                        for item in entry:
                                                mtu = item.getMTU() if mtu < item.getMTU() else mtu
                                        if((mtu < 10) and (mtu > -1)):
                                                ret_S += ("  {s:1.1s}  ".format(s = str(mtu)))
                                        else:
                                                ret_S += (" {s:4.2s}".format(s = str(mtu)))                                                
                                elif(isinstance(entry, Route)):
                                        mtu = entry.getMTU()
                                        if((mtu < 10) and (mtu > -1)):
                                                ret_S += ("  {s:1.1s}  ".format(s = str(mtu)))
                                        else:
                                                ret_S += (" {s:4.2s}".format(s = str(mtu)))
                                elif(isinstance(entry, int)):
                                        ret_S += (" {s:4.2s}".format(s = str(entry)))
                                        
                                if(j == (len(self.table[i])-1)):
                                        ret_S += '\n'
                return ret_S
                
        
## configuration parameters
router_queue_size = 0  # 0 means unlimited
simulation_time = 8 # give the network sufficient time to transfer all packets before quitting

if __name__ == '__main__':
        object_L = []  # keeps track of objects, so we can kill their threads
        
        # create network nodes
        client1 = network.Host(1)
        object_L.append(client1)
        client2 = network.Host(2)
        object_L.append(client2)
        server1 = network.Host(3)
        object_L.append(server1)
        server2 = network.Host(4)
        object_L.append(server2)
        router_a = network.Router(name='A', intf_count=2, max_queue_size=router_queue_size)
        object_L.append(router_a)
        router_b = network.Router(name='B', intf_count=1, max_queue_size=router_queue_size)
        object_L.append(router_b)
        router_c = network.Router(name='C', intf_count=1, max_queue_size=router_queue_size)
        object_L.append(router_c)
        router_d = network.Router(name='D', intf_count=2, max_queue_size=router_queue_size)
        object_L.append(router_d)
        
        
        # create a Link Layer to keep track of links between network nodes
        link_layer = link.LinkLayer()
        object_L.append(link_layer)
        
        # add all the links
        # link parameters: from_node, from_intf_num, to_node, to_intf_num, mtu
        link_layer.add_link(link.Link(client1, 0, router_a, 0, 50)) #host1 to A
        link_layer.add_link(link.Link(client2, 0, router_a, 1, 50)) #host2 to A
        link_layer.add_link(link.Link(router_a, 0, router_b, 0, 50)) #A to B
        link_layer.add_link(link.Link(router_a, 1, router_c, 0, 50)) #A to C
        link_layer.add_link(link.Link(router_b, 0, router_d, 0, 50)) #B to D
        link_layer.add_link(link.Link(router_c, 0, router_d, 1, 50)) #C to D
        link_layer.add_link(link.Link(router_d, 0, server1, 0, 50)) #D to host3
        link_layer.add_link(link.Link(router_d, 1, server2, 0, 50)) #D to host4

##        print("Links:")
##        for link in link_layer.link_L:
##                print(str(link))
##        print()

        # create routing table
        hosts = [client1, client2, server1, server2]
        routers = [router_a, router_b, router_c, router_d]
        table = RoutingTable(link_layer, hosts, routers)
        path1 = Route(1, 3, "1ABD3", table)
        path2 = Route(1, 4, "1ABD4", table)
        path3 = Route(1, 3, "1ACD3", table)
        path4 = Route(1, 4, "1ACD4", table)
        path5 = Route(2, 3, "2ABD3", table)
        path6 = Route(2, 4, "2ABD4", table)
        path7 = Route(2, 3, "2ACD3", table)
        path8 = Route(2, 4, "2ACD4", table)
        path1.mtu = 50
        paths = [path1, path2, path3, path4, path5, path6, path7, path8]
        table.putRoute(paths)
        rmv = [path3, path4, path5, path6]
        table.rmvRoute(rmv)
        print()
        print(str(table))
        print()
        
        for router in routers:
                router.setTable(table)        
        
        # start all the objects
        thread_L = [threading.Thread(name=object.__str__(), target=object.run) for object in object_L]
        for t in thread_L:
                t.start()
        print()
        try:
                #client2.udt_send(3, "DATA")
                #sleep(0.5)
                #client2.udt_send(3, "DATA")
                
                client1.udt_send(3, 'We the People of the United States, in Order to form a more perfect Union, establish Justice, insure domestic Tranquility, provide for the common defense, promote the general Welfare, and secure the Blessings of Liberty to ourselves and our Posterity, do ordain and establish this Constitution for the United States of America.')
                sleep(simulation_time)
                print()
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
