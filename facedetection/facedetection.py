import cv
#import cv2

def detect(image):
    #cv.Rectangle(image, (10,10), (50,50), cv.RGB(255,0,0)) 
    image_size = cv.GetSize(image)
	
    # create grayscale version
    grayscale = cv.CreateImage(image_size, 8, 1)
    cv.CvtColor(image, grayscale, cv.CV_BGR2GRAY)
 
    # create storage
    storage = cv.CreateMemStorage(0)
    #cv.ClearMemStorage(storage)
 
    # equalize histogram
    cv.EqualizeHist(grayscale, grayscale)
 
    # detect objects
    cascade = cv.Load('haarcascade_frontalface_alt.xml')#, cv.Size(1,1))
    faces = cv.HaarDetectObjects(grayscale, cascade, storage, 1.2, 2, cv.CV_HAAR_DO_CANNY_PRUNING, (100, 100))
 
    if faces:
        #print len(faces), 'face(s) detected!'
        #if len(faces)>1: print '2 faces found'
        for i in faces:
            j = i[0]
            cv.Rectangle(image, ( int(j[0]), int(j[1])),
                         (int(j[0] + j[2]), int(j[1] + j[3])),
                         cv.RGB(0, 255, 0), 3, 8, 0)

						 
cv.NamedWindow("camera", 1)
capture = cv.CaptureFromCAM(0)

while True:
    img = cv.QueryFrame(capture)	
    frame = cv.QueryFrame(capture)
    if frame is None:
        print 'frame creation failed'
        break
 
    # mirror
    cv.Flip(frame, None, 1)
	
    # face detection
    detect(frame)
    cv.ShowImage("camera", img)
	
    if cv.WaitKey(10) == 27:
        break
cv.DestroyWindow("camera")
