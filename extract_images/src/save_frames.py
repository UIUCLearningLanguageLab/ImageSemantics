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

	def save_frames(self, images_per_second, window_size):
		
		success, image = self.video.read()   # cv2 command that reads the first frame of the video, successful, the image is stored in image, 
						     # and success is a boolean telling us if it succeeded
		image_list = []  # a list for keeping track of a set of images so we can pick the least blurry one
		
		# if the first retrieval was a success add it to the list
		if success:
			image_list.append(image)
		
		 #  while an image continues to be sucessfully extracted from the video, add them to the list
		while success:
			success,image = self.video.read()
			image_list.append(image)
		
		num_images = len(image_list)
		for i in range(num_images):
			
			# checks to see if i (the counter for where we are in the image list) is one we want, based on how often we wanted to sample images
			# for example, if the (rounded to int) frame rate was 30 fps, and we wanted 1 image every five seconds (ips = 1/5) 
			# then denominator is 30/(1/5) = 150, meaning we want to grab every 150th frame
			if i % (self.frame_rate/images_per_second) == 0:
				
				# if window size is 0, we are skipping the pick least blurry step and saving this image regardless
				if window_size == 0:
					image = image_list[i]
					image_index = i
					
				# if window size is greater than 0, we want to use that window size and pick the least blurry one
				elif window_size > 0:
					
					# get the start and stop index for what images we want to get based on the current i and window size
					# this list will always be window size long, unless the window would take us before or after the end of 
					# 	image list, in which case it will truncate it
					start_index = int(i-window_size/2)
					if start_index < 0:
						start_index = 0
					stop_index = int(i+window_size/2)+1
					if stop_index > num_images-1:
						stop_index = num_images-1
			
					# get the window of images, and choose the least blurry one
					image_window = image_list[start:stop]
					image, window_index = self.get_least_blurry_image(image_window)
					image_index = i-window_size/2+window_index
					
				save_single_image(image, image_index)
	
	def get_least_blurry_image(self, image_window):
		# Grace, your code goes here, return the least blurry image, and the index of which image in image_window that it was
		pass
	
	def save_single_image(self, image, index):
		string_index = str(index)
		while len(string_index) < 6:
			string_index = "0" + string_index
		output_file = self.image_path+self.video_name[:-4]+"_"+string_index+'.jpg'

		# save the image with that file name
		cv2.imwrite(output_file, image)     # save frame as JPEG file

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
	window_size = 10   # the number of images out of which we will choose the least blurry
	video_list_file = "../video_list1.csv"
	
	# this creates a list of video objects, which are instances of the video object class defined above.
	# This class is basically a cv2 video object, plus some associated information we are keeping track of, like the video name, file path, etc.
	# the movies that will be added to the list are specified in the video list file
	video_object_dict = get_video_object_list(video_list_file)
	
	# for each video in the list, we are going to save frames from it according to the images_per_second variable
	for video_name in video_object_dict:
		video_object = video_object_dict[video_name]
		video_object.save_frames(images_per_second, window_size)
	


main()
