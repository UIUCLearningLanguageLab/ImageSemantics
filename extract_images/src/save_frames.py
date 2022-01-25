import cv2
import os
import time
import csv
import shutil
import sys


class VideoObject:
	''' a class to store the information about each video'''
	
	def __init__(self, video_name):
		self.video_name = video_name
		self.mp4_path = '../mp4_videos/' + video_name
		self.image_path = '../images/' + video_name[:-4] + "/"    # a directory named after the image, where the images will be stored
		self.image_list = []

		self.video = None
		self.fps = None
		self.frame_rate = None
		self.num_frames = None
		self.length = None

		self.create_directory()
		self.load_video()

	def create_directory(self):
		# try statement here is basically checking to make sure the directory named after this movie doesnt already exit
		try:
			os.makedirs(self.image_path)
		except:
			print("Could not make directory {}".format(self.image_path))
			sys.exit()
		return success

	def load_video(self):
		self.video = cv2.VideoCapture(self.mp4_path)     # a built in command from cv2 that creates a video object from the video
		self.fps = self.video.get(cv2.CAP_PROP_FPS)      # saving the frames per second of the video
		self.frame_rate = round(self.fps)			# rounding fps to an int
		self.num_frames = int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))		# getting the total number of frames in the video
		self.length = (self.num_frames/self.fps)/60				# getting the length of the video

	def save_frames(self, images_per_second):

		success, image = self.video.read()   # cv2 command that reads the first frame of the video, successful, the image is stored in image, 
							# and success is a boolean telling us if it succeeded
		count = 0			    # counter to keep track of what frame we are on
		
		while success:    #  while an image continues to be sucessfully extracted from the video
			
			# if images_per_second == 0, we want to get every frame, or
			# if if we are getting n images per second, and the image count tells us we are currently on that image
			
			#	save the image
			if (images_per_second == 0) or (count % (self.frame_rate/images_per_second) == 0):
				
				# create the image's file name by taking the count and appending it to the movie name, but padding with zeros so the number of digits always same 
				string_count = str(count)
				while len(string_count) < 6:
					string_count = "0" + string_count
				output_file = self.image_path+self.video_name[:-4]+"_"+string_count+'.jpg'
				
				# save the image with that file name
				cv2.imwrite(output_file, image)     # save frame as JPEG file
			success,image = self.video.read()
			count += 1

def get_video_object_list(video_list_file):
	''' create a dictionary of video names pointing to video objects '''
	video_object_dict = {}
	with open(video_list_file) as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=',')
		for row in csv_reader:
			new_video_object = VideoObject(row[0])
			video_object_dict[row[0]] = new_video_object
	return video_object_dict


def main():
	images_per_second = 1/5  # a fraction of 1/n means that an image will be gathered every n seconds, a whole number means n images per second
	video_list_file = "../video_list1.csv"
	
	# this creates a list of video objects, which are instances of the video object class defined above.
	# This class is basically a cv2 video object, plus some associated information we are keeping track of, like the video name, file path, etc.
	# the movies that will be added to the list are specified in the video list file
	video_object_dict = get_video_object_list(video_list_file)
	
	# for each video in the list, we are going to save frames from it according to the images_per_second variable
	for video_name in video_object_dict:
		video_object = video_object_dict[video_name]
		video_object.save_frames(images_per_second)
	


main()
