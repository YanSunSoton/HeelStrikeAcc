from __future__ import division
import numpy as np
# import os
from tangential_radial import tan_rad
from PIL import ImageDraw,Image
# import pdb

radius = 1

def heel_strike(mask,frame_row,frame_col,bound_U,bound_D,bound_L,bound_R,
	u1,v1,u2,v2,threshold,flow,heel,walkingDir):
	maskShape = mask.shape
	if len(maskShape) == 2:
		mask = mask[bound_U:bound_D, bound_L:bound_R]
	elif len(maskShape) == 3:
		mask = mask[bound_U:bound_D, bound_L:bound_R,:]

	# print maskShape
	maskShape = mask.shape
	row = maskShape[0]
	col = maskShape[1]

	radCenter_map = np.zeros((row,col), dtype = np.uint8)
	flow_count = 0
	center_count = 0

	if walkingDir == 'L':
		# print mask.shape
		row_top, row_bottom, col_left, col_right = frontFeet_thresL(mask)
		# print row_top, row_bottom, col_left, col_right
		
		if col_left < 0:
			col_left = 0
		if col_right > col:
			col_right = col

		row_start = bound_U
		col_start = bound_L
		
		draw = ImageDraw.Draw(flow)
		draw.line((col_left+col_start, row_top+row_start, col_right+col_start,
			row_top+row_start), fill = (0,255,0), width=3)
		# print col_left, col_start, row_bottom, row_start, col_right, row_bottom
		draw.line((col_left+col_start, row_bottom+row_start, col_right+col_start, 
			row_bottom+row_start), fill = (0,255,0), width=3)
		draw.line((col_left+col_start, row_top+row_start, col_left+col_start, 
			row_bottom+row_start), fill = (0,255,0), width=3)
		draw.line((col_right+col_start, row_top+row_start, col_right+col_start, 
			row_bottom+row_start), fill = (0,255,0), width=3)
		del draw


		for i in range (row_top, row_bottom):
			for j in range (col_left, col_right):

				acc_u = u1[i,j] + u2[i,j]
				acc_v = v1[i,j] + v2[i,j]

				acc_mag = np.sqrt(acc_u**2 + acc_v**2)

				if acc_mag>threshold:
					RADi, RADj, TANi, TANj, Oi, Oj = tan_rad(row, col,
						(i,j), (u1[i,j],v1[i,j]), (u2[i,j],v2[i,j]))
					RAD_u = RADj - j
					RAD_v = RADi - i
				
					rad_mag = np.sqrt(RAD_u**2 + RAD_v**2)

					if (rad_mag>threshold and i<RADi and j<RADj):
						flow_count = flow_count + 1
					
						RAD_u = int(round(RAD_u))
						RAD_v = int(round(RAD_v))

						flow = draw_flow(frame_row, frame_col, i+row_start,
							j+col_start, RAD_u, RAD_v, flow)
					
						Oi = int(round(Oi))	
						Oj = int(round(Oj))
						
						if (0<=Oi<row and 0<=Oj<col):
							# print Oi,Oj
							center_count = center_count + 1
							radCenter_map[Oi, Oj] = radCenter_map[Oi, Oj] + 1

	else:
		row_top, row_bottom, col_left, col_right = frontFeet_thresR(mask)
		if col_left < 0:
			col_left = 0
		
		
		for i in range (row_top, row_bottom):
			for j in range (col_left, col_right):

				acc_u = u1[i,j] + u2[i,j]
				acc_v = v1[i,j] + v2[i,j]

				acc_mag = np.sqrt(acc_u**2 + acc_v**2)

				if acc_mag>threshold:
					RADi, RADj, TANi, TANj, Oi, Oj = tan_rad(row,
						col, (i,j), (u1[i,j],v1[i,j]), (u2[i,j],v2[i,j]))
					RAD_u = RADj - j
					RAD_v = RADi - i
				
					rad_mag = np.sqrt(RAD_u**2 + RAD_v**2)

					if (rad_mag>threshold and i<RADi and j>RADj):
						flow_count = flow_count + 1
					
						RAD_u = int(round(RAD_u))
						RAD_v = int(round(RAD_v))
						flow = draw_flow(480, 640,
							i+row_start, j+col_start, RAD_u, RAD_v, flow)
					
						Oi = int(round(Oi))	
						Oj = int(round(Oj))
						
						if (0<= Oi<row and 0<=Oj<col):
							center_count = center_count + 1
							radCenter_map[Oi, Oj] = radCenter_map[Oi, Oj] + 1

	heelR = 0
	heelC = 0

	if center_count > 0:
		index = np.argwhere(radCenter_map != 0)

		centersR = index[:, 0]
		centersC = index[:, 1]

		for m in range (len(centersR)):
			factor = radCenter_map[centersR[m], centersC[m]]/center_count
			
			heelR = heelR + factor*centersR[m]
			heelC = heelC + factor*centersC[m]
		
		heelR = int(round(heelR))+bound_U
		heelC = int(round(heelC))+bound_L
		# print heelR, heelC

		# draw = ImageDraw.Draw(heel)
		# draw.ellipse((heelC-radius, heelR-radius, heelC+radius, heelR+radius), fill='red')
		# del draw

	draw = ImageDraw.Draw(flow)
	draw.line((col_left + col_start, row_top + row_start, col_right + col_start, row_top + row_start), fill = (0,255,0), width=1)
	draw.line((col_left + col_start, row_bottom + row_start, col_right + col_start, row_bottom + row_start), fill = (0,255,0), width=1)
	draw.line((col_left + col_start, row_top + row_start, col_left + col_start, row_bottom + row_start), fill = (0,255,0), width=1)
	draw.line((col_right + col_start, row_top + row_start, col_right + col_start, row_bottom + row_start), fill = (0,255,0), width=1)
	del draw

	return flow_count, flow, heel, heelR, heelC


