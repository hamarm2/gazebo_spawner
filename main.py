import pygame, sys
from pygame.locals import *
import copy
from math import dist
from math import asin
from math import acos
from math import sin
from math import cos
from math import copysign
from math import atan2
from math import pi
import json

import worldgen as wg
import colours as col
from extra import Cylinder as Cyl
from extra import Box as Box
from extra import drawCross

# outputFiles
sdfFile = "testfile.world"
initPosFile = "initPos.txt"
jsFile = "waypoints.json"
obstacleDensity = 500
obstacleHeight = 3.5

width = 1400     # velikost celeho okna, pocatek v levem hornim rohu
height = 1200
canvasOrigin = (100, 100)   # pocatek platna, ktery je v jeho levem hornim rohu
grid = 10      # grid line distance
canvasWidth = width-2*canvasOrigin[0]
canvasHeight = height-2*canvasOrigin[1]
center = (width/2, height/2)
crossSize = 0.005
robotSize = 0.05

buttonDist = 10
textMargin = 10
fontSize = 40
buttonWidth = 170
buttonHeight = 2*textMargin + fontSize

hDispTextMargin = 5
hDispFontSize = 25
hDescWidth = 40
hDispWidth = 85
hDispHeight = 0.5*hDispTextMargin + hDispFontSize

pygame.init()
pygame.display.set_caption("Primitive world generator for gazebo")
window = pygame.display.set_mode((width,height))    # vytvori surface (na nej lze vykreslovat)
window.fill(col.DARK_GREY)
clock = pygame.time.Clock()
FONT = pygame.freetype.Font("AovelSansRounded-rdDL.ttf", fontSize)
FONT2 = pygame.freetype.Font("AovelSansRounded-rdDL.ttf", hDispFontSize)

# ulozeni platna jako objektu, ale jeste se nevykresli
canvas = pygame.Rect(canvasOrigin, (canvasWidth, canvasHeight))  # pocatek vlevo nahore, sirka, vyska

# value shortcuts
button_y = height-buttonHeight-buttonDist   # levy horni roh tlacitka
hDisp_y = height-hDispHeight-buttonDist
boxBT_x = buttonDist
cylinderBT_x = buttonDist*2+buttonWidth
robotBT_x = buttonDist*3+buttonWidth*2
waypointBT_x = buttonDist*4+buttonWidth*3
undoBT_x = buttonDist*5+buttonWidth*4
saveBT_x = buttonDist*6+buttonWidth*5
clearBT_x = buttonDist*7+buttonWidth*6
hDisp_x = buttonDist*8+buttonWidth*7
hDescR_x = buttonDist*8+buttonWidth*7+hDescWidth+hDispTextMargin
safeDist = 0.5    # to prevent division by zero when rendering box previews

# buttons
boxBT = pygame.Rect((boxBT_x, button_y), (buttonWidth, buttonHeight))               # objekt jen obsahuje souradnice
cylinderBT = pygame.Rect((cylinderBT_x, button_y), (buttonWidth, buttonHeight))
robotBT = pygame.Rect((robotBT_x, button_y), (buttonWidth, buttonHeight))
waypointBT = pygame.Rect((waypointBT_x, button_y), (buttonWidth, buttonHeight))
undoBT = pygame.Rect((undoBT_x, button_y), (buttonWidth, buttonHeight))
saveBT = pygame.Rect((saveBT_x, button_y), (buttonWidth, buttonHeight))
clearBT = pygame.Rect((clearBT_x, button_y), (buttonWidth, buttonHeight))

# obstacle height display
hDescL = pygame.Rect((hDisp_x, button_y), (hDescWidth, hDispHeight))
hDescR = pygame.Rect((hDescR_x, button_y), (hDescWidth, hDispHeight))
hDisp = pygame.Rect((hDisp_x, hDisp_y), (hDispWidth, hDispHeight))

# is the button on?
box_on = False
cyl_on = False
rob_on = False
way_on = False

stage = 0   # stage of creating obstacles

# robot state
rob_yaw = 0     # in rad, calculated from waypoints and latest robot coords

