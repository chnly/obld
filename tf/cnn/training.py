'''
download FashionMNIST data
and do a simple image classification
'''

import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import time


s_time = time.time()
print('current tensorflow version is: ', tf.__version__)

# load fashion mnist data
fashion_mnist = tf.keras.datasets.fashion_mnist
(train_images, train_labels), (test_images, test_labels) = fashion_mnist.load_data()

class_names = ['T-shirt/top', 'Trouser', 'Pullover', 'Dress', 'Coat',
               'Sandal', 'Shirt', 'Sneaker', 'Bag', 'Ankle boot']

# show test images
plt.figure(figsize=(10, 10))
for i in range(25):
    plt.subplot(5, 5, i+1)
    plt.xticks([])
    plt.yticks([])
    plt.grid(False)
    plt.imshow(train_images[i], cmap=plt.cm.binary)
    plt.xlabel(class_names[train_labels[i]])
plt.show()

# data normalization
train_images = train_images / 255.0
test_images = test_images / 255.0

# create model
model = tf.keras.Sequential([
    tf.keras.layers.Flatten(input_shape=(28, 28)),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dense(10)            # only calculates logits
])

model.compile(optimizer='adam',
              loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
              metrics=['accuracy'])
model.summary()
model.save('C:/tensorflowtest/tmp/model')
model.fit(train_images, train_labels, epochs=20)

test_loss, test_acc = model.evaluate(test_images,  test_labels, verbose=2)

print('\nTest accuracy:', test_acc)
print('use_time:', time.time() - s_time)


def timeit(func):
    def wrapper():
        s_time = time.time()
        res = func()
        print('use_time:', time.time() - s_time)
        return res
    return wrapper
