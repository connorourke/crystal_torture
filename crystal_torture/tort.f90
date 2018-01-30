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




CONTAINS

     SUBROUTINE set_nodes(n)


        INTEGER, INTENT(IN)::n
        INTEGER :: node

        ALLOCATE(nodes(n))
        DO node=1,n
           nodes(node)%node_index=node+1
        END DO

     END SUBROUTINE set_nodes

     SUBROUTINE set_neighbours(ind,uc_ind,n,neigh)

        INTEGER :: i
        INTEGER, INTENT(IN):: ind,uc_ind,n
        INTEGER, DIMENSION(n), INTENT(IN):: neigh


        ALLOCATE(nodes(ind+1)%neigh_ind(n))

        DO i=1,n
          nodes(ind+1)%neigh_ind(i) = neigh(i)+1
          nodes(ind+1)%uc_index = uc_ind
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

        ALLOCATE(h)

        IF (associated(head%next_node)) THEN
           h=head
           head=>head%next_node
        END IF

        DEALLOCATE(h)

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

!        current_node => head%next_node
 
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

        INTEGER,DIMENSION(n*27)::dist,visited


        !loop over all unit cell nodes - with OpenMP
        !$OMP PARALLEL DO private(uc_node,dist,stack_head,visited_head,stack_tail)&
        !$OMP& PRIVATE(visited_tail,root_node,uc_index,neigh,next_dist,current_node,check) &
        !$OMP& SHARED(nodes,uc_nodes)
        DO uc_node=1,n

           dist(:)=0
          
           call initialise_queue(stack_head,stack_tail)
           call initialise_queue(visited_head,visited_tail)
         
           stack_head%node_index = uc_nodes(uc_node)
           visited_head%node_index = uc_nodes(uc_node)

           root_node = uc_nodes(uc_node)
           uc_index = nodes(root_node)%uc_index

            DO neigh=1,SIZE(nodes(stack_head%node_index)%neigh_ind)
               dist(nodes(stack_head%node_index)%neigh_ind(neigh)) = 1
               call enqueue_node(stack_tail,nodes(stack_head%node_index)%neigh_ind(neigh))

           END DO
           call enqueue_node(visited_tail,root_node)
           call dequeue_node(stack_head)


           DO WHILE (ASSOCIATED(stack_head))
              
              next_dist = dist(stack_head%node_index) + 1 

              current_node = stack_head%node_index
              call check_list(visited_head,current_node,check)
              
!              IF ((.NOT. check ) .and. (current_node .ne. uc_node)) THEN
               IF (.NOT. check) THEN
                
                 DO neigh=1,SIZE(nodes(stack_head%node_index)%neigh_ind)
                    if (dist(nodes(stack_head%node_index)%neigh_ind(neigh)) == 0) then
                       dist(nodes(stack_head%node_index)%neigh_ind(neigh)) = next_dist
                    END IF
                    call enqueue_node(stack_tail,nodes(stack_head%node_index)%neigh_ind(neigh))
                 END DO 
                 call enqueue_node(visited_tail,current_node)
                

!                 IF ((nodes(stack_head%node_index)%uc_index .EQ. uc_index) .AND. &
!                     (stack_head%node_index .NE. root_node)) THEN
                  IF (nodes(stack_head%node_index)%uc_index .EQ. uc_index) THEN
                    print*,"Tortuosity for node",uc_node,next_dist-1
                    EXIT
                 END IF
        

              END IF
              call dequeue_node(stack_head)
               
           END DO   
           
         
           call shut_down_queue(stack_head)
           call shut_down_queue(visited_head)


       END DO
      !$OMP END PARALLEL DO


          
     




     END SUBROUTINE torture



END MODULE tort_mod





















