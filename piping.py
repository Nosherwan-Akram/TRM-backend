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


htrData = pd.read_excel('out.xlsx',header=None).iloc[1:,1:]

'''
htrdata = pd.read_excel('HTR/output.xlsx',header=None)
ptrdata = pd.read_excel('PTR/output.xlsx',header=None)

ptr = ptrdata.iloc[3:,0:len(ptrdata.iloc[0])-2]
htr = htrdata.iloc[3:,len(htrdata.iloc[0])-2:]
ptrHead = ptrdata.iloc[0:3,:]


data = pd.concat([ptr,htr],axis=1)
data = pd.concat([ptrHead,data],axis=0)


workbook = xlsxwriter.Workbook('output.xlsx')
worksheet = workbook.add_worksheet()

excelData = (np.array(data))

row = 0
col = 0

if (len(data.iloc[0]) == 7):
	for a, b, c, d, e, f, g in (excelData):
		worksheet.write(row, col,     a)
		worksheet.write(row, col + 1, b)
		worksheet.write(row, col + 2, c)
		worksheet.write(row, col + 3, d)
		worksheet.write(row, col + 4, e)
		worksheet.write(row, col + 5, f)
		worksheet.write(row, col + 6, g)

		row += 1

	worksheet.merge_range('A2:G2', 'PhysicalandChemicalParameters')
	worksheet.merge_range('A21:G21', 'BacteriologicalParameters')
	worksheet.merge_range('A24:G24', 'ToxicSubstances')


	workbook.close()

elif (len(data.iloc[0]) == 6):
	for a, b, c, d, e, f in (excelData):
		worksheet.write(row, col,     a)
		worksheet.write(row, col + 1, b)
		worksheet.write(row, col + 2, c)
		worksheet.write(row, col + 3, d)
		worksheet.write(row, col + 4, e)
		worksheet.write(row, col + 5, f)
		row += 1

	worksheet.merge_range('A2:F2', 'PhysicalandChemicalParameters')
	worksheet.merge_range('A21:F21', 'BacteriologicalParameters')
	worksheet.merge_range('A24:F24', 'ToxicSubstances')


	workbook.close()



data = pd.read_excel('output.xlsx',header=None)
testData = pd.read_excel('testOutput.xlsx',header=None)
testData.fillna('*',inplace=True)

numCharErr = 0
numCharTotal = 0
numWordOK = 0
numWordTotal = 0

print(data)
print(testData)
for i in range(data.shape[0]):
	for j in range(data.shape[1]):
		numWordOK += 1 if str(data.iloc[i][j]) == str(testData.iloc[i][j]) else 0
		numWordTotal += 1
		dist = editdistance.eval(str(data.iloc[i][j]), str(testData.iloc[i][j]))
		numCharErr += dist
		numCharTotal += len(str(testData.iloc[i][j]))
		#print('[OK]' if dist==0 else '[ERR:%d]' % dist,'"' + batch.gtTexts[i] + '"', '->', '"' + recognized[i] + '"')
	
charErrorRate = numCharErr / numCharTotal
wordAccuracy = numWordOK / numWordTotal
print('Character error rate: %f%%. Word accuracy: %f%%.' % (charErrorRate*100.0, wordAccuracy*100.0))

'''

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

cols_start_end = [(7, 100), (94, 425), (399, 606), (602, 772), (768, 942), (938, 1095), (1091, 1264)]
rows_start_end = [(6, 67), (73, 108), (112, 144), (147, 178), (181, 212), (215, 245), (249, 278), (282, 312), (315, 346), (348, 379), (382, 413), (417, 447), (449, 480), (482, 513), (516, 547), (549, 581), (585, 615), (618, 649), (652, 683), (686, 718), (721, 759), (760, 791), (795, 826), (829, 865), (868, 901), (904, 936)]


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

