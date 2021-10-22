# FPAG backend

## 架构

```
                                         +-------------------------+                                             +-------------------------+
                                         |                         |                                             |                         |
                              +----------+                         +------+                                      | websocket server        |
                              |          |    main process         |      |                 +------------------> |                         |
                              |          |                         |      |                 |                    |                         |
                              |          +-------------------------+      |                 |                    +-------------+-----------+
                              |                                           |                 |                                  |
                              |                                           |                 |                                  |
                 +------------+----------+                   +------------+----+            |                                  |
                 |       thread          |                   |    thread       |            |                                  |
+--------+       |     serial listener   |     +--------+    |                 |            |                                  |
|       +---------------------+--------------> | queue  +--->+  db writer      |            |                                  v
| serial |       |            |          |     +--------+    |                 |            |
+--------+       +--------+--------+-----+                   +-----------------+    +-------+-------+                    +------------------+
                          |   |    |                                                |               |                    |                  |
                          |  hook  +----------------------------------------------->+ ws client     |                    |                  |
                          +---+----+                                                |               |                    | ws client        |
                              v                                                     +---------------+                    |                  |
                                                                                                                         +------------------+

```

## 通信方式

### 前后端

#### 前端发送

| 作用           | 格式                        | 备注                              |
| -------------- | --------------------------- | --------------------------------- |
| 控制示波器模式 | {type: 'model', data: 1/2}  |                                   |
| 阈值电压       | {type: 'voltage', data: 5}  |                                   |
| 时钟频率       | {type: 'clock', data: 1000} | 每个单位代表1k hz，数值1000代表1M |

#### 后端发送

| 作用           | 格式                                                  | 备注                             |
| -------------- | ----------------------------------------------------- | -------------------------------- |
| 示波器数据     | {type: 1, data: [{ch: 1,  num: 5}, {ch: 1,  num: 5}]} |                                  |
| 逻辑分析仪数据 | {type: 2, data: []}                                   |                                  |
| 周期           | {type: 3, data: {peroid: 1000}}                       | 每个单位代表1ms ，数值1000代表1s |
| 峰峰值         | {type: 3, data: {vpp:  5.00}}                         | 电压                             |

> type3 的数据会在一起发出去
>
> {type: 3, data: {peroid: 1000, vpp:  5.00}}

### 后端与开发板

#### 后端发送

| 作用             | 格式       | 备注 |
| ---------------- | ---------- | ---- |
| 进入示波器模式   | 0f ff    |      |
| 进入逻辑分析模式 | 0f ff      |      |
| 时钟分频的倍数   | f- -- 0- -- | f123 0456 那么时钟分频为十六进制123456 |
| 阈值电压 | 1- -- | 低12位代表阈值电压，不发送的话就是默认电压 |

#### 开发板发送

| 作用      | 格式                 | 备注 |
| --------- | -------------------- | ---- |
| 通道1数据 | 000- ----   010- ---- |      |
| 通道2数据 | 100- ----   110- ---- | |
| 通道1数据 逻辑分析 | 000- ----   010- ---- | 每一位代表一个0/1 |
| 通道2数据 逻辑分析 | 100- ----   110- ---- | 每一位代表一个0/1 |



