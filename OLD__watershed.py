# Antonio Leonti & Grayson Kelly & Devin Cannistraro
# 1.29.2020
#

import numpy as np
import cv2
import random
import math
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt

# temp notes
# add seed to stack
# add all neighbors to temp stack, if none are step downs from before commit stack to pool
distanceIncrements = []

def checkNewWaterLevel(outerEdgeStack, img, basinNum, waterLevel, newAdditionsStack,inStack):
    tempOuterEdge = outerEdgeStack.copy()
    newAdditionsStack.clear()
    newOuterEdge = []
    shouldReject = False
    print("Current water level:" + str(waterLevel))
    while(len(tempOuterEdge) and not shouldReject):
        x,y = tempOuterEdge.pop()
        coordarray = [(x, y + 1), (x - 1, y), (x + 1, y), (x, y - 1), (x - 1, y + 1), (x + 1, y + 1), (x - 1, y - 1),
                      (x + 1, y - 1)]
        usedNeighbors = 0 # count meant to determine if this point should still be on the outerEdgeStack if = 8 removes
        for neighborCoord in coordarray:
            neighborElevation = img[neighborCoord[0],neighborCoord[1]]
            if inStack[neighborCoord[0]][neighborCoord[1]] == -1:
                if neighborElevation == waterLevel:
                    newAdditionsStack.append((neighborCoord[0],neighborCoord[1]))
                    tempOuterEdge.append((neighborCoord[0],neighborCoord[1]))
                    inStack[neighborCoord[0]][neighborCoord[1]] = basinNum
                    usedNeighbors += 1
                elif neighborElevation < waterLevel:
                    print("ShouldReject height:" + str(neighborElevation))
                    shouldReject = True
            else:
                usedNeighbors += 1
        if usedNeighbors != 8:
            newOuterEdge.append((x,y))

    if not shouldReject:
        outerEdgeStack = newOuterEdge
    else:
        while(len(newAdditionsStack)):
            x,y = newAdditionsStack.pop()
            inStack[x][y] = -1

    return shouldReject

def segmentBasin2(seed , img, basinNum ,testMarker, inStack, color):
    global distanceIncrements
    outerEdgeStack = []
    outerEdgeStack.append(seed)
    waterLevel = img[seed[0],seed[1]]
    waterIncrementIndex = distanceIncrements.index(waterLevel)
    newAdditions = []
    currBasin = []
    print("Starting water height:" + str(waterLevel))
    numberOfwaterLevelRises = 0
    while not checkNewWaterLevel(outerEdgeStack,img,basinNum,waterLevel,newAdditions,inStack) and waterIncrementIndex < len(distanceIncrements):
        currBasin += newAdditions
        waterIncrementIndex += 1
        waterLevel = distanceIncrements[waterIncrementIndex]
        numberOfwaterLevelRises += 1

    #TODO debug only
    while len(currBasin):
        x,y = currBasin.pop()
        testMarker[x,y] = color
    print("Number of water level rises:" + str(numberOfwaterLevelRises) )


def segmentBasin(seed , img, basinNum ,testMarker, inStack, color):
    basinStack = []
    basinStack.append(seed)
    outerEdgeStack = []
    outerEdgeStack.append(seed)
    tempStack = []
    size = 0
    peakReached = False
    waterHeight = img[seed[0],seed[1]]
    print("WaterHeight:" + str(waterHeight))
    while not peakReached:
        while len(outerEdgeStack):
            x,y = outerEdgeStack.pop()
            testMarker[x,y] = color
            size += 1
            coordarray = [(x, y + 1), (x - 1, y), (x + 1, y), (x, y - 1), (x-1,y+1),(x+1,y+1),(x-1,y-1), (x+1,y-1)]
            for pixel in coordarray:
                if img[pixel[0],pixel[1]] > waterHeight:
                    if inStack[pixel[0]][pixel[1]] == -1:
                        inStack[pixel[0]][pixel[1]] = basinNum
                        tempStack.append(pixel)
                        basinStack.append(pixel)
        outerEdgeStack = tempStack
        if len(outerEdgeStack) == 0:
            peakReached = True

    print("Size " + str(size))

def main():
    #import image
    img = cv2.imread("data/batch_test.tif", cv2.IMREAD_GRAYSCALE) #important
    testMarker = cv2.imread("data/batch_test.tif") # for testing only
    #img = cv2.imread("data/batch_one_obj_test.png", cv2.IMREAD_GRAYSCALE)  # important
    #testMarker = cv2.imread("data/batch_one_obj_test.png")  # for testing only
    #kernel = numpy.ones((3,3),numpy.uint8) #for later
    #threshold
    thr = cv2.threshold(img, 1,255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1] #important
    # Copy the thresholded image.
    im_floodfill = thr.copy()

    # Mask used to flood filling.
    # Notice the size needs to be 2 pixels than the image.

    # Floodfill from point (0, 0)
    cv2.floodFill(im_floodfill, None, (0, 0), 255);

    # Invert floodfilled image
    im_floodfill_inv = cv2.bitwise_not(im_floodfill)

    # Combine the two images to get the foreground.
    im_out = thr | im_floodfill_inv

    dist = cv2.distanceTransform(im_out, cv2.DIST_L2, 3) #important
    dist = cv2.bitwise_not(dist)
    show_image("dist", dist)
    localMinima = []
    deepestPoints = np.array(dist)
    imgWidth = deepestPoints.shape[1]
    imgHeight = deepestPoints.shape[0]

    for row in deepestPoints:
        for pixel in row:
            if not math.isnan(pixel):
                if pixel not in distanceIncrements:
                    distanceIncrements.append(pixel)

    print("number of increments:" + str(len(distanceIncrements)))
    distanceIncrements.sort()
    print(str(distanceIncrements))

    for row in range(1,imgHeight - 1):
        for column in range(1,imgWidth - 1):
            if deepestPoints[row + 1,column] <= deepestPoints[row,column] and deepestPoints[row-1, column] <= deepestPoints[row,column] and deepestPoints[row,column + 1] <= deepestPoints[row,column] and deepestPoints[row,column - 1] <= deepestPoints[row,column]   and deepestPoints[row + 1,column+ 1] <= deepestPoints[row,column] and deepestPoints[row-1, column + 1] <= deepestPoints[row,column] and deepestPoints[row - 1,column - 1] <= deepestPoints[row,column] and deepestPoints[row + 1,column - 1] <= deepestPoints[row,column]:
                testMarker[row,column] = (255,255,0)
                localMinima.append((row,column))
                #print("Test" + str(deepestPoints[row,column]) +" " + str(deepestPoints[row + 1,column]))
                #print("Test" + str(row) + " " + str(column))
    # sorts so lowest points are filled from first
    localMinima.sort(key=lambda point: deepestPoints[point[0], point[1]], reverse=False)
    '''for minima in localMinima:
        print(deepestPoints[minima[0],minima[1]])'''
    basinNum = 0
    inStack = [[-1 for row in range(img.shape[1])] for column in range(img.shape[0])]
    basinsToFill = 30
    while(len(localMinima) and basinNum < basinsToFill):
        x,y = localMinima.pop()
        if inStack[x][y] == -1:
            color = (random.randint(0, 254), random.randint(0, 254), random.randint(0, 255)) # color to render for testing
            segmentBasin2((x,y), dist, basinNum, testMarker,inStack, color)
            print("AmountLeft:" + str(len(localMinima)))
            basinNum += 1
    show_image("testMarker",testMarker)
    cv2.imwrite("data/testMarker.tif",testMarker)


    #show all images
    show_image("src", img)


def show_image(str, img):
    cv2.imshow(str, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()