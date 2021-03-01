import tensorflow as tf
import numpy as np
import time


s_time = time.time()
# load fashion mnist data
fashion_mnist = tf.keras.datasets.fashion_mnist
(train_images, train_labels), (test_images, test_labels) = fashion_mnist.load_data()

class_names = ['T-shirt/top', 'Trouser', 'Pullover', 'Dress', 'Coat',
               'Sandal', 'Shirt', 'Sneaker', 'Bag', 'Ankle boot']


# load model
loaded_model = tf.keras.models.load_model('C:/tensorflowtest/tmp/model')
# loaded_model = tf.keras.models.load_model('http://47.92.83.35/home/tensorflow/model')
# connect a softmax layer to the loaded model
probability_model = tf.keras.Sequential([loaded_model, tf.keras.layers.Softmax()])
predictions = probability_model.predict(test_images)

# verification
index = 0
print(f'prediction result is: {class_names[np.argmax(predictions[index])]}')
print(f'ground truth is {class_names[test_labels[index]]}')
for i in range(0, 3):
    print(i, 'The model thought this was a {} (class {}), and it was actually a {} (class {})'.format(
        class_names[np.argmax(predictions[i])],
        np.argmax(predictions[i]), class_names[test_labels[i]],
        test_labels[i]))

print('use_time:', time.time() - s_time)
