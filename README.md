# ControlSpeed  
这项目是用来控制函数调用的频率, 不仅支持本地的同步线程模式, 而且支持分布式模式. 
[更多开发描述,请点击链接](http://xiaorui.cc)

#Usage:

装饰器使用方法
```
from controlspeed import ControlSpeed
@ControlSpeed(max_calls=10, period=1.0)
def do_something():
    pass
```

with关键词控制上下文
```
from controlspeed import ControlSpeed
rate = ControlSpeed(max_calls=10, period=1.0)
for i in range(100):
    with rate:
        do_something()
```

支持回调函数的控速
```
from controlspeed import ControlSpeed
import time
def limited(until):
    duration = int(round(until - time.time()))
    print 'Speed limited, sleeping for %d seconds' % duration

rate = ControlSpeed(max_calls=2, period=3, callback=limited)
for i in range(3):
    with rate:
        print i
```
