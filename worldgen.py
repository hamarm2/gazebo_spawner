import pcg_gazebo.parsers.sdf as sdf
import math
#import pcg_gazebo.parsers.types as types

#file.write("")

# default reflectivities
BOX_REFL = 500
CYL_REFL = 1000

def begin(file):
    file.write("<sdf version='1.5'>\n")
    file.write("<world name=\"default\">\n")
    file.write("  <include>\n")
    file.write("    <uri>model://sun</uri>\n")
    file.write("  </include>\n")
    file.write("  <include>\n")
    file.write("    <uri>model://ground_plane</uri>\n")
    file.write("  </include>\n")
    file.write("\n")
    
    
def end(file):
    file.write("</world>\n")
    file.write("</sdf>\n")
    
def box(file, x, y, yaw, modelName, linkName, a, b, c, density, reflectivity = BOX_REFL):

    link = sdf.create_sdf_element("link")
    
    visual = sdf.create_sdf_element("visual")   # name required, link can have more than one visual
    boxV = sdf.create_sdf_element("box")
    boxV.size = [a, b, c]    # in x, y, z
    visual.geometry.box = boxV
    link.add_visual("visual1", visual)
    
    
    collision = sdf.create_sdf_element("collision")
    #collision.density = density       # not available?  default is 1000 (density of water)
    #lasTag = sdf.create_sdf_element("laser_retro")
    #lasTag._set_value(BOX_REFL)
    collision._add_child_element("laser_retro", BOX_REFL)
    boxC = sdf.create_sdf_element("box")
    boxC.size = [a, b, c]    # in x, y, z
    collision.geometry.box = boxC
    link.add_collision("collision1", collision)     # name required, link can have more than one collision
    
    mass = a*b*c*density   # the parser does not know <inertial auto="true" />
    #link.inertial._attributes["auto"] = "true"     # possible fix for the aforementioned problem - will override the values in the inertial tag
    link.mass = mass
    link.inertia.ixx = mass * (b*b+c*c) / 12
    link.inertia.iyy = mass * (a*c+c*c) / 12
    link.inertia.izz = mass * (a*a+b*b) / 12
    
    
    model = sdf.create_sdf_element("model")
    model.name = modelName   # must be unique
    model.pose = [x, y, c/2, 0, 0, (yaw if yaw <= math.pi else (yaw-2*math.pi))]     # with respect to the world frame
    model.add_link(linkName, link)   # link name must be unique
        
    file.write(str(model))
    file.write("\n")
    
    print(modelName + " finished")
    

def cylinder(file, x, y, modelName, linkName, r, h, density, reflectivity = CYL_REFL):

    link = sdf.create_sdf_element("link")
    
    visual = sdf.create_sdf_element("visual")   # name required, link can have more than one visual
    cylinderV  = sdf.create_sdf_element("cylinder")
    cylinderV.radius = r
    cylinderV.length = h
    visual.geometry.cylinder = cylinderV
    link.add_visual("visual1", visual)
    
    
    collision = sdf.create_sdf_element("collision")
    densTag = sdf.create_sdf_element("density")
    densTag._set_value(density)
    collision.density = densTag
    collision._add_child_element("laser_retro", CYL_REFL)
    cylinderC  = sdf.create_sdf_element("cylinder")
    cylinderC.radius = r
    cylinderC.length = h
    collision.geometry.cylinder = cylinderC
    link.add_collision("collision1", collision)     # name required, link can have more than one collision
    
    mass = math.pi*r*r*density 
    #link.mass = 500   # set mass so the inertial tag gets created
    #link.inertial._attributes["auto"] = "true"     
    link.mass = mass
    link.inertia.ixx = mass * (3*r*r+h*h) / 12
    link.inertia.iyy = mass * (3*r*r+h*h) / 12
    link.inertia.izz = mass * (r*r) / 2
    
    
    model = sdf.create_sdf_element("model")
    model.name = modelName   # must be unique
    model.pose = [x, y, h/2, 0, 0, 0]     # with respect to the world frame
    model.add_link(linkName, link)   # link name must be unique
        
    file.write(str(model))
    file.write("\n")
    
    print(modelName + " finished")
    
    
def initRobotPos(filename, x, y, z, yaw):
    with open(filename, "w") as file:
        file.write(str(x)+" ")  # m
        file.write(str(y)+" ")
        file.write(str(z)+" ")  
        file.write(str(yaw if yaw <= math.pi else (yaw-2*math.pi)))  # rad
    print("initial position finished")