MODULE tort_mod

use omp_lib

IMPLICIT NONE

  TYPE test_node
     INTEGER:: node_index, uc_index
     INTEGER,allocatable, DIMENSION(:)::neigh_ind
  END TYPE test_node

    
  TYPE queued_node
      INTEGER  :: node_index
      TYPE(queued_node),POINTER:: next_node
  END TYPE queued_node


  TYPE(test_node),ALLOCATABLE,DIMENSION(:)::nodes

  INTEGER,ALLOCATABLE,DIMENSION(:):: uc_tort

CONTAINS

     SUBROUTINE allocate_nodes(n,n2)
       INTEGER, INTENT(IN)::n,n2


        ALLOCATE(nodes(0:n-1))
        ALLOCATE(uc_tort(0:n2-1))
        uc_tort(:) = 0
     END SUBROUTINE allocate_nodes

     SUBROUTINE set_nodes(n,n2)


        INTEGER, INTENT(IN)::n,n2
        INTEGER :: node

!        ALLOCATE(nodes(0:n-1))
!        DO node=0,n-1
!           nodes(node)%node_index=node
!        END DO
!        ALLOCATE(uc_tort(0:n2-1))
         
       
     END SUBROUTINE set_nodes

     SUBROUTINE tear_down

        INTEGER::i,no_nodes
  
        no_nodes = SIZE(nodes)-1

        DO i=0,no_nodes
           IF (ALLOCATED(nodes(i)%neigh_ind)) THEN
              DEALLOCATE(nodes(i)%neigh_ind)
           END IF
        END DO
        DEALLOCATE(nodes,uc_tort)

     END SUBROUTINE tear_down

     SUBROUTINE set_neighbours(ind,uc_ind,n,neigh)

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

        TYPE(queued_node),POINTER,INTENT(INOUT)::tail
        TYPE(integer),INTENT(IN)::node_index

        ALLOCATE(tail%next_node)
        tail%next_node%node_index = node_index
        tail => tail%next_node
        NULLIFY(tail%next_node)

     END SUBROUTINE enqueue_node

     SUBROUTINE dequeue_node(head)

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


     SUBROUTINE check_list(head,index_to_check,check)
        TYPE(queued_node), POINTER, INTENT(IN):: head
        INTEGER,INTENT(IN) :: index_to_check
        TYPE(queued_node), POINTER :: current_node
        LOGICAL, INTENT(OUT) :: check

        current_node => head
        check = .False.

        DO WHILE(ASSOCIATED(current_node))
          IF (current_node%node_index == index_to_check) THEN
             check = .True.
             EXIT
          END IF
          current_node => current_node%next_node

        END DO
     END SUBROUTINE check_list

     SUBROUTINE initialise_queue(head,tail)
 
        TYPE(queued_node), POINTER, INTENT(INOUT)::head,tail
 
        INTEGER::AllocStat
           
        ALLOCATE(head,STAT=AllocStat)
        ALLOCATE(tail,STAT=AllocStat)

        tail => head
        NULLIFY(tail%next_node)

     END SUBROUTINE

     SUBROUTINE shut_down_queue(head)

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





















