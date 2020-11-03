'''
Created on Oct 12, 2016

@author: mwittie
'''

import network_1 as network
import link_1 as link
import threading
from time import sleep
from rprint import print


## configuration parameters
router_queue_size = 0  # 0 means unlimited
simulation_time = 2  # give the network sufficient time to transfer all packets before quitting

if __name__ == '__main__':
        object_L = []  # keeps track of objects, so we can kill their threads
        
        # create network nodes
        client = network.Host(1)
        object_L.append(client)
        server = network.Host(2)
        object_L.append(server)
        router_a = network.Router(name='A', intf_count=1, max_queue_size=router_queue_size)
        object_L.append(router_a)
        
        # create a Link Layer to keep track of links between network nodes
        link_layer = link.LinkLayer()
        object_L.append(link_layer)
        
        # add all the links
        # link parameters: from_node, from_intf_num, to_node, to_intf_num, mtu
        link_layer.add_link(link.Link(client, 0, router_a, 0, 50))
        link_layer.add_link(link.Link(router_a, 0, server, 0, 50))
        
        # start all the objects
        thread_L = [threading.Thread(name=object.__str__(), target=object.run) for object in object_L]
        for t in thread_L:
                t.start()

        try:
                client.udt_send(2, "DATA")
                sleep(0.1)
                #client.udt_send(2, "We the People of the United States, in Order to form a more perfect...")
                client.udt_send(2, 'We the People of the United States, in Order to form a more perfect Union, establish Justice, insure domestic Tranquility, provide for the common defense, promote the general Welfare, and secure the Blessings of Liberty to ourselves and our Posterity, do ordain and establish this Constitution for the United States of America.')
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


                
        # create some send events
##      for i in range(3):
##              client.udt_send(2, 'Sample data %d' % i)
        
##      client.udt_send(2, 'We the People of the United States, in Order to form a more perfect Union, establish Justice, insure domestic Tranquility, provide for the common defense, promote the general Welfare, and secure the Blessings of Liberty to ourselves and our Posterity, do ordain and establish this Constitution for the United States of America.')
        
##      # give the network sufficient time to transfer all packets before quitting
##      sleep(simulation_time)
##      
##      # join all threads
##      for o in object_L:
##              o.stop = True
##      for t in thread_L:
##              t.join()
        
        print("All simulation threads joined")
