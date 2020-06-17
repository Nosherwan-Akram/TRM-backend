from __future__ import division
from __future__ import print_function

import xlsxwriter
import pandas as pd 
import numpy as np 
from PIL import Image
from PIL import ImageFilter

import sys
import argparse
import cv2
import editdistance
import os
from DataLoader import DataLoader, Batch
from Model import Model, DecoderType
from SamplePreprocessor import preprocess


class FilePaths:
	"filenames and paths to data"
	fnCharList = 'HTR/model/charList.txt'
	fnAccuracy = 'HTR/model/accuracy.txt'
	fnTrain = 'HTR/data/'
	fnInfer = 'HTR/data/coordinates/test.png'
	fnInferDir = 'HTR/data/coordinates'
	fnCorpus = 'HTR/data/corpus.txt'


def train(model, loader):
	"train NN"
	epoch = 0 # number of training epochs since start
	bestCharErrorRate = float('inf') # best valdiation character error rate
	noImprovementSince = 0 # number of epochs no improvement of character error rate occured
	earlyStopping = 5 # stop training after this number of epochs without improvement
	while True:
		epoch += 1
		print('Epoch:', epoch)

		# train
		print('Train NN')
		loader.trainSet()
		while loader.hasNext():
			iterInfo = loader.getIteratorInfo()
			batch = loader.getNext()
			loss = model.trainBatch(batch)
			print('Batch:', iterInfo[0],'/', iterInfo[1], 'Loss:', loss)

		# validate
		charErrorRate = validate(model, loader)
		
		# if best validation accuracy so far, save model parameters
		if charErrorRate < bestCharErrorRate:
			print('Character error rate improved, save model')
			bestCharErrorRate = charErrorRate
			noImprovementSince = 0
			model.save()
			open(FilePaths.fnAccuracy, 'w').write('Validation character error rate of saved model: %f%%' % (charErrorRate*100.0))
		else:
			print('Character error rate not improved')
			noImprovementSince += 1

		# stop training if no more improvement in the last x epochs
		if noImprovementSince >= earlyStopping:
			print('No more improvement since %d epochs. Training stopped.' % earlyStopping)
			break


def validate(model, loader):
	"validate NN"
	print('Validate NN')
	loader.validationSet()
	numCharErr = 0
	numCharTotal = 0
	numWordOK = 0
	numWordTotal = 0
	while loader.hasNext():
		iterInfo = loader.getIteratorInfo()
		print('Batch:', iterInfo[0],'/', iterInfo[1])
		batch = loader.getNext()
		(recognized) = model.inferBatch(batch)
		
		print('Ground truth -> Recognized')	
		for i in range(len(recognized)):
			numWordOK += 1 if batch.gtTexts[i] == recognized[i] else 0
			numWordTotal += 1
			dist = editdistance.eval(recognized[i], batch.gtTexts[i])
			numCharErr += dist
			numCharTotal += len(batch.gtTexts[i])
			print('[OK]' if dist==0 else '[ERR:%d]' % dist,'"' + batch.gtTexts[i] + '"', '->', '"' + recognized[i] + '"')
	
	# print validation result
	charErrorRate = numCharErr / numCharTotal
	wordAccuracy = numWordOK / numWordTotal
	print('Character error rate: %f%%. Word accuracy: %f%%.' % (charErrorRate*100.0, wordAccuracy*100.0))
	return charErrorRate


