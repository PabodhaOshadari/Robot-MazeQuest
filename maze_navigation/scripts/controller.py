#!/usr/bin/env python
import math
import rospy
import time
from geometry_msgs.msg import Twist, Point
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
from tf.transformations import euler_from_quaternion, quaternion_from_euler

CMD_PUB = None    
#Laser scan changes
Front = 0
Left = 0
FLeft = 0
FRight = 0
Right = 0

DOOR1 = 0
DOOR2 = 0
#currunt position of the robot
ROBOT_POS = Point()
#currunt orientation
ROBOT_YAW = 0

YAW_PREC = math.pi / 90
DIST_PRE = 0.3

# Door 1
DES_POS1 = Point()
DES_POS1.x = 3
DES_POS1.y = 3.5
DES_POS1.z = 0

#Door 2
DES_POS2 = Point()
DES_POS2.x = 3.0
DES_POS2.y = 4.3
DES_POS2.z = 0

# Cylinder Front Clockwise
DES_POS3 = Point()
DES_POS3.x = 2.75
DES_POS3.y = 5.5
DES_POS3.z = 0

# Cylinder Front Counterclockwoise
DES_POS4 = Point()
DES_POS4.x = 3.25
DES_POS4.y = 5.5
DES_POS4.z = 0

# Cylinder Front 
DES_POS5 = Point()
DES_POS5.x = 3
DES_POS5.y = 4.7
DES_POS5.z = 0

STATE = 0 #tracks navigation porgress wthin the sections
SECTION = 0#different stages of the task

TS = 0 
TD = 0


def ODOM_CALLBACK(msg):  #update currunt position using odometry data
    global ROBOT_YAW,ROBOT_POS
    ROBOT_POS = msg.pose.pose.position
    odom_ori = msg.pose.pose.orientation
    euler = euler_from_quaternion([odom_ori.x, odom_ori.y, odom_ori.z, odom_ori.w])
    ROBOT_YAW = euler[2]

def CHANGE_STATE(new_state):
    global STATE
    STATE = new_state

def NORMALIZE_ANGLE(angle):
    if(math.fabs(angle) > math.pi):
        angle = angle - (2 * math.pi * angle) / (math.fabs(angle))
    return angle

def done_moving():
    command = Twist()
    command.linear.x = 0
    command.angular.z = 0
    CMD_PUB.publish(command)
    command.linear.x = 0
    command.angular.z = 0

def FIX_YAW(des_pos):  #align the robot orientation toward a diseired position
    global ROBOT_YAW, CMD_PUB, YAW_PREC
    destination_yaw = math.atan2(des_pos.y - ROBOT_POS.y, des_pos.x - ROBOT_POS.x)
    err_yaw = NORMALIZE_ANGLE(destination_yaw - ROBOT_YAW)
    command = Twist()
    if math.fabs(err_yaw) > YAW_PREC:
        command.angular.z = 0.3 if err_yaw > 0 else -0.3
    CMD_PUB.publish(command)
    if math.fabs(err_yaw) <= YAW_PREC:
        CHANGE_STATE(1)

def ODOM_ROTATION(des_angle_in_radian,kp): #calculate the rotation velocity required to turn the robot toward a desird angle
    global ROBOT_YAW
    err_yaw = NORMALIZE_ANGLE(des_angle_in_radian - ROBOT_YAW)
    return kp * err_yaw

def shallStop(des_pos): #stop the robot if it is within a close distance of the target
    global CMD_PUB
    err_pos = math.sqrt(pow(des_pos.y - ROBOT_POS.y, 2) + pow(des_pos.x - ROBOT_POS.x, 2))
    if err_pos < 0.15:
        command = Twist()
        command.linear.x = 0
        command.angular.z = 0
        CMD_PUB.publish(command)

