from crystal_torture.node import  Node
import copy
import sys
import pathos.multiprocessing as mp
from queue import Queue
from crystal_torture import tort
from threading import Thread


class Cluster:
    """
    Cluster class: group of connected nodes within graph
    """

    def __init__(self,nodes):
        """
        Initialise a cluster.

        Args:
            nodes (set(Node)): set of nodes in the cluster.
        """

        self.nodes = nodes
        self.periodic = None #[False, False, False]
        

    def merge(self, other_cluster):
        """
        Merge two clusters into one
 
        Args:
            other_cluster (Cluster): cluster to be joined
        """
        
        new_cluster =  Cluster(self.nodes|other_cluster.nodes )
        
        return new_cluster

    def is_neighbour(self, other_cluster):
        """
        Check if one cluster of nodes is connected to another
        """

        return bool( self.nodes & other_cluster.nodes ) 

#    @profile
    def grow_cluster(self,key=None,value=None):
        """
        Grow cluster by adding neighbours
 
        Args:
            key (str): label key to selectively choose nodes in cluster
            value : value for label to selectively choose nodes in cluster
        """

        nodes_to_visit = set([ self.nodes.pop() ])

        
        visited = set()      
        add = visited.add        
 
        if key:
           
           while nodes_to_visit:
              # print("nodes to visit",[node.index for node in nodes_to_visit])
               node = nodes_to_visit.pop()
              # print("popped node",node.index)
#               nodes_to_visit += set([ neigh for neigh in node.neighbours if (neigh not in visited and neigh.labels[key]==value)])
               nodes_to_visit = nodes_to_visit.union(set([ neigh for neigh in node.neighbours if (neigh not in visited and neigh.labels[key]==value)]))
              # print("adding neighbours of node",node.index,"to stack:",[node.index for node in nodes_to_visit])
              # print([(n_node.index,n_node.labels[key]) for n_node in node.neighbours if n_node.labels[key]==value]) 

#               visited.add(node)   
               add(node)
             #  print("******************")
        else:
           while nodes_to_visit:
               node = nodes_to_visit.pop()
              # nodes_to_visit += [ neigh for neigh in node.neighbours if neigh not in visited ]
               nodes_to_visit = nodes_to_visit.union(set([ neigh for neigh in node.neighbours if neigh not in visited]))
               #visited.add(node)
               add(node)

        self.nodes = visited
        print("Nodes in cluster",len(self.nodes))


    def return_key_nodes(self,key,value):
        """
        Returns the nodes in a cluster corresponding to a particular label

        Args:
           key (str): Dictionary key for filtering nodes
           value    : value held in dictionary for label key

        Returns:
           key_nodes (set(Node)): set of nodes in cluster for which (node.labels[key] == value)
       
        """

        key_nodes=set([node for node in self.nodes if node.labels[key]==value])
 
        return key_nodes
            

    def return_index_node(self,index):
       
        index_node = [node for node in self.nodes if node.index == index]

        return index_node
    
    def torture(self):
        """
        Calculates the average tortuosity of the cluster
        but includes all nodes in path -

        this is wrong.
 
        the nodes on the path will not necessarily have the same tortuosity,
        but it provides a bound on them 

        if the path between i and i contains j, and the path between j and j contains
        i then both have the same tortuosity

        

 
         -      o
         |      |
         |      |
         |      o
                |
                |
       ---------|--------------
                |      !
                |      ! 
                o--------------o     
                |      !       |
                |      !       |
                o      |       o
         
        """
        print("about to torture")
 
        uc = self.return_key_nodes(key="Halo",value=False)

        while uc:

           path_stack = [[uc.pop()]]
           uc_index = path_stack[0][0].labels["UC_index"]
           index = path_stack[0][0].index
#           print("Popped index", index,"(",uc_index,")")

           steps = 0    
         
           visited = set()
           dist = [0]*len(self.nodes)        

           while path_stack:
           
               path = path_stack.pop(0)
               node = path[-1]
               next_dist = dist[node.index] + 1
               if node not in visited:
                  if (node.labels["UC_index"] == uc_index) and (node.index != index):
                      for node_p in path:
                          #print("LOOPED:","SEEKING",index,"(",uc_index,")  at:",node.index,"(",node.labels["UC_index"],")",node.labels["UC_index"] == uc_index , node.index == index)
                          #print("UC_index set",[nodet.labels("UC_index") for nodet in self.node])
#                          print("Setting tortuosity",node_p.index,node_p.labels["UC_index"],node_p.tortuosity,next_dist-1)
                          if node_p.tortuosity == None:
                              for node_t in self.return_key_nodes(key="UC_index",value=node_p.labels["UC_index"]):
                                  node_t.tortuosity = next_dist-1
                          elif node_p.tortuosity > next_dist -1:
                               node_t.tortuosity = next_dist-1
                             #sys.exit("Error in torture. Calculated tortuosity doesn't match for node")
                      
 #                     print("Path",[node_p.index for node_p in path],next_dist-1)

                      break 
            
                  for neighbour in node.neighbours:
                      if dist[neighbour.index] == 0:
                         dist[neighbour.index] = next_dist

                      new_path = list(path)
                      new_path.append(neighbour)
                      path_stack.append(new_path)
                  visited.add(node)

       
        for node in self.nodes:
            print("Tortuosity",node.index,node.tortuosity) 
              
