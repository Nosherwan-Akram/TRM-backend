import pandas as pd 
import numpy as np 
import xlsxwriter
import os
import editdistance
from scipy.spatial import distance
import math
import json
from google.protobuf.json_format import MessageToJson
import cv2


htrData = pd.read_excel('demo.xlsx',header=None).iloc[1:,1:]


def detect_text(path):
    """Detects text in the file."""
    from google.cloud import vision
    import io
    filename = path.split('/')[-1]
    client = vision.ImageAnnotatorClient()
    
    img = cv2.imread(path)
    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.types.Image(content=content)

    response = client.text_detection(image=image)

    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))
    return response

# c_s_e = [(7, 100), (94, 425), (399, 606), (602, 772), (768, 942), (938, 1095), (1091, 1264)]
c_s_e = open('cols_start_end.json')
c_s_e = json.load(c_s_e)
cols_start_end = []
for val in c_s_e:
		cols_start_end.append(tuple(val))

# rows_start_end = [(6, 67), (73, 108), (112, 144), (147, 178), (181, 212), (215, 245), (249, 278), (282, 312), (315, 346), (348, 379), (382, 413), (417, 447), (449, 480), (482, 513), (516, 547), (549, 581), (585, 615), (618, 649), (652, 683), (686, 718), (721, 759), (760, 791), (795, 826), (829, 865), (868, 901), (904, 936)]
r_s_e = open('rows_start_end.json')
r_s_e = json.load(r_s_e)
rows_start_end = []
for val in r_s_e:
		rows_start_end.append(tuple(val))


text_detections = detect_text('HTR/test.jpg').text_annotations[1:]


col_mappings = []
for i in range(len(cols_start_end)+1):
    col_mappings.append([])
row_mappings = []
for i in range(len(rows_start_end)+1):
    row_mappings.append([])

row_map={}
col_map={}
TEXTS = []

for i, detection in enumerate(text_detections):

    text_obj = {}
    text_obj['left'] = detection.bounding_poly.vertices[0].x
    text_obj['right'] = detection.bounding_poly.vertices[1].x
    text_obj['top'] = detection.bounding_poly.vertices[0].y
    text_obj['bottom'] = detection.bounding_poly.vertices[3].y
    text_obj['right_mid'] = (int((detection.bounding_poly.vertices[1].x+detection.bounding_poly.vertices[2].x)/2), int((detection.bounding_poly.vertices[1].y+detection.bounding_poly.vertices[2].y)/2))
    text_obj['description'] = detection.description
    text_obj['prev'] = (0,0)


    left_bound = text_obj['left']
    right_bound = text_obj['right']
    top_bound = text_obj['top']
    bottom_bound = text_obj['bottom']

    min_left_diff = 99999
    min_right_diff = 99999
    min_top_diff = 99999
    min_bottom_diff = 99999
    start_col = 0
    end_col = 0
    start_row = 0
    end_row = 0
    for j in range(0, len(cols_start_end)):
        if left_bound < cols_start_end[j][0] :
            continue
        left_diff = abs(left_bound - cols_start_end[j][0])
        
        if left_diff < min_left_diff:
            min_left_diff = left_diff
            start_col = j + 1

    for j in range(len(cols_start_end)-1, start_col-2, -1):
        #if right_bound > cols_start_end[j][1]:
        #    continue
        right_diff = abs(right_bound - cols_start_end[j][1])
        if (right_diff <= min_right_diff):
            min_right_diff = right_diff
            end_col = j + 1
    
    col_map[i] = (start_col,end_col)
            
    # And do the same for rows:
    for j in range(0, len(rows_start_end)):
        if top_bound < rows_start_end[j][0]:
            continue
        top_diff = abs(top_bound - rows_start_end[j][0])
        
        if top_diff < min_top_diff:
            min_top_diff = top_diff
            start_row = j + 1
        
    
    for j in range(len(rows_start_end)-1, start_row-2, -1):
