#include "cv.h"
#include "highgui.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <iostream>
#include <assert.h>
#include <math.h>
#include <float.h>
#include <limits.h>
#include <time.h>
#include <ctype.h>
#include <ApplicationServices/ApplicationServices.h>
#include <unistd.h>

using namespace cv;
using namespace std;

static CvMemStorage* storage = 0;

static CvHaarClassifierCascade* cascade = 0;

void detect_and_draw( IplImage* image );

void set_pointer_location(int x, int y);

const char* cascade_name = "haarcascade_frontalface_alt.xml";
/*    "haarcascade_profileface.xml";*/

int main( int argc, char** argv )
{
    CvCapture* capture = 0;
    IplImage *frame, *frame_copy = 0;
    int optlen = strlen("--cascade=");
    const char* input_name;

    // Check for the correct usage of the command line
    if( argc > 1 && strncmp( argv[1], "--cascade=", optlen ) == 0 )
    {
        cascade_name = argv[1] + optlen;
        input_name = argc > 2 ? argv[2] : 0;
    }

    cascade = (CvHaarClassifierCascade*)cvLoad( cascade_name, 0, 0, 0 );
    if( !cascade )
    {
        fprintf( stderr, "ERROR: Could not load classifier cascade\n" );
        return -1;
    }
    
    // Allocate the memory storage
    storage = cvCreateMemStorage(0);
    
    // Find whether to detect the object from file or from camera.
    if( !input_name || (isdigit(input_name[0]) && input_name[1] == '\0') )
        capture = cvCaptureFromCAM( !input_name ? 0 : input_name[0] - '0' );
    else
        capture = cvCaptureFromAVI( input_name ); 

    // Create a new named window with title: result
    cvNamedWindow( "result", 1 );

    if( capture )
    {
        for(;;)
        {
            if( !cvGrabFrame( capture )) break;
            frame = cvRetrieveFrame( capture );
            if( !frame ) break;
            if( !frame_copy )
                frame_copy = cvCreateImage( cvSize(frame->width,frame->height),
                                            IPL_DEPTH_8U, frame->nChannels );
	    cvFlip( frame, frame_copy, 1);
            detect_and_draw( frame_copy );
            if( cvWaitKey( 10 ) >= 0 ) break;
        }

        cvReleaseImage( &frame_copy );
        cvReleaseCapture( &capture );
    }
    
    cvDestroyWindow("result");
    return 0;
}

// Function to detect and draw any faces that is present in an image
void detect_and_draw( IplImage* img )
{
    int scale = 1;

    IplImage* temp = cvCreateImage( cvSize(img->width/scale,img->height/scale), 8, 3 );

    CvPoint pt1, pt2;
    int i;
    cvClearMemStorage( storage );

    if( cascade )
    {
        // There can be more than one face in an image. So create a growable sequence of faces.
        // Detect the objects and store them in the sequence
        CvSeq* faces = cvHaarDetectObjects( img, cascade, storage,
                                            1.1, 2, CV_HAAR_DO_CANNY_PRUNING,
                                            cvSize(40, 40) );

        for( i = 0; i < (faces ? faces->total : 0); i++ ) //faces->total
        {
            CvRect* r = (CvRect*)cvGetSeqElem( faces, i );
            pt1.x = r->x*scale;
            pt2.x = (r->x+r->width)*scale;
            pt1.y = r->y*scale;
            pt2.y = (r->y+r->height)*scale;

	    //move mouse to center of the face's rectangle
	    set_pointer_location((pt1.x+pt2.x)/2, (pt1.y+pt2.y)/2);
	    
            // Draw the rectangle in the input image
            cvRectangle( img, pt1, pt2, CV_RGB(0,255,0), 3, 8, 0 );
        }
    }

    cvShowImage( "result", img );
    cvReleaseImage( &temp );
}

void set_pointer_location(int x, int y)
{
    cout << "moving mouse pointer to (" << x << ", " << y <<")"<< endl;
    CGEventRef move = CGEventCreateMouseEvent(
        NULL, kCGEventMouseMoved,
        CGPointMake(x*2, y*2),
        kCGMouseButtonLeft
    );

    CGEventPost(kCGHIDEventTap, move);
    sleep(1);
    CFRelease(move);
}
