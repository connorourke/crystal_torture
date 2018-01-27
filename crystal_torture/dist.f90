
subroutine dist(coord1,coord2,n,dist_matrix)

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

IMPLICIT NONE

integer, intent(in) :: index_n
integer, dimension(3), intent(in):: shift
integer, intent(out) :: new_index

integer::new_x,new_y,new_z

new_x = MOD(int(index_n/9)+shift(1),3)
new_y = MOD(int(index_n/3) + shift(2),3)
new_z = MOD(index_n +shift(3),3)

new_index = int(27*int(index_n/(27))+(MOD(new_x,3)*9+MOD(new_y,3)*3+MOD(new_z,3)))
end subroutine shift_index