#         if bottom_bound > rows_start_end[j][1]:
#             continue
        bottom_diff = abs(bottom_bound - rows_start_end[j][1])
        if (bottom_diff <= min_bottom_diff):
            min_bottom_diff = bottom_diff
            end_row = j + 1
    row_map[i] = (start_row,end_row)
    TEXTS.append(detection.description)


for i in col_map:
	if col_map[i][0]>col_map[i][1]:
		col_map[i][1] = col_map[i][0]

for i in row_map:
	if row_map[i][0]>row_map[i][1]:
		row_map[i] = (row_map[i][0],row_map[i][0])

col_m = col_map

row_m = row_map

columns = range(1,len(cols_start_end)+1)
index = range(1,len(rows_start_end)+1)


data = pd.DataFrame(index=index,columns=columns)


for i in row_m:
	if str(data.iloc[row_m[i][0]-1][col_m[i][0]]) == 'nan':
		data.iloc[row_m[i][0]-1][col_m[i][0]] = str(TEXTS[i])

	else:
		data.iloc[row_m[i][0]-1][col_m[i][0]] = str(data.iloc[row_m[i][0]-1][col_m[i][0]])+ " "+str(TEXTS[i])


ptr = data.iloc[2:,0:len(data.iloc[0])-2]
htr = htrData.iloc[2:,len(htrData.iloc[0])-2:]
ptrHead = data.iloc[0:2,:]


data = pd.concat([ptr,htr],axis=1)
data = pd.concat([ptrHead,data],axis=0)

data.fillna('*',inplace=True)

for row in range(len(data.iloc[:,0])):
	for col in range(1,len(data.iloc[0])+1):
		if data.iloc[row][col] == '*':
			data.iloc[row][col] = htrData.iloc[row][col]

print(data)

col_maps = open('col_m.json')
col_maps = json.load(col_maps)
col_m = {}
for key,val in col_maps.items():
    col_m[int(key)] = tuple(val)

row_maps = open('row_m.json')
row_maps = json.load(row_maps)
row_m = {}
for key,val in row_maps.items():
    row_m[int(key)] = tuple(val)

alphaNum = {1:'A', 2:'B', 3:'C', 4:'D', 5:'E', 6:'F', 7:'G', 8:'H'}


workbook = xlsxwriter.Workbook('output_demo.xlsx')
worksheet = workbook.add_worksheet()

excelData = (np.array(data))

for row in range(0,len(data.iloc[:,0])):
	for col in range(1,len(data.iloc[0])+1):
		worksheet.write(row, col-1, data.iloc[row][col])

for i in range(1,len(col_m)+1):
	if col_m[i][0]!= col_m[i][1]:
		merge_text = ''
		for j in range(col_m[i][0],col_m[i][1]+1):
			merge_text = merge_text + ' ' + data.iloc[row_m[i][0]-1][j]
		merge_text = merge_text.replace('*','').replace('-','').strip()
		#print(alphaNum[col_m[i][0]]+str(row_m[i][0])+':'+alphaNum[col_m[i][1]]+str(row_m[i][1]))
		worksheet.merge_range(alphaNum[col_m[i][0]]+str(row_m[i][0])+':'+alphaNum[col_m[i][1]]+str(row_m[i][1]),merge_text)

for i in range(1,len(row_m)+1):
	if row_m[i][0]!= row_m[i][1]:
		merge_text = ''
		for j in range(row_m[i][0],row_m[i][1]+1):
			merge_text = merge_text + ' ' + data.iloc[j][col_m[i][0]-1]
		merge_text = merge_text.replace('*','').replace('-','').strip()
		print(alphaNum[col_m[i][0]]+str(row_m[i][0])+':'+alphaNum[col_m[i][1]]+str(row_m[i][1]))
		worksheet.merge_range(alphaNum[col_m[i][0]]+str(row_m[i][0])+':'+alphaNum[col_m[i][1]]+str(row_m[i][1]),merge_text)

workbook.close()
