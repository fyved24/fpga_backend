import math
import matplotlib.pyplot as plt  # 导入

import seaborn as sns

sns.set(color_codes=True)  # 导入seaborn包设定颜色
i = 0
X = []
Y = []
plt.ion()
while True:
    X.append(i)
    X = X[-100:]
    Y.append(5 * math.sin(i))
    Y = Y[-100:]
    print(X)
    plt.clf()
    plt.plot(X, Y)
    i += 0.1
    plt.pause(0.01)
    plt.ioff()
