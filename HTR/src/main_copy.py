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
import json


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
		(recognized, _) = model.inferBatch(batch)
		
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

	corner_maps = open('corner_m.json')
	corner_maps = json.load(corner_maps)
	cm = {}
	for key,val in corner_maps.items():
		cm[int(key)] = tuple(val)

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
	data.to_excel('demo.xlsx',index=True,header=True)



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

