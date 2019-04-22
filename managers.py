import cv2
import time
import numpy as np

# In this programme:
# None means we need a function at this location, sometimes the function can be a class defined already.
# False or True means that we need a bool value here

class CaptureManager(object):

	def __init__(self, capture, previewWindowManager = None, shouldMirrorPreview = False):
		self.previewWindowManager = previewWindowManager
		self.shouldMirrorPreview = shouldMirrorPreview
		self._capture = capture
		self._channel = 0
		self._enteredFrame = False
		self._frame = None
		self._imageFilename = None
		self._videoFilename = None
		self._videoEncoding = None
		self._videoWriter = None
		self._startTime = None
		self._framesElapsed = np.long(0)
		# long(x) can convert x into data type 'long int', x can be a string or a number.
		self._fpsEstimate = None

	#@property can convert function channel into the property of class defined before.
	#we can check the value of self._channel in self.channel.
	@property
	def channel(self):
		return self._channel

	#this is a function of self._channel, it makes that we can change channel's value easily.
	#class.channel = value can change channel's value
	@channel.setter
	def channel(self,value):
		if self._channel != value:
			self._channel = value
			self._frame = None

	@property
	def frame(self):
		if self._enteredFrame and self._frame is None:
			_, self._frame = self._capture.retrieve()
			#we can use capture.read() to get frame when there is only on camera
			#when there are several cameras, we should use grab() to get status and use retrieve() to get frame
			return self._frame

	#'is not None' is a kind of judgement, if the object is False, the function will return True. 
	@property
	def isWritingImage(self):
		return self._imageFilename is not None
		#when we write image, the filename will be given

	@property
	def isWritingVideo(self):
		return self._videoFilename is not None

	def enterFrame(self):
		#when sentence following assert is not true, the programme will exit and throw out the message after \
		assert not self._enteredFrame,\
		'previous enterFrame() had no matching exitFrame()'
		#when there exists frame, self._enteredFrame is True until the frame exits.

		if self._capture is not None:
			self._enteredFrame = self._capture.grab()
			#get the status of capture next frame.
			#function grab() will return the status of capture, True or False

	def exitFrame(self):
		if self._frame is None:
			self._enteredFrame = False
			return
			#it means that there is no frame, so we have no need to do the followings.

		#Calculate the fps
		if self._framesElapsed == 0:
			self._startTime = time.time()
			#time.time() can get the current time
		else:
			timeElapsed = time.time() - self._startTime
			#calculate the fps approximately
			self._fpsEstimate = self._framesElapsed / timeElapsed
		#Increase
		self._framesElapsed += 1

		if self.previewWindowManager is not None:
			if self.shouldMirrorPreview:
				mirroredFrame = np.fliplr(self._frame).copy()
				self.previewWindowManager.show(mirroredFrame)
			else:
				self.previewWindowManager.show(self._frame)

		if self.isWritingImage:
			cv2.imwrite(self._imageFilename, self._frame)
			self._imageFilename = None
			#after writing, reset the filename.
			#filename exists only when we are writing
		self._writeVideoFrame()
		self._frame = None
		self._enteredFrame = False

	def writeImage(self, filename):
		self._imageFilename = filename

	def startWritingVideo(self, filename, encoding = cv2.VideoWriter_fourcc('I','4','2','0')):
		self._videoFilename = filename
		self._videoEncoding = encoding

	def stopWritingVideo(self):
		self._videoFilename = None
		self._videoEncoding = None
		self._videoWriter = None

	def _writeVideoFrame(self):
		if not self.isWritingVideo:
			return
		#if we are writing a video, we can do nothing but wait.
		if self._videoWriter is None:
			#when the writer is free we can write
			#get the fps, if unknown, we have to use the estimated fps
			fps = self._capture.get(cv2.CAP_PROP_FPS)
			if fps == 0.0:
				if self._framesElapsed < 20:
					#few frames to estimate, wait for a while
					return
				else:
					fps = self._fpsEstimate
			#when self._videoWriter is None and we get enough information, we can create the Writer
			size = (np.int(self._capture.get(cv2.CAP_PROP_FRAME_WIDTH)),np.int(self._capture.get(cv2.CAP_PROP_FRAME_HEIGHT)))
			self._videoWriter = cv2.VideoWriter(self._videoFilename, self._videoEncoding, fps, size)
		#write by each frame
		self._videoWriter.write(self._frame)


class WindowManager(object):

	def __init__(self, windowName, keypressCallback = None):
		self.keypressCallback = keypressCallback
		self._windowName = windowName
		self._isWindowCreated = False
	@property
	def isWindowCreated(self):
		return self._isWindowCreated

	def createWindow(self):
		cv2.namedWindow(self._windowName)
		self._isWindowCreated = True

	def show(self, frame):
		cv2.imshow(self._windowName, frame)

	def destroyWindow(self):
		cv2.destroyWindow(self._windowName)
		self._isWindowCreated = False

	def processEvents(self):
		keycode = cv2.waitKey(1)
		if self.keypressCallback is not None and keycode != -1:
			keycode &= 0xFF
			#get the last 8 bits
			self.keypressCallback(keycode)
		#keypressCallback is a class defined in cameo.py and keycode is its parameter 




