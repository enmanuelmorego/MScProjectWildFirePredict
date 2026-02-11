import ee
import tensorflow as tf
import numpy as np
import os
from pathlib import Path
'''
for each image downloaded
'''
import tensorflow as tf

# fpath = "data/SentinelPixels/sentinel_patches_2019_01.tfrecord"
# raw_dataset = tf.data.TFRecordDataset(fpath)

# raw_record = next(iter(raw_dataset))

# example = tf.train.Example()
# example.ParseFromString(raw_record.numpy())

# print(example.features.feature.keys())



# fpath = Path('data/SentinelPixels/sentinel_patches_2019_01.tfrecord')

# # Arguments passed in function
# # fpath = 'data/SentinelPixels/sentinel_patches_2019_01.tfrecord.gz'
# raw_dataset = tf.data.TFRecordDataset(fpath)
# raw_record = next(iter(raw_dataset))
# feature_description = {
#     "grid_id": tf.io.FixedLenFeature([], tf.float32),
#     "date": tf.io.FixedLenFeature([], tf.string),
#     "patch": tf.io.FixedLenFeature([], tf.string),
# }
# example = tf.io.parse_single_example(raw_record, feature_description)

# grid_id = example["grid_id"].numpy()
# date    = example["date"].numpy().decode("utf-8")

# patch = tf.io.parse_tensor(example["patch"], out_type=tf.float32).numpy()
# print(grid_id, date)
# print(patch.shape, patch.dtype)
# import matplotlib.pyplot as plt
# import numpy as np

# rgb = patch[:, :, [2, 1, 0]]  # B4, B3, B2

# # simple normalisation for display
# rgb = rgb / np.percentile(rgb, 99)

# plt.figure(figsize=(4, 4))
# plt.imshow(np.clip(rgb, 0, 1))
# plt.title(f"grid {grid_id} | {date}")
# plt.axis("off")
# plt.show()



# for record in raw_dataset:
#     example = tf.train.Example()
#     example.ParseFromString(record.numpy())

#     grid_id = example.features.feature['grid_id'].int64_list.value[0]
#     date    = example.features.feature['date'].bytes_list.value[0].decode()

#     patch = tf.io.parse_tensor(
#         example.features.feature['patch'].bytes_list.value[0],
#         out_type=tf.float32
#   