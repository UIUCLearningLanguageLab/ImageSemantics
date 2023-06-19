

def get_descriptives(the_dataset, output_path, overwrite_existing_data=False):
    pickle_dataset_path = '../data/DTW1_2023_03_16_154635.pkl'
    analysis_path = '../analyses/DTW1_2023_03_16_154635'
    the_dataset.output_descriptive_info(analysis_path, overwrite_existing_data)