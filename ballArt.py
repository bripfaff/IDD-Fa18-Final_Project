
# import the necessary packages
from collections import deque
from imutils.video import VideoStream
from imutils.video import FPS

import numpy as np
import argparse
import cv2
import imutils
import time


# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
	help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=100,
	help="max buffer size")
args = vars(ap.parse_args())

# Define the lower and upper boundaries of the colored
# balls in the RGB color space
greenLower = (29, 86, 6)
greenUpper = (64, 255, 200)

# redLower = (166, 84, 141)
# redUpper = (186,255,255)

redLower = (0, 50, 80)
redUpper = (20,255,255)

blueLower = (97, 100, 117)
blueUpper = (117,255,255)

# orangeLower = (0, 50, 80)
# orangeUpper = (20,255,255)

# lower = {'red':(166, 84, 141), 'green':(66, 122, 129), 'blue':(97, 100, 117), 'yellow':(23, 59, 119), 'orange':(0, 50, 80)} #assign new item lower['blue'] = (93, 10, 0)
# upper = {'red':(186,255,255), 'green':(86,255,255), 'blue':(117,255,255), 'yellow':(54,255,255), 'orange':(20,255,255)}

#green points
ptsg = deque(maxlen=args["buffer"])

#red points
ptsr = deque(maxlen=args["buffer"])

#blue points
ptsb = deque(maxlen=args["buffer"])

# Grab reference to the Pi Camera and set the desired size of the frame.
d1=480
d2=480
vs = VideoStream(usePiCamera=True, resolution = (d1,d2)).start()


# allow the camera or video file to warm up
time.sleep(2.0)
fps = FPS().start()

