#!/usr/bin/env python3
import rospy
from std_msgs.msg import Int32  # Import Int32 message type

def detect_slits():
    rospy.init_node("slit_detection")
    
    # Example logic for detecting open slits (replace with your actual logic)
    open_slits = 3  # Placeholder value for detected slits

    # Log the information using string formatting
    rospy.loginfo("Open slits detected: {}".format(open_slits))

    # Simulate publishing the open slit count
    slit_count_publisher = rospy.Publisher('/open_slits', Int32, queue_size=10)  # Use Int32 here
    rate = rospy.Rate(1)  # 1 Hz rate
    while not rospy.is_shutdown():
        slit_count_publisher.publish(open_slits)
        rate.sleep()

if __name__ == "__main__":
    try:
        detect_slits()
    except rospy.ROSInterruptException:
        pass
