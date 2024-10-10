import os
import sys
import numpy as np
import copy
image_semantics_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(image_semantics_dir)
from src.dataset import datasets


def main():

    np.set_printoptions(precision=3, suppress=True)
    json_path = '../data/'
    the_dataset = datasets.Dataset()
    the_dataset.load_dataset(json_path)
    print(len(the_dataset.instance_df))

    bounding_box_filtered_dataset = copy.deepcopy(the_dataset)
    bounding_box_filtered_dataset.filter_dataset(bounding_box=False, big_object=True, infant_touching=False)
    bounding_box_filtered_dataset.save_dataset(file_name="bounding_box_filtered")


if __name__ == "__main__":
    main()
