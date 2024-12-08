#!/usr/bin/env python3
import rospy
from std_msgs.msg import Int32  # Import Int32 message type

def select_path():
    rospy.init_node("path_selection")
    
    # Example logic for selecting a path (replace with your actual logic)
    slit_count = 3  # Placeholder value for selected path

    # Log the selected path
    rospy.loginfo("Selecting path: {}".format(slit_count))

    # Simulate publishing the selected path
    path_publisher = rospy.Publisher('/selected_path', Int32, queue_size=10)  # Use Int32 here
    rate = rospy.Rate(1)  # 1 Hz rate
    while not rospy.is_shutdown():
        path_publisher.publish(slit_count)
        rate.sleep()

if __name__ == "__main__":
    try:
        select_path()
    except rospy.ROSInterruptException:
        pass