'''prev = text_detections[0]


text_detections_copy = text_detections.copy()
for i, detection in enumerate(text_detections[1:]):
    text_obj = {}
    #text_obj['left'] = detection.bounding_poly.vertices[0].x
    #text_obj['right'] = detection.bounding_poly.vertices[1].x
    #text_obj['top'] = detection.bounding_poly.vertices[0].y
    #text_obj['bottom'] = detection.bounding_poly.vertices[3].y
    text_obj['right_mid'] = (int((detection.bounding_poly.vertices[0].x+detection.bounding_poly.vertices[3].x)/2), int((detection.bounding_poly.vertices[0].y+detection.bounding_poly.vertices[3].y)/2))
    text_obj['prev_right_mid'] = (int((prev.bounding_poly.vertices[1].x+prev.bounding_poly.vertices[2].x)/2), int((prev.bounding_poly.vertices[1].y+prev.bounding_poly.vertices[2].y)/2))
    text_obj['description'] = detection.description
    text_obj['prev_description'] = prev.description

    if distance.euclidean(text_obj['prev_right_mid'],text_obj['right_mid'])<15:
    #	print(prev.description,detection.description,text_obj['prev_right_mid'],text_obj['right_mid'])
    	text_detections[i-1].description = prev.description + " " + detection.description
    	#text_detections[i-1].bounding_poly.vertices = text_detections[i].bounding_poly.vertices
    	#text_detections[i-1].bounding_poly.vertices[2] = text_detections[i].bounding_poly.vertices[2]
    	text_detections[i].description = ''
	
    prev = detection

    print(text_detections[i].description)'''

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
            continue;
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
    '''
    for j in range(0, len(cols_start_end)):
#         if left_bound < cols_start_end[j][0]:
#             continue;
        left_diff = abs(left_bound - cols_start_end[j][0])
        
        if left_diff < min_left_diff:
            min_left_diff = left_diff
            start_col = j + 1

    for j in range(len(cols_start_end)-1, start_col-2, -1):
#         if right_bound > cols_start_end[j][1]:
#             continue
        right_diff = abs(right_bound - cols_start_end[j][1])
        if (right_diff <= min_right_diff):
            min_right_diff = right_diff
            end_col = j + 1
            
    col_map[i] = (start_col, end_col)
            
    # And do the same for rows:
    for j in range(0, len(rows_start_end)):
#         if top_bound < rows_start_end[j][0]:
#             continue;
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
    row_map[i] = (start_row, end_row)
    '''
    TEXTS.append(detection.description)




for i in row_map:
	#if row_map[i][0]<row_map[i][1]:
	#	print(i,row_map[i],TEXTS[i])
	if row_map[i][0]!=row_map[i][1]:
		print(row_map[i][0],row_map[i][1])
for i in col_map:
	#if row_map[i][0]<row_map[i][1]:
	#	print(i,row_map[i],TEXTS[i])
	if col_map[i][0]!=col_map[i][1]:
		print(col_map[i][0],col_map[i][1])

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


col_m = {1: (1, 1), 2: (2, 2), 3: (3, 3), 4: (4, 4), 5: (5, 5), 6: (6, 6), 7: (7, 7), 8: (1, 7), 9: (1, 1), 10: (2, 2), 11: (3, 3), 12: (4, 4), 13: (5, 5), 14: (6, 6), 15: (7, 7), 16: (1, 1), 17: (2, 2), 18: (4, 4), 19: (5, 5), 20: (6, 6), 21: (7, 7), 22: (3, 3), 23: (1, 1), 24: (2, 2), 25: (4, 4), 26: (5, 5), 27: (6, 6), 28: (7, 7), 29: (3, 3), 30: (1, 1), 31: (2, 2), 32: (3, 3), 33: (4, 4), 34: (5, 5), 35: (6, 6), 36: (7, 7), 37: (1, 1), 38: (2, 2), 39: (3, 3), 40: (4, 4), 41: (5, 5), 42: (6, 6), 43: (7, 7), 44: (1, 1), 45: (2, 2), 46: (3, 3), 47: (4, 4), 48: (5, 5), 49: (6, 6), 50: (7, 7), 51: (3, 3), 52: (4, 4), 53: (5, 5), 54: (6, 6), 55: (7, 7), 56: (1, 1), 57: (2, 2), 58: (1, 1), 59: (2, 2), 60: (3, 3), 61: (4, 4), 62: (5, 5), 63: (6, 6), 64: (7, 7), 65: (1, 1), 66: (2, 2), 67: (3, 3), 68: (4, 4), 69: (5, 5), 70: (6, 6), 71: (7, 7), 72: (1, 1), 73: (2, 2), 74: (3, 3), 75: (4, 4), 76: (5, 5), 77: (6, 6), 78: (7, 7), 79: (1, 1), 80: (2, 2), 81: (3, 3), 82: (4, 4), 83: (5, 5), 84: (6, 6), 85: (7, 7), 86: (1, 1), 87: (2, 2), 88: (3, 3), 89: (4, 4), 90: (5, 5), 91: (6, 6), 92: (7, 7), 93: (1, 1), 94: (2, 2), 95: (3, 3), 96: (4, 4), 97: (5, 5), 98: (6, 6), 99: (7, 7), 100: (1, 1), 101: (2, 2), 102: (3, 3), 103: (4, 4), 104: (5, 5), 105: (6, 6), 106: (7, 7), 107: (1, 1), 108: (2, 2), 109: (3, 3), 110: (4, 4), 111: (5, 5), 112: (6, 6), 113: (7, 7), 114: (1, 1), 115: (2, 2), 116: (3, 3), 117: (4, 4), 118: (5, 5), 119: (6, 6), 120: (7, 7), 121: (1, 1), 122: (2, 2), 123: (3, 3), 124: (4, 4), 125: (5, 5), 126: (6, 6), 127: (7, 7), 128: (1, 1), 129: (2, 2), 130: (3, 3), 131: (4, 4), 132: (5, 5), 133: (6, 6), 134: (7, 7), 135: (1, 7), 136: (1, 1), 137: (2, 2), 138: (3, 3), 139: (4, 4), 140: (5, 5), 141: (6, 6), 142: (7, 7), 143: (1, 1), 144: (2, 2), 145: (3, 3), 146: (4, 4), 147: (5, 5), 148: (6, 6), 149: (7, 7), 150: (1, 7), 151: (1, 1), 152: (2, 2), 153: (3, 3), 154: (4, 4), 155: (5, 5), 156: (6, 6), 157: (7, 7), 158: (1, 1), 159: (2, 2), 160: (3, 3), 161: (4, 4), 162: (5, 5), 163: (6, 6), 164: (7, 7)}

