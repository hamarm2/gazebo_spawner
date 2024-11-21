def box(file, x, y, name, a, b, c, density):

    link = sdf.create_sdf_element('link')
    link.name = name   # must be unique
    
    link.mass = a*b*c*density   # the parser does not know <inertial auto="true" />
    link.inertia.ixx = 0.5
    link.inertia.iyy = 0.5
    link.inertia.izz = 0.5
    
    file.write(str(link))
    file.write("\n")
    
    
    
with open("testfile.world", "w") as file:
    wg.begin(file)
    wg.box(file, 0, 0, "box1","box1link", 2, 3, 4, 500)
    wg.cylinder(file, 5, 0, "cyl1","cyl1link", 0.5, 1, 500)
    wg.end(file)
    
wg.initRobotPos("initPos.txt", -2, -2, 0, wg.math.pi/4)