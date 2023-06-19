import os
import sys
image_semantics_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(image_semantics_dir)
from src.dataset import datasets
from src.relabeler import app


def main():
    pickle_data_path = '../data/DTW1_2023_04_10_191348.pkl'
    the_dataset = datasets.Dataset()

    the_dataset.load_dataset(pickle_data_path, "../superannotate_datasets/DTW/")
    print(the_dataset.image_dict[the_dataset.image_name_list[0]].name)
    print(the_dataset.image_dict[the_dataset.image_name_list[0]].path)
    print(the_dataset.image_dict[the_dataset.image_name_list[0]].json_file_name)
    the_relabeler_app = app.RelabelerApp(the_dataset)
    the_relabeler_app.root.mainloop()


if __name__ == "__main__":
    main()


