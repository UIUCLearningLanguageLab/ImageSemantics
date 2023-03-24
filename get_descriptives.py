import os
import sys
image_semantics_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(image_semantics_dir)
from src.dataset import datasets


def main():
    overwrite_existing_data = True
    pickle_dataset_path = '../data/DTW1_2023_03_16_154635.pkl'
    analysis_path = '../analyses/DTW1_2023_03_16_154635.pkl'
    the_dataset = datasets.Dataset()
    the_dataset.load_dataset(pickle_dataset_path)
    the_dataset.output_descriptive_info(analysis_path, overwrite_existing_data)


if __name__ == "__main__":
    main()
