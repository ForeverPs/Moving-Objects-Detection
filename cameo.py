import os
import cv2
import filters
import numpy as np
import matplotlib.pyplot as plt
from managers import CaptureManager, WindowManager

class Cameo(object):
	def __init__(self):
		self.shootcount = 1
		self.castcount = 1
		self.mean = None
		self.sigma = None
		self._windowManager = WindowManager('REAL', self.onKeypress)
		self._captureManager = CaptureManager(cv2.VideoCapture(0), self._windowManager, shouldMirrorPreview = True)
		#shouldMirrorPreview can convert the image into its mirrored image
		#self._curveFilter = filters.SharpFilter()
		self._curveFilter = filters.EmbossFilter()

	def background(self):
		self._windowManager.createWindow()
		while self._windowManager.isWindowCreated:
			self._captureManager.enterFrame()
			frame = self._captureManager.frame
			self._captureManager.exitFrame()
			self._windowManager.processEvents()

	def run(self, k = 3):
		self.Gaussian()
		self._windowManager.createWindow()
		cv2.namedWindow('Object')
		while self._windowManager.isWindowCreated:
			self._captureManager.enterFrame()
			frame = self._captureManager.frame
			self.judge(frame, k)
			self._captureManager.exitFrame()
			self._windowManager.processEvents()

	def judge(self, frame, k):
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		m, n = np.shape(gray)
		low = self.mean - k * self.sigma
		upper = self.mean + k * self.sigma
		temp = np.multiply((gray - low), (upper - gray))
		temp[temp >= 0] = 0
		temp[temp < 0] = 1
		#show the moving object which doesn't contain in background
		new = (np.multiply(gray, temp)).astype(np.uint8)
		cv2.imshow('Object', new)

	def Gaussian(self, filename = 'screenshoot'):
		img = []
		names = os.listdir(filename)
		for name in names:
			temp = filename + '/' + name
			img.append(cv2.imread(temp, cv2.IMREAD_GRAYSCALE))
		m, n = np.shape(img[0])
		mean = np.zeros((m, n))
		var = np.zeros((m, n))
		#calculate by matrix is faster
		for ele in img:
			mean += ele
		mean /= len(img)
		for ele in img:
			var += np.multiply((ele - mean), (ele - mean))
		var /= len(img)
		self.mean = mean
		self.sigma = np.sqrt(var)

	def onKeypress(self, keycode):
		if keycode == 32:#space
			print(str(self.shootcount)+' Screenshot Finished')
			self._captureManager.writeImage('screenshoot/'+str(self.shootcount)+'.png')
			self.shootcount += 1
		elif keycode == 9:#tab
			if not self._captureManager.isWritingVideo:
				print(str(self.castcount)+' Screencast Begins')
				self._captureManager.startWritingVideo('screencast/'+str(self.castcount)+'.avi')
			else:
				self._captureManager.stopWritingVideo()
				print(str(self.castcount)+' Screencast Finished')
				self.castcount += 1
		elif keycode == 27:#Esc
			self._windowManager.destroyWindow()
			self._captureManager._capture.release()

if __name__ == '__main__':
	Cameo().background()
	Cameo().run(k = 5)