row_m = {1: (1, 1), 2: (1, 1), 3: (1, 1), 4: (1, 1), 5: (1, 1), 6: (1, 1), 7: (1, 1), 8: (2, 2), 9: (3, 3), 10: (3, 3), 11: (3, 3), 12: (3, 3), 13: (3, 3), 14: (3, 3), 15: (3, 3), 16: (4, 4), 17: (4, 4), 18: (4, 4), 19: (4, 4), 20: (4, 4), 21: (4, 4), 22: (4, 4), 23: (5, 5), 24: (5, 5), 25: (5, 5), 26: (5, 5), 27: (5, 5), 28: (5, 5), 29: (5, 5), 30: (6, 6), 31: (6, 6), 32: (6, 6), 33: (6, 6), 34: (6, 6), 35: (6, 6), 36: (6, 6), 37: (7, 7), 38: (7, 7), 39: (7, 7), 40: (7, 7), 41: (7, 7), 42: (7, 7), 43: (7, 7), 44: (8, 8), 45: (8, 8), 46: (8, 8), 47: (8, 8), 48: (8, 8), 49: (8, 8), 50: (8, 8), 51: (9, 9), 52: (9, 9), 53: (9, 9), 54: (9, 9), 55: (9, 9), 56: (9, 9), 57: (9, 9), 58: (10, 10), 59: (10, 10), 60: (10, 10), 61: (10, 10), 62: (10, 10), 63: (10, 10), 64: (10, 10), 65: (11, 11), 66: (11, 11), 67: (11, 11), 68: (11, 11), 69: (11, 11), 70: (11, 11), 71: (11, 11), 72: (12, 12), 73: (12, 12), 74: (12, 12), 75: (12, 12), 76: (12, 12), 77: (12, 12), 78: (12, 12), 79: (13, 13), 80: (13, 13), 81: (13, 13), 82: (13, 13), 83: (13, 13), 84: (13, 13), 85: (13, 13), 86: (14, 14), 87: (14, 14), 88: (14, 14), 89: (14, 14), 90: (14, 14), 91: (14, 14), 92: (14, 14), 93: (15, 15), 94: (15, 15), 95: (15, 15), 96: (15, 15), 97: (15, 15), 98: (15, 15), 99: (15, 15), 100: (16, 16), 101: (16, 16), 102: (16, 16), 103: (16, 16), 104: (16, 16), 105: (16, 16), 106: (16, 16), 107: (17, 17), 108: (17, 17), 109: (17, 17), 110: (17, 17), 111: (17, 17), 112: (17, 17), 113: (17, 17), 114: (18, 18), 115: (18, 18), 116: (18, 18), 117: (18, 18), 118: (18, 18), 119: (18, 18), 120: (18, 18), 121: (19, 19), 122: (19, 19), 123: (19, 19), 124: (19, 19), 125: (19, 19), 126: (19, 19), 127: (19, 19), 128: (20, 20), 129: (20, 20), 130: (20, 20), 131: (20, 20), 132: (20, 20), 133: (20, 20), 134: (20, 20), 135: (21, 21), 136: (22, 22), 137: (22, 22), 138: (22, 22), 139: (22, 22), 140: (22, 22), 141: (22, 22), 142: (22, 22), 143: (23, 23), 144: (23, 23), 145: (23, 23), 146: (23, 23), 147: (23, 23), 148: (23, 23), 149: (23, 23), 150: (24, 24), 151: (25, 25), 152: (25, 25), 153: (25, 25), 154: (25, 25), 155: (25, 25), 156: (25, 25), 157: (25, 25), 158: (26, 26), 159: (26, 26), 160: (26, 26), 161: (26, 26), 162: (26, 26), 163: (26, 26), 164: (26, 26)}

alphaNum = {1:'A', 2:'B', 3:'C', 4:'D', 5:'E', 6:'F', 7:'G', 8:'H'}


workbook = xlsxwriter.Workbook('output.xlsx')
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
