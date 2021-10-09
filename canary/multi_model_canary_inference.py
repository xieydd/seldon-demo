import numpy as np
from matplotlib import pyplot as plt
import requests
import json
import os
import _pickle as cPickle


def load_data():
  """Loads the CIFAR10 dataset.
  This is a dataset of 50,000 32x32 color training images and 10,000 test
  images, labeled over 10 categories. See more info at the
  [CIFAR homepage](https://www.cs.toronto.edu/~kriz/cifar.html).
  The classes are:
  | Label | Description |
  |:-----:|-------------|
  |   0   | airplane    |
  |   1   | automobile  |
  |   2   | bird        |
  |   3   | cat         |
  |   4   | deer        |
  |   5   | dog         |
  |   6   | frog        |
  |   7   | horse       |
  |   8   | ship        |
  |   9   | truck       |
  Returns:
    Tuple of NumPy arrays: `(x_train, y_train), (x_test, y_test)`.
  **x_train**: uint8 NumPy array of grayscale image data with shapes
    `(50000, 32, 32, 3)`, containing the training data. Pixel values range
    from 0 to 255.
  **y_train**: uint8 NumPy array of labels (integers in range 0-9)
    with shape `(50000, 1)` for the training data.
  **x_test**: uint8 NumPy array of grayscale image data with shapes
    (10000, 32, 32, 3), containing the test data. Pixel values range
    from 0 to 255.
  **y_test**: uint8 NumPy array of labels (integers in range 0-9)
    with shape `(10000, 1)` for the test data.
  Example:
  ```python
  (x_train, y_train), (x_test, y_test) = keras.datasets.cifar10.load_data()
  assert x_train.shape == (50000, 32, 32, 3)
  assert x_test.shape == (10000, 32, 32, 3)
  assert y_train.shape == (50000, 1)
  assert y_test.shape == (10000, 1)
  ```
  """
  dirname = 'cifar-10-batches-py'
  path = os.path.join("../data/cifar10",dirname)

  num_train_samples = 50000

  x_train = np.empty((num_train_samples, 3, 32, 32), dtype='uint8')
  y_train = np.empty((num_train_samples,), dtype='uint8')

  for i in range(1, 6):
    fpath = os.path.join(path, 'data_batch_' + str(i))
    (x_train[(i - 1) * 10000:i * 10000, :, :, :],
     y_train[(i - 1) * 10000:i * 10000]) = load_batch(fpath)

  fpath = os.path.join(path, 'test_batch')
  x_test, y_test = load_batch(fpath)

  y_train = np.reshape(y_train, (len(y_train), 1))
  y_test = np.reshape(y_test, (len(y_test), 1))

  x_train = x_train.transpose(0, 2, 3, 1)
  x_test = x_test.transpose(0, 2, 3, 1)

  x_test = x_test.astype(x_train.dtype)
  y_test = y_test.astype(y_train.dtype)

  return (x_train, y_train), (x_test, y_test)

def load_batch(fpath, label_key='labels'):
  """Internal utility for parsing CIFAR data.
  Args:
      fpath: path the file to parse.
      label_key: key for label data in the retrieve
          dictionary.
  Returns:
      A tuple `(data, labels)`.
  """
  with open(fpath, 'rb') as f:
    d = cPickle.load(f, encoding='bytes')
    # decode utf8
    d_decoded = {}
    for k, v in d.items():
      d_decoded[k.decode('utf8')] = v
    d = d_decoded
  data = d['data']
  labels = d[label_key]

  data = data.reshape(data.shape[0], 3, 32, 32)
  return data, labels

def main():
    nums = 1000

    print("model1: half_plus_two start")
    # half_plus_two demo
    for chosen in range(nums):
        payload={"instances": [1.0, 2.0, 5.0]}

        url = 'http://%s/seldon/default/multi-model-tfserving-canary/v1/models/half_plus_two/:predict'%os.getenv("SELDON_URL")
        response = requests.post(
            url, json=payload
        )
        print(response.status_code)
    print("model1: half_plus_two end")

     cifar10 demo
    print("model2: cifar10 resnet32 start")
    for idx in range(10):
        train, test = load_data()
        X_test, y_test = test
        X_test = X_test.astype('float32') / 255
        print(X_test.shape, y_test.shape)
        class_names = ['airplane', 'automobile', 'bird', 'cat', 'deer',
               'dog', 'frog', 'horse', 'ship', 'truck']
        test_example=X_test[idx:idx+1].tolist()
        payload={"instances": test_example}

        url = 'http://%s/seldon/default/multi-model-tfserving-canary/v1/models/cifar10/:predict'%os.getenv("SELDON_URL")
        response = requests.post(
            url, json=payload
        )
        print(response.status_code)
        res=json.loads(response.text)
        print(res)
        arr=np.array(res["predictions"][0])
        X = X_test[idx].reshape(1, 32, 32, 3)
        plt.imshow(X.reshape(32, 32, 3))
        plt.axis('off')
        plt.show()
        print("class:",class_names[y_test[idx][0]])
        print("prediction:",class_names[arr.argmax()])
    print("model2: cifar10 resnet32 end")



if __name__ == '__main__':
    main()