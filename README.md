## 微信聊天记录分析报告非官方版

## 注意事项 / Attention, Please！

1. 使用本项目至少拥有一台 iOS /iPadOS 设备，如果只是安卓用户，可能会浪费你的时间。
2. 需要有耐心等待不确定的备份时间，一般在几个小时以上，并且有重来一次的决心。
3. 聊天记录备份及详细的技术细节请参照博客[《微信聊天记录分析报告？看看你们平时都聊些啥》](https://www.xyzlab.ai/2022-02-18-1d99dd9f6e1d/)。

## 使用方法 / Usage

1. Clone 本仓库到本地

```bash
git clone https://github.com/VXenomac/DS_Store_Cleaner.git
```

2. 安装项目依赖

```bash
pip install -r requirements.txt # 安装项目依赖
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple # 如果安装比较慢可以使用清华源安装
```

3. 修改 analyser.py 中的文件夹路径

```python
folder = '' # 替换为导出联系人的文件夹名称
```

4. 运行 analyser.py

```bash
python analyser.py
```

运行完后你会得到如下的结果：

![](https://raw.githubusercontent.com/VXenomac/wechat-chat-history-analyser/main/assets/demo.jpeg)

