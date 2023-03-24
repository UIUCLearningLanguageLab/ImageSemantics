import os
import sys
image_semantics_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(image_semantics_dir)
from src.dataset import datasets
from src.relabeler import app

def main():
    pickle_data_path = '../data/DTW1_2023_03_16_154635.pkl'
    the_dataset = datasets.Dataset()
    the_dataset.load_dataset(pickle_data_path, "../")
    the_relabeler_app = app.RelabelerApp(the_dataset)
    the_relabeler_app.root.mainloop()

if __name__ == "__main__":
    main()