ball_bounce = []
frame1 = np.zeros((d1,d2,3))+255
# frame1 = vs.read()
while True:
	# grab the current frame
	frame = vs.read()

	# Blur the frame and convert it to the HSV color space
    # frame = imutils.resize(frame, width=600)
	blurred = cv2.GaussianBlur(frame, (11, 11), 0)
	hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

	# construct a mask for the color "green", then perform
	# a series of dilations and erosions to remove any small
	# blobs left in the mask
	maskg = cv2.inRange(hsv, greenLower, greenUpper)
	maskg = cv2.erode(maskg, None, iterations=2)
	maskg = cv2.dilate(maskg, None, iterations=2)

	# do the same for the red
	maskr = cv2.inRange(hsv, redLower, redUpper)
	maskr = cv2.erode(maskr, None, iterations=2)
	maskr = cv2.dilate(maskr, None, iterations=2)

	# do the same for the blue
	maskb = cv2.inRange(hsv, blueLower, blueUpper)
	maskb = cv2.erode(maskb, None, iterations=2)
	maskb = cv2.dilate(maskb, None, iterations=2)

	# find contours in the mask and initialize the current
	# (x, y) center of the ball
	# green
	cntsg = cv2.findContours(maskg.copy(), cv2.RETR_EXTERNAL,  cv2.CHAIN_APPROX_SIMPLE)
	cntsg = cntsg[0] if imutils.is_cv2() else cntsg[1]
	centerg = None

	#red
	cntsr = cv2.findContours(maskr.copy(), cv2.RETR_EXTERNAL,  cv2.CHAIN_APPROX_SIMPLE)
	cntsr = cntsr[0] if imutils.is_cv2() else cntsr[1]
	centerr = None

	#blue
	cntsb = cv2.findContours(maskb.copy(), cv2.RETR_EXTERNAL,  cv2.CHAIN_APPROX_SIMPLE)
	cntsb = cntsb[0] if imutils.is_cv2() else cntsb[1]
	centerb = None



	# only proceed if at least one contour was found
	if len(cntsg) > 0:
		# find the largest contour in the mask, then use
		# it to compute the minimum enclosing circle and
		# centroid
		c = max(cntsg, key=cv2.contourArea)
		((x, y), radius) = cv2.minEnclosingCircle(c)
		M = cv2.moments(c)
		centerg = (d1-int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

		# only proceed if the radius meets a minimum size
		if radius > 1:
			# draw the circle and centroid on the frame,
			# then update the list of tracked points
			cv2.circle(frame, (int(x), int(y)), int(radius),
				(0, 255, 255), 2)
			cv2.circle(frame, centerg, 5, (0, 0, 255), -1)
	ptsg.appendleft(centerg)

	if len(cntsr) > 0:
		# find the largest contour in the mask, then use
		# it to compute the minimum enclosing circle and
		# centroid
		c = max(cntsr, key=cv2.contourArea)
		((x, y), radius) = cv2.minEnclosingCircle(c)
		M = cv2.moments(c)
		centerr = (d1-int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

		# only proceed if the radius meets a minimum size
		if radius > 1:
			# draw the circle and centroid on the frame,
			# then update the list of tracked points
			cv2.circle(frame, (int(x), int(y)), int(radius),
				(0, 255, 255), 2)
			cv2.circle(frame, centerr, 5, (0, 0, 255), -1)
	ptsr.appendleft(centerr)

	if len(cntsb) > 0:
		# find the largest contour in the mask, then use
		# it to compute the minimum enclosing circle and
		# centroid
		c = max(cntsb, key=cv2.contourArea)
		((x, y), radius) = cv2.minEnclosingCircle(c)
		M = cv2.moments(c)
		centerb = (d1-int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

		# only proceed if the radius meets a minimum size
		if radius > 1:
			# draw the circle and centroid on the frame,
			# then update the list of tracked points
			cv2.circle(frame, (int(x), int(y)), int(radius),
				(0, 255, 255), 2)
			cv2.circle(frame, centerb, 5, (0, 0, 255), -1)
	ptsb.appendleft(centerb)
	# loop over the set of tracked points
	for i in range(1, len(ptsg)):
		# if either of the tracked points are None, ignore
		# them
		if ptsg[i - 1] is None or ptsg[i] is None:
			continue


		# otherwise, compute the thickness of the line and
		# draw the connecting lines
		thickness = int(np.sqrt(args["buffer"] / float(i + 1)))

		# color_val = tuple([int(x) for x in frame[center]])
		color_val = (0,255,255)
		cv2.line(frame1, ptsg[i - 1], ptsg[i], color_val, thickness)
	for i in range(1, len(ptsr)):
		# if either of the tracked points are None, ignore
		# them
		if ptsr[i - 1] is None or ptsr[i] is None:
			continue


		# otherwise, compute the thickness of the line and
		# draw the connecting lines
		thickness = int(np.sqrt(args["buffer"] / float(i + 1)))

		# color_val = tuple([int(x) for x in frame[center]])
		color_val = (0,0,255)
		cv2.line(frame1, ptsr[i - 1], ptsr[i], color_val, thickness)

	for i in range(1, len(ptsb)):
		# if either of the tracked points are None, ignore
		# them
		if ptsb[i - 1] is None or ptsb[i] is None:
			continue


		# otherwise, compute the thickness of the line and
		# draw the connecting lines
		thickness = int(np.sqrt(args["buffer"] / float(i + 1)))

		# color_val = tuple([int(x) for x in frame[center]])
		color_val = (255,0,0)
		cv2.line(frame1, ptsb[i - 1], ptsb[i], color_val, thickness)

	# show the frame to our screen

	cv2.imshow("Frame", frame1)
	key = cv2.waitKey(0) & 0xFF

	# if the 'q' key is pressed, stop the loop
	if key == ord("q"):
		cv2.imwrite("my_art.jpg", frame1)
		break
	#
	# elif key == ord("s"):
	# 	print("reached here")
	# 	cv2.imwrite("my_art.png",frame1)

	fps.update()

# if we are not using a video file, stop the camera video stream
if not args.get("video", False):
	vs.stop()

# otherwise, release the camera
else:
	vs.release()
fps.stop()
cv2.imwriter(r"./my_art.png",frame1)
print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

# time.sleep(20.0)

# close all windows

cv2.destroyAllWindows()
