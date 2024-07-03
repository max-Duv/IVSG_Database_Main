#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
python 3.8

This script parse data in bagfile and then store them into PostgreSQL database.

Accepts a filename as an optional argument. Operates on all bagfiles in current directory if no argument provided

Written by Liming Gao at 2020 Feb. at IVSG

Edited by Wushuang Bai 2022 11 03

Supervised by Professor Sean Brennan

To do list:
1. (DONE) Make the insert of base_stations and vehicle just executes once.(done use conflict on)
2. (DONE - NEW) similar with setBaseStation, we need a setVehicle method,
3. add a class method in database to insert multiple rows data. and then modify sensors method, and try to select sensor id before parsing 
4. add position variance to parseGarminGP
5. it seems that the first line was missed when using bulk insert
6. (DONE) Check the source of adis imu data covariance,datasheet or? http://docs.ros.org/melodic/api/sensor_msgs/html/msg/Imu.html(done)
7. modify adis_code.cpp where covariacne bwt accelaration and angular velocity is reverse. 
8. (DONE) and put the parameters in /home/brennan/Documents/Liming/mapping_van_data/src/adis_16407/include/adis_16407/adis_structures.h
into adis_16407 parameters table.(done)
9. add parameters table for each sensor, store parameters including units, variances, and so on 
10. think about how to orginaize the topic with two sensors, eg, encoder and steering angle
11. (DONE) conflict on setBaseStation and vehicel id,and the repeat issue of trips
12. (DONE - NEW) add temperature, pressure and magnetic into adis_imu
13. for laser, change the text data type to array
14. improve the process when you re-parse the data. error capture in database.py bulk insert
15. debug the delete and reinsert part
16. fix correctTimeTrigger() method
17. (DONE) add parse function for encoder
18. (DONE) add parse function for trigger

Finished:
	 2. similar with setBaseStation, we need a setVehicle method
	12. add temperature, pressure and magnetic into adis_imu

To do:
	3. add a class method in database to insert multiple rows data. and then modify sensors method, and try to select sensor id before parsing 
	4. add position variance to parseGarminGP
	5. it seems that the first line was missed when using bulk insert
	7. modify adis_code.cpp where covariacne bwt accelaration and angular velocity is reverse. 
	9. add parameters table for each sensor, store parameters including units, variances, and so on 
	10. think about how to orginaize the topic with two sensors, eg, encoder and steering angle
	13. for laser, change the text data type to array
	14. improve the process when you re-parse the data. error capture in database.py bulk insert
	15. debug the delete and reinsert part
	16. fix correctTimeTrigger() method

To work on for improved runtime (check with Xinyu):
	 3. add a class method in database to insert multiple rows data. and then modify sensors method,
	    and try to select sensor id before parsing 
	 5. it seems that the first line was missed when using bulk insert
	10. think about how to orginaize the topic with two sensors, eg, encoder and steering angle
	14. improve the process when you re-parse the data. error capture in database.py bulk insert
	15. debug the delete and reinsert part
	16. fix correctTimeTrigger() method

USAGE:
	python Parse_and_insert.py /path/to/rawdata.bag