def infer(model, fnImg):
	"recognize text in image provided by file path"
	imgs = []

	
	col = Image.open('HTR/test.jpg')
	gray = col.convert('L')
	bw = gray.point(lambda x: 0 if x<128 else 255, '1')
	dilation_img = bw.filter(ImageFilter.MinFilter(3))
	dilation_img.save("HTR/test2.jpg")
	img = cv2.imread('HTR/test.jpg',cv2.IMREAD_GRAYSCALE)


	col_m = {1: (1, 1), 2: (2, 2), 3: (3, 3), 4: (4, 4), 5: (5, 5), 6: (6, 6), 7: (7, 7), 8: (1, 7), 9: (1, 1), 10: (2, 2), 11: (3, 3), 12: (4, 4), 13: (5, 5), 14: (6, 6), 15: (7, 7), 16: (1, 1), 17: (2, 2), 18: (4, 4), 19: (5, 5), 20: (6, 6), 21: (7, 7), 22: (3, 3), 23: (1, 1), 24: (2, 2), 25: (4, 4), 26: (5, 5), 27: (6, 6), 28: (7, 7), 29: (3, 3), 30: (1, 1), 31: (2, 2), 32: (3, 3), 33: (4, 4), 34: (5, 5), 35: (6, 6), 36: (7, 7), 37: (1, 1), 38: (2, 2), 39: (3, 3), 40: (4, 4), 41: (5, 5), 42: (6, 6), 43: (7, 7), 44: (1, 1), 45: (2, 2), 46: (3, 3), 47: (4, 4), 48: (5, 5), 49: (6, 6), 50: (7, 7), 51: (3, 3), 52: (4, 4), 53: (5, 5), 54: (6, 6), 55: (7, 7), 56: (1, 1), 57: (2, 2), 58: (1, 1), 59: (2, 2), 60: (3, 3), 61: (4, 4), 62: (5, 5), 63: (6, 6), 64: (7, 7), 65: (1, 1), 66: (2, 2), 67: (3, 3), 68: (4, 4), 69: (5, 5), 70: (6, 6), 71: (7, 7), 72: (1, 1), 73: (2, 2), 74: (3, 3), 75: (4, 4), 76: (5, 5), 77: (6, 6), 78: (7, 7), 79: (1, 1), 80: (2, 2), 81: (3, 3), 82: (4, 4), 83: (5, 5), 84: (6, 6), 85: (7, 7), 86: (1, 1), 87: (2, 2), 88: (3, 3), 89: (4, 4), 90: (5, 5), 91: (6, 6), 92: (7, 7), 93: (1, 1), 94: (2, 2), 95: (3, 3), 96: (4, 4), 97: (5, 5), 98: (6, 6), 99: (7, 7), 100: (1, 1), 101: (2, 2), 102: (3, 3), 103: (4, 4), 104: (5, 5), 105: (6, 6), 106: (7, 7), 107: (1, 1), 108: (2, 2), 109: (3, 3), 110: (4, 4), 111: (5, 5), 112: (6, 6), 113: (7, 7), 114: (1, 1), 115: (2, 2), 116: (3, 3), 117: (4, 4), 118: (5, 5), 119: (6, 6), 120: (7, 7), 121: (1, 1), 122: (2, 2), 123: (3, 3), 124: (4, 4), 125: (5, 5), 126: (6, 6), 127: (7, 7), 128: (1, 1), 129: (2, 2), 130: (3, 3), 131: (4, 4), 132: (5, 5), 133: (6, 6), 134: (7, 7), 135: (1, 7), 136: (1, 1), 137: (2, 2), 138: (3, 3), 139: (4, 4), 140: (5, 5), 141: (6, 6), 142: (7, 7), 143: (1, 1), 144: (2, 2), 145: (3, 3), 146: (4, 4), 147: (5, 5), 148: (6, 6), 149: (7, 7), 150: (1, 7), 151: (1, 1), 152: (2, 2), 153: (3, 3), 154: (4, 4), 155: (5, 5), 156: (6, 6), 157: (7, 7), 158: (1, 1), 159: (2, 2), 160: (3, 3), 161: (4, 4), 162: (5, 5), 163: (6, 6), 164: (7, 7)}

	row_m = {1: (1, 1), 2: (1, 1), 3: (1, 1), 4: (1, 1), 5: (1, 1), 6: (1, 1), 7: (1, 1), 8: (2, 2), 9: (3, 3), 10: (3, 3), 11: (3, 3), 12: (3, 3), 13: (3, 3), 14: (3, 3), 15: (3, 3), 16: (4, 4), 17: (4, 4), 18: (4, 4), 19: (4, 4), 20: (4, 4), 21: (4, 4), 22: (4, 4), 23: (5, 5), 24: (5, 5), 25: (5, 5), 26: (5, 5), 27: (5, 5), 28: (5, 5), 29: (5, 5), 30: (6, 6), 31: (6, 6), 32: (6, 6), 33: (6, 6), 34: (6, 6), 35: (6, 6), 36: (6, 6), 37: (7, 7), 38: (7, 7), 39: (7, 7), 40: (7, 7), 41: (7, 7), 42: (7, 7), 43: (7, 7), 44: (8, 8), 45: (8, 8), 46: (8, 8), 47: (8, 8), 48: (8, 8), 49: (8, 8), 50: (8, 8), 51: (9, 9), 52: (9, 9), 53: (9, 9), 54: (9, 9), 55: (9, 9), 56: (9, 9), 57: (9, 9), 58: (10, 10), 59: (10, 10), 60: (10, 10), 61: (10, 10), 62: (10, 10), 63: (10, 10), 64: (10, 10), 65: (11, 11), 66: (11, 11), 67: (11, 11), 68: (11, 11), 69: (11, 11), 70: (11, 11), 71: (11, 11), 72: (12, 12), 73: (12, 12), 74: (12, 12), 75: (12, 12), 76: (12, 12), 77: (12, 12), 78: (12, 12), 79: (13, 13), 80: (13, 13), 81: (13, 13), 82: (13, 13), 83: (13, 13), 84: (13, 13), 85: (13, 13), 86: (14, 14), 87: (14, 14), 88: (14, 14), 89: (14, 14), 90: (14, 14), 91: (14, 14), 92: (14, 14), 93: (15, 15), 94: (15, 15), 95: (15, 15), 96: (15, 15), 97: (15, 15), 98: (15, 15), 99: (15, 15), 100: (16, 16), 101: (16, 16), 102: (16, 16), 103: (16, 16), 104: (16, 16), 105: (16, 16), 106: (16, 16), 107: (17, 17), 108: (17, 17), 109: (17, 17), 110: (17, 17), 111: (17, 17), 112: (17, 17), 113: (17, 17), 114: (18, 18), 115: (18, 18), 116: (18, 18), 117: (18, 18), 118: (18, 18), 119: (18, 18), 120: (18, 18), 121: (19, 19), 122: (19, 19), 123: (19, 19), 124: (19, 19), 125: (19, 19), 126: (19, 19), 127: (19, 19), 128: (20, 20), 129: (20, 20), 130: (20, 20), 131: (20, 20), 132: (20, 20), 133: (20, 20), 134: (20, 20), 135: (21, 21), 136: (22, 22), 137: (22, 22), 138: (22, 22), 139: (22, 22), 140: (22, 22), 141: (22, 22), 142: (22, 22), 143: (23, 23), 144: (23, 23), 145: (23, 23), 146: (23, 23), 147: (23, 23), 148: (23, 23), 149: (23, 23), 150: (24, 24), 151: (25, 25), 152: (25, 25), 153: (25, 25), 154: (25, 25), 155: (25, 25), 156: (25, 25), 157: (25, 25), 158: (26, 26), 159: (26, 26), 160: (26, 26), 161: (26, 26), 162: (26, 26), 163: (26, 26), 164: (26, 26)}

	cm = {1: (9, 98, 6, 66), 2: (100, 425, 6, 67), 3: (427, 606, 7, 67), 4: (609, 772, 6, 67), 5: (775, 942, 6, 67), 6: (945, 1095, 6, 67), 7: (1098, 1264, 6, 66), 8: (9, 1262, 73, 108), 9: (10, 98, 112, 143), 10: (101, 424, 112, 144), 11: (426, 606, 113, 144), 12: (608, 771, 112, 144), 13: (774, 941, 112, 144), 14: (943, 1093, 112, 144), 15: (1096, 1262, 112, 144), 16: (11, 98, 147, 178), 17: (102, 424, 147, 178), 18: (609, 770, 147, 178), 19: (774, 940, 147, 178), 20: (943, 1093, 147, 177), 21: (1096, 1262, 147, 178), 22: (426, 605, 148, 178), 23: (11, 99, 181, 212), 24: (102, 423, 181, 212), 25: (609, 770, 181, 212), 26: (773, 939, 181, 211), 27: (943, 1092, 181, 211), 28: (1096, 1262, 181, 212), 29: (427, 605, 182, 212), 30: (11, 100, 215, 245), 31: (103, 424, 215, 245), 32: (427, 605, 215, 245), 33: (608, 770, 215, 245), 34: (773, 938, 215, 245), 35: (942, 1092, 215, 245), 36: (1095, 1261, 215, 245), 37: (11, 99, 249, 278), 38: (103, 422, 249, 278), 39: (427, 604, 249, 278), 40: (608, 769, 249, 278), 41: (773, 938, 249, 278), 42: (942, 1091, 249, 278), 43: (1095, 1261, 249, 278), 44: (12, 99, 282, 312), 45: (103, 422, 282, 312), 46: (426, 603, 282, 312), 47: (608, 769, 282, 312), 48: (773, 938, 282, 312), 49: (942, 1091, 282, 312), 50: (1095, 1261, 282, 312), 51: (426, 603, 315, 346), 52: (608, 769, 315, 346), 53: (773, 938, 315, 346), 54: (941, 1091, 315, 346), 55: (1094, 1260, 315, 346), 56: (12, 99, 316, 346), 57: (103, 422, 316, 346), 58: (12, 99, 348, 379), 59: (103, 421, 349, 379), 60: (426, 603, 349, 379), 61: (607, 768, 348, 379), 62: (772, 938, 348, 379), 63: (941, 1090, 348, 379), 64: (1094, 1259, 348, 379), 65: (12, 99, 382, 413), 66: (103, 421, 382, 413), 67: (425, 603, 382, 413), 68: (607, 768, 382, 413), 69: (772, 938, 382, 413), 70: (941, 1090, 382, 413), 71: (1094, 1258, 382, 413), 72: (12, 99, 417, 447), 73: (102, 421, 417, 447), 74: (425, 603, 417, 447), 75: (607, 768, 417, 447), 76: (771, 937, 417, 447), 77: (941, 1089, 417, 447), 78: (1093, 1259, 417, 447), 79: (12, 99, 449, 480), 80: (103, 421, 449, 480), 81: (424, 603, 449, 480), 82: (606, 768, 449, 480), 83: (771, 937, 449, 480), 84: (940, 1090, 449, 480), 85: (1092, 1258, 449, 480), 86: (13, 98, 482, 513), 87: (103, 421, 482, 513), 88: (424, 602, 482, 513), 89: (606, 767, 482, 513), 90: (771, 935, 482, 513), 91: (940, 1088, 482, 513), 92: (1092, 1258, 482, 513), 93: (13, 98, 516, 547), 94: (102, 420, 516, 547), 95: (424, 602, 516, 547), 96: (606, 766, 516, 547), 97: (771, 936, 516, 547), 98: (940, 1088, 516, 547), 99: (1092, 1258, 516, 547), 100: (13, 98, 549, 581), 101: (102, 420, 549, 581), 102: (423, 602, 549, 581), 103: (605, 766, 549, 581), 104: (770, 935, 549, 581), 105: (940, 1087, 549, 581), 106: (1092, 1258, 549, 581), 107: (13, 97, 585, 615), 108: (101, 419, 585, 615), 109: (423, 601, 585, 615), 110: (605, 766, 585, 615), 111: (770, 935, 585, 615), 112: (939, 1088, 585, 615), 113: (1092, 1257, 585, 615), 114: (12, 96, 618, 649), 115: (100, 418, 618, 649), 116: (422, 601, 618, 649), 117: (605, 767, 618, 649), 118: (770, 935, 618, 649), 119: (940, 1088, 618, 649), 120: (1092, 1257, 618, 649), 121: (11, 95, 652, 683), 122: (99, 418, 652, 683), 123: (422, 601, 652, 683), 124: (604, 767, 652, 683), 125: (770, 935, 652, 683), 126: (939, 1087, 652, 683), 127: (1092, 1255, 652, 683), 128: (9, 95, 686, 718), 129: (97, 418, 686, 718), 130: (421, 600, 686, 718), 131: (604, 766, 686, 718), 132: (769, 936, 686, 718), 133: (938, 1089, 687, 718), 134: (1091, 1256, 686, 718), 135: (9, 1256, 721, 759), 136: (9, 93, 760, 791), 137: (96, 399, 760, 791), 138: (401, 600, 760, 791), 139: (603, 767, 760, 791), 140: (768, 936, 760, 791), 141: (938, 1088, 760, 791), 142: (1092, 1255, 761, 791), 143: (9, 92, 795, 826), 144: (96, 397, 795, 826), 145: (401, 599, 795, 826), 146: (603, 766, 795, 826), 147: (769, 935, 795, 826), 148: (939, 1088, 795, 826), 149: (1091, 1255, 795, 826), 150: (8, 1255, 829, 865), 151: (7, 91, 868, 901), 152: (94, 397, 868, 901), 153: (400, 599, 868, 901), 154: (602, 766, 868, 900), 155: (768, 936, 868, 901), 156: (938, 1088, 868, 901), 157: (1091, 1255, 869, 901), 158: (8, 90, 904, 936), 159: (94, 396, 904, 936), 160: (399, 597, 904, 936), 161: (602, 765, 904, 936), 162: (769, 936, 904, 936), 163: (939, 1087, 904, 936), 164: (1091, 1254, 904, 936)}
	
	index = range(1,row_m[len(row_m)][1]+1)
	columns = range(1,col_m[len(col_m)][1]+1)

	data = pd.DataFrame(index=index,columns=columns)

	for i in cm:
		crop_img = img[cm[i][2]:cm[i][3],cm[i][0]:cm[i][1]]
		IMG = preprocess(crop_img,Model.imgSize)
		imgs.append(IMG)
		#cv2.imwrite('HTR/imgs/'+str(i)+'.jpg',crop_img)

	batch = Batch(None, imgs)#imgs)
	recognized = model.inferBatch(batch, True)
	for i in cm:
		if recognized[i-1] == "":
			recognized[i-1] = "?"
		data.iloc[row_m[i][0]-1][col_m[i][0]] = recognized[i-1]

		data.fillna('*',inplace=True)
	print(data)
	data.to_excel('out.xlsx',index=True,header=True)



