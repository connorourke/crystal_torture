MODULE tort_mod

use omp_lib

IMPLICIT NONE

  TYPE test_node
  ! Type for storing node data:
  ! Contains:
  !    node_index(int): index of node
  !    uc_index(int): unit cell index label of node
  !    neigh_ind([int]): array to store neighbour indices
     INTEGER:: node_index, uc_index
     INTEGER,allocatable, DIMENSION(:)::neigh_ind
  END TYPE test_node

    
  TYPE queued_node
  ! Type for queued nodes:
  ! Contains:
  !    node_index(int): index of node
  !    next_node(queded_node(pointer)): pointer to next node in queue

      INTEGER  :: node_index
      TYPE(queued_node),POINTER:: next_node
  END TYPE queued_node


  TYPE(test_node),ALLOCATABLE,DIMENSION(:)::nodes

  INTEGER,ALLOCATABLE,DIMENSION(:):: uc_tort

CONTAINS

     SUBROUTINE allocate_nodes(n,n2)
     ! Allocate the space for the nodes and to store the
     ! unit cell node tortuosity
     ! Args:
     !     n(int): number of nodes in graph
     !     n2(int): number of nodes in original unit cell
   
           

       INTEGER, INTENT(IN)::n,n2

        call tear_down()

        ALLOCATE(nodes(0:n-1))
        ALLOCATE(uc_tort(0:n2-1))
        uc_tort(:) = 0
     END SUBROUTINE allocate_nodes


     SUBROUTINE tear_down
     ! Free up space used to store nodes, tortuosity and neighbours
     ! Args:
     !    None
     !
        INTEGER::i,no_nodes
    
        IF (allocated(nodes)) THEN
           no_nodes = SIZE(nodes)-1
           DO i=0,no_nodes
              IF (ALLOCATED(nodes(i)%neigh_ind)) THEN
                 DEALLOCATE(nodes(i)%neigh_ind)
              END IF
           END DO
           DEALLOCATE(nodes,uc_tort)
        END IF

     END SUBROUTINE tear_down

     SUBROUTINE set_neighbours(ind,uc_ind,n,neigh)
     ! Set the neighbour list and the unit cell index for the graph nodes
     ! Args:
     !   ind(int): node index to set
     !   uc_ind(int): unit cell index label for node
     !   n(int): the number of neighbours for the node
     !   neigh([int,int..]): array containing neighbour indices for node
        INTEGER :: i
        INTEGER, INTENT(IN):: ind,uc_ind,n
        INTEGER, DIMENSION(n), INTENT(IN):: neigh


        ALLOCATE(nodes(ind)%neigh_ind(n))
        DO i=1,n
          nodes(ind)%neigh_ind(i) = neigh(i)
          nodes(ind)%uc_index = uc_ind
        END DO

     END SUBROUTINE


     SUBROUTINE enqueue_node(tail,node_index)
     ! Add node to a queue of nodes
     ! Args:
     !   tail(queued_node): tail node of queue
     !   node_index(int): index of node to add to queue

        TYPE(queued_node),POINTER,INTENT(INOUT)::tail
        TYPE(integer),INTENT(IN)::node_index

        ALLOCATE(tail%next_node)
        tail%next_node%node_index = node_index
        tail => tail%next_node
        NULLIFY(tail%next_node)

     END SUBROUTINE enqueue_node

     SUBROUTINE dequeue_node(head)
     ! Remove head node from queue of nodes
     ! Args:
     !   head(queued_node): head node of queue to remove


        TYPE(queued_node),POINTER,INTENT(INOUT)::head
        TYPE(queued_node),POINTER:: h

         
        IF (associated(head%next_node)) THEN
           h=>head
           head=>head%next_node
        END IF

        IF (ASSOCIATED(h)) THEN
           DEALLOCATE(h)
        END IF

     END SUBROUTINE dequeue_node


     SUBROUTINE initialise_queue(head,tail)
     ! Set up a queue of nodes by allocating head and tail
     ! Args:
     !    head(queued_node): head node in queue
     !    tail(queued_node): tail node in queue
 
        TYPE(queued_node), POINTER, INTENT(INOUT)::head,tail
 
        INTEGER::AllocStat
           
        ALLOCATE(head,STAT=AllocStat)
        ALLOCATE(tail,STAT=AllocStat)

        tail => head
        NULLIFY(tail%next_node)

     END SUBROUTINE

     SUBROUTINE shut_down_queue(head)
     ! Close down a queue of nodes by cyclng through linked list and deallocating
     ! Args:
     !    head(queued_node): head of queue to close down

        TYPE(queued_node),POINTER,INTENT(INOUT)::head

        TYPE(queued_node), POINTER :: current_node

        current_node => head%next_node
 
        DO WHILE(ASSOCIATED(current_node))
           current_node => head%next_node
           deallocate(head)
           head=>current_node
        END DO
     END SUBROUTINE shut_down_queue

     SUBROUTINE torture(n,uc_nodes)
     ! Perform tortuosity analysis on cluster using a BFS & OpenMP
     ! The nodes in the cluster are tortured in parallel until all
     ! nodes in the cluster have been tortured, and only the
     ! nodes that reside in the original unit cell are tortured
     ! Args:
     !      n(int): number of nodes in original unit cell
     !      uc_nodes ([int]): array containing the indices of the unit cell nodes in the cluster
     ! Sets:
     !   uc_tort([int]: array containing the tortuosity for each unit cell node in cluster
     
    

        INTEGER,INTENT(IN):: n
        INTEGER,DIMENSION(n),INTENT(IN)::uc_nodes

        TYPE(queued_node), POINTER:: stack_head, stack_tail
        TYPE(queued_node), POINTER:: visited_head, visited_tail,temp
        INTEGER:: node, current_node, neigh, uc_node, uc_index, root_node, next_dist
        LOGICAL::check

        INTEGER,DIMENSION(size(NODES))::dist,visited
  
        !loop over all unit cell nodes - with OpenMP
        !$OMP PARALLEL DO private(uc_node,dist,stack_head,visited_head,stack_tail,visited)&
        !$OMP& PRIVATE(visited_tail,root_node,uc_index,neigh,next_dist,current_node,check) &
        !$OMP& SHARED(nodes,uc_nodes,uc_tort)
        DO uc_node=1,n
           dist(:) = 0
           visited(:)=0          
           
           call initialise_queue(stack_head,stack_tail)
           call initialise_queue(visited_head,visited_tail)
         
           stack_head%node_index = uc_nodes(uc_node)

           root_node = uc_nodes(uc_node)
           uc_index = nodes(root_node)%uc_index

            DO neigh=1,SIZE(nodes(stack_head%node_index)%neigh_ind)
               dist(nodes(stack_head%node_index)%neigh_ind(neigh)) = 1
               call enqueue_node(stack_tail,nodes(stack_head%node_index)%neigh_ind(neigh))

           END DO
           visited(root_node)=1
           call dequeue_node(stack_head)
            

           DO WHILE (ASSOCIATED(stack_head))
              
              next_dist = dist(stack_head%node_index) + 1
              current_node = stack_head%node_index
              
              IF (visited(current_node)==0) THEN
                
                 DO neigh=1,SIZE(nodes(stack_head%node_index)%neigh_ind)
                    if (dist(nodes(stack_head%node_index)%neigh_ind(neigh)) == 0) then
                       dist(nodes(stack_head%node_index)%neigh_ind(neigh)) = next_dist
                    END IF
                    call enqueue_node(stack_tail,nodes(stack_head%node_index)%neigh_ind(neigh))
                 END DO 
                  visited(current_node) = 1
                   
                  IF (nodes(stack_head%node_index)%uc_index .EQ. uc_index) THEN
                    uc_tort(uc_index) = next_dist - 1
                    EXIT
                 END IF
        

              END IF
              call dequeue_node(stack_head)
               
           END DO   
           
         
           call shut_down_queue(stack_head)

       END DO
      !$OMP END PARALLEL DO

     END SUBROUTINE torture



END MODULE tort_mod





















