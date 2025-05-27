module tort_c_interface
    use iso_c_binding
    use tort_mod
    implicit none
    
contains
    
    subroutine c_allocate_nodes(n, n2) bind(c, name='allocate_nodes')
        integer(c_int), intent(in), value :: n
        integer(c_int), intent(in), value :: n2
        call allocate_nodes(n, n2)
    end subroutine c_allocate_nodes
    
    subroutine c_tear_down() bind(c, name='tear_down')
        call tear_down()
    end subroutine c_tear_down
    
    subroutine c_set_neighbours(ind, uc_ind, n, neigh) bind(c, name='set_neighbours')
        integer(c_int), intent(in), value :: ind
        integer(c_int), intent(in), value :: uc_ind
        integer(c_int), intent(in), value :: n
        integer(c_int), intent(in) :: neigh(n)
        call set_neighbours(ind, uc_ind, n, neigh)
    end subroutine c_set_neighbours
    
    subroutine c_torture(n, uc_nodes) bind(c, name='torture')
        integer(c_int), intent(in), value :: n
        integer(c_int), intent(in) :: uc_nodes(n)
        call torture(n, uc_nodes)
    end subroutine c_torture
    
    function c_get_uc_tort(index) bind(c, name='get_uc_tort') result(tort_value)
        integer(c_int), intent(in), value :: index
        integer(c_int) :: tort_value
        if (allocated(uc_tort) .and. index >= 0 .and. index < size(uc_tort)) then
            tort_value = uc_tort(index)
        else
            tort_value = -1
        end if
    end function c_get_uc_tort
    
    function c_get_uc_tort_size() bind(c, name='get_uc_tort_size') result(array_size)
        integer(c_int) :: array_size
        if (allocated(uc_tort)) then
            array_size = size(uc_tort)
        else
            array_size = 0
        end if
    end function c_get_uc_tort_size

end module tort_c_interface
