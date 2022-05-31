import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import numpy
import os
from PIL import Image
import matplotlib.pyplot as plt
from math import ceil

# START CONFIG

VAL_ACCURACY_TARGET = 0.98
# num of images MUST BE >= BATCH_SIZE * EPOCHS * STEPS
BATCH_SIZE = 40
EPOCHS = 65
STEPS = max(EPOCHS // BATCH_SIZE, 1)
REPEATS = 25
SEED = 100

VALIDATION_SPLIT = 0.1

IMAGE_SIZE = (50, 50)
CLASS_MODE = "categorical"
LOSS = "categorical_crossentropy"
INTERPOLATION = "nearest"
OPTIMIZER = tf.keras.optimizers.Nadam()
METRICS = ["accuracy"]
MODEL = tf.keras.models.Sequential(
    [
        tf.keras.layers.Rescaling(1.0 / 255, input_shape=(*IMAGE_SIZE, 3)),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(160, activation="relu"),
        tf.keras.layers.Dense(80, activation="relu"),
        tf.keras.layers.Dense(40, activation="softmax"),
    ]
)

# END CONFIG

PATH = os.getcwd()
TRAIN_PATH = os.path.join(PATH, "train")
VALIDATION_PATH = os.path.join(PATH, "validation")


class AccuracyCallback(tf.keras.callbacks.Callback):
    def on_epoch_end(self, epoch, logs={}):
        if logs.get("val_accuracy") >= VAL_ACCURACY_TARGET:
            print(
                f"Reached {round(logs.get('accuracy'), 4)} accuracy. Cancelling training."
            )
            self.model.stop_training = True


# train_datagen = ImageDataGenerator(
#     rescale=1 / 255,
#     validation_split=VALIDATION_SPLIT,
#     width_shift_range=0.1,
#     height_shift_range=0.1,
#     fill_mode="nearest",
# )
train_generator = tf.keras.utils.image_dataset_from_directory(
    TRAIN_PATH,
    validation_split=VALIDATION_SPLIT,
    label_mode=CLASS_MODE,
    image_size=IMAGE_SIZE,
    interpolation=INTERPOLATION,
    batch_size=BATCH_SIZE,
    seed=SEED,
    subset="training",
)
validation_generator = tf.keras.utils.image_dataset_from_directory(
    TRAIN_PATH,
    validation_split=VALIDATION_SPLIT,
    label_mode=CLASS_MODE,
    image_size=IMAGE_SIZE,
    interpolation=INTERPOLATION,
    batch_size=BATCH_SIZE,
    seed=SEED,
    subset="validation",
)

print(train_generator.element_spec)

# train_generator = train_datagen.flow_from_directory(
#     TRAIN_PATH,
#     target_size=IMAGE_SIZE,
#     batch_size=BATCH_SIZE,
#     class_mode=CLASS_MODE,
#     seed=SEED,
# )
# validation_generator = train_datagen.flow_from_directory(
#     TRAIN_PATH,
#     target_size=IMAGE_SIZE,
#     batch_size=BATCH_SIZE,
#     class_mode=CLASS_MODE,
#     seed=SEED,
#     subset="validation",
# )

# I can't find a way to pull the number of images directly from the generators- which is stupid because they output it to console
# this repeat stuff just outright doesn't work, even if I pass in the correct amount of repeats.
# files = 0
# for dir in os.listdir(TRAIN_PATH):
#     files += len(os.listdir(os.path.join(TRAIN_PATH, dir)))
# repeats = ceil((STEPS * EPOCHS * BATCH_SIZE) / files)
# print(f"Using {repeats} repeats of training data")

# train_generator.repeat(count=repeats)
# validation_generator.repeat(count=repeats)

MODEL.compile(loss=LOSS, optimizer=OPTIMIZER, metrics=METRICS)

history = MODEL.fit(
    train_generator,
    validation_data=validation_generator,
    verbose=2,
    epochs=EPOCHS,
    steps_per_epoch=STEPS,
    callbacks=[AccuracyCallback()],
)
acc = history.history["accuracy"]
val_acc = history.history["val_accuracy"]
loss = history.history["loss"]
val_loss = history.history["val_loss"]

for i in range(REPEATS - 1):
    if val_acc[-1] > VAL_ACCURACY_TARGET:
        break

    print(f"Repeat {i+1}")
    repeat_history = MODEL.fit(
        train_generator,
        validation_data=validation_generator,
        verbose=2,
        epochs=EPOCHS,
        steps_per_epoch=STEPS,
        callbacks=[AccuracyCallback()],
    )
    acc += repeat_history.history["accuracy"]
    val_acc += repeat_history.history["val_accuracy"]
    loss += repeat_history.history["loss"]
    val_loss += repeat_history.history["val_loss"]

epochs = range(len(acc))

plt.plot(epochs, acc, "bo", label="Training accuracy")
plt.plot(epochs, val_acc, "b", label="Validation accuracy")
plt.title("Training and validation accuracy")
plt.legend()

plt.figure()

plt.plot(epochs, loss, "bo", label="Training Loss")
plt.plot(epochs, val_loss, "b", label="Validation Loss")
plt.title("Training and validation loss")
plt.legend()

plt.show()

MODEL.save(os.path.join(PATH, "model"))
