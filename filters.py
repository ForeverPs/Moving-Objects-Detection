import cv2
import numpy as np
import utils


#src means source while dst means destination
#this function will make dst as the filtered image of src
def strokeEdges(src, dst, blurKsize = 7, edgeKsize = 5):
	#bulrKsize can be used to determine whether we should blur
	if blurKsize >= 3:
		blurredSrc = cv2.medianBlur(src, blurKsize)
		graySrc = cv2.cvtColor(blurredSrc, cv2.COLOR_BGR2GRAY)
	else:
		graySrc = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
	#Laplacian can get the edge of picture especially the gray picture
	cv2.Laplacian(graySrc, cv2.CV_8U, graySrc, ksize = edgeKsize)
	#this matrix can make the image inverse
	normalizedInverseAlpha = (255 - graySrc) / 255
	#spilt src into several channels
	channels = cv2.split(src)
	for channel in channels:
		channel[:] = channel * normalizedInverseAlpha
	#merge several channels into dst
	cv2.merge(channels, dst)

#this function can apply convolution between source and given filter
class VConvolutionFilter(object):
	def __init__(self, kernel):
		self._kernel = kernel
	def apply(self, src, dst):
		cv2.filter2D(src, -1, self._kernel, dst)

#this function can sharpen the image
class SharpFilter(VConvolutionFilter):
	def __init__(self):
		kernel = -1 * np.ones((3, 3))
		kernel[1, 1] = 9
		VConvolutionFilter.__init__(self, kernel)

#this function can blur the image
class BlurFilter(VConvolutionFilter):
	def __init__(self):
		kernel = 0.04 * np.ones((5, 5))
		VConvolutionFilter(self, kernel)

#this function can make the image both blurred and sharpen
class EmbossFilter(VConvolutionFilter):
	def __init__(self):
		kernel = np.array([[-2, -1, 0],
							[-1, 1, 1],
							[0, 1, 2]])
		VConvolutionFilter.__init__(self, kernel)
