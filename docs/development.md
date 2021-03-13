# 开发指南

## 安装机器人
+ 安装`go-cqhttp`
+ 安装`Python 3.7+`
+ 安装依赖项
```
    pip/pip3 install -r requirements.txt
```
+ 根据[go-cqhttp](https://docs.go-cqhttp.org/)和[nonebot2](https://v2.nonebot.dev/)文档修改相关配置
+ 运行环境变量配置程序
```
	py -3/python3 wizard.py 
```
+ 运行机器人
```
    py -3/python3 bot.py
```

## 环境变量的进一步配置
+ 所有环境变量均写入`.env`文件，通过`wizard.py`可以对以下环境变量进行配置:
```
    host # 监听IP
    port # 监听端口
    debug # 调试模式
    superusers # 超级用户
    command_start # 命令识别前缀
    mswar_uid # 联萌关联账号
    autopvp_uid # 联萌autopvp账号
    mswar_token # 联萌关联账号登录token
    mswar_host # 联萌服务器地址与端口
    mswar_version # 联萌版本
    mswar_encryption_key # 联萌加密密钥
    mswar_decryption_key # 联萌解密密钥
    database_location # 本地数据库地址(建议以.gz结尾)
    policy_config_location # 本地配置文件地址(建议以.json结尾)
    resource_location # 本地资源索引文件地址(建议以.csv结尾)
```

除此以外，如果希望丰富机器人的功能，还可以对其它环境变量进行手动配置:
```
	access_token # API上报密钥
	frequent_face_id # 常用QQ表情ID(用于变形复读时表情替换)
	database_compress_level # 数据库压缩程度(0-9, 默认为9)
	ftpts_allowed_hours # 允许42点游戏的小时
	ftpts_max_number # 42点最大可选择数字
	ftpts_target # 42点目标数字
    ftpts_random_threshold # 42点目标阈值(该值越高, 目标不为42点可能性越大)
```

> 请务必注意，环境变量中的数据**相当敏感**，**一定不要泄露给他人**！

## 数据库相关
+ 数据库采用`JSON`格式，将所有数据存放在一起。索引使用`universal_id`，当数据为共用的全局数据时，`universal_id = 0`，当数据为群组相关的局部数据时，`universal_id = 机器人QQ号拼接群号`。

+ 从00:30:00开始，每两小时数据库将写入磁盘一次，超级管理员可以通过`save`指令手动存盘。

## 超级管理员相关
超级管理员可以执行较多核心控制权限:
+ 写入数据库
```
	save/存档
```

+ 查看复读状态
```
	repeaterstatus/复读状态
```

+ 手动开启42点
```
	manual42/手动42点
```

> 42点只要开始，在结束前就不能再次触发。

> 42点游戏频率及手工开启的权限默认为普通用户均可执行，需要进一步的权限配置。

## 更精细的权限控制
+ 为了使机器人在不同的群内使用不同的功能，可以新建一个权限控制文件`policy.json`，内部的结构需要写成这样:
```json
	{
		"qq_group_number": {
			"plugin_name": [ 1, 2, 3 ],
			"another_plugin_name": [ 4, 5, 6 ]
		}, 
		"another_qq_group_number": {
			"plugin_name": [ -1, -2, -3 ],
			"another_plugin_name": [ -4, -5, -6 ]
		}, 
	}
```

* `plugin_name`为`./mswar/plugins/*.py`中的文件名，`qq_group_number`里面写群号，`[ ... ]`里面写用户QQ号，对每个群组单独配置，并遵循如下规则:
	+ 如果机器人所在群组不在配置文件`qq_group_number`中，自动放行;
	+ 如果机器人所在群组在配置文件`qq_group_number`中，但所执行函数不在`plugin_name`中，自动放行;
	+ 如果机器人所在群组在配置文件`qq_group_number`中，所执行函数也在`plugin_name`中，根据用户QQ是否在允许/拒绝放行列表`[ ... ]`中进行放行，放行的规则为: 用户QQ在白名单中**或**不在黑名单中;
	+ 如果需要设置放行白名单，放行列表中的元素为**正值**; 如果需要设置放行黑名单，放行列表中的元素为**负值**;
	+ 当`qq_group_number`和`plugin_name`均已设置，定时触发的任务所在函数在`plugin_name`中时，自动**拒绝**放行;
	+ 在配置文件中**不能包含注释**，否则会解析错误。

> 此功能较为复杂，**不建议**使用，或者仅建议在小范围内使用，项目本身不提供配置文件，需要自行编写。

### 精细权限控制的例子
```json
	{
		"a0": {
			"b": [ 1 ],
			"c": [ 2 ],
			"d": [ -1 ],
			"e": [ ]
		}, 
		"a1": {}
	}
```

> 上述例子表明，机器人在`a0`群中，只响应用户`1`触发的`b`命令(准确是函数中包含的所有命令)，与用户`2`触发的`c`命令，只不响应用户`1`触发的`d`命令，同时响应**所有**用户触发的`e`命令，且如果`b, c, d, e`三个命令中含有定时命令，均不会被触发，其余命令没有限制，机器人在`a1`群中，响应用户的所有命令，机器人在其余加入的群中，响应用户的所有命令。

> 请务必注意，权限配置文件中的数据**相当敏感**，**一定不要泄露给他人**！

## 资源文件
+ 资源文件由`csv`格式构成索引。每个资源由`资源内容`，`资源分类`，`资源是否为图片` 和 `加载权重`四个部分构成。示例资源文件如下：

```csv
太强了|1|0|2
tql|1|0|2
冲鸭|1|0|1
！|-1|0|1
[CQ:face,id=41]|-1|0|1
加油鸭|2|0|3
加油冲鸭|2|0|1
💪|-2|0|1
！|-2|0|1
resource/exclaim/1.gif|1|1|1
```

## 测试
+ 本项目提供了用于测试的`dev.py`文件，仅建议在开发环境中使用，它内置了`nonebot-plugin-test`插件，无需框架就可以测试大部分指令。

## 协议
+ 本项目基于`AGPL 3.0`开源, 详细的协议见[这里](http://www.gnu.org/licenses/agpl-3.0.html)。

## 其它
+ 欢迎提出意见与贡献代码。
