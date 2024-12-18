import os
import sys
image_semantics_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(image_semantics_dir)
from src.dataset import datasets
from src.annotator import app


def main():
    path = '../data'

    the_dataset = datasets.Dataset()
    the_dataset.load_dataset(path)
    the_relabeler_app = app.RelabelerApp(the_dataset)
    the_relabeler_app.root.mainloop()


if __name__ == "__main__":
    main()
