from django.shortcuts import render

def modified(request):
  pathImage = "media//images//page1.jpg"
  final_result =[]

  if request.method == 'POST':
    def splitBoxes(img,rows):
      boxes=[]
      i=0
      j=0
      for r in range(0,rows*100,100):
        for c in range(0,600,200):
                    
          # cv2_imshow(img[r:r+100,c:c+200])
          # print("\n\n")
          boxes.append(cv2.countNonZero(img[r:r+100,c:c+200]))
      return boxes

    def rectContour(contours):

      rectCon = []
      max_area = 0
      for i in contours:
        area = cv2.contourArea(i)
        if area > 50:
          peri = cv2.arcLength(i, True)
          approx = cv2.approxPolyDP(i, 0.02 * peri, True)
          if len(approx) == 4:
            rectCon.append(i)
      rectCon = sorted(rectCon, key=cv2.contourArea,reverse=False)
                #print(len(rectCon))
      return rectCon

    def getCornerPoints(cont):
      peri = cv2.arcLength(cont, True) # LENGTH OF CONTOUR
      approx = cv2.approxPolyDP(cont, 0.02 * peri, True) # APPROXIMATE THE POLY TO GET CORNER POINTS
      return approx

    def reorder(myPoints):

      myPoints = myPoints.reshape((4, 2)) # REMOVE EXTRA BRACKET
      # print(myPoints)
      myPointsNew = np.zeros((4, 1, 2), np.int32) # NEW MATRIX WITH ARRANGED POINTS
      add = myPoints.sum(1)
      # print(add)
      # print(np.argmax(add))
      myPointsNew[0] = myPoints[np.argmin(add)]  #[0,0]
      myPointsNew[3] =myPoints[np.argmax(add)]   #[w,h]
      diff = np.diff(myPoints, axis=1)
      myPointsNew[1] =myPoints[np.argmin(diff)]  #[w,0]
      myPointsNew[2] = myPoints[np.argmax(diff)] #[h,0]

      return myPointsNew

          # Commented out IPython magic to ensure Python compatibility.
          #changing the working directory
          # %cd /content/drive/MyDrive/OMR

    import cv2
    import numpy as np
            # from google.colab.patches import cv2_imshow


            ########################################################################
    webCamFeed = False
    # pathImage = "/content/drive/MyDrive/OMR/page4.jpg"
    
    cap = cv2.VideoCapture(1)
    cap.set(10,160)
    heightImg = 700
    widthImg  = 700
    ans= [1,2,0,2,4]
  ########################################################################

    if webCamFeed:
      success, img = cap.read()
    else:
        img = cv2.imread(pathImage)


  ######## Cropping the image 
    crop_img = img[1110:-150, 0:1200]
    #cv2_imshow(crop_img)
    img = crop_img

    img.shape

    imgBlank = np.zeros((heightImg,widthImg, 3), np.uint8) # CREATE A BLANK IMAGE FOR TESTING DEBUGGING IF REQUIRED
    #img = cv2.resize(img, (widthImg, heightImg)) # RESIZE IMAGE
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) # CONVERT IMAGE TO GRAY SCALE
    #cv2_imshow(imgGray)
    imgBlur = cv2.GaussianBlur(imgGray, (5, 5), 1) # ADD GAUSSIAN BLUR
    #cv2_imshow(imgBlur)
    imgCanny = cv2.Canny(imgBlur,10,70) # APPLY CANNY 
    cv2.imshow("image",imgCanny)

    # FIND ALL COUNTOURS
    imgContours = img.copy() # COPY IMAGE FOR DISPLAY PURPOSES
    imgBigContour = img.copy() # COPY IMAGE FOR DISPLAY PURPOSES
    contours, hierarchy = cv2.findContours(imgCanny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE) # FIND ALL CONTOURS
    cv2.drawContours(imgContours, contours, -1, (0, 255, 0), 10) # DRAW ALL DETECTED CONTOURS
    rectCon = rectContour(contours) # FILTER FOR RECTANGLE CONTOURS

    for i in range(3):

      biggestPoints= getCornerPoints(rectCon[i]) # GET CORNER POINTS OF THE BIGGEST RECTANGLE
                
      # BIGGEST RECTANGLE WARPING
      biggestPoints=reorder(biggestPoints) # REORDER FOR WARPING
      cv2.drawContours(imgBigContour, biggestPoints, -1, (0, 255, 0), 20) # DRAW THE BIGGEST CONTOUR
      pts1 = np.float32(biggestPoints) # PREPARE POINTS FOR WARP
      pts2 = np.float32([[0, 0],[widthImg, 0], [0, heightImg],[widthImg, heightImg]]) # PREPARE POINTS FOR WARP
      matrix = cv2.getPerspectiveTransform(pts1, pts2) # GET TRANSFORMATION MATRIX
      imgWarpColored = cv2.warpPerspective(img, matrix, (widthImg, heightImg)) # APPLY WARP PERSPECTIVE
      #cv2_imshow(imgWarpColored)
      if i==0:
        upper = 100
        rows = 5
      elif i==1 :
        upper = 59
        rows = 9
      else :
        upper = 47
        rows = 11
      # Cropping
      cv2.imshow("image",imgWarpColored[upper:,120:])
      imgWarpColored = imgWarpColored[upper:,120:]
      imgWarpColored.shape

              # Resizing image 
      imgWarpColored = cv2.resize(imgWarpColored,(600,rows*100))
      #print("size of the image is :",imgWarpColored.shape)
      # APPLY THRESHOLD
      imgWarpGray = cv2.cvtColor(imgWarpColored,cv2.COLOR_BGR2GRAY) # CONVERT TO GRAYSCALE
      #cv2_imshow(imgWarpGray)
      imgThresh = cv2.threshold(imgWarpGray, 200, 255,cv2.THRESH_BINARY_INV )[1] # APPLY THRESHOLD AND INVERSE

      box = splitBoxes(imgThresh,rows)
      resultMat = np.resize(box,(rows,3))

      temp = 0
      for index in np.argmax(resultMat, axis=1):
        if index==0:
          a ="A"
          final_result.append(a) 
          print(a)
                   
        elif index ==1 and resultMat[temp,1]>4200:
          b="B"
          final_result.append(b)
          print(b)
          
        elif index==2:
          c="C"
          final_result.append(c)
          print(c)
        else : 
          d='Empty'
          final_result.append(d) 
          print(d)
        
        temp+=1
    
  
    # context={'a':a,'b':b,'c':c}
    # return render(request,'modified.html',context)
  return render(request,'modified.html',{'pathImage':pathImage,'final_result':final_result})