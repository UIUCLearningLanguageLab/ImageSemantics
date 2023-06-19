from superannotate import SAClient
import superannotate as sa


SA_TOKEN = "3bb8707e5efb0980f9f58e396a4666ebf6f8ed83409da10a20cbec5a7074f6df201b081a0502ef95t=4083"
sa_client = SAClient(SA_TOKEN)


sa_client.prepare_export(
    project = "first-round_child-2_DTW",
    folder_names = ["video-9_DTW_2022_01_04_1715", "video-10_DTW_2022_01_23_1332"])