def GO(des_pos):  #move the robot toward the target position
    global ROBOT_YAW, CMD_PUB, YAW_PREC, DIST_PRE
    destination_yaw = math.atan2(des_pos.y - ROBOT_POS.y, des_pos.x - ROBOT_POS.x)
    err_yaw = destination_yaw - ROBOT_YAW
    err_pos = math.sqrt(pow(des_pos.y - ROBOT_POS.y, 2) + pow(des_pos.x - ROBOT_POS.x, 2))  
    if err_pos > DIST_PRE:
        command = Twist()
        command.linear.x = 0.2 # m/s
        command.angular.z = 0.2 if err_yaw > 0 else -0.2 # rad/s.
        CMD_PUB.publish(command)
    else:
        CHANGE_STATE(2)
    if math.fabs(err_yaw) > YAW_PREC:
        CHANGE_STATE(0)

def SCAN_CALLBACK(msg):
    global Front, FLeft, Left, Right, FRight      #extract laser scan reading for specific angular ranges 
    Front = min(min(msg.ranges[0:5]), min(msg.ranges[355:]))
    FLeft = min(msg.ranges[14:60])
    Left = min(msg.ranges[74:105])
    Right = min(msg.ranges[268:271])
    FRight = min(msg.ranges[299:345])

def MAIN():
    global CMD_PUB, SECTION, DOOR1, DOOR2, STATE, TS, TD, Front, FLeft, Left, Right, FRight, YAW_PREC
    CMD_PUB = rospy.Publisher('/cmd_vel', Twist, queue_size=1)
    scan_sub = rospy.Subscriber('/scan', LaserScan, SCAN_CALLBACK)
    odom_sub = rospy.Subscriber('/odom', Odometry, ODOM_CALLBACK)
    rospy.init_node('maze_navigation')
    command = Twist()
    command.linear.x = 0.0
    command.angular.z = 0.0
    rate = rospy.Rate(10)
    time.sleep(1)  
    near_wall = 0  
    distance = 0.275
    print("Turning...")
    command.angular.z = -0.5
    command.linear.x = 0.35
    CMD_PUB.publish(command)
    time.sleep(2)

    while not rospy.is_shutdown():

        if(SECTION == 1):
            print("Maze Solved Successfully!")
            print("Looking for Door 1")
            if(STATE == 0):
                FIX_YAW(DES_POS1)
            elif(STATE == 1):
                GO(DES_POS1)
            else:
                SECTION = 2
                STATE = 0
            
            if(math.isinf(Left) and math.isinf(Right)):
                DOOR1 = DOOR1 + 1
                print("Door 1 detected")
            if(DOOR1 > 1):
                DOOR1 = 1
                print("Door 1 is open")            
             
        elif(SECTION == 2):
            print("Looking for Door 2")
            if(STATE == 0):
                FIX_YAW(DES_POS2)
            elif(STATE == 1):
                GO(DES_POS2)
            else:
                SECTION = 3
                STATE = 0

            if(math.isinf(Left) and math.isinf(Right)):
                DOOR2 = DOOR2 + 1
                print("Door 2 detected")
            if(DOOR2 > 1):
                DOOR2 = 1
                print("Door 2 is open")

        elif(SECTION == 3):
            print("Moving towards Cylinder")
            if(STATE == 0):
                if (DOOR1 + DOOR2 == 1):
                    FIX_YAW(DES_POS3)
                elif (DOOR1 + DOOR2 == 2):
                    FIX_YAW(DES_POS4)
            elif(STATE == 1):
                if (DOOR1 + DOOR2 == 1):
                    GO(DES_POS3)
                elif (DOOR1 + DOOR2 == 2):
                    GO(DES_POS4)
            else:
                SECTION = 4
                STATE = 0

        # Cylinder Following Part
        elif(SECTION == 4):
            print("Rotating around Cylinder")
            print("Total Door count: " + str(DOOR1 + DOOR2))
            if (DOOR1 + DOOR2 == 1):
                print("Clockwise")

                if(Front > distance):
                    if(FRight < (distance / 2)):
                        print("Range: {:.2f}m - Too close. Backing up.".format(FRight))
                        command.angular.z = +0.5
                        command.linear.x = 0.25
                    elif(FRight >= (distance /2 )):
                        print("Range: {:.2f}m - Cylinder-rotation; turn right.".format(FRight))
                        command.angular.z = -0.4
                        command.linear.x = 0.3
                    else:
                        print("Range: {:.2f}m - Cylinder-rotation; turn left.".format(FRight))
                        command.angular.z = +0.4
                        command.linear.x = 0.3
                else:
                    print("Front obstacle detected. Turning away.")
                    command.angular.z = +1.0
                    command.linear.x = 0.0
                    CMD_PUB.publish(command)
                    while(Front < 0.3 and not rospy.is_shutdown()):
                        CMD_PUB.publish(command)
                CMD_PUB.publish(command)

            elif (DOOR1 + DOOR2 == 2):
                print("Counter-clockwise")

                if(Front > distance):
                    if(FLeft < (distance / 2)):
                        print("Range: {:.2f}m - Too close. Backing up.".format(FRight))
                        command.angular.z = -0.5
                        command.linear.x = 0.25
                    elif(FLeft >= (distance /2 )):
                        print("Range: {:.2f}m - Cylinder rotation; turn left.".format(FRight))
                        command.angular.z = +0.4
                        command.linear.x = 0.3
                    else:
                        print("Range: {:.2f}m - Cylinder rotation; turn right.".format(FRight))
                        command.angular.z = -0.4
                        command.linear.x = 0.3
                else:
                    print("Front obstacle detected. Turning away.")
                    command.angular.z = -1.0
                    command.linear.x = 0.0
                    CMD_PUB.publish(command)
                    while(Front < 0.3 and not rospy.is_shutdown()):
                        CMD_PUB.publish(command)
                CMD_PUB.publish(command)
                
            else:
                print("Error detecting doors")
                done_moving()

            if (DOOR1 + DOOR2 == 1):
                shallStop(DES_POS4)
            elif (DOOR1 + DOOR2 == 2):
                shallStop(DES_POS3)

        else:
            # Maze Solving Part
            while(near_wall == 0 and not rospy.is_shutdown()): #wall following 
                if(Front > distance and FRight > distance and FLeft > distance):
                    command.angular.z = -0.1
                    command.linear.x = 0.22
                elif(FLeft < distance):
                    near_wall = 1
                else:
                    command.angular.z = -0.25
                    command.linear.x = 0.0

                CMD_PUB.publish(command)
            else:
                if(Front > distance):
                    if(FRight < (distance / 2)):
                        print("Range: {:.2f}m - Too close. Backing up.".format(FRight))
                        command.angular.z = +1.2
                        command.linear.x = -0.1
                    elif(FRight > (distance * 0.75)):
                        print("Range: {:.2f}m - Wall-following; turn left.".format(FRight))
                        command.angular.z = -0.8
                        command.linear.x = 0.22
                    else:
                        print("Range: {:.2f}m - Wall-following; turn right.".format(FRight))
                        command.angular.z = +0.8
                        command.linear.x = 0.22
                elif (Front <= distance  and FLeft < Front):
                	print("Rotating right")
                	command.angular.z = -0.5
                	command.linear.x = 0.0
                else:
                    print("Front obstacle detected. Turning away.")
                    command.angular.z = +1.0
                    command.linear.x = 0.0
                    CMD_PUB.publish(command)
                    while(Front < 0.3 and not rospy.is_shutdown()):
                        CMD_PUB.publish(command)
                CMD_PUB.publish(command)
        if(math.isinf(Front) and math.isinf(FLeft) and not math.isinf(Right)):
            if(not SECTION == 2 and not SECTION == 3 and not SECTION == 4 and not SECTION == 5):
                SECTION = 1
        rate.sleep()
if __name__ == '__main__':
    MAIN()
