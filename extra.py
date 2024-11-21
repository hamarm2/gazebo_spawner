import pygame
import colours as col
import math

def drawCross(surface, colour, center, endpointOffset):
    pygame.draw.line(surface, colour, (center[0]-endpointOffset, center[1]-endpointOffset), (center[0]+endpointOffset, center[1]+endpointOffset))
    pygame.draw.line(surface, colour, (center[0]+endpointOffset, center[1]-endpointOffset), (center[0]-endpointOffset, center[1]+endpointOffset))

class Cylinder():
    
    drawColour = col.DARK_GREY
    
    def __init__(self, center, r):
        self.S = center    # coords of the center
        self.r = r
        
    def draw(self, surface):    pygame.draw.circle(surface, Cylinder.drawColour, self.S, self.r)
    

class Box():
    
    drawColour = col.TEAL
    
    def __init__(self, S, corner, yaw):
        self.S = S  # coords of the center
        self.a = abs(S[0]-corner[0]) * 2
        self.b = abs(S[1]-corner[1]) * 2
        self.yaw = yaw
        
        l = math.dist(S,corner)
        k = math.asin(self.b/2/l)     
        
        # coords of the corners - only used for rendering
        self.A = (S[0]-l*math.cos(k+yaw), S[1]+l*math.sin(k+yaw))
        self.B = (S[0]+l*math.cos(k-yaw), S[1]+l*math.sin(k-yaw))
        self.C = (S[0]+l*math.cos(k+yaw), S[1]-l*math.sin(k+yaw))
        self.D = (S[0]-l*math.cos(k-yaw), S[1]-l*math.sin(k-yaw))
        #print("A = " + str((self.A[0]-S[0], self.A[1]-S[1])) + " B = " + str((self.B[0]-S[0], self.B[1]-S[1])) + " C = " + str((self.C[0]-S[0], self.C[1]-S[1])) + " D = " + str((self.D[0]-S[0], self.D[1]-S[1])))
        #print("yaw = " + str(yaw) + " A = " + str(self.A) + " B = " + str(self.B) + " C = " + str(self.C) + " D = " + str(self.D))
        
    def draw(self, surface):                    pygame.draw.polygon(surface, Box.drawColour, (self.A, self.B, self.C, self.D)) 
    def draw2(self, surface, colour, width):     pygame.draw.polygon(surface, colour, (self.A, self.B, self.C, self.D), width = width)
        
        