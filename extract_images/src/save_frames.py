import cv2
import os
import time
import csv
import shutil


class VideoObject:

	def __init__(self, video_name):
		self.video_name = video_name
		self.mp4_path = '../mp4_videos/' + video_name
		self.image_path = '../images/' + video_name[:-4] + "/"
		self.timestamp_list = []
		self.image_list = []

		self.video = None
		self.fps = None
		self.frame_rate = None
		self.num_frames = None
		self.length = None

		self.create_directory()
		self.load_video()

	def create_directory(self):
		try:
			os.makedirs(self.image_path)
			success = True
		except:
			print("Could not make directory {}".format(self.image_path))
			success = False
		return success

	def load_video(self):
		self.video = cv2.VideoCapture(self.mp4_path)
		self.fps = self.video.get(cv2.CAP_PROP_FPS)
		self.frame_rate = round(self.fps)
		self.num_frames = int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))
		self.length = (self.num_frames/self.fps)/60

	def save_frames(self, images_per_second):

		success, image = self.video.read()
		count = 0
		while success:
			
			if (images_per_second == 0) or (count % (self.frame_rate/images_per_second) == 0):

				string_count = str(count)
				while len(string_count) < 6:
					string_count = "0" + string_count

				output_file = self.image_path+self.video_name[:-4]+"_"+string_count+'.jpg'
				cv2.imwrite(output_file, image)     # save frame as JPEG file
			success,image = self.video.read()
			count += 1

def get_video_object_list(video_list_file):
	video_object_dict = {}
	with open(video_list_file) as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=',')
		for row in csv_reader:
			new_video_object = VideoObject(row[0])
			video_object_dict[row[0]] = new_video_object
	return video_object_dict


def main():
	images_per_second = 1/5
	video_object_dict = get_video_object_list("../video_list1.csv")

	for video_name in video_object_dict:
		video_object = video_object_dict[video_name]
		video_object.save_frames(images_per_second)
	


main()