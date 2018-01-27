! Module tort_mod defined in file tort.f90

subroutine f90wrap_test_node__array__neigh_ind(this, nd, dtype, dshape, dloc)
    use tort_mod, only: test_node
    implicit none
    type test_node_ptr_type
        type(test_node), pointer :: p => NULL()
    end type test_node_ptr_type
    integer, intent(in) :: this(2)
    type(test_node_ptr_type) :: this_ptr
    integer, intent(out) :: nd
    integer, intent(out) :: dtype
    integer, dimension(10), intent(out) :: dshape
    integer*8, intent(out) :: dloc
    
    nd = 1
    dtype = 5
    this_ptr = transfer(this, this_ptr)
    if (allocated(this_ptr%p%neigh_ind)) then
        dshape(1:1) = shape(this_ptr%p%neigh_ind)
        dloc = loc(this_ptr%p%neigh_ind)
    else
        dloc = 0
    end if
end subroutine f90wrap_test_node__array__neigh_ind

subroutine f90wrap_test_node_initialise(this)
    use tort_mod, only: test_node
    implicit none
    
    type test_node_ptr_type
        type(test_node), pointer :: p => NULL()
    end type test_node_ptr_type
    type(test_node_ptr_type) :: this_ptr
    integer, intent(out), dimension(2) :: this
    allocate(this_ptr%p)
    this = transfer(this_ptr, this)
end subroutine f90wrap_test_node_initialise

subroutine f90wrap_test_node_finalise(this)
    use tort_mod, only: test_node
    implicit none
    
    type test_node_ptr_type
        type(test_node), pointer :: p => NULL()
    end type test_node_ptr_type
    type(test_node_ptr_type) :: this_ptr
    integer, intent(in), dimension(2) :: this
    this_ptr = transfer(this, this_ptr)
    deallocate(this_ptr%p)
end subroutine f90wrap_test_node_finalise

subroutine f90wrap_set_nodes(n, indices, n0)
    use tort_mod, only: set_nodes
    implicit none
    
    integer, intent(in) :: n
    integer, intent(in), dimension(n0) :: indices
    integer :: n0
    !f2py intent(hide), depend(indices) :: n0 = shape(indices,0)
    call set_nodes(n=n, indices=indices)
end subroutine f90wrap_set_nodes

subroutine f90wrap_set_neighbours(ind, n, neigh, n0)
    use tort_mod, only: set_neighbours
    implicit none
    
    integer, intent(in) :: ind
    integer, intent(in) :: n
    integer, intent(in), dimension(n0) :: neigh
    integer :: n0
    !f2py intent(hide), depend(neigh) :: n0 = shape(neigh,0)
    call set_neighbours(ind=ind, n=n, neigh=neigh)
end subroutine f90wrap_set_neighbours

subroutine f90wrap_torture(n)
    use tort_mod, only: torture
    implicit none
    
    integer, intent(in) :: n
    call torture(n=n)
end subroutine f90wrap_torture

! End of module tort_mod defined in file tort.f90

