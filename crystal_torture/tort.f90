MODULE tort_mod

IMPLICIT NONE

  type test_node
     integer:: node_index
     integer,allocatable, dimension(:)::neigh_ind
  end type test_node

    
  TYPE queued_node
      INTEGER  :: node_index
      TYPE(queued_node),POINTER:: next_node
  END TYPE queued_node


  TYPE(test_node),ALLOCATABLE,DIMENSION(:)::nodes


CONTAINS


     SUBROUTINE set_nodes( n, indices)

        
        integer, intent(in)::n
        integer, dimension(n), intent(in)::indices
        integer :: i

        allocate(nodes(n))
        DO i=1,n
           nodes(i)%node_index=indices(i)
        END DO

     END SUBROUTINE set_nodes

     SUBROUTINE set_neighbours(ind,n,neigh)

        integer :: i
        integer, intent(in):: ind,n
        integer, dimension(n), intent(in):: neigh


        allocate(nodes(ind+1)%neigh_ind(n))

        DO i=1,n
          nodes(ind+1)%neigh_ind(i) = neigh(i)
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

     SUBROUTINE torture(n)

        TYPE(queued_node), POINTER:: head_node, tail_node

        integer :: i, AllocStat
        integer, intent(in):: n
        LOGICAL ::check

        ALLOCATE( head_node, STAT=AllocStat)
        ALLOCATE( tail_node, STAT=AllocStat)
        head_node%node_index = nodes(1)%node_index
        tail_node => head_node
        NULLIFY(tail_node%next_node)
         


        if (allocated(nodes)) then
           print*,"nodes allocated"
        else
           print*,"node isn't allocated"
        end if

       
        DO i=2,n
           print*,"node",i,"neighbours",nodes(i)%neigh_ind 
           call enqueue_node(tail_node,nodes(i)%node_index) 
        END DO
 
          
         
        call check_list(head_node,213,check)
        DO i=1,n
           print*,"Node index",head_node%node_index
           
           call dequeue_node(head_node)
        END DO
       
     END SUBROUTINE torture

     SUBROUTINE torture_test


     END SUBROUTINE torture_test


END MODULE tort_mod
