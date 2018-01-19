
subroutine dist(coord1,coord2,n,dist_matrix)

use omp_lib

IMPLICIT NONE

integer, intent(in) :: n

real,dimension(n,3),intent(in) :: coord1,coord2
real,dimension(n,n),intent(out) :: dist_matrix
integer:: i,j,nthreads

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

