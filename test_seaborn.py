import math
import matplotlib.pyplot as plt  # 导入

import seaborn as sns

sns.set(color_codes=True)  # 导入seaborn包设定颜色
i = 0
Y = []
plt.ion()
while True:

    Y.append(5 * math.sin(i))
    Y = Y[-100:]
    plt.clf()
    plt.plot(Y)
    i += 0.1
    plt.pause(0.01)
    plt.ioff()