'''

import sys
import csv
import rosbag
import glob  # The glob module finds all the pathnames matching a specified pattern according to the rules used by the Unix shell, although results are returned in arbitrary order. No tilde expansion is done, but *, ?, and character ranges expressed with [] will be correctly matched.
# The errno module defines a number of symbolic error codes, such as ENOENT (“no such directory entry”) and EPERM (“permission denied”).
import errno
import cv2  # opencv
import numpy as np
import time
import datetime
import string
import os  # for operation system, such as file management make directory
import shutil  # for file and directory management, copy file
import hashlib
from database import Database
# from __future__ import print_function

class Parse:

	kind = 'canine'   # class variable shared by all instances

	__weight = 0  # 定义私有属性,私有属性在类外部无法直接进行访问

	def __init__(self, folder_name, db_name=None):

		# instance variable unique to each instance
		self.srid = 4326  # geographic coordinate system wgs 84

		if db_name is not None:
			# create the connection to the database
			self.db = Database(db_name=db_name)

		# create the folder for txt files
		self.folder_name = folder_name

		# NEW: Based off of fcn_DataClean_determineDataType
		self.make_sure_path_exists(self.folder_name + '/gps')
		self.make_sure_path_exists(self.folder_name + '/imu')
		self.make_sure_path_exists(self.folder_name + '/trigger')
		self.make_sure_path_exists(self.folder_name + '/encoder')
		self.make_sure_path_exists(self.folder_name + '/lidar2d')
		self.make_sure_path_exists(self.folder_name + '/lidar3d')
		self.make_sure_path_exists(self.folder_name + '/diagnostic')
		self.make_sure_path_exists(self.folder_name + '/ntrip')
		self.make_sure_path_exists(self.folder_name + '/rosout')
		self.make_sure_path_exists(self.folder_name + '/transform')
		self.make_sure_path_exists(self.folder_name + '/camera')
		self.make_sure_path_exists(self.folder_name + '/other')
		self.replace_all = False

		'''
		self.make_sure_path_exists(self.folder_name + '/gps')
		self.make_sure_path_exists(self.folder_name + '/imu')
		self.make_sure_path_exists(self.folder_name + '/laser')
		self.make_sure_path_exists(self.folder_name + '/images')
		self.make_sure_path_exists(self.folder_name + '/power_data')
		self.make_sure_path_exists(self.folder_name + '/wheel_encoder')
		self.make_sure_path_exists(self.folder_name + '/parseEncoder')
		self.make_sure_path_exists(self.folder_name + '/parseTrigger')
		self.replace_all = False
		'''

	'''
		============================= Method make_sure_path_exists() ====================================
		#	Method Purpose:
		#		check if the expected folder exists, if not create one
		#
		#	Input Variable:
		#		self, path
		#
		#	Output/Return:
		#		None
		#
		#	Algorithm:
				create a directory in path
		#
		# 	Restrictions/Notes:
		# 		None
		#
		# 	The follow methods are called:

		# 	Author: Liming Gao
		# 	Date: 02/05/2020
		#
		================================================================================

	'''

	def make_sure_path_exists(self, path):

		try:
			os.makedirs(path)
		except OSError as exception:
			pass
			print('This folder already exists:', path)
			if exception.errno != errno.EEXIST:
				raise  # stop the code
	'''
		============================= Method md5Image() ====================================
		#	Method Purpose:
		#		produce the md5 hash code for string
		#	Input Variable:
		#		img:
		#
		#	Output/Return:
		#		None
		#
		#	Algorithm:
				# initializing string
		str = "GeeksforGeeks"

		# encoding GeeksforGeeks using encode()
		# then sending to md5()
		result = hashlib.md5(str.encode())

		# printing the equivalent hexadecimal value.
		print("The hexadecimal equivalent of hash is : ", end ="")
		print(result.hexdigest())
		#
		# 	Restrictions/Notes:
		# 		None
		#
		# 	The follow methods are called:

		# 	Author: Liming Gao
		# 	Date: 02/05/2020
		#
		================================================================================
	'''

	def md5Image(self, img):

		# img.tostring()
		md5Image = hashlib.md5(img.tostring()).hexdigest()

		return md5Image

	'''
		============================= Method saveMD5Image() ====================================
		Method Purpose:
			save img into the folder with hash value filename as .jpg format
		Input Variable:
			img:

		Output/Return:
			None

		Algorithm:
			cv2.imwrite(filename, img[, params])
			cv2.imwrite('img_CV2_90.jpg', a, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
		Restrictions/Notes:
			None

		The follow methods are called:

		Author: Liming Gao
		Date: 02/05/2020

		================================================================================
	'''

	def saveMD5Image(self, img):

		md5_filename = self.md5Image(img)
		# create folder according to hash valus of img
		self.make_sure_path_exists(
			self.folder_name + '/images/' + md5_filename[0:2] + '/' + md5_filename[2:4] + '/')
		# create the file name using the hash value of img
		filename = self.folder_name + '/images/' + \
			md5_filename[0:2] + '/' + md5_filename[2:4] + \
			'/' + md5_filename + '.jpg'

		# from 0 to 100 (the higher is the better). Default value is 95.
		cv2.imwrite(filename, img, [int(cv2.IMWRITE_JPEG_QUALITY), 100])

		return md5_filename

	def rotateImage(self, img, angle):

		(h, w) = img.shape[:2]
		center = (w/2, h/2)

		M = cv2.retval = cv2.getRotationMatrix2D(center, angle, scale=1.0)
		# M = cv2.retval = cv2.getRotationMatrix2D((w/2, h/2), angle, scale=1.0)
		rotated = cv2.warpAffine(img, M, (w, h))

		return rotated


	def parseBagFileNameForDateTime(self, file_name):

		# file_name: mapping_van_2019-10-18-20-39-30_12.bag
		date_time = file_name.split('_')[2]
		date_time = date_time.split('-')
		date_time = '-'.join(date_time[0:3]) + ' ' + ':'.join(date_time[3:6])

		# date_time: 2019-10-18 20:39:30
		return date_time

	def parseBagFileNameForSplitFileIndex(self, file_name):

		# file_name: mapping_van_2019-10-18-20-39-30_12.bag
		split_file_index = file_name.split('_')[3]

		split_file_index = split_file_index.split('.')[0]

		return int(split_file_index)  # 12

	def unixTimeToTimeStamp(self, unix_time):

		return datetime.datetime.fromtimestamp(int(unix_time)).strftime('%Y-%m-%d %H:%M:%S')

		# input 0, output 1970-01-01 00:00:00

	'''
		a.How to Print Without Newline? python2, print is a statment, pyhton3 print is a function
			1. for python3, use end= 
				print("Hello World!", end = '')
				print("My name is Karim")
				# output:
				# Hello World!My name is Karim
			2. for python2, use a comma at the end of your print statement
				print "Hello World!",
				print "My name is Karim"
				# output
				# Hello World! My name is Karim

		b.Print iterations progress
		# http://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console/34325723#34325723
		# https://gist.github.com/aubricus/f91fb55dc6ba5557fbab06119420dd6a
	'''

	def printProgress(self, iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█'):
		"""
		Call in a loop to create terminal progress bar
		@params:
			iteration   - Required  : current iteration (Int)
			total       - Required  : total iterations (Int)
			prefix      - Optional  : prefix string (Str)
			suffix      - Optional  : suffix string (Str)
			decimals    - Optional  : positive number of decimals in percent complete (Int)
			length      - Optional  : character length of bar (Int)
			fill        - Optional  : bar fill character (Str)
		"""
		percent = ("{0:." + str(decimals) + "f}").format(100 *(iteration / float(total)))
		filledLength = int(length * iteration // total)
		bar = fill * filledLength + '-' * (length - filledLength)
		print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end='\r') # python 3
		# print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix),) # python 2

		# Print New Line on Complete
		if iteration == total:
			print()

	'''
		============================= Method correctTimeTrigger() ====================================
		#	Method Purpose:
		#
		#
		#	Input Variable:
		#		self, path
		#
		#	Output/Return:
		#		None
		#
		#	Algorithm:

		#
		# 	Restrictions/Notes:
		# 		None
		#
		# 	The follow methods are called:

		# 	Author: Liming Gao
		# 	Date: 02/05/2020
		#
		================================================================================

	'''

	def correctTimeTrigger(self, bag_file_ids, sensor_id, dt):

		where_bag_file_id = '('
		for (i, bag_file_id) in enumerate(bag_file_ids):

			if i != len(bag_file_ids) - 1:
				where_bag_file_id += 'bag_files_id=' + str(bag_file_id) + ' OR '
			else:
				where_bag_file_id += 'bag_files_id=' + str(bag_file_id)
		where_bag_file_id += ')'

		data, status = self.db.select(table='camera', fields=['id', 'seconds', 'nanoseconds'], where=[where_bag_file_id, 'sensors_id='+str(sensor_id)], orderby='seconds, nanoseconds')

		data = np.asarray(data, dtype=np.uint64)

		ids = data[:, 0]
		seconds = data[:, 1]
		nanoseconds = data[:, 2]

		unique_seconds = np.unique(seconds)

		frames_per_second = 1 / dt
		for t_ in unique_seconds:

			ind = np.argwhere(seconds == t_)
			desired_ind = np.arange(frames_per_second)

			# We did not collect the desired number of frames (frames dropped),
			# so we now need to figure out which frame dropped and adjust the times
			# accordingly.
			if len(ind) != frames_per_second:

				# Find the change in time between each frame and see if any of them
				# exceed 1.5 times the expected delta t. Shift by one because we
				# are looking at the diff in time.
				near_dropped_frame_inds = np.argwhere(
					np.diff(nanoseconds[ind], axis=0) > 1.5 * dt * 10 ** 9)[:, 0] + 1

				# If we have detected a dropped frame, we need to figure out which frame was missed.
				if len(near_dropped_frame_inds) != 0:

					number_of_dropped_frames = len(near_dropped_frame_inds)
					if number_of_dropped_frames == 1:
						print('1 dropped frame at ' + str(t_))
					else:
						print(str(number_of_dropped_frames) + ' dropped frames at ' + str(t_))

					desired_ind = np.delete(
						desired_ind, near_dropped_frame_inds)

				else:

					desired_ind = np.round(nanoseconds[ind] * 10 ** (-9) / dt)

			nanoseconds[ind] = desired_ind * (dt * 10 ** 9)

		# return seconds, nanoseconds
		q = 'UPDATE camera SET seconds_triggered = data_table.seconds_triggered, nanoseconds_triggered = data_table.nanoseconds_triggered '
		q += 'FROM ( SELECT unnest(array[' + \
			','.join(map(str, ids)) + ']) AS id, '
		q += 'unnest(array[' + ','.join(map(str, seconds)) + \
			']) AS seconds_triggered, '
		q += 'unnest(array[' + ','.join(map(str, nanoseconds)) + \
			']) AS nanoseconds_triggered) AS data_table '
		q += 'WHERE camera.id = data_table.id'

		_, status = self.db.query(query=q)
		self.db.conn.commit()

	'''
		============================= Method parseINS() ====================================
		#	Method Purpose:
		#		parse the NovAtel_gps data into txt file and inser them into database 
		#	
		#	Input Variable: 
		#		sensor_id			0
				bag_file_id 		return when insert bag data 
				bag_file           	bag = rosbag.Bag(bag_file_name)
				topic 				topic = '/INS' 		
				output_file_name 	output_file_name = folder_name + '/gps/' + bag_file_name.replace('.bag', '-INS.txt')
		# 	
		#	Output/Return: 
		#		None
		#
		#	Algorithm:  
				str() and repr() both are used to get a string representation of object. 
				But they have some difference: 
				today = 1571445783.475081288
				# Prints readable format for date-time object 
				print str(today) 
				# prints the official format of date-time object 
				print repr(today)	

				1571445783.48
				1571445783.4750813
		#
		# 	Restrictions/Notes:
		# 		1. file.write(str(np.deg2rad(90 - msg.Azimuth)))
				2. need to confirm that whether the order of table field in DB shoud be the same as insert file.
					I have confirmed that the order does not matter, if the fields are assigned
		#
		# 	The follow methods are called:
				self.printProgress

		# 	Author: Liming Gao
		# 	Date: 02/05/2020
		#
		================================================================================
	'''

	def parseINS(self, sensor_id, bag_file_id, bag_file, topic, output_file_name):

		file = open(output_file_name, "w")

		number_of_messages = bag_file.get_message_count(topic_filters=topic)

		count = 0  # row numbers

		for topic, msg, t in bag_file.read_messages(topics=[topic]):

			self.printProgress(count + 1, number_of_messages,
							   prefix='Progress:', suffix='Complete', decimals=1, length=50)

			time = repr(msg.header.stamp.secs +
						msg.header.stamp.nsecs * 10 ** (-9))
			
			# NEW: use a nested loop instead to speed things up and simplify code?
			# Many parse functions also start with sensor_id, bag_file_id, self.unixTimeToTimeStamp(msg.header.stamp.secs), 
			# msg.header.stamp.secs, msg.header.stamp.nsecs, and time -- create global variable so only have to type this once

			to_write = [sensor_id, bag_file_id, self.unixTimeToTimeStamp(msg.header.stamp.secs), 
			   msg.header.stamp.secs, msg.header.stamp.nsecs, time, msg.Status, msg.Latitude, msg.Longitude,
			   msg.Height, msg.East_Velocity, msg.North_Velocity, msg.Up_Velocity, np.deg2rad(msg.Roll), 
			   np.deg2rad(msg.Pitch), np.deg2rad(90 - msg.Azimuth), msg.GPS_Week, msg.Seconds]
			
			for item in to_write:
				file.write(str(item))
				file.write(',')

			'''
			file.write(str(sensor_id))
			file.write(',')
			file.write(str(bag_file_id))
			file.write(',')
			file.write(str(self.unixTimeToTimeStamp(msg.header.stamp.secs)))
			file.write(',')
			file.write(str(msg.header.stamp.secs))
			file.write(',')
			file.write(str(msg.header.stamp.nsecs))
			file.write(',')
			file.write(time)
			file.write(',')
			file.write(str(msg.Status))
			file.write(',')
			file.write(str(msg.Latitude))
			file.write(',')
			file.write(str(msg.Longitude))
			file.write(',')
			file.write(str(msg.Height))
			file.write(',')
			file.write(str(msg.East_Velocity))
			file.write(',')
			file.write(str(msg.North_Velocity))
			file.write(',')
			file.write(str(msg.Up_Velocity))
			file.write(',')
			file.write(str(np.deg2rad(msg.Roll)))
			file.write(',')
			file.write(str(np.deg2rad(msg.Pitch)))
			file.write(',')
			file.write(str(np.deg2rad(90 - msg.Azimuth)))
			file.write(',')
			file.write(str(msg.GPS_Week))
			file.write(',')
			file.write(str(msg.Seconds))
			'''

			file.write('\n')

			count += 1

		file.close()

		# then we insert them into database
		try:

			self.db.bulk_insert(table='novatel_gps', fields=['sensors_id', 'bag_files_id', 'timestamp', 'seconds', 'nanoseconds', 'time', 'status', 'latitude', 'longitude', 'altitude', 'east_velocity', 'north_velocity', 'up_velocity', 'roll', 'pitch', 'yaw', 'gps_week', 'gps_seconds'], file_name=output_file_name)
			print("Insert INS to database Successfully!")
		except:

			# Since the try failed above, we need to rollback the connection. If we don't do this, the NEXT query call (the one below)
			# will error saying it can't complete the query. Which will make you think it's the NEXT query, but it was really the last one...
			self.db.conn.rollback()

			if self.replace_all is False:

				user_input = input(
					'It looks like the novatel_gps data has already been added to the database. Would you like to overwrite the corresponding data? [y/n/a] ')

				if user_input == 'a':

					self.replace_all = True

			if self.replace_all is True or user_input == 'y':

				status = self.db.delete(table='novatel_gps', using=None, where=[
										'bag_files_id='+str(bag_file_id)])
				self.db.bulk_insert(table='novatel_gps', fields=['sensors_id', 'bag_files_id', 'timestamp', 'seconds', 'nanoseconds', 'time', 'status', 'latitude', 'longitude',
														 'altitude', 'east_velocity', 'north_velocity', 'up_velocity', 'roll', 'pitch', 'yaw', 'gps_week', 'gps_seconds'], file_name=output_file_name)

			else:

				return

	'''
		============================= Method parseGarminGPS() ====================================
		#	Method Purpose:
		#		parse the parseGarminGPS data into txt file and inser them into database 
		#	
		#	Input Variable: 
		#		sensor_id			8
				bag_file_id 		return when insert bag data 
				bag_file           	bag = rosbag.Bag(bag_file_name)
				topic 				topic = '/fix' 		
				output_file_name 	output_file_name = folder_name + '/gps/' + bag_file_name.replace('.bag', '-garmin-gps.txt')
		# 	
		#	Output/Return: 
		#		None
		#
		#	Algorithm:  
		#
		# 	Restrictions/Notes:
		# 		1. file.write(str(np.deg2rad(90 - msg.Azimuth)))
		#
		# 	The follow methods are called:
				self.printProgress

		# 	Author: Liming Gao
		# 	Date: 02/05/2020
		#
		================================================================================

	'''
	def parseGarminGPS(self, sensor_id, bag_file_id, bag_file, topic, output_file_name):	

		file = open(output_file_name, "w")

		number_of_messages = bag_file.get_message_count(topic_filters=topic)

		count = 0
		for topic, msg, t in bag_file.read_messages(topics=[topic]):

			self.printProgress(count + 1, number_of_messages, prefix='Progress:', suffix='Complete', decimals=1, length=50)

			time = repr(msg.header.stamp.secs + msg.header.stamp.nsecs * 10 ** (-9))

			#NEW: use a nested loop instead to speed things up and simplify code?
			to_write = [sensor_id, bag_file_id, self.unixTimeToTimeStamp(msg.header.stamp.secs), 
			   msg.header.stamp.secs, msg.header.stamp.nsecs, time, msg.status.status, 
			   msg.status.service, msg.latitude, msg.longitude, msg.altitude]
			
			for item in to_write:
				file.write(str(item))
				file.write(',')

			'''
			file.write(str(sensor_id))
			file.write(',')
			file.write(str(bag_file_id))
			file.write(',')
			file.write(str(self.unixTimeToTimeStamp(msg.header.stamp.secs)))
			file.write(',')
			file.write(str(msg.header.stamp.secs))
			file.write(',')
			file.write(str(msg.header.stamp.nsecs))
			file.write(',')
			file.write(time)
			file.write(',')
			file.write(str(msg.status.status))
			file.write(',')
			file.write(str(msg.status.service))
			file.write(',')
			file.write(str(msg.latitude))
			file.write(',')
			file.write(str(msg.longitude))
			file.write(',')
			file.write(str(msg.altitude))
			'''

			file.write('\n')

			count += 1

		file.close()

		try:
			self.db.bulk_insert(table='garmin_gps', fields=['sensors_id', 'bag_files_id', 'timestamp', 'seconds', 'nanoseconds', 'time', 'status','service', 'latitude', 'longitude', 'altitude'], file_name=output_file_name)
			#self.db.bulk_insertCopyfrom(table='garmin_gps', fields=['sensors_id', 'bag_files_id', 'timestamp', 'seconds', 'nanoseconds', 'time', 'status','service', 'latitude', 'longitude', 'altitude'], file_name=output_file_name)

			print ("Insert Garmin_gps to database Succseefully!")
		except:

			# Since the try failed above, we need to rollback the connection. If we don't do this, the NEXT query call (the one below)
			# will error saying it can't complete the query. Which will make you think it's the NEXT query, but it was really the last one...
			self.db.conn.rollback()

			if self.replace_all is False:

				user_input = input('It looks like the Garmin GPS data has already been added to the database. Would you like to overwrite the corresponding data? [y/n/a] ')

				if user_input == 'a':

					self.replace_all = True

			if self.replace_all is True or user_input == 'y':

				status = self.db.delete(table='garmin_gps', using=None, where=['bag_files_id='+str(bag_file_id)])
				self.db.bulk_insert(table='garmin_gps', fields=['sensors_id', 'bag_files_id', 'timestamp', 'seconds', 'nanoseconds', 'time', 'status', 'service','latitude', 'longitude', 'altitude'], file_name=output_file_name)

			else:

				return

		'''
		============================= Method parseGarminVelocity() ====================================
		#	Method Purpose:
		#		parse the parseGarminVelocity data into txt file and inser them into database
		#
		#	Input Variable:
		#		sensor_id			8
				bag_file_id 		return when insert bag data
				bag_file           	bag = rosbag.Bag(bag_file_name)
				topic 				topic = '/vel'
				output_file_name 	output_file_name = folder_name + '/gps/' + bag_file_name.replace('.bag', '-garmin-velocity.txt')
		#
		#	Output/Return:
		#		None
		#
		#	Algorithm:
		#
		# 	Restrictions/Notes:
		# 		1. file.write(str(np.deg2rad(90 - msg.Azimuth)))
		#
		# 	The follow methods are called:
				self.printProgress

		# 	Author: Liming Gao
		# 	Date: 02/05/2020
		#
		================================================================================

	'''
	def parseGarminVelocity(self, sensor_id, bag_file_id, bag_file, topic, output_file_name):

		file = open(output_file_name, "w")

		number_of_messages = bag_file.get_message_count(topic_filters=topic)

		count = 0
		for topic, msg, t in bag_file.read_messages(topics=[topic]):

			self.printProgress(count + 1, number_of_messages, prefix='Progress:', suffix='Complete', decimals=1, length=50)

			time = repr(msg.header.stamp.secs + msg.header.stamp.nsecs * 10 ** (-9))

			file.write(str(sensor_id))
			file.write(',')
			file.write(str(bag_file_id))
			file.write(',')
			file.write(str(self.unixTimeToTimeStamp(msg.header.stamp.secs)))
			file.write(',')
			file.write(str(msg.header.stamp.secs))
			file.write(',')
			file.write(str(msg.header.stamp.nsecs))
			file.write(',')
			file.write(time)
			file.write(',')
			file.write(str(msg.twist.linear.x))
			file.write(',')
			file.write(str(msg.twist.linear.y))
			file.write('\n')

			count += 1

		file.close()

		try:

			self.db.bulk_insert(table='garmin_velocity', fields=['sensors_id', 'bag_files_id', 'timestamp', 'seconds', 'nanoseconds', 'time', 'east_velocity', 'north_velocity'], file_name=output_file_name)
			print ("Insert garmin_velocity to database Succseefully!")
		except:

			# Since the try failed above, we need to rollback the connection. If we don't do this, the NEXT query call (the one below)
			# will error saying it can't complete the query. Which will make you think it's the NEXT query, but it was really the last one...
			self.db.conn.rollback()

			if self.replace_all is False:

				user_input = input('It looks like the Garmin Velocity data has already been added to the database. Would you like to overwrite the corresponding data? [y/n/a] ')

				if user_input == 'a':

					self.replace_all = True

			if self.replace_all is True or user_input == 'y':

				status = self.db.delete(table='garmin_velocity', using=None, where=['bag_files_id='+str(bag_file_id)])
				self.db.bulk_insert(table='garmin_velocity', fields=['sensors_id', 'bag_files_id', 'timestamp', 'seconds', 'nanoseconds', 'time', 'east_velocity', 'north_velocity'], file_name=output_file_name)

			else:

				return


	'''
		============================= Method parseHemisphereGPS() ====================================
		#	Method Purpose:
		#		parse the HemisphereGPS data into txt file and inser them into database
		#
		#	Input Variable:
		#		sensor_id			9
				bag_file_id 		return when insert bag data
				bag_file           	bag = rosbag.Bag(bag_file_name)
				topic 				topic = '/Bin1'
				output_file_name 	output_file_name = folder_name + '/gps/' + bag_file_name.replace('.bag', '-Hemisphere-GPS.txt')
		#
		#	Output/Return:
		#		None
		#
		#	Algorithm:
				str() and repr() both are used to get a string representation of object.
				But they have some difference:
				today = 1571445783.475081288
				# Prints readable format for date-time object
				print str(today)
				# prints the official format of date-time object
				print repr(today)

				1571445783.48
				1571445783.4750813
		#
		# 	Restrictions/Notes:
		# 		1. file.write(str(np.deg2rad(90 - msg.Azimuth)))
				2. need to confirm that whether the order of table field in DB shoud be the same as insert file.
					I have confirmed that the order does not matter, if the fields are assigned
		#
		# 	The follow methods are called:
				self.printProgress

		# 	Author: Liming Gao
		# 	Date: 02/05/2020
		#
		================================================================================
	'''

	def parseHemisphereGPS(self, sensor_id, bag_file_id, bag_file, topic, output_file_name):

		file = open(output_file_name, "w")

		number_of_messages = bag_file.get_message_count(topic_filters=topic)

		count = 0  # row numbers

		for topic, msg, t in bag_file.read_messages(topics=[topic]):

			self.printProgress(count + 1, number_of_messages,
							   prefix='Progress:', suffix='Complete', decimals=1, length=50)

			time = repr(msg.header.stamp.secs +
						msg.header.stamp.nsecs * 10 ** (-9))
			
			file.write(str(sensor_id))
			file.write(',')
			file.write(str(bag_file_id))
			file.write(',')
			file.write(str(self.unixTimeToTimeStamp(msg.header.stamp.secs)))
			file.write(',')
			file.write(str(msg.header.stamp.secs))
			file.write(',')
			file.write(str(msg.header.stamp.nsecs))
			file.write(',')
			file.write(time)
			file.write(',')
			file.write(str(msg.AgeOfDiff))
			file.write(',')
			file.write(str(msg.NumOfSats))
			file.write(',')
			file.write(str(msg.GPSWeek))
			file.write(',')
			file.write(str(msg.GPSTimeOfWeek))
			file.write(',')
			file.write(str(msg.Latitude))
			file.write(',')
			file.write(str(msg.Longitude))
			file.write(',')
			file.write(str(msg.Height))
			file.write(',')
			file.write(str(msg.VNorth))
			file.write(',')
			file.write(str(msg.VEast))
			file.write(',')
			file.write(str(msg.VUp))
			file.write(',')
			file.write(str(msg.StdDevResid))
			file.write(',')
			file.write(str(msg.NavMode))
			file.write(',')
			file.write(str(msg.ManualMark))
			file.write(',')
			file.write(str(msg.ExtendedAgeOfDiff))
			file.write('\n')

			count += 1

		file.close()

		# then we insert them into database
		try:

			self.db.bulk_insert(table='hemisphere_gps', fields=['sensors_id', 'bag_files_id', 'timestamp', 'seconds', 'nanoseconds', 'time', 'ageofdiff', 'numofsats', 'gps_week', 'gps_seconds', 'latitude', 'longitude', 'altitude', 'vnorth', 'veast', 'vup', 'stddevresid', 'navmode', 'manualmark', 'extendedageofdiff'], file_name=output_file_name)
			print("Insert Hemisphere to database Successfully!")
		except:

			# Since the try failed above, we need to rollback the connection. If we don't do this, the NEXT query call (the one below)
			# will error saying it can't complete the query. Which will make you think it's the NEXT query, but it was really the last one...
			self.db.conn.rollback()

			if self.replace_all is False:

				user_input = input(
					'It looks like the Hemisphere gps data has already been added to the database. Would you like to overwrite the corresponding data? [y/n/a] ')

				if user_input == 'a':

					self.replace_all = True

			if self.replace_all is True or user_input == 'y':

				status = self.db.delete(table='hemisphere_gps', using=None, where=['bag_files_id='+str(bag_file_id)])
				self.db.bulk_insert(table='hemisphere_gps', fields=['sensors_id', 'bag_files_id', 'timestamp', 'seconds', 'nanoseconds', 'time', 'ageofdiff', 'numofsats', 'gps_week', 'gps_seconds', 'latitude', 'longitude', 'altitude', 'vnorth', 'veast', 'vup', 'stddevresid', 'navmode', 'manualmark', 'extendedageofdiff'], file_name=output_file_name)

			else:

				return

	'''
		============================= Method parseNovatelIMU() ====================================
		#	Method Purpose:
		#		parse the parseNovatelIMU data into txt file and inser them into database
		#
		#	Input Variable:
		#		sensor_id			1
				bag_file_id 		return when insert bag data
				bag_file           	bag = rosbag.Bag(bag_file_name)
				topic 				topic = '/IMU'
				output_file_name 	output_file_name = folder_name + '/imu/' + bag_file_name.replace('.bag', '-NovAtel-IMU.txt')
		#
		#	Output/Return:
		#		None
		#
		#	Algorithm:
		#
		# 	Restrictions/Notes:
		#
		# 	The follow methods are called:
				self.printProgress

		# 	Author: Liming Gao
		# 	Date: 02/05/2020
		#
		================================================================================

	'''
	def parseNovatelIMU(self, sensor_id, bag_file_id, bag_file, topic, output_file_name):

		file = open(output_file_name, "w")

		number_of_messages = bag_file.get_message_count(topic_filters=topic)

		count = 0
		for topic, msg, t in bag_file.read_messages(topics=[topic]):

			self.printProgress(count + 1, number_of_messages, prefix='Progress:', suffix='Complete', decimals=1, length=50)

			time = repr(msg.header.stamp.secs + msg.header.stamp.nsecs * 10 ** (-9))

			file.write(str(sensor_id))
			file.write(',')
			file.write(str(bag_file_id))
			file.write(',')
			file.write(str(self.unixTimeToTimeStamp(msg.header.stamp.secs)))
			file.write(',')
			file.write(str(msg.header.stamp.secs))
			file.write(',')
			file.write(str(msg.header.stamp.nsecs))
			file.write(',')
			file.write(time)
			file.write(',')
			file.write(str(msg.IMU_Status))
			file.write(',')
			file.write(str(msg.X_Accel))
			file.write(',')
			file.write(str(msg.Y_Accel))
			file.write(',')
			file.write(str(msg.Z_Accel))
			file.write(',')
			file.write(str(msg.X_Gyro))
			file.write(',')
			file.write(str(msg.Y_Gyro))
			file.write(',')
			file.write(str(msg.Z_Gyro))
			file.write(',')
			file.write(str(msg.GPS_Week))
			file.write(',')
			file.write(str(msg.Seconds))
			file.write('\n')

			count += 1

		file.close()

		try:

			self.db.bulk_insert(table='novatel_imu', fields=['sensors_id', 'bag_files_id', 'timestamp', 'seconds', 'nanoseconds', 'time', 'status', 'x_acceleration', 'y_acceleration', 'z_acceleration', 'x_angular_velocity', 'y_angular_velocity', 'z_angular_velocity', 'gps_week', 'gps_seconds'], file_name=output_file_name)
			print ("Insert Novatel IMU into database successfully!")
		except:

			# Since the try failed above, we need to rollback the connection. If we don't do this, the NEXT query call (the one below)
			# will error saying it can't complete the query. Which will make you think it's the NEXT query, but it was really the last one...
			self.db.conn.rollback()

			if self.replace_all is False:

				user_input = input('It looks like the Novatel IMU data has already been added to the database. Would you like to overwrite the corresponding data? [y/n/a] ')

				if user_input == 'a':

					self.replace_all = True

			if self.replace_all is True or user_input == 'y':

				status = self.db.delete(table='novatel_imu', using=None, where=['bag_files_id='+str(bag_file_id)])
				self.db.bulk_insert(table='novatel_imu', fields=['sensors_id', 'bag_files_id', 'timestamp', 'seconds', 'nanoseconds', 'time', 'status', 'x_acceleration', 'y_acceleration', 'z_acceleration', 'x_angular_velocity', 'y_angular_velocity', 'z_angular_velocity', 'gps_week', 'gps_seconds'], file_name=output_file_name)

			else:

				return
	'''
		============================= Method parseAdisIMU() ====================================
		#	Method Purpose:
		#		parse the parseAdisIMU data into txt file and inser them into database
		#
		#	Input Variable:
		#		sensor_id			10
				bag_file_id 		return when insert bag data
				bag_file           	bag = rosbag.Bag(bag_file_name)
				topic 				topic = '/imu/data'
				output_file_name 	folder_name + '/imu/' + bag_file_name.replace('.bag', '-Adis-IMU.txt')
		#
		#	Output/Return:
		#		None
		#
		#	Algorithm:
		#
		# 	Restrictions/Notes:
		#
		# 	The follow methods are called:
				self.printProgress
		#
		# 	Author: Liming Gao
		# 	Date: 02/05/2020
		#
		================================================================================

	'''
	def parseAdisIMU(self, sensor_id, bag_file_id, bag_file, topic, output_file_name):

		file = open(output_file_name, "w")

		number_of_messages = bag_file.get_message_count(topic_filters=topic)

		count = 0
		for topic, msg, t in bag_file.read_messages(topics=[topic]):

			self.printProgress(count + 1, number_of_messages, prefix='Progress:', suffix='Complete', decimals=1, length=50)

			time = repr(msg.header.stamp.secs + msg.header.stamp.nsecs * 10 ** (-9))

			file.write(str(sensor_id))
			file.write(',')
			file.write(str(bag_file_id))
			file.write(',')
			file.write(str(self.unixTimeToTimeStamp(msg.header.stamp.secs)))
			file.write(',')
			file.write(str(msg.header.stamp.secs))
			file.write(',')
			file.write(str(msg.header.stamp.nsecs))
			file.write(',')
			file.write(time)
			file.write(',')
			file.write(str(msg.linear_acceleration.x))
			file.write(',')
			file.write(str(msg.linear_acceleration.y))
			file.write(',')
			file.write(str(msg.linear_acceleration.z))
			file.write(',')
			file.write(str(msg.angular_velocity.x))
			file.write(',')
			file.write(str(msg.angular_velocity.y))
			file.write(',')
			file.write(str(msg.angular_velocity.z))
			file.write('\n')

			count += 1

		file.close()
		#parameters in /home/brennan/Documents/Liming/mapping_van_data/src/adis_16407/include/adis_16407/adis_structures.h
		self.db.insert(table='adis16407_parameters', fields=['sensors_id', 'accel_scale', 'gyro_scale', 'mag_scale', 'bar_scale', 'temp_scale',
															 'gravity','accel_cov','gyro_cov','mag_cov','bar_cov'],
													 values=[sensor_id, '0.03269673 m/s^2', '0.05', '0.00000005', '8', '0.136',
													 		'9.80665','0.0077898','0.64','0.000000000000013225','7.29'],
													 upsert=True,
													 conflict_on=['sensors_id', 'accel_scale', 'gyro_scale', 'mag_scale', 'bar_scale', 'temp_scale',
															 'gravity','accel_cov','gyro_cov','mag_cov','bar_cov'])

		try:

			#add temperature, pressure and magnetic into adis_imu
			self.db.bulk_insert(table='adis_imu', fields=['sensors_id', 'bag_files_id', 'timestamp', 'seconds', 'nanoseconds', 'time',
														  'x_acceleration', 'y_acceleration', 'z_acceleration', 'x_angular_velocity', 'y_angular_velocity', 'z_angular_velocity',
														  'temperature', 'pressure', 'magnetic_x', 'magnetic_y', 'magnetic_z'], file_name=output_file_name)
			print ("Insert Adis IMU into database successfully!")
		except:

			# Since the try failed above, we need to rollback the connection. If we don't do this, the NEXT query call (the one below)
			# will error saying it can't complete the query. Which will make you think it's the NEXT query, but it was really the last one...
			self.db.conn.rollback()

			if self.replace_all is False:

				user_input = input('It looks like the Adis IMU data has already been added to the database. Would you like to overwrite the corresponding data? [y/n/a] ')

				if user_input == 'a':

					self.replace_all = True

			if self.replace_all is True or user_input == 'y':

				status = self.db.delete(table='adis_imu', using=None, where=['bag_files_id='+str(bag_file_id)])
				self.db.bulk_insert(table='adis_imu', fields=['sensors_id', 'bag_files_id', 'timestamp', 'seconds', 'nanoseconds', 'time',
														  'x_acceleration', 'y_acceleration', 'z_acceleration', 'x_angular_velocity', 'y_angular_velocity', 'z_angular_velocity',
														  'temperature', 'pressure', 'magnetic_x', 'magnetic_y', 'magnetic_z'], file_name=output_file_name)

			else:

				return

	'''
		============================= Method parseEncoder() ====================================
		#	Method Purpose:
		#		parse the parseEncoder data into txt file and insert them into database
		#
		#	Input Variable:
		#		sensor_id_left		6
				bag_file_id 		return when insert bag data
				bag_file           	bag = rosbag.Bag(bag_file_name)
				topic 				topic = '/raw_encoder'
				output_file_name    folder_name + '/wheel_encoder/' + bag_file_name.replace('.bag', '-encoder.txt')

		#	Output/Return:
		#		None
		#
		#	Algorithm:

		# 	Restrictions/Notes:
		#
		#
		# 	The follow methods are called:
				self.printProgress

		# 	Author: Liming Gao
		# 	Date: 03/17/2020
		#
		================================================================================

	'''
	def parseEncoder(self,trip_id, sensor_id, bag_file_id, bag_file, topic, output_file_name):
		file = open(output_file_name, "w")

		number_of_messages = bag_file.get_message_count(topic_filters=topic)

		count = 0
		for topic, msg, t in bag_file.read_messages(topics=[topic]):

			self.printProgress(count + 1, number_of_messages, prefix='Progress:', suffix='Complete', decimals=1, length=50)

			time = repr(msg.header.stamp.secs + msg.header.stamp.nsecs * 10 ** (-9))

			file.write(str(sensor_id))
			file.write(',')
			file.write(str(bag_file_id))
			file.write(',')
			file.write(str(self.unixTimeToTimeStamp(msg.header.stamp.secs)))
			file.write(',')
			file.write(str(msg.header.stamp.secs))
			file.write(',')
			file.write(str(msg.header.stamp.nsecs))
			file.write(',')
			file.write(time)
			file.write(',')
			file.write(str(10000))
			file.write(',')
			file.write(str(msg.counts[0]))
			file.write(',')
			file.write(str(msg.counts[1]))
			file.write(',')
			file.write(str(msg.delta_counts[0]))  # type(msg.counts) is tuple
			file.write(',')
			file.write(str(msg.delta_counts[1]))
			file.write(',')
			file.write(str(msg.angular_velocity[0]))
			file.write(',')
			file.write(str(msg.angular_velocity[1]))
			file.write('\n')

			count += 1

		file.close()

		# encoder parameters
		self.db.insert(table='encoder_parameters', fields=['sensors_id', 'counts_per_revolution'],
													 values=[sensor_id, '10000'],
													 upsert=True,
													 conflict_on=['sensors_id', 'counts_per_revolution'])

		try:

			self.db.bulk_insert(table='encoder', fields=['sensors_id', 'bag_files_id', 'timestamp', 'seconds', 'nanoseconds', 'time',
															 'revolutions', 'left_counts', 'right_counts', 'left_delta_counts', 'right_delta_counts', 'left_angular_velocity',
															 'right_angular_velocity'], file_name=output_file_name)
			print ("Insert encoder into database successfully!")
		except:

			# Since the try failed above, we need to rollback the connection. If we don't do this, the NEXT query call (the one below)
			# will error saying it can't complete the query. Which will make you think it's the NEXT query, but it was really the last one...
			self.db.conn.rollback()

			if self.replace_all is False:

				user_input = input('It looks like the encoder data has already been added to the database. Would you like to overwrite the corresponding data? [y/n/a] ')

				if user_input == 'a':

					self.replace_all = True

			if self.replace_all is True or user_input == 'y':

				status = self.db.delete(table='encoder', using=None, where=['bag_files_id='+str(bag_file_id)])
				self.db.bulk_insert(table='encoder', fields=['sensors_id', 'bag_files_id', 'timestamp', 'seconds', 'nanoseconds', 'time',
															 'revolutions', 'left_counts', 'right_counts', 'left_delta_counts', 'right_delta_counts', 'left_angular_velocity',
															 'right_angular_velocity'], file_name=output_file_name)
			else:

				return

	'''
		============================= Method parseSteeringAngle() ====================================
		#	Method Purpose:
		#		parse the SteeringAngle data into txt file and insert them into database
		#
		#	Input Variable:
		#		sensors_id_SteerAngle_left			14
				bag_file_id 		return when insert bag data
				bag_file           	bag = rosbag.Bag(bag_file_name)
				topic 				'/steering_angle'
				output_file_name    folder_name + '/wheel_encoder/' + bag_file_name.replace('.bag', '-steering-angle.txt')

		#	Output/Return:
		#		None
		#
		#	Algorithm:

		# 	Restrictions/Notes:
		#
		#
		# 	The follow methods are called:
				self.printProgress

		# 	Author: Liming Gao
		# 	Date: 03/17/2020
		#
		================================================================================

	'''
	def parseSteeringAngle(self,trip_id, sensor_id, bag_file_id, bag_file, topic, output_file_name):
		file = open(output_file_name, "w")

		number_of_messages = bag_file.get_message_count(topic_filters=topic)

		count = 0
		for topic, msg, t in bag_file.read_messages(topics=[topic]):

			self.printProgress(count + 1, number_of_messages, prefix='Progress:', suffix='Complete', decimals=1, length=50)

			time = repr(msg.header.stamp.secs + msg.header.stamp.nsecs * 10 ** (-9))

			file.write(str(sensor_id))
			file.write(',')
			file.write(str(bag_file_id))
			file.write(',')
			file.write(str(self.unixTimeToTimeStamp(msg.header.stamp.secs)))
			file.write(',')
			file.write(str(msg.header.stamp.secs))
			file.write(',')
			file.write(str(msg.header.stamp.nsecs))
			file.write(',')
			file.write(time)
			file.write(',')
			file.write(str(msg.left_counts))
			file.write(',')
			file.write(str(msg.right_counts))
			file.write(',')
			file.write(str(msg.left_counts_filtered))
			file.write(',')
			file.write(str(msg.right_counts_filtered))
			file.write(',')
			file.write(str(msg.left_angle))
			file.write(',')
			file.write(str(msg.right_angle))
			file.write(',')
			file.write(str(msg.angle))
			file.write('\n')

			count += 1

		file.close()

		try:

			self.db.bulk_insert(table='steering_angle', fields=['sensors_id', 'bag_files_id', 'timestamp', 'seconds', 'nanoseconds', 'time',
															'left_counts', 'right_counts', 'left_counts_filtered', 'right_counts_filtered', 'left_angle', 'right_angle',
															'angle'], file_name=output_file_name)
			print ("Insert steering angle into database successfully!")
		except:

			# Since the try failed above, we need to rollback the connection. If we don't do this, the NEXT query call (the one below)
			# will error saying it can't complete the query. Which will make you think it's the NEXT query, but it was really the last one...
			self.db.conn.rollback()

			if self.replace_all is False:

				user_input = input('It looks like the steering angle data has already been added to the database. Would you like to overwrite the corresponding data? [y/n/a] ')

				if user_input == 'a':

					self.replace_all = True

			if self.replace_all is True or user_input == 'y':

				status = self.db.delete(table='steering_angle', using=None, where=['bag_files_id='+str(bag_file_id)])
				self.db.bulk_insert(table='steering_angle', fields=['sensors_id', 'bag_files_id', 'timestamp', 'seconds', 'nanoseconds', 'time',
															'left_counts', 'right_counts', 'left_counts_filtered', 'right_counts_filtered', 'left_angle', 'right_angle',
															'angle'], file_name=output_file_name)
			else:

				return


	'''
		============================= Method parseLaser() ====================================
		#	Method Purpose:
		#		parse the parseLaser data into txt file and insert them into database
		#
		#	Input Variable:
		#		sensors_id			2
				bag_file_id 		return when insert bag data
				bag_file           	bag = rosbag.Bag(bag_file_name)
				topic 				'/sick_lms500/scan'
				output_file_name    folder_name + '/laser/' + bag_file_name.replace('.bag', '-laser.txt')
		#	Output/Return:
		#		None
		#
		#	Algorithm:

		# 	Restrictions/Notes:
		#
		# 	The follow methods are called:
				self.printProgress
		# 	Author: Liming Gao
		# 	Date: 03/17/2020
		#
		================================================================================
	'''

	def parseLaser(self, trip_id, sensor_id, bag_file_id, bag_file, topic, output_file_name):

		file = open(output_file_name, "w")

		number_of_messages = bag_file.get_message_count(topic_filters=topic)

		count = 0
		for topic, msg, t in bag_file.read_messages(topics=[topic]):

			self.printProgress(count + 1, number_of_messages, prefix='Progress:', suffix='Complete', decimals=1, length=50)

			angle_min = msg.angle_min
			angle_max = msg.angle_max
			angle_increment = msg.angle_increment
			time_increment = msg.time_increment
			range_min = msg.range_min
			range_max = msg.range_max

			time = repr(msg.header.stamp.secs + msg.header.stamp.nsecs * 10 ** (-9))

			file.write(str(sensor_id))
			file.write(',')
			file.write(str(bag_file_id))
			file.write(',')
			file.write(str(self.unixTimeToTimeStamp(msg.header.stamp.secs)))
			file.write(',')
			file.write(str(msg.header.stamp.secs))
			file.write(',')
			file.write(str(msg.header.stamp.nsecs))
			file.write(',')
			file.write(time)
			file.write(',')
			file.write(str(msg.scan_time))
			file.write(',')
			# file.write('"' + ' '.join(map(str, msg.ranges)) + '"')  # This removes the leading and lagging parentheses from this message
			# file.write(',')
			# file.write('"' + ' '.join(map(str, msg.intensities)) + '"')  # This removes the leading and lagging parentheses from this message
			file.write(' '.join(map(str, msg.ranges)))  # This join the element in msg.ranges tuple
			file.write(',')
			file.write(' '.join(map(str, msg.intensities)))  # This removes the leading and lagging parentheses from this message
			file.write('\n')

			count += 1

		file.close()

		self.db.insert(table='laser_parameters', fields=['sensors_id', 'angle_min', 'angle_max', 'angle_increment', 'time_increment', 'range_min', 'range_max'],
			values=[sensor_id, angle_min, angle_max, angle_increment, time_increment, range_min, range_max],
			upsert=False,
			conflict_on=['sensors_id', 'angle_min', 'angle_max', 'angle_increment', 'time_increment', 'range_min', 'range_max'])

		try:

			self.db.bulk_insert(table='laser', fields=['sensors_id', 'bag_files_id', 'timestamp', 'seconds', 'nanoseconds', 'time', 'scan_time', 'ranges', 'intensities'], file_name=output_file_name)
			print ("Insert steering angle into database successfully!")
		except:

			# Since the try failed above, we need to rollback the connection. If we don't do this, the NEXT query call (the one below)
			# will error saying it can't complete the query. Which will make you think it's the NEXT query, but it was really the last one...
			self.db.conn.rollback()

			if self.replace_all is False:

				user_input = input('It looks like the LASER data has already been added to the database. Would you like to overwrite the corresponding data? [y/n/a] ')

				if user_input == 'a':

					self.replace_all = True

			if self.replace_all is True or user_input == 'y':

				status = self.db.delete(table='laser', using=None, where=['bag_files_id='+str(bag_file_id)])
				self.db.bulk_insert(table='laser', fields=['sensors_id', 'bag_files_id', 'timestamp', 'seconds', 'nanoseconds', 'time', 'scan_time', 'ranges', 'intensities'], file_name=output_file_name)

			else:

				return


	'''
		============================= Method parseCamera() ====================================
		#	Method Purpose:
		#		parse the Camera data into txt file and inser them into database 
		#
		#	Input Variable:
		#		sensor_id			3,4,5
		#		bag_file_id 		return when insert bag data
		#		bag_file           	bag = rosbag.Bag(bag_file_name)
		# 		camera_info_topic	camera_info_topic = '/front_center_camera/camera_info'
		# 		image_topic			image_topic = '/front_center_camera/image_rect_color/compressed'
		# 		output_file_name_images 	output_file_name_images = folder_name + '/images/' + bag_file_name.replace('.bag', '-front_center_camera-header.txt')
		# 		output_file_name_camera_info	output_file_name_camera_info = folder_name + '/images/' + bag_file_name.replace('.bag', '-front_center_camera-info.txt')
		#
		#
		#	Output/Return:
		#		None
		#
		#	Algorithm:
		#
		#
		# 	Restrictions/Notes:
		#
		#
		# 	The follow methods are called:
		#		self.printProgress
		#
		# 	Author: Liming Gao
		# 	Date: 02/05/2020
		#
		================================================================================

	'''

	def parseCamera(self, trip_id, sensor_id, bag_file_id, bag_file, image_topic, camera_info_topic, output_file_name_images, output_file_name_camera_info, rotate=False, angle=0):

		file = open(output_file_name_camera_info, "w")

		count = 0
		for topic, msg, t in bag_file.read_messages(topics=[camera_info_topic]):

			if count == 0:
				file.write(str(msg.width))
				file.write(',')
				file.write(str(msg.height))
				file.write(',')
				file.write(', '.join(map(str, msg.K)))  # This removes the leading and lagging parentheses from this message
				file.write(',')
				file.write(', '.join(map(str, msg.D)))  # This removes the leading and lagging parentheses from this message
				file.write('\n')

				break

				# K_left = np.array(msg.K).reshape((3, 3))
				# D_left = np.array(msg.D)
			count += 1

		file.close()
		#values=[bag_file_id,sensor_id, msg.K[0], msg.K[4], msg.K[2], msg.K[5], msg.K[1], msg.width, msg.height, msg.D[0], msg.D[1], msg.D[2], msg.D[3], msg.D[4]]
		self.db.insert(table='camera_parameters', fields=['bag_files_id','sensors_id', 'focal_x', 'focal_y', 'center_x', 'center_y', 'skew', 'image_width', 'image_height', 'distortion_k1', 'distortion_k2', 'distortion_p1', 'distortion_p2', 'distortion_k3'],
					values=(bag_file_id,sensor_id, msg.K[0], msg.K[4], msg.K[2], msg.K[5], msg.K[1], msg.width, msg.height, msg.D[0], msg.D[1], msg.D[2], msg.D[3], msg.D[4]),
								upsert=True,conflict_on=['bag_files_id','sensors_id', 'focal_x', 'focal_y', 'center_x', 'center_y', 'skew', 'image_width', 'image_height', 'distortion_k1', 'distortion_k2', 'distortion_p1', 'distortion_p2', 'distortion_k3'])
		print ("Insert front_center camera parameters into database successfully!")

		file = open(output_file_name_images, "w")

		number_of_messages = bag_file.get_message_count(topic_filters=image_topic)

		count = 0
		for topic, msg, t in bag_file.read_messages(topics=[image_topic]):
			# This must be used for compressed images. CvBridge does not
			# support compressed images.
			# http://wiki.ros.org/rospy_tutorials/Tutorials/WritingImagePublisherSubscriber
			np_arr = np.fromstring(msg.data, np.uint8)
			img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

			if rotate is True:
				img = self.rotateImage(img, angle)

			# This can be used for raw images, but not for compressed. CvBridge
			# does not support compressed images.
			# https://gist.github.com/wngreene/835cda68ddd9c5416defce876a4d7dd9
			# try:
			# 	img = self.bridge.imgmsg_to_cv2(msg)
			# except CvBridgeError, e:
			# 	print e

			# img = cv2.undistort(img,K_left,D_left)

			md5_filename = self.saveMD5Image(img)

			# print 'Saving image from ' + topic + ': ' + str(count + 1)

			self.printProgress(count + 1, number_of_messages, prefix='Progress:', suffix='Complete', decimals=1, length=50)

			time = repr(msg.header.stamp.secs + msg.header.stamp.nsecs * 10 ** (-9))

			file.write(str(sensor_id))
			file.write(',')
			file.write(str(bag_file_id))
			file.write(',')
			file.write(str(self.unixTimeToTimeStamp(msg.header.stamp.secs)))
			file.write(',')
			file.write(str(msg.header.stamp.secs))
			file.write(',')
			file.write(str(msg.header.stamp.nsecs))
			file.write(',')
			file.write(time)
			file.write(',')
			file.write(str(md5_filename))
			file.write('\n')

			count += 1

		file.close()

		try:

			self.db.bulk_insert(table='camera', fields=['sensors_id', 'bag_files_id', 'timestamp', 'seconds', 'nanoseconds', 'time', 'file_name'], file_name=output_file_name_images)
			print ("Insert front_center camera into database successfully!")
		except:

			# Since the try failed above, we need to rollback the connection. If we don't do this, the NEXT query call (the one below)
			# will error saying it can't complete the query. Which will make you think it's the NEXT query, but it was really the last one...
			self.db.conn.rollback()

			if self.replace_all is False:

				user_input = input('It looks like the front_center CAMERA data has already been added to the database. Would you like to overwrite the corresponding data? [y/n/a] ')

				if user_input == 'a':

					self.replace_all = True

			if self.replace_all is True or user_input == 'y':

				status = self.db.delete(table='camera', using=None, where=['bag_files_id='+str(bag_file_id)])
				self.db.bulk_insert(table='camera', fields=['sensors_id', 'bag_files_id', 'timestamp', 'seconds', 'nanoseconds', 'time', 'file_name'], file_name=output_file_name_images)

			else:

				return
#####################################################
# Added after rebuilding mapping van
#####################################################

	'''
		============================= Method parseEncoderNew() ====================================
		#	Method Purpose:
		#		parse the new encoder data into txt file and inser them into database
		#
		#	Input Variable:
		#		sensor_id			1
				bag_file_id 		return when insert bag data
				bag_file           	bag = rosbag.Bag(bag_file_name)
				topic 				topic = '/parseEncoder'
				output_file_name 	output_file_name = folder_name + '/parseEncoder/' + bag_file_name.replace('.bag', '-encoder-new.txt')
		#
		#	Output/Return:
		#		None
		#
		#	Algorithm:
		#
		# 	Restrictions/Notes:
		#
		# 	The follow methods are called:
				self.printProgress

		# 	Author: Wushuang Bai
		# 	Date: 03/11/2022
		#
		================================================================================

	'''
	def parseEncoderNew(self, sensor_id, bag_file_id, bag_file, topic, output_file_name):

		file = open(output_file_name, "w")

		number_of_messages = bag_file.get_message_count(topic_filters=topic)

		count = 0
		for topic, msg, t in bag_file.read_messages(topics=[topic]):

			self.printProgress(count + 1, number_of_messages, prefix='Progress:', suffix='Complete', decimals=1, length=50)

			time = repr(msg.header.stamp.secs + msg.header.stamp.nsecs * 10 ** (-9))

			file.write(str(sensor_id))
			file.write(',')
			file.write(str(bag_file_id))
			file.write(',')
			file.write(str(self.unixTimeToTimeStamp(msg.header.stamp.secs)))
			file.write(',')
			file.write(str(msg.header.stamp.secs))
			file.write(',')
			file.write(str(msg.header.stamp.nsecs))
			file.write(',')
			file.write(time)
			file.write(',')
			file.write(str(msg.C1))
			file.write(',')
			file.write(str(msg.C2))
			file.write(',')
			file.write(str(msg.C3))
			file.write(',')
			file.write(str(msg.C4))
			file.write(',')
			file.write(str(msg.E1))
			file.write(',')
			file.write(str(msg.P1))
			file.write(',')
			file.write(str(msg.err_bad_character))
			file.write(',')
			file.write(str(msg.err_bad_element_structure))
			file.write(',')
			file.write(str(msg.err_bad_lowercase_character))
			file.write(',')
			file.write(str(msg.err_bad_uppercase_character))
			file.write(',')
			file.write(str(msg.err_failed_time))
			file.write(',')
			file.write(str(msg.err_wrong_element_length))
			file.write('\n')

			count += 1

		file.close()

		try:

			self.db.bulk_insert(table='encoder_new', fields=['sensors_id', 'bag_files_id', 'timestamp', 'seconds', 'nanoseconds', 'time', 'c1', 'c2', 'c3', 'c4', 'e1', 'p1', 'err_bad_character', 'err_bad_element_structure', 'err_bad_lowercase_character', 'err_bad_uppercase_character', 'err_failed_time', 'err_wrong_element_length'], file_name=output_file_name)
			print ("Insert ENCODER NEW into database successfully!")
		except:

			# Since the try failed above, we need to rollback the connection. If we don't do this, the NEXT query call (the one below)
			# will error saying it can't complete the query. Which will make you think it's the NEXT query, but it was really the last one...
			self.db.conn.rollback()

			if self.replace_all is False:

				user_input = input('It looks like the Encoder New data has already been added to the database. Would you like to overwrite the corresponding data? [y/n/a] ')

				if user_input == 'a':

					self.replace_all = True

			if self.replace_all is True or user_input == 'y':

				status = self.db.delete(table='encoder_new', using=None, where=['bag_files_id='+str(bag_file_id)])
				self.db.bulk_insert(table='encoder_new', fields=['sensors_id', 'bag_files_id', 'timestamp', 'seconds', 'nanoseconds', 'time', 'c1', 'c2', 'c3', 'c4', 'e1', 'p1', 'err_bad_character', 'err_bad_element_structure', 'err_bad_lowercase_character', 'err_bad_uppercase_character', 'err_failed_time', 'err_wrong_element_length'], file_name=output_file_name)

			else:

				return

	'''
		============================= Method parseTrigger() ====================================
		#	Method Purpose:
		#		parse the trigger box data into txt file and inser them into database
		#
		#	Input Variable:
		#		sensor_id			1
				bag_file_id 		return when insert bag data
				bag_file           	bag = rosbag.Bag(bag_file_name)
				topic 				topic = '/parseTrigger'
				output_file_name 	output_file_name = folder_name + '/parseTrigger/' + bag_file_name.replace('.bag', '-encoder-new.txt')
		#
		#	Output/Return:
		#		None
		#
		#	Algorithm:
		#
		# 	Restrictions/Notes:
		#
		# 	The follow methods are called:
				self.printProgress

		# 	Author: Wushuang Bai
		# 	Date: 03/11/2022
		#
		================================================================================

	'''
	def parseTrigger(self, sensor_id, bag_file_id, bag_file, topic, output_file_name):

		file = open(output_file_name, "w")

		number_of_messages = bag_file.get_message_count(topic_filters=topic)

		count = 0
		for topic, msg, t in bag_file.read_messages(topics=[topic]):

			self.printProgress(count + 1, number_of_messages, prefix='Progress:', suffix='Complete', decimals=1, length=50)

			time = repr(msg.header.stamp.secs + msg.header.stamp.nsecs * 10 ** (-9))

			file.write(str(sensor_id))
			file.write(',')
			file.write(str(bag_file_id))
			file.write(',')
			file.write(str(self.unixTimeToTimeStamp(msg.header.stamp.secs)))
			file.write(',')
			file.write(str(msg.header.stamp.secs))
			file.write(',')
			file.write(str(msg.header.stamp.nsecs))
			file.write(',')
			file.write(time)
			file.write(',')
			file.write(str(msg.mode))
			file.write(',')
			file.write(str(msg.mode_counts))
			file.write(',')
			file.write(str(msg.adjone))
			file.write(',')
			file.write(str(msg.adjtwo))
			file.write(',')
			file.write(str(msg.adjthree))
			file.write(',')
			file.write(str(msg.err_failed_mode_count))
			file.write(',')
			file.write(str(msg.err_failed_XI_format))
			file.write(',')
			file.write(str(msg.err_failed_checkInformation))
			file.write(',')
			file.write(str(msg.err_trigger_unknown_error_occured))
			file.write(',')
			file.write(str(msg.err_bad_uppercase_character))
			file.write(',')
			file.write(str(msg.err_bad_lowercase_character))
			file.write(',')
			file.write(str(msg.err_bad_three_adj_element))
			file.write(',')
			file.write(str(msg.err_bad_first_element))
			file.write(',')
			file.write(str(msg.err_bad_character))
			file.write(',')
			file.write(str(msg.err_wrong_element_length))
			file.write('\n')

			count += 1

		file.close()

		try:

			self.db.bulk_insert(table='trigger', fields=['sensors_id', 'bag_files_id', 'timestamp', 'seconds', 'nanoseconds', 'time', 'mode', 'mode_counts', 'adjone', 'adjtwo', 'adjthree', 'err_failed_mode_count', 'err_failed_XI_format', 'err_failed_checkInformation', 'err_trigger_unknown_error_occured', 'err_bad_uppercase_character', 'err_bad_lowercase_character', 'err_bad_three_adj_element', 'err_bad_first_element','err_bad_character','err_wrong_element_length'], file_name=output_file_name)
			print ("Insert Trigger into database successfully!")
		except:

			# Since the try failed above, we need to rollback the connection. If we don't do this, the NEXT query call (the one below)
			# will error saying it can't complete the query. Which will make you think it's the NEXT query, but it was really the last one...
			self.db.conn.rollback()

			if self.replace_all is False:

				user_input = input('It looks like the Encoder New data has already been added to the database. Would you like to overwrite the corresponding data? [y/n/a] ')

				if user_input == 'a':

					self.replace_all = True

			if self.replace_all is True or user_input == 'y':

				status = self.db.delete(table='trigger', using=None, where=['bag_files_id='+str(bag_file_id)])
				self.db.bulk_insert(table='trigger', fields=['sensors_id', 'bag_files_id', 'timestamp', 'seconds', 'nanoseconds', 'time', 'mode', 'mode_counts', 'adjone', 'adjtwo', 'adjthree', 'err_failed_mode_count', 'err_failed_XI_format', 'err_failed_checkInformation', 'err_trigger_unknown_error_occured', 'err_bad_uppercase_character', 'err_bad_lowercase_character', 'err_bad_three_adj_element', 'err_bad_first_element','err_bad_character','err_wrong_element_length'], file_name=output_file_name)
				print ("Insert Trigger into database successfully!")

			else:

				return

	'''
		insert basestation info

	'''

	def setBaseStation(self, id, name, latitude, longitude, altitude, latitude_std, longitude_std, altitude_std):

		return self.db.insert(table='base_stations', fields=['id', 'name', 'latitude', 'longitude', 'altitude', 'latitude_std', 'longitude_std', 'altitude_std'],
							  values=[id, name, latitude, longitude, altitude,latitude_std, longitude_std, altitude_std],
							  upsert=True,
							  conflict_on=['id'])
	
	'''
		insert vehicle info
	'''

	def setVehicle(self, id, name):

		return self.db.insert(table='Vehicle', fields=['id', 'name'],
							  values=[id, name],
							  upsert=True,
							  conflict_on=['id'])

	'''
		insert sensors info

	'''
	def setSensor(self,id,product_name):

		return self.db.insert(table='sensors', fields=['id', 'product_name'],
							  values=[id, product_name],
							  upsert=True,
							  conflict_on=['id'])

	'''
		update table in database, insert geog

	'''

	def setLatitudeLongitudeToGISPoint(self,bag_file_id):
		print('setting Latitude Longitude To GISPoint with bag_file_id = ', bag_file_id)
		self.db.update(table='base_stations', update_set=['geography=ST_SetSRID(ST_MakePoint(longitude,latitude),' + str(self.srid) + ')::geography'])
		self.db.update(table='novatel_gps', update_set=['geography=ST_SetSRID(ST_MakePoint(longitude,latitude),' + str(self.srid) + ')::geography'],where=['bag_files_id=' + str(bag_file_id)])
		self.db.update(table='garmin_gps', update_set=['geography=ST_SetSRID(ST_MakePoint(longitude,latitude),' + str(self.srid) + ')::geography'],where=['bag_files_id=' + str(bag_file_id)])
		self.db.update(table='hemisphere_gps', update_set=['geography=ST_SetSRID(ST_MakePoint(longitude,latitude),' + str(self.srid) + ')::geography'],where=['bag_files_id=' + str(bag_file_id)])
		self.db.update(table='novatel_imu', update_set=['geography=ST_SetSRID(ST_MakePoint(longitude,latitude),' + str(self.srid) + ')::geography'],where=['bag_files_id=' + str(bag_file_id)])
		# self.db.update(table='pos', update_set=['geography=ST_SetSRID(ST_MakePoint(longitude,latitude),' + str(self.srid) + ')::geography'])
		# self.db.update(table='laser', update_set=['geography=ST_SetSRID(ST_MakePoint(longitude,latitude),' + str(self.srid) + ')::geography'])
		# self.db.update(table='camera', update_set=['geography=ST_SetSRID(ST_MakePoint(longitude,latitude),' + str(self.srid) + ')::geography'])
		# self.db.update(table='encoder', update_set=['geography=ST_SetSRID(ST_MakePoint(longitude,latitude),' + str(self.srid) + ')::geography'])
		print('set Latitude Longitude To GISPoint done!')
	'''
		Ternary operator:

		if data is not None:
			if data is not None and data[1] == 1:
				True
			else:
				False,data[0]
		else:
			None

	'''

	def checkIfBagFileAlreadyParsed(self, file_name):

		data, status = self.db.select(table='bag_files', fields=['id, parsed'], where=['name=\''+str(file_name)+'\''])

		return True if (data is not None and data[1] == 1) else False, data[0] if (data is not None) else None

	'''
		============================= Method parse() ====================================
		#	Method Purpose:
		#		parse the sensor's data into txt or cav format
		#
		#	Input Variable:
		#		bag_file_names      grab from current work folder
				folder_name 		user input, single
				base_station_id  	1, for test track
				trip_id 			insert trip data in main, and then return id, there are one trip id for each .bag file
				vehicle_id 			insert vehicle data in main, and then return id
		#
		#	Output/Return:
		#		None
		#
		#	Algorithm:
		#
		# 	Restrictions/Notes:
		# 		To do list: 1.
		#
		# 	The follow methods are called:
				self.parseINS()

		# 	Author: Liming Gao
		# 	Date: 02/05/2020
		#
		================================================================================

	'''

	def parse(self, bag_file_name, directory,folder_name, base_station_id, trip_id, vehicle_id):

		# TODO: REMOVE
		# bag_file_id = 10

		date_time = self.parseBagFileNameForDateTime(bag_file_name)
		trip_date = date_time[0:10]

		print('--->Parsing: ' + bag_file_name)

		bag_file_id, status = self.db.insert(table='bag_files', fields=['Vehicle_id', 'trips_id', 'file_path','name', 'datetime'],
											 values=[vehicle_id, trip_id,directory,bag_file_name, date_time],
											 upsert=True,
											 conflict_on=['name'])

		bag = rosbag.Bag(bag_file_name)
		'''
		# obtain the topic list ##it is time consuming
		bagContents = bag.read_messages()
		listOfTopics = []
		for topic, msg, t in bagContents:
			if topic not in listOfTopics:
				listOfTopics.append(topic)

		if '/power_data/supply_load' in listOfTopics:
			OutputFileName = folder_name + '/power_data/' + \
			bag_file_name.replace('.bag', '-supply_load.txt')
			File = open(OutputFileName, "w")
			print("Parsing Power Suppy Load...")
			for topic, msg, t in bag.read_messages(topics=['/power_data/supply_load']):

				File.write(str(msg.data))
				File.write('\n')

			File.close()
		'''
		# Get topic list
		topics = bag.get_type_and_topic_info().topics
		if '/INS' in topics:
			print("Parsing INS...")
			# result, status = self.db.select(table='sensors', fields=['id','product_name'], where=['product_name= Novatel_gps'])
			# sensor_id = result[0]
			sensor_id = 0
			# in string bag_file_name, replace .bag with -INS.txt
			output_file_name = folder_name + '/gps/' + bag_file_name.replace('.bag', '-INS.txt')
			topic = '/INS'
			self.parseINS(sensor_id, bag_file_id, bag, topic, output_file_name)
		
		if '/fix' in topics:
			print("Parsing Garmin GPS...")
			# result, status = self.db.select(table='sensors', fields=['id','product_name'], where=['product_name = '+'Garmin_gps'])
			# if result is not None:
			# 	sensor_id_garmin = result[0]
			sensor_id_garmin = 8
			output_file_name = folder_name + '/gps/' + bag_file_name.replace('.bag', '-garmin-gps.txt')
			topic = '/fix'
			self.parseGarminGPS(sensor_id_garmin, bag_file_id, bag, topic, output_file_name)

		if '/vel' in topics:
			print("Parsing Garmin Velocity...")
			sensor_id_garmin = 8
			output_file_name = folder_name + '/gps/' + bag_file_name.replace('.bag', '-garmin-velocity.txt')
			topic = '/vel'
			self.parseGarminVelocity(sensor_id_garmin, bag_file_id, bag, topic, output_file_name)

		if '/Bin1' in topics:
			print("Parsing Hemisphere_GPS...")
			sensor_id_hemisphere = 9
			output_file_name = folder_name + '/gps/' + bag_file_name.replace('.bag', '-Hemisphere-GPS.txt')
			topic = '/Bin1'
			self.parseHemisphereGPS(sensor_id_hemisphere, bag_file_id, bag, topic, output_file_name)

		if 'IMU' in topics:
			print("Parsing NovAtel IMU...")
			sensor_id_novatel_imu = 1
			output_file_name = folder_name + '/imu/' + bag_file_name.replace('.bag', '-NovAtel-IMU.txt')
			topic = '/IMU'
			self.parseNovatelIMU(sensor_id_novatel_imu, bag_file_id, bag, topic, output_file_name)

		if '/front_center_camera/camera_info' in topics and '/front_center_camera/image_rect_color/compressed' in topics:
			print("Parsing Front Center Camera...")
			sensor_id_front_center_camera = 4
			output_file_name_images = folder_name + '/images/' + bag_file_name.replace('.bag', '-front_center_camera-header.txt')
			output_file_name_camera_info = folder_name + '/images/' + bag_file_name.replace('.bag', '-front_center_camera-info.txt')
			camera_info_topic = '/front_center_camera/camera_info'
			image_topic = '/front_center_camera/image_rect_color/compressed'
			self.parseCamera(trip_id, sensor_id_front_center_camera, bag_file_id, bag, image_topic, camera_info_topic, output_file_name_images, output_file_name_camera_info, rotate=False, angle=180)

		if '/raw_encoder' in topics:
			print("Parsing Encoder...")
			sensors_id_US_encoder_left = 6
			output_file_name = folder_name + '/wheel_encoder/' + bag_file_name.replace('.bag', '-encoder.txt')
			topic = '/raw_encoder'
			self.parseEncoder(trip_id, sensors_id_US_encoder_left, bag_file_id, bag, topic, output_file_name)

		if '/imu/data' in topics:
			print("Parsing ADIS IMU...")
			sensors_id_Adis_imu = 10
			output_file_name = folder_name + '/imu/' + bag_file_name.replace('.bag', '-Adis-IMU.txt')
			topic = '/imu/data'
			self.parseAdisIMU(sensors_id_Adis_imu, bag_file_id, bag, topic, output_file_name)

		if '/steering_angle' in topics:
			print("Parsing Steering Angle...")
			sensors_id_SteerAngle_left = 14
			output_file_name = folder_name + '/wheel_encoder/' + bag_file_name.replace('.bag', '-steering-angle.txt')
			topic = '/steering_angle'
			self.parseSteeringAngle(trip_id, sensors_id_SteerAngle_left, bag_file_id, bag, topic, output_file_name)

		if '/sick_lms500/scan' in topics:
			print("Parsing Laser...")
			sensors_id_Sick_laser = 2
			output_file_name = folder_name + '/laser/' + bag_file_name.replace('.bag', '-laser.txt')
			topic = '/sick_lms500/scan'
			self.parseLaser(trip_id, sensors_id_Sick_laser, bag_file_id, bag, topic, output_file_name)

		if '/parseEncoder' in topics:
			print("Parsing Encoder New...")
			sensors_id_Encoder_New = 16
			output_file_name = folder_name + '/parseEncoder/' + bag_file_name.replace('.bag', '-encoder-new.txt')
			topic = '/parseEncoder'
			self.parseEncoderNew(sensors_id_Encoder_New, bag_file_id, bag, topic, output_file_name)
		
		if '/parseTrigger' in topics:
			print("Parsing Trigger...")
			sensors_id_Encoder_New = 17
			output_file_name = folder_name + '/parseTrigger/' + bag_file_name.replace('.bag', '-trigger.txt')
			topic = '/parseTrigger'
			self.parseTrigger(sensors_id_Encoder_New, bag_file_id, bag, topic, output_file_name)

		if '/sick_lms500/sicktime' in topics:
			print("Parsing Laser Trigger...")
			OutputFileName = folder_name + '/laser/' + bag_file_name.replace('.bag', '-laser-trigger.txt')
			File = open(OutputFileName, "w")
			for topic, msg, t in bag.read_messages(topics=['/sick_lms500/sicktime']):

				File.write(str(msg.header.seq))
				File.write(',')
				File.write(str(msg.header.stamp.secs))
				File.write(',')
				File.write(str(msg.header.stamp.nsecs))
				File.write(',')
				File.write(str(msg.sick_time.secs))
				File.write(',')
				File.write(str(msg.sick_time.nsecs))
				File.write(',')
				File.write(str(msg.header.stamp.secs + msg.header.stamp.nsecs * 10 ** (-9)))
				File.write('\n')
				File.close()

		#edit stop here
		self.setLatitudeLongitudeToGISPoint(bag_file_id)

		bag.close()

		# update datetime end for each bag file
		result, status = self.db.select(table='Hemisphere_gps', fields=['bag_files_id,timestamp'], where=['bag_files_id='+str(bag_file_id)],orderby ='timestamp DESC',limit = 1)

		datetime_end = str(result[1])

		self.db.update(table='bag_files', update_set=['datetime_end=\'' + datetime_end + '\''], where=['id=' + str(bag_file_id)])

		# change flag
		self.db.update(table='bag_files', update_set=['parsed=TRUE'], where=['id=' + str(bag_file_id)])

		self.replace_all = False

'''
	purpose: exit the system
	algorithm: input(),os.listdir(directory)
	Notes: compare input() with raw_input()
	In os.listdir(directory), the directory should be a absolute path. Absolute path: start with '/'
	"~/Documents/Liming/database_NSF/MappingVan_Database/Example_data/" is a Relative Path

'''
def input_confirm(trip,directory):
	s = 'Do you want to parse the data for this trip: ['+ trip +  ']? [y/n]\n'
	confirm_input = input(s)
	# confirm_input = input("'Do you want to parse the [ ',trip,  '] data? [y/n]\n'")
	if confirm_input == 'y':
		print('The path of the bag files for the trip is: '+ directory)
		Path_confirm_input = input("Is the path in args Correct?[y/n]\n")
		if Path_confirm_input == 'y':
			print(trip + ' data will be parsed!')
			# os.chdir(directory + ".")  # change work path to directory,ignore the dot

			listOfBagFiles = [f for f in os.listdir(directory) if f[-4:] == ".bag"]	#get list of only bag files in current dir.
			numberOfFiles = str(len(listOfBagFiles))
			print("Parsing all " + numberOfFiles + " bagfiles in current directory: \n")
			for f in listOfBagFiles:
				print(f)
			print("\n press ctrl+c in the next 15 seconds to cancel \n")
			time.sleep(5)
		else:
			exit_parse()
	elif confirm_input == 'n':
		exit_parse()
	else:
		print('Input error!')
		exit_parse()
	return numberOfFiles
'''
	purpose: exit the system
	algorithm: sys.exit(0)
	Notes: compare sys.exit(o) to os._exit(0)

'''
def exit_parse():
	try:
		sys.exit(0)
	except:
		print('Parsing is abandoned')
	finally:
		print('clean-up')
		sys.exit(0)

''' MAIN Function '''

def main(args):

	# Step1: folder directory with bag file
	directory = ''
	if len(args) > 1:
		directory = args[1]

	# Step2: trips info
	user_input = int(input('Choose the trip you want to parse:\n \
[1]:test track \n [2]:wahba loop \n \
[3]:test track Lane Change \n [4]:test track  Decision Points \n \
[5]:I99 State College to CityA \n [6]:I99 CityA to State College \n \
[7]:I99 State College to Altoona \n [8]:I99 Altoona to State College \n \
[9]:Static GPS (Construction cone) at mapping van garage \n \
[10]:Image server test I99 Altoona to State College \n \
[11]:Test Around LTI Garage 2022-10-25 \n'))

	if user_input == 1:
		trip_description = "Test Track MappingVan."
		trip_name = "Test Track MappingVan 2019-10-19"
		trip_passengers = " "
		trip_driver = "LimingGao"
		trip_notes = "without traffic light, at night"
		numberOfBagFiles = input_confirm(trip_name,directory)
		base_station_of_trip = 'LTI'
		# *.bag files folder: /media/brennan/My Book/RoadMeasurement/mapping_van_testtrack_10182019

	elif user_input == 2:
		trip_description = "Wahba Loop MappingVan"
		trip_name = "Wahba Loop MappingVan 2019-09-17"
		trip_passengers = "LimingGao"
		trip_driver = "Dr. Brennan"
		trip_notes = "with traffic light, highway, four loops, DGPS inactive at some location"
		numberOfBagFiles = input_confirm(trip_name,directory)
		base_station_of_trip = 'LTI'
		# *.bag files folder: ["/media/brennan/My Book/RoadMeasurement/mapping_van_WahbaLoop_09172019/"], //for Wahba Loop
	elif user_input == 3:
		trip_name = "Test Track Decision Points with Lane Change MappingVan 2020-03-13"
		trip_description = "Test Track, Decision Points with Lane Change, MappingVan"
		trip_passengers = "Liming Gao"
		trip_driver = "Guangwei Zhou"
		trip_notes = "Mapping at test track vehicle durability course area with lane change"
		numberOfBagFiles = input_confirm(trip_name,directory)
		base_station_of_trip = 'LTI'
		# *.bag files folder: ["/media/brennan/My Book/RoadMeasurement//mapping_van_decisionPoint/mapping_van_testtrack_decisionPoint_03132020/"], //for test track decision point with lane change
	elif user_input == 4:
		trip_name = "Test Track Decision Points MappingVan 2020-02-24"
		trip_description = "Test Track, Decision Points, MappingVan"
		trip_passengers = "Liming Gao"
		trip_driver = "Guangwei Zhou"
		trip_notes = "Mapping at test track area with brach driving path at each road intersection"
		numberOfBagFiles = input_confirm(trip_name,directory)
		base_station_of_trip = 'Test Track'
		# *.bag files folder: ["/media/brennan/My Book/RoadMeasurement/mapping_van_decisionPoint/mapping_van_testtrack_decisionPoint_02242020/"], //for test track decision point
	elif user_input == 5:
		trip_name = "State College to City A MappingVan 2019-12-10"
		trip_description = "Map from State College to CityA"
		trip_passengers = "Liming Gao"
		trip_driver = "Wushuang Bai"
		trip_notes = "Mapping from State College to CityA through I-99. DGPS was active. There are some road segments where GPS signal is missing."
		numberOfBagFiles = input_confirm(trip_name,directory)
		base_station_of_trip = 'LTI'
		# *.bag files folder: ["/media/brennan/My Book/RoadMeasurement/12-10-2019_MappingVan_LimingWushuang_I99_cityA/StateCollegeToCityA/"], //for mapping from state college to CityA 2019-12-10
	elif user_input == 6:
		trip_name = "CityA to State College MappingVan 2019-12-10"
		trip_description = "Map from CityA to State College"
		trip_passengers = "Liming Gao"
		trip_driver = "Wushuang Bai"
		trip_notes = "Mapping from CityA to State College through I-99. DGPS was active. There are some road segments where GPS signal is missing."
		numberOfBagFiles = input_confirm(trip_name,directory)
		base_station_of_trip = 'LTI'
		# *.bag files folder: ["/media/brennan/My Book/RoadMeasurement/12-10-2019_MappingVan_LimingWushuang_I99_cityA/CityAToStateCollege/"], //for mapping from cityA to state college 2019-12-10
	elif user_input == 7:
		trip_name = "State College to Altoona MappingVan 2021-01-23"
		trip_description = "Map I99 from State College(exit 73) to Altoona (exit 33)"
		trip_passengers = "Liming Gao"
		trip_driver = "Wushuang Bai"
		trip_notes = "Mapping from State College(exit 73) to Altoona (exit 33) through I-99. Lost DGPS mode when approaching Altoona. Drving on the right lane."
		numberOfBagFiles = input_confirm(trip_name,directory)
		base_station_of_trip = 'LTI'
		# *.bag files folder: ["/media/brennan/My Book/RoadMeasurement/stateCollege_Altoona_I99_20210123/StateCollege_to_Altoona_I99_RightLane/"]
	elif user_input == 8:
		trip_name = "Altoona to State College MappingVan 2021-01-23"
		trip_description = "Map I99 from Altoona (exit 33) to State College(exit 73)"
		trip_passengers = "Liming Gao"
		trip_driver = "Wushuang Bai"
		trip_notes = "Mapping from Altoona (exit 33) to State College(exit 73) through I-99. Nexver lost DGPS mode except for passing below bridge or traffic sign. Drving on the right lane."
		numberOfBagFiles = input_confirm(trip_name,directory)
		base_station_of_trip = 'LTI'
		# *.bag files folder: ["/media/brennan/My Book/RoadMeasurement/stateCollege_Altoona_I99_20210123/Altoona_to_StateCollege_I99_RightLane/"]
	elif user_input == 9:
		trip_name = "Static GPS (Construction cone) 2021-05-25 "
		trip_description = "Static GPS (Construction cone) near mapping van garage "
		trip_passengers = ""
		trip_driver = "Liming Gao"
		trip_notes = "Static GPS (Construction cone) near mapping van garage. 10mins static measurement, then move about 20cm, stay 10mins, move about 15m, stay another 10 mins. Navmode 5."
		numberOfBagFiles = input_confirm(trip_name,directory)
		base_station_of_trip = 'LTI'
		# *.bag files folder: ["/media/brennan/My Book/RoadMeasurement/mapping_van_static_20210525/"]
	elif user_input == 10:
		trip_name = "Altoona to State College MappingVan with image 2021-01-23 "
		trip_description = "100 seconds Map data with camera I99 from Altoona (exit 33) to State College(exit 73) "
		trip_passengers = ""
		trip_driver = "Liming Gao"
		trip_notes = "this is used for image server test."
		numberOfBagFiles = input_confirm(trip_name,directory)
		base_station_of_trip = 'LTI'
		# *.bag files folder: ["/media/brennan/My Book/RoadMeasurement/mapping_van_static_20210525/"]
	elif user_input == 11:
		trip_name = "Test Around LTI Garage 2022-10-25 "
		trip_description = "Test trigger, encoder, hemisphere and adisimu"
		trip_passengers = "Wushuang Bai"
		trip_driver = "Dr. Brennan"
		trip_notes = "This is to validate sensors working after rebuilding the van"
		numberOfBagFiles = input_confirm(trip_name,directory)
		base_station_of_trip = 'LTI'
		# *.bag files folder: ["/media/brennan/My Book/RoadMeasurement/mapping_van_static_20210525/"]
	else:
		print('Input error!')
		exit_parse()

	# Step3: Instance of Parse class
	db_name = 'mapping_van_raw'
	folder_name = directory + 'raw_data'  # the folder
	p = Parse(folder_name, db_name)

	# Step4: set base station

	# BASE STATION PARAMETERS(at test track)
	if base_station_of_trip == 'Test Track':
		base_station_name = 'Test Track'
		base_station_latitude = 40 + 51.0 / 60.0 + 44.32334 / 3600.0  # degrees
		base_station_longitude = -(77 + 50.0 / 60.0 + 10.57246 / 3600.0)  # degrees
		base_station_altitude = 333.817  # meters
		base_station_latitude_std = 0.004  # meters
		base_station_longitude_std = 0.002  # meters
		base_station_altitude_std = 0.006  # meters

		base_station_id = 1
		base_station_id, status = p.setBaseStation(base_station_id, base_station_name, base_station_latitude, base_station_longitude,base_station_altitude, base_station_latitude_std, base_station_longitude_std, base_station_altitude_std)
	elif base_station_of_trip == 'LTI':
		# BASE STATION PARAMETERS(at LTI) Note: need further edited
		base_station_name = 'LTI, Larson  Transportation Institute'
		base_station_latitude = 40+48.0/60+ 24.81098/3600.0
		base_station_longitude = -77 - 50.0/60 - 59.26859/3600.0
		base_station_altitude = 337.6654968261719
		base_station_latitude_std = 0.004  # meters
		base_station_longitude_std = 0.002  # meters
		base_station_altitude_std = 0.006  # meters

		base_station_id = 2
		base_station_id, status = p.setBaseStation(base_station_id, base_station_name, base_station_latitude, base_station_longitude,base_station_altitude, base_station_latitude_std, base_station_longitude_std, base_station_altitude_std)
	else:
		print('base_station name error!')
		exit_parse()

	# Step5: insert vehicle Information
	vehicle_id = 1
	vehicle_name = 'mapping van'
	vehicle_id, status = p.setVehicle(vehicle_id, vehicle_name)
	'''
	OLD
	vehicle_id, status = p.db.insert(table='Vehicle', fields=['id','name'],values=[vehicle_id,vehicle_name],upsert=True,
											 conflict_on=['id'])
	'''

	print('vehicle_id is: ', vehicle_id)

	# Step5: insert sensors
	sensors_id_Novatel_gps = 0
	sensors_id_Novatel_imu = 1
	sensors_id_Sick_laser = 2
	sensors_id_Camera_frontLeft = 3
	sensors_id_Camera_frontCenter = 4
	sensors_id_Camera_frontRight = 5
	sensors_id_US_encoder_left = 6
	sensors_id_US_encoder_right = 7
	sensors_id_Garmin_gps = 8
	sensors_id_Hemisphere_gps = 9
	sensors_id_Adis_imu = 10
	sensors_id_Camera_rearLeft = 11
	sensors_id_Camera_rearCenter = 12
	sensors_id_Camera_rearRight = 13
	sensors_id_SteerAngle_left = 14
	sensors_id_SteerAngle_right = 15
	sensors_id_Encoder_New = 16	
	sensors_id_Trigger = 17
	# sensors_id, status = p.db.insert(table='sensors', fields=['id','product_name'],
	# 									values=[sensors_id_Novatel,'Novatel_gps'],
	# 									upsert=True,
	# 									conflict_on=['id'])
	p.setSensor(sensors_id_Novatel_gps,'Novatel_gps')
	p.setSensor(sensors_id_Novatel_imu,'Novatel_imu')
	p.setSensor(sensors_id_Sick_laser,'Sick_laser')
	p.setSensor(sensors_id_Camera_frontLeft,'Camera_frontLeft')
	p.setSensor(sensors_id_Camera_frontCenter,'Camera_frontCenter')
	p.setSensor(sensors_id_Camera_frontRight,'Camera_frontRight')
	p.setSensor(sensors_id_US_encoder_left,'US_encoder_left')
	p.setSensor(sensors_id_US_encoder_right,'US_encoder_right')
	p.setSensor(sensors_id_Garmin_gps,'Garmin_gps')
	p.setSensor(sensors_id_Hemisphere_gps,'Hemisphere_gps')
	p.setSensor(sensors_id_Adis_imu,'Adis16407_imu')
	p.setSensor(sensors_id_Camera_rearLeft,'Camera_rearLeft')
	p.setSensor(sensors_id_Camera_rearCenter,'Camera_rearCenter')
	p.setSensor(sensors_id_Camera_rearRight,'Camera_rearRight')
	p.setSensor(sensors_id_SteerAngle_left,'SteerAngle_left')
	p.setSensor(sensors_id_SteerAngle_right,'SteerAngle_right')
	p.setSensor(sensors_id_Encoder_New,'Encoder_New')
	p.setSensor(sensors_id_Trigger,'Trigger')
	# sensor_id = 6
	# p.db.insert(table='encoder_parameters', fields=['sensors_id', 'counts_per_revolution'],
	# 												 values=[sensor_id, '10000'],
	# 												 upsert=True,
	# 												 conflict_on=['sensors_id', 'counts_per_revolution'])

	# Step6: Choose timer to use
	if sys.platform.startswith('win'):
		default_timer = time.clock
	else:
		default_timer = time.time

	# start clock
	total_start = default_timer()

	# Step7: bag files id
	bag_file_ids = []
	retval = os.getcwd()  # get current path

	os.chdir(directory + ".")  # change work path to directory,ignore the dot
	retval = os.getcwd()  # get current path
	print("work path:", retval)  # eg.work path: /media/brennan/My Book/RoadMeasurement/mapping_van_WahbaLoop_09172019

	# Step8:  we check if all the .bag files have been parsed. If yes, correct time; if not, insert trip id and then insert other data.
	# glob: Filename pattern matching. find bag files in current path
	bag_conut = 0
	for file_name in sorted(glob.glob("*.bag")):
		bag_conut += 1
		print('\nParsing[',bag_conut, '/', numberOfBagFiles, ']:', file_name) # eg. mapping_van_2019-09-17-15-07-19_0.bag
		# find the bag files which have been parsed.
		already_parsed, bag_file_id = p.checkIfBagFileAlreadyParsed(file_name) # eg, true, 39

		start = default_timer()

		trip_date = p.parseBagFileNameForDateTime(file_name)  #'2019-09-17 15:07:19'

		trip_date_added = p.unixTimeToTimeStamp(start)
		split_file_index = p.parseBagFileNameForSplitFileIndex(file_name)  #eg, 0 for mapping_van_2019-09-17-15-07-19_0.bag

		if len(bag_file_ids) > 0 and split_file_index == 0:

			print('Fixing time triggers...')

			dt = 1.0 / 25.0
			'''
			sensor_id = 3
			p.correctTimeTrigger(bag_file_ids, sensor_id, dt)

			sensor_id = 4
			p.correctTimeTrigger(bag_file_ids, sensor_id, dt)

			sensor_id = 5
			p.correctTimeTrigger(bag_file_ids, sensor_id, dt)

			bag_file_names = []
			'''
		#
		if bag_file_id is not None:  # the bag file has been parsed

			bag_file_ids.append(bag_file_id)

		if bag_file_id is not None:

			result, status = p.db.select(table='bag_files', fields=['trips_id'], where=['id='+str(bag_file_id)])
			trip_id = result[0]

		else:

			# insert the trip id for each bag files
			trip_id, status = p.db.insert(table='trips', fields=['name', 'base_stations_id', 'date', 'description', 'passengers', 'driver','notes', 'date_added'],
										  values=[trip_name, base_station_id, trip_date, trip_description, trip_passengers, trip_driver,trip_notes, trip_date_added])  # ,
			# upsert=True,
			# conflict_on=['date'])

		if already_parsed is True:

			user_input = input(
				'Would you like to re-parse the data for ' + file_name + '? [y/n] ')

			if user_input == 'y':

				# Re-parse the data
				p.parse(file_name, directory, folder_name, base_station_id, trip_id,vehicle_id)

			# Otherwise, continue on to the next bag file
			else:

				continue
		else:
			# call parse for each bag files 
			p.parse(file_name, directory, folder_name, base_station_id, trip_id,vehicle_id)

		finish = default_timer()

		print("Finished " + file_name + " in " +
			  str(finish - start) + " seconds.")

	if len(bag_file_ids) > 0:

		print('Fixing time triggers...')

		dt = 1.0 / 25.0

		#sensor_id = 3
		#p.correctTimeTrigger(bag_file_ids, sensor_id, dt)

		#sensor_id = 4
		#p.correctTimeTrigger(bag_file_ids, sensor_id, dt)

		#sensor_id = 5
		#p.correctTimeTrigger(bag_file_ids, sensor_id, dt)

	# shutil.rmtree('raw_data')

	total_finish = default_timer()

	print("Total time: " + str(total_finish - total_start) + " seconds.")


if __name__ == '__main__':
	main(sys.argv)
