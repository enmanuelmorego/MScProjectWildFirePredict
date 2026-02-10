import ee
import tensorflow as tf
import numpy as np
'''
for each image downloaded
'''
# Arguments passed in function
fpath = 'data/SentinelPixels/sentinel_patches_2019_01.tfrecord.gz'
raw_dataset = tf.data.TFRecordDataset("sentinel_patches_2019_01.tfrecord")

# for record in raw_dataset:
#     example = tf.train.Example()
#     example.ParseFromString(record.numpy())

#     grid_id = example.features.feature['grid_id'].int64_list.value[0]
#     date    = example.features.feature['date'].bytes_list.value[0].decode()

#     patch = tf.io.parse_tensor(
#         example.features.feature['patch'].bytes_list.value[0],
#         out_type=tf.float32
#     ).numpy()
