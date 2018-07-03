
subroutine dist(coord1,coord2,n,dist_matrix)

! Obtains the distance matrix between sites in pymatgen structure, used to 
! obtain a neighbour list for sites (and is faster than using the
! python version in pymatgen)
! Args:
!     coord1 ([[real,real,real],...]): array of site coords
!     coord2 ([[real,real,real],...]): array of site coords
!     n (int): number of elements in coord arrays
! Return:
!     dist_matrix([n X n array of reals]): dist matrix for sites 

use omp_lib

IMPLICIT NONE

integer, intent(in) :: n

real,dimension(n,3),intent(in) :: coord1,coord2
real,dimension(n,n),intent(out) :: dist_matrix
integer:: i,j

!$OMP PARALLEL DO private(i,j) shared(coord1,coord2,dist_matrix)
do i=1,n
  do j=1,n
     dist_matrix(i,j) = ((coord1(i,1)-coord2(j,1))* (coord1(i,1)-coord2(j,1))+&
                        (coord1(i,2)-coord2(j,2))* (coord1(i,2)-coord2(j,2))+&
                        (coord1(i,3)-coord2(j,3))* (coord1(i,3)-coord2(j,3)))**0.5
  END DO
END DO
!$OMP END PARALLEL DO

end subroutine dist

subroutine shift_index(index_n,shift,new_index)

! Shifts the index of a site in the unit cell to the corresponding
! index in the 3x3x3 halo supercell.
! Used when getting neighbour list for supercell from unit cell neighbour list
! 
! Args:
!    index_n (int): original index
!    shift ([int,int,int]): shift to image for which to obatin index eg. [-1,-1,-1]
!    
! Returns:
!    new_index (int): index for image site in supercell

IMPLICIT NONE

integer, intent(in) :: index_n
integer, dimension(3), intent(in):: shift
integer, intent(out) :: new_index

integer::new_x,new_y,new_z

new_x = MODULO((MODULO(int(index_n/9),3)+shift(1)),3)
new_y = MODULO((MODULO(int(index_n/3),3)+shift(2)),3)
new_z = MODULO((MODULO(index_n,3)+shift(3)),3)

new_index = int(27*int(index_n/(27))+(MODULO(new_x,3)*9+MODULO(new_y,3)*3+MODULO(new_z,3)))
end subroutine shift_index

