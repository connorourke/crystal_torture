! Module tort_mod defined in file tort.f90

subroutine f90wrap_test_node__get__node_index(this, f90wrap_node_index)
    use tort_mod, only: test_node
    implicit none
    type test_node_ptr_type
        type(test_node), pointer :: p => NULL()
    end type test_node_ptr_type
    integer, intent(in)   :: this(2)
    type(test_node_ptr_type) :: this_ptr
    integer, intent(out) :: f90wrap_node_index
    
    this_ptr = transfer(this, this_ptr)
    f90wrap_node_index = this_ptr%p%node_index
end subroutine f90wrap_test_node__get__node_index

subroutine f90wrap_test_node__set__node_index(this, f90wrap_node_index)
    use tort_mod, only: test_node
    implicit none
    type test_node_ptr_type
        type(test_node), pointer :: p => NULL()
    end type test_node_ptr_type
    integer, intent(in)   :: this(2)
    type(test_node_ptr_type) :: this_ptr
    integer, intent(in) :: f90wrap_node_index
    
    this_ptr = transfer(this, this_ptr)
    this_ptr%p%node_index = f90wrap_node_index
end subroutine f90wrap_test_node__set__node_index

subroutine f90wrap_test_node__get__uc_index(this, f90wrap_uc_index)
    use tort_mod, only: test_node
    implicit none
    type test_node_ptr_type
        type(test_node), pointer :: p => NULL()
    end type test_node_ptr_type
    integer, intent(in)   :: this(2)
    type(test_node_ptr_type) :: this_ptr
    integer, intent(out) :: f90wrap_uc_index
    
    this_ptr = transfer(this, this_ptr)
    f90wrap_uc_index = this_ptr%p%uc_index
end subroutine f90wrap_test_node__get__uc_index

subroutine f90wrap_test_node__set__uc_index(this, f90wrap_uc_index)
    use tort_mod, only: test_node
    implicit none
    type test_node_ptr_type
        type(test_node), pointer :: p => NULL()
    end type test_node_ptr_type
    integer, intent(in)   :: this(2)
    type(test_node_ptr_type) :: this_ptr
    integer, intent(in) :: f90wrap_uc_index
    
    this_ptr = transfer(this, this_ptr)
    this_ptr%p%uc_index = f90wrap_uc_index
end subroutine f90wrap_test_node__set__uc_index

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

subroutine f90wrap_queued_node__get__node_index(this, f90wrap_node_index)
    use tort_mod, only: queued_node
    implicit none
    type queued_node_ptr_type
        type(queued_node), pointer :: p => NULL()
    end type queued_node_ptr_type
    integer, intent(in)   :: this(2)
    type(queued_node_ptr_type) :: this_ptr
    integer, intent(out) :: f90wrap_node_index
    
    this_ptr = transfer(this, this_ptr)
    f90wrap_node_index = this_ptr%p%node_index
end subroutine f90wrap_queued_node__get__node_index

subroutine f90wrap_queued_node__set__node_index(this, f90wrap_node_index)
    use tort_mod, only: queued_node
    implicit none
    type queued_node_ptr_type
        type(queued_node), pointer :: p => NULL()
    end type queued_node_ptr_type
    integer, intent(in)   :: this(2)
    type(queued_node_ptr_type) :: this_ptr
    integer, intent(in) :: f90wrap_node_index
    
    this_ptr = transfer(this, this_ptr)
    this_ptr%p%node_index = f90wrap_node_index
end subroutine f90wrap_queued_node__set__node_index

subroutine f90wrap_queued_node__get__next_node(this, f90wrap_next_node)
    use tort_mod, only: queued_node
    implicit none
    type queued_node_ptr_type
        type(queued_node), pointer :: p => NULL()
    end type queued_node_ptr_type
    integer, intent(in)   :: this(2)
    type(queued_node_ptr_type) :: this_ptr
    integer, intent(out) :: f90wrap_next_node(2)
    type(queued_node_ptr_type) :: next_node_ptr
    
    this_ptr = transfer(this, this_ptr)
    next_node_ptr%p => this_ptr%p%next_node
    f90wrap_next_node = transfer(next_node_ptr,f90wrap_next_node)
