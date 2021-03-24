# heicore-suite
heicore-suite是一个黑曜石浏览器的子项目,它主要参考的是burp-suite

暂时使用eel实现界面和python的交互,前端使用vue,element-ui

## 运行方式
`pip install eel gevent`


```python
python main.py
```
然后就会打开edge浏览器到localhost:8000

代理监听在6666端口上

![Snipaste_2021-03-24_21-15-52](/assets/Snipaste_2021-03-24_21-15-52.png)

## 目录结构

`vue`:前端源码

`web`:构建出的前端文件

`HttpProxy.py`:http/https代理

`main.py`:使用eel开启前端以及和后端通信
