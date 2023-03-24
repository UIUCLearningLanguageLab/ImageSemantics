from tkinter import N
from xml.etree.ElementInclude import include
import superannotate as sa
from superannotate import SAClient
import os
import json
import numpy as np


def get_annotated_images(team_1, project_name, path_header, user_list, image_list):

    for user_name in user_list:
        image_path = project_name + "/" + path_header + "_" + user_name
        try:
            os.mkdir("../images/" + user_name)
        except:
            pass
        for image in image_list:
            try:
                team_1.download_image(project=image_path, 
                                image_name=image,
                                local_dir_path = '../images/'+user_name,
                                include_annotations=True,
                                include_overlay=True)
            except:
                print("WARNING: No image {} for User {}".format(image, user_name))


def get_instance_count_matrix(user_list, image_list, category_index_dict):

    instance_count_matrix = np.zeros([len(user_list), len(image_list), len(category_index_dict)], int)

    for i in range(len(user_list)):
        user_name = user_list[i]
        for j in range(len(image_list)):
            image_name = image_list[j]
            json_path = '../images/'+ user_name + "/" + image_name + "___pixel.json"
            
            if os.path.exists(json_path):
                with open(json_path, 'r') as json_file:
                    json_data = json.loads(json_file.read())
                instance_data = json_data["instances"]

                for instance in instance_data:
                    k = category_index_dict[instance['className']]
                    instance_count_matrix[i,j,k] += 1
            
    return instance_count_matrix


def create_html(user_list, image_list, instance_count_matrix, category_index_dict):
    w = 1920*.25
    h = 1080*.25

    for j in range(len(image_list)):
        image_name = image_list[j]

        current_image_count_matrix = instance_count_matrix[:,j,:]

        f = open("../html/{}.htm".format(image_name[:-4]), "w")
        html_text = '<html>\n'
        html_text += '<title>{}</title>\n'.format(image_name[:-4] + " Annotations")
        html_text += '<table>\n'
        html_text += '<tr>\n'
        for i in range(len(user_list)):
            html_text += '<td>{}</td>'.format(user_list[i])
        html_text += '</tr>\n'
        html_text += '<tr>\n'
        for i in range(len(user_list)):
            image_path = "../images/{}/{}".format(user_list[0], image_name)
            html_text += '<td><img width={} height={} image_semantics="{}"></td>\n'.format(w, h, image_path)
        html_text += '</tr>\n'
        html_text += '<tr>\n'
        for i in range(len(user_list)):
            image_path = "../images/{}/{}___fuse.png".format(user_list[i], image_name)
            html_text += '<td><img width={} height={} image_semantics="{}"></td>\n'.format(w, h, image_path)
        html_text += '</tr>\n'
        html_text += '<tr>\n'
        for i in range(len(user_list)):
            html_text += '<td>'
            for category, k in category_index_dict.items():
                if instance_count_matrix[i,j,k] > 0:

                    html_text += '{}: {}<br>'.format(category, instance_count_matrix[i,j,k])
            html_text += '</td><\n'
        html_text += '</tr>\n'
        html_text += "</html>\n"

        f.write(html_text)
        f.close()


def load_categories():
    n = 0
    category_index_dict = {}
    f = open("../data/categories.csv")
    for line in f:
        data = line.strip().strip('\n').strip()
        category_index_dict[data] = n 
        n += 1
    f.close()
    return category_index_dict


def main():
    token = "e73b2267ee343392e8df24368b7388ccb1cd041f44033b20a7226305717c00eacdd36dd9bdfd8b76t=4083"
    team_1 = SAClient()
    project_name = '2022-4fall_training_sets'
    user_list = ['dan', 'dita', 'heeva', 'michael']
    image_list = ['DTW_2021_12_30_1735_001500.jpg',
                'DTW_2021_12_31_1102_002550.jpg',
                'DTW_2021_12_31_1102_024150.jpg',
                'DTW_2022_01_01_1630_025500.jpg',
                'DTW_2022_01_03_1640_009119.jpg',
                'DTW_2022_01_03_1640_020720.jpg',
                'DTW_2022_01_16_1430_000525.jpg',
                'DTW_2022_01_16_1430_006762.jpg',
                'DTW_2022_01_16_1430_011790.jpg',
                'DTW_2022_01_16_1430_018390.jpg',
                'DTW_2022_01_16_1430_021086.jpg']
    path_header = "set3"

    get_annotated_images(team_1, project_name, path_header, user_list, image_list)
    category_index_dict = load_categories()
    instance_count_matrix = get_instance_count_matrix(user_list, image_list, category_index_dict)
    create_html(user_list, image_list, instance_count_matrix, category_index_dict)


if __name__ == "__main__":
    main()