end subroutine f90wrap_queued_node__get__next_node

subroutine f90wrap_queued_node__set__next_node(this, f90wrap_next_node)
    use tort_mod, only: queued_node
    implicit none
    type queued_node_ptr_type
        type(queued_node), pointer :: p => NULL()
    end type queued_node_ptr_type
    integer, intent(in)   :: this(2)
    type(queued_node_ptr_type) :: this_ptr
    integer, intent(in) :: f90wrap_next_node(2)
    type(queued_node_ptr_type) :: next_node_ptr
    
    this_ptr = transfer(this, this_ptr)
    next_node_ptr = transfer(f90wrap_next_node,next_node_ptr)
    this_ptr%p%next_node = next_node_ptr%p
end subroutine f90wrap_queued_node__set__next_node

subroutine f90wrap_queued_node_initialise(this)
    use tort_mod, only: queued_node
    implicit none
    
    type queued_node_ptr_type
        type(queued_node), pointer :: p => NULL()
    end type queued_node_ptr_type
    type(queued_node_ptr_type) :: this_ptr
    integer, intent(out), dimension(2) :: this
    allocate(this_ptr%p)
    this = transfer(this_ptr, this)
end subroutine f90wrap_queued_node_initialise

subroutine f90wrap_queued_node_finalise(this)
    use tort_mod, only: queued_node
    implicit none
    
    type queued_node_ptr_type
        type(queued_node), pointer :: p => NULL()
    end type queued_node_ptr_type
    type(queued_node_ptr_type) :: this_ptr
    integer, intent(in), dimension(2) :: this
    this_ptr = transfer(this, this_ptr)
    deallocate(this_ptr%p)
end subroutine f90wrap_queued_node_finalise

subroutine f90wrap_allocate_nodes(n, n2)
    use tort_mod, only: allocate_nodes
    implicit none
    
    integer, intent(in) :: n
    integer, intent(in) :: n2
    call allocate_nodes(n=n, n2=n2)
end subroutine f90wrap_allocate_nodes

subroutine f90wrap_tear_down
    use tort_mod, only: tear_down
    implicit none
    
    call tear_down()
end subroutine f90wrap_tear_down

subroutine f90wrap_set_neighbours(ind, uc_ind, n, neigh, n0)
    use tort_mod, only: set_neighbours
    implicit none
    
    integer, intent(in) :: ind
    integer, intent(in) :: uc_ind
    integer, intent(in) :: n
    integer, intent(in), dimension(n0) :: neigh
    integer :: n0
    !f2py intent(hide), depend(neigh) :: n0 = shape(neigh,0)
    call set_neighbours(ind=ind, uc_ind=uc_ind, n=n, neigh=neigh)
end subroutine f90wrap_set_neighbours

subroutine f90wrap_torture(n, uc_nodes, n0)
    use tort_mod, only: torture
    implicit none
    
    integer, intent(in) :: n
    integer, intent(in), dimension(n0) :: uc_nodes
    integer :: n0
    !f2py intent(hide), depend(uc_nodes) :: n0 = shape(uc_nodes,0)
    call torture(n=n, uc_nodes=uc_nodes)
end subroutine f90wrap_torture

subroutine f90wrap_tort_mod__array__uc_tort(dummy_this, nd, dtype, dshape, dloc)
    use omp_lib
    use tort_mod, only: tort_mod_uc_tort => uc_tort
    implicit none
    integer, intent(in) :: dummy_this(2)
    integer, intent(out) :: nd
    integer, intent(out) :: dtype
    integer, dimension(10), intent(out) :: dshape
    integer*8, intent(out) :: dloc
    
    nd = 1
    dtype = 5
    if (allocated(tort_mod_uc_tort)) then
        dshape(1:1) = shape(tort_mod_uc_tort)
        dloc = loc(tort_mod_uc_tort)
    else
        dloc = 0
    end if
end subroutine f90wrap_tort_mod__array__uc_tort

! End of module tort_mod defined in file tort.f90

