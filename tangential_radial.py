import numpy as np
from numpy.linalg import inv


def im2Cartesian(x,y,(row,col)):
	matrix = np.array([[1,0,0],[0,-1,0],[-0.5*col, 0.5*row, 1]])
	transfered = np.array([[x,y,1]]).dot(matrix)

	return transfered[0,0], transfered[0,1]


def Cartesian2im(x,y,(row,col)):
	matrix = np.array([[1,0,0],[0,-1,0],[0.5*col, 0.5*row, 1]])
	transfered = np.array([[x,y,1]]).dot(matrix)
	
	return transfered[0,0], transfered[0,1]


def rotate((x,y), radi):
	matrix = (np.array([[np.cos(radi),-np.sin(radi),0],
		[np.sin(radi),np.cos(radi),0],[0,0,1]]))
	rotated = np.array([[x,y,1]]).dot(matrix)
	
	return rotated[0,0], rotated[0,1]


def circle_center((x1,y1), (x2,y2), (x3,y3)):
	A = np.array([[x2-x1, y2-y1], [x3-x2, y3-y2]])
	B = np.array([[0.5*(x2**2-x1**2+y2**2-y1**2)], [0.5*(x3**2-x2**2+y3**2-y2**2)]])
	center = inv(A).dot(B)
	
	return center[0,0], center[1,0]



def tan_rad(row, col, (i,j), (u1,v1), (u2,v2)):
	x,y = im2Cartesian(j,i,(row,col))

	back_x = x + u1
	back_y = y - v1
	for_x = x + u2
	for_y = y - v2

	A = np.array([[x-back_x, y-back_y], [for_x-x, for_y-y]])
	if A.shape[0] == A.shape[1] and np.linalg.matrix_rank(A) == A.shape[0]:
		Ox,Oy = circle_center((back_x,back_y), (x,y), (for_x,for_y))

		PO = np.array([Ox-x, Oy-y])
		POmag = np.sqrt(PO.dot(PO))
	
		if POmag < 0:
			print 'Problem: negative POmag', POmag
	
		sinPOX = (y-Oy)/POmag
		cosPOX = (x-Ox)/POmag

		POX = np.arcsin(sinPOX)
		if cosPOX < 0:
			POX = np.pi - POX
			
		Ox_rotated, Oy_rotated = rotate((Ox, Oy), POX)
		x_rotated, y_rotated = rotate((x, y), POX)

		ACCx, ACCy = rotate((x+u1+u2, y-v1-v2), POX)

		RADx, RADy = rotate((ACCx, y_rotated), -POX)
		TANx, TANy = rotate((x_rotated, ACCy), -POX)

		RADj, RADi = Cartesian2im(RADx, RADy, (row, col))
		TANj, TANi = Cartesian2im(TANx, TANy, (row, col))
		Oj, Oi = Cartesian2im(Ox, Oy, (row, col))
	
	else:
		RADi=0
		RADj=0
		TANi=0
		TANj=0
		Oi=i
		Oj=j

	return RADi, RADj, TANi, TANj, Oi, Oj