#    @profile
    def torture_no_path(self,uc_q):
         while True:
            uc = uc_q.get()
            node_stack = self.return_index_node(uc)
            visited = set()
            root_node = node_stack[0]
            index = node_stack[0].index
            uc_index = node_stack[0].labels["UC_index"]
            dist={str(root_node.index):0}

            while node_stack:

               node = node_stack.pop(0)
               next_dist = dist[str(node.index)] + 1
            
               if node not in visited:
                  for neigh in node.neighbours:
                     if str(neigh.index) not in dist:
                         dist[str(neigh.index)] = next_dist
                     node_stack.append(neigh)
               if (node.labels["UC_index"] == uc_index) and (node.index != index):
                  root_node.tortuosity = next_dist-1
                  break
               visited.add(node) 
            uc_q.task_done()

    def torture_no_path_mp(self,uc):
            node_stack = self.return_index_node(uc)
            visited = set()
            root_node = node_stack[0]
            index = node_stack[0].index
            uc_index = node_stack[0].labels["UC_index"]
            dist={str(root_node.index):0}

            while node_stack:

               node = node_stack.pop(0)
               next_dist = dist[str(node.index)] + 1

               if node not in visited:
                  for neigh in node.neighbours:
                     if str(neigh.index) not in dist:
                         dist[str(neigh.index)] = next_dist
                     node_stack.append(neigh)
               if (node.labels["UC_index"] == uc_index) and (node.index != index):
                 # root_node.tortuosity = next_dist-1
                  break
               visited.add(node)

#    @profile
    def torture_multi(self):
        sys.setrecursionlimit(100000)
        uc_node_index = [node.index for node in self.return_key_nodes(key="Halo",value=False)]
        pool_size = int(mp.cpu_count())        
        pool = mp.Pool(processes=pool_size,maxtasksperchild=1)
        pool_outputs = pool.map(self.torture_no_path,uc_node_index)
        pool.close()
        pool.join()

        for i,index in enumerate(uc_node_index):
            print("i",i,index,"pool_outputs[i]",pool_outputs[i])
          
        for node in self.return_key_nodes(key="Halo",value=False) :
            print("Tortuosity",node.index,node.tortuosity)

    def torture_thread(self):
        uc_node_index = [node.index for node in self.return_key_nodes(key="Halo",value=False)]
        q = Queue(maxsize=0)
        num_threads = 4


        for i in range(num_threads):
            worker = Thread(target=self.torture_no_path, args=(q,))
            worker.setDaemon(True)
            worker.start()
     
        for node in uc_node_index:
            q.put(node)
       

        q.join()
        for node in self.return_key_nodes(key="Halo",value=False):
            print("index",node.index,"tort",node.tortuosity)        

    def torture_test(self):
###
###  this works
###
        uc = self.return_key_nodes(key="Halo",value=False)
#        print("popped",uc.pop())
        print("UC",[node.index for node in uc])
        while uc:

            
           node_stack = [uc.pop()]

           visited = set()
           dist = [0]*len(self.nodes)
           uc_index = node_stack[0].labels["UC_index"]
           index = node_stack[0].index
           root_node = node_stack[0]
        #   print("Searching for node",index,"(",uc_index,")")

           while node_stack:
 

              node=node_stack.pop(0)
              print("At node",node.index,"UC_index",node.labels["UC_index"],uc_index,"dist",dist[node.index])
              next_dist = dist[node.index] + 1

              if node not in visited:
                
                 for neigh in node.neighbours:
                     if dist[neigh.index] == 0:
                        dist[neigh.index] = next_dist 
                        print("Adding neighbours",neigh.index,next_dist)
                    # if neigh not in visited:
                        node_stack.append(neigh)
              if (node.labels["UC_index"] == uc_index) and (node.index != index):
            #     print("Found image",node.index,"(",node.labels["UC_index"],")",next_dist)
                 root_node.tortuosity = next_dist
                 break
              visited.add(node)
           print("Tortuosity  =",root_node.tortuosity-1)
           print("*********************")     
        for node in self.return_key_nodes(key="Halo",value=False):
           print("tortuosity",node.index,node.labels["UC_index"],node.tortuosity-1)
 


#    def torture_fort_play(self):
#        print("in torture fort")

#        tort.tort_mod.check_omp()
#        tort.tort_mod.set_nodes(len(self.nodes),)#,[n.index for n in self.nodes])
#        for node in self.nodes:
#           tort.tort_mod.set_neighbours(node.index,int(node.labels["UC_index"]),len(node.neighbours_ind),[ind for ind in node.neighbours_ind])
#
#        print("*********************")
#        for node in self.nodes:
#           print("PNode",node.index,"neighbours",[neigh.index for neigh in node.neighbours])


        
#        tort.tort_mod.torture(len(self.nodes))

#    @profile
    def torture_fort(self):

        uc_nodes = [node.index for node in self.return_key_nodes(key="Halo",value=False)]
        tort.tort_mod.set_nodes(len(self.nodes))
 
        for node in self.nodes:
           tort.tort_mod.set_neighbours(node.index,int(node.labels["UC_index"]),len(node.neighbours_ind),[ind for ind in node.neighbours_ind])
        
        tort.tort_mod.torture(len(uc_nodes),uc_nodes)   







