from imutils.perspective import four_point_transform
import cv2 
import pytesseract
import argparse
import imutils
import re

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i","--image", required=True, help="path to input receipt image")
ap.add_argument("-d", "--debug", type=int, default=-1, help="whether or not we are visualizing each step of the pipeline")
args = vars(ap.parse_args())

#load input image from disk. resize image and compute the ratio of new : old width

orig = cv2.imread(args["image"])
image = orig.copy()
image = imutils.resize(image, width=500) #noise reduction
ratio = orig.shape[1] / float(image.shape[1]) #used for perspective transform


#convert image to grayscale. blur slightly. edge detection
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (5,5,), 0) #reduces noise
edged = cv2.Canny(blurred, 50, 200)

# #if debug, show output of edge detection
# if args["debug"] > 0:
# 	cv2.imshow("Input", image)
# 	cv2.imshow("Edged", edged)
# 	cv2.waitKey(0)
	
#find contours in edge map and sort them by size in descending order
contours = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
contours = imutils.grab_contours(contours)
contours = sorted(contours, key=cv2.contourArea, reverse=True)

# initialize a contour that corresponds to the receipt outline
receipt_contour = None
# loop over the contours
for c in contours:
	# approximate the contour
	peri = cv2.arcLength(c, True)
	approx = cv2.approxPolyDP(c, 0.02 * peri, True)
	
	# if our approximated contour has four points, then we can
	# assume we have found the outline of the receipt
	if len(approx) == 4:
		receiptCnt = approx
		break
	
# if the receipt contour is empty then our script could not find the
# outline and we should be notified
if receiptCnt is None:
	raise Exception(("Could not find receipt outline. "
		"Try debugging your edge detection and contour steps."))


# check to see if we should draw the contour of the receipt on the
# image and then display it to our screen
if args["debug"] > 0:
	output = image.copy()
	cv2.drawContours(output, [receiptCnt], -1, (0, 255, 0), 2)
	cv2.imshow("Receipt Outline", output)
	cv2.waitKey(0)

# apply a four-point perspective transform to the *original* image to
# obtain a top-down bird's-eye view of the receipt
receipt = four_point_transform(orig, receiptCnt.reshape(4, 2) * ratio)

# show transformed image
cv2.imshow("Receipt Transform", imutils.resize(receipt, width=500))
cv2.waitKey(0)


# apply OCR to the receipt image by assuming column data, ensuring
# the text is *concatenated across the row* 
options = "--psm 4"
text = pytesseract.image_to_string(
	cv2.cvtColor(receipt, cv2.COLOR_BGR2RGB),
	config=options)

# show the raw output of the OCR process
print("[INFO] raw output:")
print("==================")
print(text)
print("\n")

pricePattern = r'([0-9]+\.[0-9]+)'

print("[INFO] price line items:")
print("========================")

#loop over each of the line items in the OCR'd receipt
for row in text.split("\n"):
	if re.search(pricePattern, row) is not None:
		print(row)