def main():
	"main function"
	# optional command line args
	parser = argparse.ArgumentParser()
	parser.add_argument('--train', help='train the NN', action='store_true')
	parser.add_argument('--validate', help='validate the NN', action='store_true')
	parser.add_argument('--beamsearch', help='use beam search instead of best path decoding', action='store_true')
	parser.add_argument('--wordbeamsearch', help='use word beam search instead of best path decoding', action='store_true')
	parser.add_argument('--dump', help='dump output of NN to CSV file(s)', action='store_true')

	args = parser.parse_args()

	decoderType = DecoderType.BestPath
	if args.beamsearch:
		decoderType = DecoderType.BeamSearch
	elif args.wordbeamsearch:
		decoderType = DecoderType.WordBeamSearch

	# train or validate on IAM dataset	
	if args.train or args.validate:
		# load training data, create TF model
		loader = DataLoader(FilePaths.fnTrain, Model.batchSize, Model.imgSize, Model.maxTextLen)

		# save characters of model for inference mode
		open(FilePaths.fnCharList, 'w').write(str().join(loader.charList))
		
		# save words contained in dataset into file
		open(FilePaths.fnCorpus, 'w').write(str(' ').join(loader.trainWords + loader.validationWords))

		# execute training or validation
		if args.train:
			model = Model(loader.charList, decoderType)
			train(model, loader)
		elif args.validate:
			model = Model(loader.charList, decoderType, mustRestore=True)
			validate(model, loader)

	# infer text on test image
	else:
		print(open(FilePaths.fnAccuracy).read())
		model = Model(open(FilePaths.fnCharList).read(), decoderType, mustRestore=True, dump=args.dump)
		
		infer(model, FilePaths.fnInfer)


if __name__ == '__main__':
	main()

