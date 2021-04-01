# 配置与部署
如果你也想自己折腾一只小鱼，那么以下的内容可能会适合你；不过如果你不爱折腾，这些内容可能会让你比较通过。

## 前提条件
+   **必须**有一个持续开机的电脑或买一台服务器。
+   **必须**有一个能自动运行的联萌账号。
+   **建议**面对问题时保持探索精神和乐观的心态。
+   **最好**使用过一种QQ机器人的框架。

## 安装小鱼
+   安装`go-cqhttp`。
+   安装`Python 3.7.3+`。
+   安装依赖项:
```bash
    pip3 install -r requirements.txt # on *nix
    pip install -r requirements.txt # on Windows
```
+   根据[go-cqhttp](https://docs.go-cqhttp.org/)和[nonebot2](https://v2.nonebot.dev/)文档修改相关配置。
+   运行配置程序:
```bash
	python3 wizard.py # on *nix
    py -3 wizard.py # on Windows
```
+   运行小鱼:
```bash
    python3 bot.py # on *nix
    py -3 bot.py # on Windows
```

## 环境变量的进一步配置
+   所有环境变量均写入`.env`文件，通过`wizard.py`可以对以下环境变量进行配置:
```tex
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

除此以外，如果希望丰富小鱼的功能，还可以对其它环境变量进行手动配置:
```tex
	access_token # API上报密钥
	frequent_face_id # 常用QQ表情ID(用于变形复读时表情替换)
	database_compress_level # 数据库压缩程度(0-9, 默认为9)
	ftpts_max_number # 42点最大可选择数字
	ftpts_target # 42点目标数字
    ftpts_random_threshold # 42点目标阈值(该值越高, 目标不为42点可能性越大)
```

::: danger

请务必注意，环境变量中的数据**相当敏感**，**一定不要泄露给他人**！

:::

## 更精细的权限控制
+   为了使小鱼在不同的群内使用不同的功能，可以新建一个权限控制文件`policy.json`，内部的结构需要写成这样:
```json
	{
        "bot_id": {
            "group_id": {
                "command_name": {
                    "+": [1, 2, 3],
                    "-": [3, 4, 5],
                    "@": {
                        "day_of_week": "*",
                        "hour": 10,
                        "minute": 20,
                        "second": 30
                    }
                },
                "another_command_name": {
                    // write another configuration for a command
                }
            },
            "another_group_id": {
                // write another configuration for a group
            }
        },
        "another_bot_id": {
            // write another configuration for a bot
        }
	}
```

+   以下对上述配置文件的结构进行一些解释:
    +   配置文件中可以对每条小鱼所在的每个群组进行配置。其中小鱼需要提供其`bot_id`，即小鱼的QQ号，对于需要配置的每个群组，需要提供其`group_id`，即群号，对于需要配置的每个命令(组)，需要提供其`command_name`，一般情况下为每个插件的文件名。这一部分是配置的**宏观**部分，当需要配置指令时，必须准确填写。
    +   对于每个命令(组)，目前提供了三个选项(键)，**白名单筛选**，**黑名单筛选**和**广播时间控制**。白名单筛选需要采用`+`键配置，配置值为一个数组，其中包含所有在白名单中的用户QQ号。黑名单筛选需要采用`-`键配置，配置值为一个数组，其中包含所有在黑名单中的用户QQ号。广播时间控制需要采用`@`键配置，配置值为一个键值对，完全遵守`cron`语法规则。
    +   对于黑白名单筛选，当某用户**位于白名单且不位于黑名单**时，小鱼会响应用户指令。对于以上的例子，对于所有在`group_id`使用`bot_id`触发的`command_name`命令，小鱼只会响应QQ号为`1`或`2`的用户。如果不进行黑白名单筛选，小鱼默认相应所有用户的指令。
    +   对于广播时间控制，只有当前时间在控制时间范围内(误差为30秒)，小鱼才会广播相应的命令或执行相应操作。对于以上的例子，具有`bot_id`的小鱼会在每天的`10:20:30`，在`group_id`这个群中执行`command_name`相关的任务。
    +   此外，小鱼还提供了**简单识别配置**的功能，小鱼会获取`bot_id`，`group_id`和`command_name`非空的所有值，并将`bot_id`和`group_id`装配成一个元组，并将所有符合条件的元组构成一个列表。该功能目前只在`version`指令中使用到。

::: warning

权限配置较为复杂，而且向着越来越复杂的方向发展，仅建议在小范围(如`supercmd`等权限)内使用，项目本身不提供配置文件，通过`wizard.py`可以配置一些**广播时间控制**的默认值，其余部分仍需要自行编写。**强烈建议先通过`wizard.py`进行配置，这将对权限配置的格式有所帮助。**

此外，权限控制中存在所谓**临时权限**的规则，临时权限需要手动生成和手动清除，只在小鱼本次运行过程中保留，终止运行后就会自动清空。

请务必注意，权限配置文件中的数据**比较敏感**，**建议不要泄露给他人**！

:::

## 资源文件
+   资源文件由`csv`格式构成索引。每个资源由`资源内容`，`资源分类`，`资源是否为图片` 和 `加载权重`四个部分构成。示例资源文件如下：

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

## 数据库相关
+   数据库采用`gzip`压缩的`JSON`格式，将所有数据存放在一起。索引使用`universal_id`，当数据为共用的全局数据时，`universal_id = 0`，当数据为群组相关的局部数据时，`universal_id = 小鱼QQ号拼接群号`。

::: danger

由于作者能力有限，数据库的形式可能会不断变化，甚至出现版本间不兼容的情况，请谨慎开启数据库功能。

:::

## 测试
+   本项目提供了用于测试的`dev.py`文件，仅建议在**开发环境**中使用，它内置了`nonebot-plugin-test`插件，无需框架就可以测试大部分指令。
