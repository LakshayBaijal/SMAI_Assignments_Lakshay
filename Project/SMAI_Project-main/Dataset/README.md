### Dataset 

(Already converted from TTNet JSON Format to YOLO Label Img format)

```bash
https://www.kaggle.com/datasets/svmohitkumar/smai-project-dataset
```

# else


Run python codes {Found in codes/dataset_generation -

- download_dataset.py
- extract_all_images.py or extract_selected_images.py {any one}
- convert_ball_to_yolo.py

Download_Dataset.py will download data from TTNet official site ( 120 + FPS, around 40 GB)

extract_all_images.py will extract all frames from TTNet video that was downloaded. 

extract_selected_images.py will extract selected frames from TTNet video that was downloaded.

convert_ball_to_yolo.py will change from JSON format to YOLO data labels and images.


