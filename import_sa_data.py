import os
import sys
image_semantics_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(image_semantics_dir)
from image_semantics.src.dataset import datasets


def main():
    sa_dataset_path = "superannotate_datasets/DTW"
    output_dataset_path = "data/DTW1"
    the_dataset = datasets.Dataset()
    the_dataset.load_sa_dataset(sa_dataset_path)
    the_dataset.save_dataset(output_dataset_path)


main()
