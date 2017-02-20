import numpy as np

x = np.random.randint(low=0, high=10, size=(100, 10), dtype=int)
y = np.random.randint(low=0, high=10, size=(100, 10), dtype=int)


print (x * y).shape
