from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.preprocessing import image
from tensorflow.keras.optimizers import RMSprop
import matplotlib.pyplot as plt
import tensorflow as tf
import numpy as np
import cv2
import os

### config

PATH = os.getcwd()
TRAIN_PATH = os.path.join(PATH, "train")
VALIDATION_PATH = os.path.join(PATH, "validation")
BATCH_SIZE = 10
BATCHES = 30
INPUT_SHAPE = (50, 50, 3)
METRICS = ["accuracy"]

MODEL = tf.keras.models.Sequential(
    [
        tf.keras.layers.Flatten(input_shape=INPUT_SHAPE),
        tf.keras.layers.Dense(128, activation="relu"),
        tf.keras.layers.Dense(6),
    ]
)

### end config

train = ImageDataGenerator(rescale=1 / 255)
validation = ImageDataGenerator(rescale=1 / 255)

train_dataset = train.flow_from_directory(
    TRAIN_PATH, target_size=INPUT_SHAPE[:2], batch_size=BATCH_SIZE, class_mode="binary"
)
validation_dataset = train.flow_from_directory(
    VALIDATION_PATH,
    target_size=INPUT_SHAPE[:2],
    batch_size=BATCH_SIZE,
    class_mode="binary",
)

MODEL.compile(
    loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
    optimizer="adam",
    metrics=METRICS,
)


model_fit = MODEL.fit(
    train_dataset,
    steps_per_epoch=BATCH_SIZE,
    epochs=BATCHES,
    validation_data=validation_dataset,
)


# TESTING ACCURACY

test_images = train.flow_from_directory(
    "test", target_size=INPUT_SHAPE[:2], batch_size=BATCH_SIZE, class_mode="binary"
)

loss, acc = MODEL.evaluate(test_images, verbose=2)
