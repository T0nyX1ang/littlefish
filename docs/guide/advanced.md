# 配置与部署

如果你也想自己折腾一只小鱼，那么以下的内容可能会适合你，否则请直接忽略这一部分的内容。

## 前提条件

- **必须**有一个持续开机的电脑或买一台服务器。
- **必须**有一个能自动运行的联萌账号。
- **建议**面对问题时保持探索精神和乐观的心态。
- **最好**使用过一种 QQ 机器人的框架。

## 安装小鱼

- 安装`go-cqhttp`(很可能不可用)。
- 安装`Python 3.8+`。
- 安装依赖项:

    === "Windows"

        ```bash
        pip install -r requirements.txt
        ```

    === "\*nix"

        ```bash
        pip3 install -r requirements.txt
        ```

- 根据[go-cqhttp](https://docs.go-cqhttp.org/)和[nonebot2](https://v2.nonebot.dev/)文档修改相关配置。
- 运行配置程序:

    === "Windows"

        ```bash
        py -3 wizard.py
        ```

    === "\*nix"

        ```bash
        python3 wizard.py
        ```

- 运行小鱼:

    === "Windows"

        ```bash
        py -3 bot.py
        ```

    === "\*nix"

        ```bash
        python3 bot.py
        ```

## 环境变量的进一步配置

- Nonebot 相关环境变量:

  - `host`: 监听 IP :material-checkbox-marked-circle:
  - `port`: 监听端口 :material-checkbox-marked-circle:
  - `superusers`: 超级用户 :material-checkbox-marked-circle:
  - `access_token`: API 上报密钥

- 联萌相关环境变量:

  - `mswar_uid`: 联萌关联账号 :material-checkbox-marked-circle:
  - `autopvp_uid`: 联萌 autopvp 账号 :material-checkbox-marked-circle:
  - `superusers`: 联萌关联账号登录 token :material-checkbox-marked-circle:
  - `mswar_host`: 联萌服务器地址与端口 :material-checkbox-marked-circle:
  - `mswar_version`: 联萌版本 :material-checkbox-marked-circle:
  - `mswar_encryption_key`: 联萌加密密钥 :material-checkbox-marked-circle:
  - `mswar_decryption_key`: 联萌解密密钥 :material-checkbox-marked-circle:

- 本地数据库环境变量:

  - `database_location`: 本地数据库地址(建议以`.gz`结尾) :material-checkbox-marked-circle:
  - `database_compress_level`: 数据库压缩程度(0-9, 默认为`9`)
  - `database_backup_max_storage`: 数据库最大备份数目(正整数, 小于等于 0 时不限制备份数, 默认为`0`)

- 本地资源库环境变量:

  - `resource_location`: 本地资源索引文件地址(建议以`.csv`结尾) :material-checkbox-marked-circle:
  - `resource_separator`: 资源文件分隔符(默认为`|`)
  - `frequent_face_id`: 常用 QQ 表情 ID，用于变形复读时表情替换(默认为`[146]`)

- 权限配置环境变量:

  - `policy_config_location`: 本地配置文件地址(建议以`.json`结尾) :material-checkbox-marked-circle:

- 42 点小游戏环境变量:
  - `ftpts_max_number`: 42 点最大可选择数字(默认为`13`)
  - `ftpts_target`: 42 点目标数字(默认为`42`)
  - `ftpts_random_threshold`: 42 点目标阈值，该值越高, 目标不为 42 点可能性越大(默认为`0.0025`)

!!! tip

    以上环境变量中，末尾含有:material-checkbox-marked-circle:的环境变量可以使用`wizard.py`进行配置，其余环境变量必须手动配置。

!!! danger

    请务必注意，环境变量中的数据**相当敏感**，**一定不要泄露给他人**！

## 更精细的权限控制

- 为了使小鱼在不同的群内使用不同的功能，需要新建一个权限控制文件`policy.json`，内部的结构需要写成这样:

``` json
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
                },
                "@.another": {
                    "hour": 20,
                    "minute": 30,
                    "second": 40
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

- 以下对上述配置文件的结构进行一些解释:
  - 配置文件中可以对每条小鱼所在的每个群组进行配置。其中小鱼需要提供其`bot_id`，即小鱼的 QQ 号，对于需要配置的每个群组，需要提供其`group_id`，即群号，对于需要配置的每个命令(组)，需要提供其`command_name`，一般情况下为每个插件的文件名。这一部分是配置的**宏观**部分，当需要配置指令时，必须准确填写。
  - 对于每个命令(组)，目前提供了三个选项(键)，**白名单筛选**，**黑名单筛选**和**广播时间控制**。白名单筛选需要采用`+`键配置，配置值为一个数组，其中包含所有在白名单中的用户 QQ 号。黑名单筛选需要采用`-`键配置，配置值为一个数组，其中包含所有在黑名单中的用户 QQ 号。广播时间控制需要采用`@`键配置(或自定义键配置，并在程序中显式指明配置内容)，配置值为一个键值对，完全遵守`cron`语法规则。
  - 对于黑白名单筛选，当某用户**位于白名单且不位于黑名单**时，小鱼会响应用户指令。对于以上的例子，对于所有在`group_id`使用`bot_id`触发的`command_name`命令，小鱼只会响应 QQ 号为`1`或`2`的用户。如果不进行黑白名单筛选，小鱼默认相应所有用户的指令。
  - 对于广播时间控制，只有当前时间在控制时间范围内(误差为 30 秒)，小鱼才会广播相应的命令或执行相应操作。对于以上的例子，具有`bot_id`的小鱼会在每天的`10:20:30`和`20:30:40`，在`group_id`这个群中执行`command_name`相关的两个不同任务。
  - 此外，小鱼还提供了**简单识别配置**的功能，小鱼会获取`bot_id`，`group_id`和`command_name`非空的所有值，并将`bot_id`和`group_id`装配成一个元组，并将所有符合条件的元组构成一个列表。该功能目前只在`version`指令中使用到。

!!! warning

    权限配置较为复杂，而且向着越来越复杂的方向发展，仅建议在小范围(如`supercmd`等权限)内使用，项目本身不提供配置文件，通过`wizard.py`可以配置一些**广播时间控制**的默认值，其余部分仍需要自行编写。**强烈建议先通过`wizard.py`进行配置，这将对权限配置的格式有所帮助。**

    此外，权限控制中存在所谓**临时权限**的规则，临时权限需要手动生成和手动清除，只在小鱼本次运行过程中保留，终止运行后就会自动清空。

    请务必注意，权限配置文件中的数据**比较敏感**，**建议不要泄露给他人**！

## 资源文件

- 为了使小鱼表达能力更强，需要新建一个资源文件`resource.csv`，每个资源条目由`资源内容`，`资源分类`，`资源是否为图片` 和 `加载权重`四个部分构成。示例资源文件如下：

``` csv
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

- 以下进一步解释资源文件中的细节:
  - `资源内容`为纯文本形式，支持除图片与音频以外的所有 CQ 码格式，图片 CQ 码格式将单独处理，音频 CQ 码格式暂不支持。
  - `资源分类`为一个字符串，小鱼在构建资源数据库时，会将同类的资源自动整合到一起。目前小鱼用到的分类号为`1`(膜佬)，`2`(加油)，`3`(输入错误)，`4`(打断复读)，`10~19`(基于时间的打招呼)。
  - `资源是否为图片`为布尔型变量(填写`0`或`1`即可)，决定是否将`资源内容`中的文件转化为图片型 CQ 码。小鱼会基于运行路径进行自动转化，所以如果资源为图片，不需要在`资源内容`中给出 CQ 码，只需要给出文件**相对于小鱼的**路径即可。
  - `加载权重`为正整数，决定资源被发送的概率，权重越大，被发送的概率越大。
  - 在不发送图片时，基于资源文件的消息由三部分组成: `作用对象称谓`，`消息体`和`消息尾`。目前设计分类时，`消息体`和`消息尾`需要保持相同的分类号，且`消息尾`的分类号前面需要加入`-`进行标识，具体操作已经在示例资源文件中指出，此处不再赘述。

!!! tip

    由于 CQ 码中含有逗号，资源文件中的默认分隔符为`|`，可以通过`resource_separator`这一配置项进行修改。

## 数据库相关

- 数据库采用`gzip`压缩的`JSON`格式，将所有数据存放在一起。索引使用`universal_id`，当数据为共用的全局数据时，`universal_id = 0`，当数据为群组相关的局部数据时，`universal_id = 小鱼QQ号拼接群号`。
- 每次写入数据库时，小鱼会对当前数据进行全量备份，可以通过设置`database_backup_max_storage`限制最大备份数目。

!!! danger

    由于作者能力有限，数据库的形式可能会不断变化，甚至出现版本间不兼容的情况，请谨慎开启数据库功能。

## B 站直播推送相关

- 直播推送采用了双队列模式，即**群组内部的订阅队列**和**全局的订阅队列**。群组内部队列只负责从全局队列中取数据，而全局队列需要负责从 B 站获得用户的直播状态。
- 为了减少被风控的风险，本推送功能完全采用了线性的查询方式，对于全局队列而言，每 20 秒只对一个 UID 发送查询请求，并更新其状态。
- 为了减少查询流量，除队列元素更新以外，内部队列不进行任何网络访问。同时，小鱼采用了活跃度机制，每次全局队列的 UID 更新状态时，会检查其活跃度，当活跃度小于或等于 0 时，小鱼会将该 UID 移除全局队列；更新状态完成后，小鱼将降低`1点`该 UID 活跃度；而内部队列查询全局队列中的 UID 信息时，将恢复该 UID 的活跃度至`5点`。所以在权限控制中设置群组内部查询频率时，需要保证查询间隔小于`2分钟`。当然，建议将权限控制写为如下形式:

``` json hl_lines="5-11"
{
    "bot_id": {
        "group_id": {
            // other command plugins
            "bilipush": {
                "@": {
                    "hour": "8-23",
                    "minute": "*",
                    "second": "*/20"
                }
            }
            // other command plugins
        }
    }
}
```
