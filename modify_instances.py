from src.dataset import datasets


def main():
    dataset_path = '../data'

    new_dataset = datasets.Dataset()
    new_dataset.load_dataset(dataset_path)
    '''
    cloth_other,unsure,115
    human-made_object_other
    cloth_other,baby gym,8
    '''


    old = ('book', "jon's book 3")
    new = ('book', 'jons book')

    condition = (new_dataset.instance_df['category'] == old[0]) & \
                (new_dataset.instance_df['subcategory'] == old[1])
    new_dataset.instance_df.loc[condition, 'category'] = new[0]
    new_dataset.instance_df.loc[condition, 'subcategory'] = new[1]

    # condition = new_dataset.instance_df['category'] == old[0]
    # new_dataset.instance_df.loc[condition, 'category'] = new[0]

    new_dataset.generate_image_df()
    new_dataset.generate_category_df()
    new_dataset.generate_subcategory_df()

    new_dataset.save_dataset(split_by_category=True)
    new_dataset.print_subcategory_string()

if __name__ == "__main__":
    main()