obstacles = list()
waypoints = list()
robCoordsList = [(center[0], center[1])]    # should not be withour coordinates
undoList = list() # will contain pointers to the above lists


# temporary
S = None
G = None

# to gazebo coords
def convertX(val): return(val - center[0]) / grid
def convertY(val): return -(val - center[1]) / grid

# main loop     ==========================================================================================================================================================================================================================================
while(True):
    
    window.fill(col.DARK_GREY)
    pygame.draw.rect(window, col.WHITE, canvas)     # objekt, na ktery kreslim, barva, Rect objekt (ktery kreslim)
    
    # draw a grid
    for i in range(1, int(canvasWidth/2/grid)+1):     
        pygame.draw.line(window, col.GREY, (center[0]+i*grid, canvasOrigin[1]), (center[0]+i*grid, canvasOrigin[1]+canvasHeight))   # (surface, colour, start, end)
        pygame.draw.line(window, col.GREY, (center[0]-i*grid, canvasOrigin[1]), (center[0]-i*grid, canvasOrigin[1]+canvasHeight))
    for i in range(1, int(canvasHeight/2/grid)+1):     
        pygame.draw.line(window, col.GREY, (canvasOrigin[0], center[1]+i*grid), (canvasOrigin[0]+canvasWidth, center[1]+i*grid))
        pygame.draw.line(window, col.GREY, (canvasOrigin[0], center[1]-i*grid), (canvasOrigin[0]+canvasWidth, center[1]-i*grid))
       
    # center highlight 
    pygame.draw.line(window, col.BLACK, (center[0], canvasOrigin[1]), (center[0], canvasOrigin[1]+canvasHeight))
    pygame.draw.line(window, col.BLACK, (canvasOrigin[0], center[1]), (canvasOrigin[0]+canvasWidth, center[1]))
    
    # button rendering 
    pygame.draw.rect(window, col.GREY, boxBT)
    FONT.render_to(window, (buttonDist+textMargin, button_y+textMargin), "Box", col.CYAN)
    pygame.draw.rect(window, col.GREY, cylinderBT)
    FONT.render_to(window, (cylinderBT_x+textMargin, button_y+textMargin), "Cylinder", col.CYAN)
    pygame.draw.rect(window, col.GREY, robotBT)
    FONT.render_to(window, (robotBT_x+textMargin, button_y+textMargin), "Robot", col.CYAN)
    pygame.draw.rect(window, col.GREY, waypointBT)
    FONT.render_to(window, (waypointBT_x+textMargin, button_y+textMargin), "Waypoint", col.CYAN)
    pygame.draw.rect(window, col.GREY, undoBT)
    FONT.render_to(window, (undoBT_x+textMargin, button_y+textMargin), "Undo", col.CYAN)
    pygame.draw.rect(window, col.GREY, saveBT)
    FONT.render_to(window, (saveBT_x+textMargin, button_y+textMargin), "Save", col.CYAN)
    pygame.draw.rect(window, col.GREY, clearBT)
    FONT.render_to(window, (clearBT_x+textMargin, button_y+textMargin), "Clear", col.CYAN)
    
    # obstacle height control rendering 
    
    cursor = pygame.mouse.get_pos()
    pygame.draw.rect(window, col.GREY, hDisp)
    pygame.draw.rect(window, col.GREY, hDescL)
    pygame.draw.rect(window, col.GREY, hDescR)
    FONT2.render_to(window, (hDisp_x+hDispTextMargin, button_y+hDispTextMargin), "<=", col.CYAN)
    FONT2.render_to(window, (hDescR_x+hDispTextMargin, button_y+hDispTextMargin), "=>", col.CYAN)
    FONT2.render_to(window, (hDisp_x+hDispTextMargin, hDisp_y+hDispTextMargin), "{:0.2f}".format(obstacleHeight) , col.CYAN)
    
    # button appearance when on
    if box_on: pygame.draw.rect(window, col.TEAL, boxBT);           FONT.render_to(window, (boxBT_x+textMargin, button_y+textMargin), "Box", col.WHITE)
    if cyl_on: pygame.draw.rect(window, col.TEAL, cylinderBT);      FONT.render_to(window, (cylinderBT_x+textMargin, button_y+textMargin), "Cylinder", col.WHITE)
    if rob_on: pygame.draw.rect(window, col.TEAL, robotBT);         FONT.render_to(window, (robotBT_x+textMargin, button_y+textMargin), "Robot", col.WHITE)
    if way_on: pygame.draw.rect(window, col.TEAL, waypointBT);      FONT.render_to(window, (waypointBT_x+textMargin, button_y+textMargin), "Waypoint", col.WHITE)
    
    # button mouseover highlight
    if(boxBT_x < cursor[0] < boxBT_x+buttonWidth   and  button_y < cursor[1] < button_y+buttonHeight):              pygame.draw.rect(window, col.CYAN, boxBT, width = 2)
    if(cylinderBT_x < cursor[0] < cylinderBT_x+buttonWidth   and  button_y < cursor[1] < button_y+buttonHeight):    pygame.draw.rect(window, col.CYAN, cylinderBT, width = 2)
    if(robotBT_x < cursor[0] < robotBT_x+buttonWidth   and  button_y < cursor[1] < button_y+buttonHeight):          pygame.draw.rect(window, col.CYAN, robotBT, width = 2)
    if(waypointBT_x < cursor[0] < waypointBT_x+buttonWidth   and  button_y < cursor[1] < button_y+buttonHeight):    pygame.draw.rect(window, col.CYAN, waypointBT, width = 2)
    if(undoBT_x < cursor[0] < undoBT_x+buttonWidth   and  button_y < cursor[1] < button_y+buttonHeight):            pygame.draw.rect(window, col.CYAN, undoBT, width = 2)
    if(saveBT_x < cursor[0] < saveBT_x+buttonWidth   and  button_y < cursor[1] < button_y+buttonHeight):            pygame.draw.rect(window, col.CYAN, saveBT, width = 2)
    if(clearBT_x < cursor[0] < clearBT_x+buttonWidth   and  button_y < cursor[1] < button_y+buttonHeight):          pygame.draw.rect(window, col.CYAN, clearBT, width = 2)
    if(hDisp_x < cursor[0] < hDisp_x+hDescWidth   and  button_y < cursor[1] < button_y+hDispHeight):                pygame.draw.rect(window, col.CYAN, hDescL, width = 1)
    if(hDescR_x < cursor[0] < hDescR_x+hDescWidth   and  button_y < cursor[1] < button_y+hDispHeight):              pygame.draw.rect(window, col.CYAN, hDescR, width = 1)
    
    # draw all existing obstacles
    for obstacle in obstacles:
        obstacle.draw(window)
        
    # draw all existing waypoints
    if(len(waypoints) > 0):
        pygame.draw.line(window, col.TEAL, robCoordsList[-1], waypoints[0], width = 2)
        drawCross(window, col.DARK_GREY, waypoints[0], min(width, height)*crossSize)
        
        if(len(waypoints) > 1):
            for i in range(1, len(waypoints)):
                pygame.draw.line(window, col.TEAL, waypoints[i-1], waypoints[i], width = 2)
                drawCross(window, col.DARK_GREY, waypoints[i], min(width, height)*crossSize)
        
    # draw the robot
    pygame.draw.circle(window, col.TEAL, robCoordsList[-1], min(width, height)*robotSize/2)
    pygame.draw.circle(window, col.BLACK, robCoordsList[-1], min(width, height)*robotSize/2, width = 2)  
    x = robCoordsList[-1][0]+(min(width, height)*robotSize/2)*cos(rob_yaw) 
    y = robCoordsList[-1][1]-(min(width, height)*robotSize/2)*sin(rob_yaw) 
    pygame.draw.line(window, col.CYAN, robCoordsList[-1], (x,y), width = 2)
    
    # draw a cylinder currently in the making
    if cyl_on and (canvasOrigin[0] < cursor[0] < canvasOrigin[0]+canvasWidth  and  canvasOrigin[1] < cursor[1] < canvasOrigin[1]+canvasHeight):     # mouse on canvas
        if S is not None: 
            drawCross(window, col.BLACK, S, min(width, height)*crossSize)
            pygame.draw.line(window, col.BLACK, S, cursor)
            pygame.draw.circle(window, col.BLACK, S, dist(S, cursor), width = 1)
            
    # draw a box currently in the making
    if box_on and (canvasOrigin[0] < cursor[0] < canvasOrigin[0]+canvasWidth  and  canvasOrigin[1] < cursor[1] < canvasOrigin[1]+canvasHeight):     # mouse on canvas
        if (S is not None and dist(S,cursor) > safeDist and stage == 1): 
            drawCross(window, col.BLACK, S, min(width, height)*crossSize)
            tmp = Box(S, cursor, 0)
            pygame.draw.line(window, col.BLACK, S, cursor)
            tmp.draw2(window, col.BLACK, 1)
            
        if (G is not None and dist(S,cursor) > safeDist and stage == 2):
            drawCross(window, col.BLACK, S, min(width, height)*crossSize)
            yaw = (atan2(cursor[0]-S[0], cursor[1]-S[1]) - pi/2) % (pi*2)
            tmp = Box(S, G, yaw)
            pygame.draw.line(window, col.BLACK, S, cursor)
            tmp.draw2(window, col.BLACK, 1)
    
    # draw a waypoint preview
    if way_on and (canvasOrigin[0] < cursor[0] < canvasOrigin[0]+canvasWidth  and  canvasOrigin[1] < cursor[1] < canvasOrigin[1]+canvasHeight):     # mouse on canvas
        if len(waypoints) == 0: pygame.draw.line(window, col.BLACK, robCoordsList[-1], cursor)
        else: pygame.draw.line(window, col.BLACK, waypoints[-1], cursor)
    
    
    
    
    
    
    
    
    
    
    
    
    # event handling -------------------------------------------------------------------------------------------------------------------------------------------------
    for event in pygame.event.get():              
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        
        if event.type == pygame.MOUSEBUTTONUP:
            # a toggleable button was clicked on
            if(boxBT_x < cursor[0] < boxBT_x+buttonWidth   and  button_y < cursor[1] < button_y+buttonHeight):
                box_on = not box_on
                cyl_on = False
                rob_on = False
                way_on = False
                stage = 0
                S = None
            if(cylinderBT_x < cursor[0] < cylinderBT_x+buttonWidth   and  button_y < cursor[1] < button_y+buttonHeight):
                box_on = False
                cyl_on = not cyl_on
                rob_on = False
                way_on = False
                stage = 0
                S = None
                G = None  
            if(robotBT_x < cursor[0] < robotBT_x+buttonWidth   and  button_y < cursor[1] < button_y+buttonHeight):
                box_on = False
                cyl_on = False
                rob_on = not rob_on
                way_on = False
            if(waypointBT_x < cursor[0] < waypointBT_x+buttonWidth   and  button_y < cursor[1] < button_y+buttonHeight):
                box_on = False
                cyl_on = False
                rob_on = False
                way_on = not way_on
                
            # a button was clicked on
            if(undoBT_x < cursor[0] < undoBT_x+buttonWidth   and  button_y < cursor[1] < button_y+buttonHeight):
                if len(undoList) > 0: undoList.pop().pop()
                if len(waypoints) >= 1: rob_yaw = (atan2(waypoints[0][0]-robCoordsList[-1][0], waypoints[0][1]-robCoordsList[-1][1]) - pi/2) % (pi*2)      #; print(rob_yaw)
                
            if(saveBT_x < cursor[0] < saveBT_x+buttonWidth   and  button_y < cursor[1] < button_y+buttonHeight):
                # world generation part ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
                boxes = 0
                cyls = 0
                with open(sdfFile, "w") as file:
                    wg.begin(file)
                    for obstacle in obstacles:
                        if(type(obstacle).__name__ == "Box"):
                            wg.box(file, convertX(obstacle.S[0]), convertY(obstacle.S[1]), obstacle.yaw, f"box{boxes:02}",f"box{boxes:02}link", obstacle.a/grid, obstacle.b/grid, obstacle.height, obstacleDensity)
                            boxes += 1
                        else:
                            wg.cylinder(file, convertX(obstacle.S[0]), convertY(obstacle.S[1]), f"cyl{cyls:02}",f"cyl{cyls:02}link", obstacle.r/grid, obstacle.height, obstacleDensity)
                            cyls += 1
                    wg.end(file)
                    
                wg.initRobotPos(initPosFile, convertX(robCoordsList[-1][0]), convertY(robCoordsList[-1][1]), 0, rob_yaw)
                
                with open(jsFile, "w") as file:
                    finalPoints = list()
                    finalPoints.append([convertX(robCoordsList[-1][0]), convertY(robCoordsList[-1][1])])
                    for wp in waypoints:  
                        finalPoints.append([convertX(wp[0]), convertY(wp[1])])
                    json.dump({"waypoints": finalPoints, "yaw": rob_yaw if rob_yaw <= pi else (rob_yaw-2*pi)}, file)
                
                
            if(clearBT_x < cursor[0] < clearBT_x+buttonWidth   and  button_y < cursor[1] < button_y+buttonHeight):
                if(len(undoList) != 0): 
                    for i in range(0, len(undoList)): undoList.pop().pop()
                rob_yaw = 0
            
            # height down
            if(hDisp_x < cursor[0] < hDisp_x+hDescWidth   and  button_y < cursor[1] < button_y+hDispHeight):    obstacleHeight -= 0.1
            # height up
            if(hDescR_x < cursor[0] < hDescR_x+hDescWidth   and  button_y < cursor[1] < button_y+hDispHeight):    obstacleHeight += 0.1
            
            # the canvas was clicked on
            if(canvasOrigin[0] < cursor[0] < canvasOrigin[0]+canvasWidth  and  canvasOrigin[1] < cursor[1] < canvasOrigin[1]+canvasHeight):
                
                if cyl_on:
                    if stage==0: 
                        S = copy.deepcopy(cursor); stage=1
                        print("cylinder center set")
                    elif stage==1: 
                        tempCyl = Cyl(S, dist(S, cursor), obstacleHeight)
                        obstacles.append(tempCyl)
                        S = None
                        stage = 0
                        print("cylinder created")
                        undoList.append(obstacles)
                        
                if box_on:
                    if stage==0:
                        S = copy.deepcopy(cursor); stage=1
                        print("box center set")
                    elif (stage==1 and dist(S,cursor) > safeDist): 
                        G = copy.deepcopy(cursor); stage=2
                        print("box corner set")
                    elif (stage==2 and dist(S,cursor) > safeDist): 
                        temp = copy.deepcopy(cursor)
                        yaw = (atan2(cursor[0]-S[0], cursor[1]-S[1]) - pi/2) % (pi*2)
                        tempBox = Box(S, G, yaw, obstacleHeight)
                        obstacles.append(tempBox)
                        S = None
                        G = None
                        stage = 0
                        print("box created")
                        undoList.append(obstacles)
                        
                if rob_on:
                    robCoordsList.append(copy.deepcopy(cursor))
                    print("robot coordinates changed")
                    undoList.append(robCoordsList)
                    if len(waypoints) >= 1: rob_yaw = (atan2(waypoints[0][0]-robCoordsList[-1][0], waypoints[0][1]-robCoordsList[-1][1]) - pi/2) % (pi*2)    #; print(rob_yaw)
                        
                if way_on:
                    waypoints.append(copy.deepcopy(cursor))
                    print("waypoint created")
                    undoList.append(waypoints)
                    if len(waypoints) == 1: rob_yaw = (atan2(cursor[0]-robCoordsList[-1][0], cursor[1]-robCoordsList[-1][1]) - pi/2) % (pi*2)     #; print(rob_yaw)
                        
                    

    pygame.display.update()
    clock.tick(30)  # max 30 fps
