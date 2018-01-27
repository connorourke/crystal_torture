MODULE tort_mod

IMPLICIT NONE

  type test_node
     integer,allocatable, dimension(:)::neigh_ind
  end type test_node

  type(test_node),allocatable,dimension(:)::nodes
CONTAINS


     SUBROUTINE set_nodes( n, indices)

        integer :: i
        integer, intent(in)::n
        integer, dimension(n), intent(in)::indices


        allocate(nodes(n))

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

     SUBROUTINE torture(n)
 
        integer :: i
        integer, intent(in):: n

        if (allocated(nodes)) then
           print*,"nodes allocated"
        else
           print*,"node isn't allocated"
        end if
 
    
       do i=1,n
          print*,"node",i,"neighbours",nodes(i)%neigh_ind 
       end do
       
     END SUBROUTINE torture

END MODULE tort_mod
