import json
import cv2
import numpy as np

import boto3
import urllib
def lambda_handler(event, context):
    print("event: ",event)
    s3 = boto3.client("s3")
    if event:
        file_obj = event["Records"][0]
        filename = str(file_obj['s3']['object']['key'])
        bucket_name = str(file_obj['s3']['bucket']['name'])
        print("Filename : ", filename)
        #filename = urllib.parse.unquote_plus(filename)
        fileObj = s3.get_object(Bucket = bucket_name, Key=filename)
        file_content = fileObj["Body"].read()
        nparr = np.fromstring(file_content, np.uint8)
        img_np = cv2.imdecode(nparr,cv2.IMREAD_COLOR)
        gray_image = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)

        ret, binary_image = cv2.threshold(gray_image, 220, 255, cv2.THRESH_BINARY_INV)


        flood_filled_image = binary_image.copy()

        h, w = binary_image.shape[:2]
        mask = np.zeros((h + 2, w + 2), np.uint8)

        cv2.floodFill(flood_filled_image, mask, (0, 0), 255)


        inv_flood_filled_image = cv2.bitwise_not(flood_filled_image)


        flood_filled_image_fin = binary_image | flood_filled_image


        kernel = np.ones((12, 12), np.uint8)
        eroded_image = cv2.erode(flood_filled_image_fin, kernel, iterations=1)


        dilated_image = cv2.dilate(eroded_image, kernel, iterations=1)
       


        contours, hierarchy = cv2.findContours(dilated_image, 1, 2)
        image = np.ones(dilated_image.shape[:2], dtype="uint8") * 255
        k = 0
        for c in contours:
           k = k + 1
           M = cv2.moments(c)
           area = cv2.contourArea(c)
           if 500 < area < 5000:
               cv2.drawContours(image, [c], -1, 0, -1)



        cnts, hierarchy = cv2.findContours(image, 1, 2)
        threshold = 0.78
        count = 0

        contour_list = []
        for c in cnts:
           M = cv2.moments(c)
           area = cv2.contourArea(c)
           perimeter = cv2.arcLength(c, True)
           metric = (4 * 3.14 * area) / perimeter ** 2
           if metric > threshold:
               count = count + 1
               contour_list.append(c)
        #print "Total objects detected: ", k
        print "Total parkings available: ", count

       
	    