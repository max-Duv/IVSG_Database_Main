'''
FOR UBUNTU

If bagpy isn't imported:
    sudo apt install python3-virtualenv
    virtualenv -p python3 venv
    source ./venv/bin/activate
    pip install --extra-index-url https://rospypi.github.io/simple/ rospy rosbag
    pip install bagpy
    
    From: https://answers.ros.org/question/343260/install-of-the-rospyrosbag-python-libraries-standalone-not-on-ubuntu/

Can also try: sudo apt install python3-pip

Note: stay inside the virtual environment to run script, use 'deactivate' to exit.
'''

import bagpy
from bagpy import bagreader
import pandas as pd
import seaborn as sea
import matplotlib.pyplot as plt
import numpy as np
import time

def main():
    start_time = time.time()                    # Keep track of start time

    bag_file_name = 'test_parse.bag'           # Set bag file name
    #bag_file_name = 'mapping_van_2024-06-20-15-25-21_0.bag'
    b = bagreader(bag_file_name)                # Set a variable 'b' to the bag file using bagreader library
    #b.topic_table                              # Produce the table

    topic_lst = b.topic_table.Topics.unique()   # Create a list of the different topics
    for topic in topic_lst:
        data = b.message_by_topic(topic)        # For each topic, parse and write to CSV file
        print("File saved: {}".format(data))    # Inform user that file has been saved

    '''
    Note: After this loop is run, a new folder with the same name as the bag file will be created with a CSV file
    for each topic. If needed, rename this folder to be more specific. 
    ''' 

    end_time = time.time()
    total_time = end_time - start_time
    print("Total Time: ", total_time)           # Calculate total run time
        

main()