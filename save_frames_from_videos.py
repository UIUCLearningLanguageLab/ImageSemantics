import cv2
import os
import shutil
import sys


class VideoObject:
	''' a class to store the information about each video'''
	def __init__(self, video_path):
		self.video_path = video_path
		self.video_name = video_path.split("/")[-1]

		self.image_path = "../images/" + self.video_name[:-4] + "/"    # a directory named after the image, where the images will be stored
		self.image_list = []

		self.video = None
		self.fps = None
		self.rounded_frame_rate = None
		self.num_frames = None
		self.length = None

		self.create_directory()
		self.load_video()

	def create_directory(self):
		try:
			os.makedirs(self.image_path)

		except:
			print("Could not create directory {}. It probably already exists.")
			response = input("Would you like to delete the existing directory? (y/n)")
			if response == 'y' or response == "Y":
				shutil.rmtree(self.image_path)
				self.create_directory()
			else:
				sys.exit(1)

	def load_video(self):
		self.video = cv2.VideoCapture(self.video_path)     # a built in command from cv2 that creates a video object from the video
		self.fps = self.video.get(cv2.CAP_PROP_FPS)      # saving the frames per second of the video
		self.rounded_frame_rate = round(self.fps)			# rounding fps to an int
		self.num_frames = int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))		# getting the total number of frames in the video
		
		self.length = (self.num_frames/self.fps)/60				# getting the length of the video

	def save_frames(self, images_per_second, window_size):
		
		print("Saving frames for video {}".format(self.video_name))
		print("		frames per second: {}".format(self.fps))
		print("		rounded frame rate: {}".format(self.rounded_frame_rate))
		print("		num frames in video: {}".format(self.num_frames))
		print("		video length: {}".format(self.length))
		image_index_list = []
		image_list = []
		success, image = self.video.read()   # cv2 command that reads the first frame of the video, successful, the image is stored in image, 
						     # and success is a boolean telling us if it succeeded
		
		i = 0
		while success:
			image_list.append(image)
			image_index_list.append(i)
			if len(image_list) > window_size:
				image_list.pop(0)
				image_index_list.pop(0)

			if (i - window_size + 1) % (self.rounded_frame_rate/images_per_second) == 0: 
				if (len(image_list) == window_size):
					if window_size > 1:
						image_to_save, window_index = self.get_least_blurry_image(image_list)
						image_index = image_index_list[window_index]
					else:
						image_index = i
						image_to_save = image
					self.save_single_image(image_to_save, image_index)
					print("			Index {}, Chose {} from Window, Frame {}".format(i,window_index,image_index))
			success,image = self.video.read() # capture video frame by frame
			i += 1
	
	def variance_of_laplacian(self, image):
		# compute the Laplacian of the image and then return the focus
		# measure, which is simply the variance of the Laplacian
		return cv2.Laplacian(image, cv2.CV_64F).var()	

	def get_least_blurry_image(self, image_window):
		largest_number = 0
		clearest_image = None
		clearest_image_index = 0
		for i in range(len(image_window)):
			#convert the image to grayscale, and compute
			#the focus measure of the image using the Variance
			#of Laplacian method
			gray = cv2.cvtColor(image_window[i], cv2.COLOR_BGR2GRAY)
			fm = self.variance_of_laplacian(gray)
			if fm > largest_number:
				largest_number = fm
				clearest_image = image_window[i]
				clearest_image_index = i
		return clearest_image, clearest_image_index


		
	def save_single_image(self, image, index):
		string_index = str(index)
		while len(string_index) < 6:
			string_index = "0" + string_index
		output_file = self.image_path+self.video_name[:-4]+"_"+string_index+'.jpg'

		# save the image with that file name
		cv2.imwrite(output_file, image)     # save frame as JPEG file

def get_video_object_list(video_list_file):
	''' create a dictionary of video names pointing to video objects '''
	file_list = os.listdir("../mp4_videos/")
	video_object_dict = {}

	for file_name in file_list:
		if file_name[0] != '.':
			new_video_object = VideoObject(file_name)
			video_object_dict[file_name] = new_video_object
			
	return video_object_dict


def main():
	images_per_second = 1/5  # a fraction of 1/n means that an image will be gathered every n seconds, a whole number means n images per second
	window_size = 20   # the number of images out of which we will choose the least blurry
	# video_list_file = "../video_list.csv"
	file_name = sys.argv[1]
	output_path = "../images/"
	# this creates a list of video objects, which are instances of the video object class defined above.
	# This class is basically a cv2 video object, plus some associated information we are keeping track of, like the video name, file path, etc.
	# the movies that will be added to the list are specified in the video list file
	# video_object_dict = get_video_object_list(video_list_file)
	video_object = VideoObject(file_name, output_path)
	# # for each video in the list, we are going to save frames from it according to the images_per_second variable
	# for video_name in video_object_dict:
	# 	video_object = video_object_dict[video_name]
	video_object.save_frames(images_per_second, window_size)
	


main()