def draw_flow(u, v, flow_array, step=1, scale=1, thres=1):
	if len(flow_array.shape) == 2:
		flow_array = np.dstack((flow_array,flow_array,flow_array))
	
	flow_img = Image.fromarray(flow_array)
	draw = ImageDraw.Draw(flow_img)

	for x in xrange (1, flow_array.shape[1], step):
		for y in xrange (1, flow_array.shape[0], step):
 			dx = int(round(u[int(y), int(x)]))
			dy = int(round(v[int(y), int(x)]))

			if np.sqrt(dx**2 + dy**2)>thres:
 				end_x = x + scale*dx
 				end_y = y + scale*dy

				if 0<=end_y<flow_array.shape[0] and 0<=end_x<flow_array.shape[1]:
 				# print "draw_flow"
				# draw.ellipse((end_x-radius, end_y-radius, end_x+radius, end_y+radius), fill='blue')
					draw.line((x, y, end_x, end_y), fill=(255,255,255), width=2)

	del draw
	return flow_img


def frontFeet_thresL(mask):
	# print mask
	maskShape = mask.shape
	# print 'mask shape in frontFeet_thres', maskShape

	if len(maskShape) == 2:
		coords = np.argwhere(mask == 255)
	else:
		coords = np.argwhere(mask == [255,255,255])

	coord_row = coords[:,0]
	coord_col = coords[:,1]
	# print coord_row
	row_min = np.min(coord_row)
	row_max = np.max(coord_row)

	height = row_max - row_min

	row_top = row_max - 0.133*height
	row_top = int(round(row_top))
	
	col_min = np.min(coord_col)
	col_max = np.max(coord_col)

	col_left = col_min

	col_right = col_min + 0.177*height
	col_right = int(round(col_right))	

	return row_top, row_max, col_left, col_right


def frontFeet_thresR(mask):
	maskShape = mask.shape

	if len(maskShape) == 2:
		coords = np.argwhere(mask == 255)
	else:
		coords = np.argwhere(mask == (255,255,255))

	coord_row = coords[:,0]
	coord_col = coords[:,1]

	row_min = np.min(coord_row)
	row_max = np.max(coord_row)

	height = row_max - row_min

	row_top = row_max - 0.133*height
	row_top = int(round(row_top))
	
	col_min = np.min(coord_col)
	col_max = np.max(coord_col)

	col_left = col_max - 0.177*height
	col_left = int(round(col_left))	

	col_right = col_max

	return row_top, row_max, col_left, col_right

