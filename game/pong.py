'''
face-pong

author: Shashank Polasa <shashank.pv@gmail.com>
'''

import pygame
import cv
from sys import exit
from math import cos,sin
from random import randint
try:
    #required for pyinstaller on windows
    import pygame._view
except ImportError:
    pass 
 
# Define some consts
WIDTH,HEIGHT = 640,480
black    = (   0,   0,   0)
gray     = (  23,  26,  27)
white    = ( 255, 255, 255)
blue     = (  42,  64,  85)
green    = (   0, 255,   0)
yellow   = ( 193, 238,   0)
red      = ( 255,   0,   0)
purple   = (0xBF,0x0F,0xB5)
brown    = (0x55,0x33,0x00)
DEBUG = False

class ball:
    def __init__(self,x,y,direction):
        self.x,self.y,self.direction = x,y,direction
        self.speed = 10
        self.radius = 10
        self.bounce = False

    def set_attr(self,x,y,direction):
        self.x,self.y,self.direction = x,y,direction
        self.speed = 10
        self.radius = 10

    def inc_speed(self):
        self.speed += 1

    def dec_speed(self):
        self.speed = max(self.speed-1,0)

    def update(self):
        
        #update
        #TODO: jerky ball motion?
        self.x += self.speed*cos(self.direction * 0.0174532925)
        self.y += self.speed*sin(self.direction * 0.0174532925)
        
        #check x-bounds
        if self.x<=self.radius:
            if self.direction<=180: self.direction = 180-self.direction
            else: self.direction = 540-self.direction
        elif self.x>WIDTH-self.radius:
            if self.direction<=90: self.direction = 180-self.direction
            else: self.direction = 540-self.direction

        #check y-bounds
        if self.y<=self.radius:
            if self.direction<=90: self.direction = 360-self.direction
            else: self.direction = 360-self.direction
            self.bounce = not self.bounce
        elif self.y>HEIGHT-self.radius:
            self.direction = 540-self.direction
            return True
        elif abs(self.y+self.radius-paddle_y)<=(self.speed) and \
                paddle_x-paddle_width/2-5<=self.x<=paddle_x+paddle_width/2+5 and\
                not self.bounce:
            self.direction = 360-self.direction
            self.bounce = not self.bounce
            
        return False
        
    def draw(self,screen):
        pygame.draw.circle(screen,yellow,(int(self.x),int(self.y)),self.radius)

def add_position(x,y):
    #25 frames are good enough for a yes/no nod
    if len(response_coords)<25:
        response_coords.append((x,y))
        return None
    
    xlow,xhigh,ylow,yhigh=x,x,y,y
    proportions = []
    for p in response_coords[::-1]:
        px,py = p[0],p[1]
        xlow,xhigh = min(xlow,px),max(xhigh,px)
        ylow,yhigh = min(ylow,py),max(yhigh,py)
        if abs(yhigh-ylow) > 2*abs(xhigh-xlow):
            proportions.append(True)
        elif abs(xhigh-xlow) > 2*abs(yhigh-ylow):
            proportions.append(False)

    if len(proportions)<13:
        print 'not sure what you meant'
        response_coords[:] = []
        return None
    else: return proportions.count(True)>proportions.count(False)

def draw_background(screen):
    screen.fill(gray)
 
def draw_paddle(screen,x,y):
    pygame.draw.rect(screen,blue,[x,y,paddle_width,10],0)

def draw_face_not_found_error(screen):
    font = pygame.font.Font(pygame.font.match_font('bitstreamverasans'), 15)
    text = font.render("No face detected",True,(150,50,60))
    textRect = text.get_rect()
    textRect.centerx = 570
    textRect.centery = 10
    screen.blit(text, textRect)

def draw_restart_dialog(screen):
    font = pygame.font.Font(pygame.font.match_font('bitstreamverasans'), 22)
    text = font.render("Restart?",True,yellow)
    textRect = text.get_rect()
    textRect.centerx = screen.get_rect().centerx
    textRect.centery = screen.get_rect().centery
    screen.blit(text, textRect)
    
def detect(image):
    image_size = cv.GetSize(image)
	
    # create grayscale version
    grayscale = cv.CreateImage(image_size, 8, 1)
    cv.CvtColor(image, grayscale, cv.CV_BGR2GRAY)
 
    storage = cv.CreateMemStorage(0)
    cv.EqualizeHist(grayscale, grayscale)
    faces = cv.HaarDetectObjects(grayscale, cascade, storage, 1.2, 2, cv.CV_HAAR_DO_CANNY_PRUNING, (100, 100))

    if faces and len(faces)==1:
        if DEBUG:
            cv.Rectangle(image, (faces[0][0][0], faces[0][0][1]),
            (faces[0][0][2]+faces[0][0][0], faces[0][0][3]+faces[0][0][1]), green)
        return faces[0][0]
    else: return []

def exit_nicely():
    try : 
        cv.DestroyWindow("camera")
    except Exception:
        pass
	
    try : 
        pygame.quit ()
    except Exception:
        pass
    exit(0)
	
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("pong")

# Current position
x_coord=10
y_coord=10
response_coords = []
	
#Camera capture
if DEBUG: 
    cv.NamedWindow("camera", 1)
    print cv.CV_CAP_PROP_FRAME_COUNT,"fps"
    clock = pygame.time.Clock()
capture = cv.CaptureFromCAM(0)

try:
    cascade = cv.Load('haarcascade_frontalface_alt.xml')
except Exception:  
    print 'cascade file not found. exiting..'
    exit_nicely()
	
gameball = ball(screen.get_rect().centerx,50,randint(50,150))
paddle_x, paddle_y, paddle_width = 0, 400, 50

done, gameover=False, False
while gameover==False:
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            gameover = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                gameover = True
            if event.key == pygame.K_UP:
                gameball.inc_speed()
            if event.key == pygame.K_DOWN:
                gameball.dec_speed()
                 
    frame = cv.QueryFrame(capture)
    if frame is None:
        print 'frame creation failed'
        break

    # mirror
    cv.Flip(frame, None, 1)
    face_location = detect(frame)
    if DEBUG: cv.ShowImage("camera", frame)
    draw_background(screen)

    if face_location:
        x_coord = face_location[0] + (face_location[2])/2
        y_coord = face_location[1] + (face_location[3])/2
        if not done:
            paddle_x = int((x_coord-160)*(640.0/315))
            done = gameball.update()
        else:
            response = add_position(x_coord,y_coord)
            if response:
                done=False
                response_coords[:] = []
                gameball.set_attr(screen.get_rect().centerx,50,randint(50,150))
            elif response==False:
                print 'bye.'
                break
    else:
        draw_face_not_found_error(screen)

    gameball.draw(screen)
    #TODO: smoothen paddle movement
    draw_paddle(screen,paddle_x-paddle_width/2,paddle_y)

    if done: draw_restart_dialog(screen)
    pygame.display.flip()

exit_nicely()
