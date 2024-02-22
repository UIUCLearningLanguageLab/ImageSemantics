import os
import sys
image_semantics_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(image_semantics_dir)
from src.dataset import datasets


def main():
    split = False
    path = "../data"
    the_dataset = datasets.Dataset()
    the_dataset.add_sa_dataset(path)
    the_dataset.save_dataset(split_by_category=split)


main()
