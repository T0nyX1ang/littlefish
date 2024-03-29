# 功能与指令

本节仅包含对触发语法的简要介绍，不包含对函数与设计思路的详细说明。以下指令中，`/`表示等价的命令名称，请务必注意每个参数与命令之间需要`空格`间隔。扫雷联萌简称为`联萌`，中国扫雷网简称为`雷网`。为了输入方便，小鱼为每条指令设计了中英文两个版本，两个版本命令相互兼容。

## 指令权限简介

小鱼的指令支持群聊或者私聊，其支持的类型会以如下形式表现：

- 支持私聊的指令 :material-account:
- 支持群聊的指令 :material-account-group:
- 同时支持私聊与群聊的指令 :material-account: :material-account-group:

为尽可能防止功能滥用，小鱼针对**在群聊中触发的**每个指令有相应的触发权限，这些权限会以如下形式表现:

- 普通用户(小鱼无需权限)即可触发的权限 :material-circle:{.green_circle}
- 小鱼为管理员或特殊用户才能触发的权限 :material-circle:{.yellow_circle}
- 超级用户才可触发的权限 :material-circle:{.red_circle}
- 广播权限 :material-fish:{.blue_fish}

!!! warning

    目前针对私聊暂未设计相应权限，请勿恶意发起大量查询。以后可能会加入指令触发频率限制的功能，进一步防止功能滥用。

## 指南功能

- 显示此指南网址。 :material-account: :material-account-group: :material-circle:{.green_circle}

    === "中文指令"

        ```tex
        指南
        ```

    === "英文指令"

        ```tex
        guide
        ```

- 显示项目源代码地址。 :material-account: :material-account-group: :material-circle:{.green_circle}

    === "中文指令"

        ```tex
        源码
        ```

    === "英文指令"

        ```tex
        source
        ```

- 显示联萌安装包下载地址。 :material-account: :material-account-group: :material-circle:{.green_circle}

    === "中文指令 1"

        ```tex
        安装包
        ```

    === "中文指令 2"

        ```tex
        安装链接
        ```

    === "英文指令"

        ```tex
        getpackage
        ```

- 显示扫雷指南。 :material-account: :material-account-group: :material-circle:{.green_circle}

    === "中文指令"

        ```tex
        扫雷指南
        ```

    === "英文指令"

        ```tex
        msguide
        ```

- 显示联萌大表。 :material-account: :material-account-group: :material-circle:{.green_circle}

    === "中文指令"

        ```tex
        联萌大表
        ```

    === "英文指令"

        ```tex
        msbigtable
        ```

- 显示联萌推送线。 :material-account: :material-account-group: :material-circle:{.green_circle}

    === "中文指令"

        ```tex
        推送线
        ```

    === "英文指令"

        ```tex
        pushline
        ```

!!! summary

    祝早日达到目标升仙成圣~

## 雷网相关功能

!!! info

    雷网相关指令交给小爆了，小鱼不负责查询雷网了~

## 群组管理功能

- 解析加群申请：将加群用户联萌 ID 信息公开，并**自动拒绝**不符合加群条件的用户。 :material-account-group: :material-circle:{.yellow_circle}
- 欢迎新人。 :material-account-group: :material-circle:{.yellow_circle}
- 退群告别。 :material-account-group: :material-circle:{.yellow_circle}
- 更新群成员信息。 :material-account-group: :material-circle:{.red_circle}

    === "中文指令"

        ```tex
        更新群成员
        ```

    === "英文指令"

        ```tex
        updateuser
        ```

- 自动更新群成员信息: 小鱼在每天 03:00:00 每隔 4 小时自动获取一次群员信息，误差为 30 秒。 :material-account-group: :material-fish:{.blue_fish}

!!! tip

    有**新用户**加群时，小鱼也会自动更新群员信息。即使群员退群，**其信息也会保留**。

    老用户加群与新用户加群会显示**不同的**欢迎语句。

## 联萌信息查询功能

### 今日之星

- 主动查询联萌每日一星。 :material-account: :material-account-group: :material-circle:{.green_circle}

    === "中文指令"

        ```tex
        联萌每日一星
        ```

    === "英文指令"

        ```tex
        dailystar
        ```

- 主动查询联萌每日一星次数。 :material-account: :material-account-group: :material-circle:{.green_circle}

    === "中文指令"

        ```tex
        联萌每日一星次数 $用户ID$
        ```

    === "英文指令"

        ```tex
        dailystarcount $UID$
        ```

- 自动推送联萌每日一星：于每天 00:01:30 进行推送，误差为 30 秒。 :material-account-group: :material-fish:{.blue_fish}

### 每日一图

- 主动查询每日一图：图的`大小`，`bv`，`op`，`is`与`第一名成绩`。 :material-account: :material-account-group: :material-circle:{.green_circle}

    === "中文指令"

        ```tex
        每日一图
        ```

    === "英文指令"

        ```tex
        dailymap
        ```

- 自动推送每日一图：每天 00:03:00 进行推送，误差为 30 秒。 :material-account-group: :material-fish:{.blue_fish}

!!! tip

    如果每日一图尚未完成，`第一名成绩`会显示为 `inf`。

### 用户扫雷数据

- 按 ID 查询联萌用户扫雷相关数据：获得用户的`时间记录(含排名)`，`bvs记录(含排名)`，`游戏局数(含开率)`，`当前等级`与`当前排名`。 :material-account-group: :material-circle:{.green_circle}

    === "中文指令"

        ```tex
        联萌 $用户ID$
        ```

    === "英文指令"

        ```tex
        id $UID$
        ```

- 个人信息查询：本功能需要群主给以查询用户 ID 命名的头衔，查询结果与上文一致。 :material-account-group: :material-circle:{.green_circle}

    === "中文指令"

        ```tex
        个人信息
        ```

    === "英文指令"

        ```tex
        me
        ```

!!! warning

    由于该功能容易刷屏，每个联萌 ID**一个小时以内**仅能查询一次，多次查询时小鱼不会回应。

- 按昵称模糊搜索联萌用户：获得用户的`昵称`与`ID`。 :material-circle:{.green_circle}

    === "中文指令"

        ```tex
        查询昵称 $用户昵称$
        ```

    === "英文指令"

        ```tex
        search $nickname$
        ```

!!! tip

    如果使用`search %`命令，将模糊搜索前十玩家. 模糊搜索一次最多查询`10`名玩家。

- 成绩比较功能：比较两个 ID 的三个等级的`时间`和`bvs`成绩。 :material-account-group: :material-circle:{.green_circle}

    === "中文指令"

        ```tex
        对战 $用户ID$ $用户ID$
        ```

    === "英文指令"

        ```tex
        battle $UID$ $UID$
        ```

### 排行榜

- 主动获取联萌每个等级的人数与总计人数, 并比较与上周的人数变化。 :material-account: :material-account-group: :material-circle:{.green_circle}

    === "中文指令"

        ```tex
        用户等级
        ```

    === "英文指令"

        ```tex
        level
        ```

- 自动推送联萌每个等级的人数与总计人数：每周一 00:00:00 进行推送，误差为 30 秒。 :material-account-group: :material-fish:{.blue_fish}
- 经典模式排行榜查询：包含用户的`排名`，`昵称`，`ID`与`成绩`。 :material-account: :material-account-group: :material-circle:{.green_circle}

    === "中文指令"

        === "时间"

            ```tex
            排名 时间 $查询页码$ 全部/盲扫/标旗 全部/初级/中级/高级
            ```

        === "bvs"

            ```tex
            排名 bvs $查询页码$ 全部/盲扫/标旗 全部/初级/中级/高级
            ```

        === "无尽"

            ```tex
            排名 无尽 $查询页码$
            ```

        === "无猜"

            ```tex
            排名 无尽 $查询页码$
            ```

        === "雷币"

            ```tex
            排名 无尽 $查询页码$
            ```

        === "乱斗"

            ```tex
            排名 无猜 $查询页码$
            ```

        === "进步"

            ```tex
            排名 进步 $查询页码$
            ```

        === "人气"

            ```tex
            排名 人气 $查询页码$
            ```

    === "英文指令"

        === "时间"

            ```tex
            rank time $page$ all/nf/fl all/beg/int/exp
            ```

        === "bvs"

            ```tex
            rank bvs $page$ all/nf/fl all/beg/int/exp
            ```

        === "无尽"

            ```tex
            rank endless $page$
            ```

        === "无猜"

            ```tex
            rank nonguessing $page$
            ```

        === "雷币"

            ```tex
            rank coins $page$
            ```

        === "乱斗"

            ```tex
            rank chaos $page$
            ```

        === "进步"

            ```tex
            rank advance $page$
            ```

        === "人气"

            ```tex
            rank visit $page$
            ```

!!! tip

    查询的每一页会显示 10 名用户，例如第 1 页有排行榜 1-10 名的用户，第 2 页有排行榜 11-20 名的用户，以此类推。

!!! warning

    此部分代码即将重构，指令说明可能不具备时效性。

### 录像解析

- 录像数据解析功能：包含扫雷局面的信息以及用户的操作信息，基本与电脑端`arbiter`的计数器的统计信息保持一致。 :material-account: :material-account-group: :material-circle:{.green_circle}

    === "中文指令"

        === "解析录像ID"

            ```tex
            分析 录像 $录像ID$
            ```

        === "解析发帖ID"

            ```tex
            分析 帖子 $发帖ID$
            ```

    === "英文指令"

        === "解析录像ID"

            ```tex
            analyze record $recordID$
            ```

        === "解析发帖ID"

            ```tex
            analyze post $postID$
            ```

!!! tip

    上述指令中`record`可以简写为`r`，`post`可以简写为`p`。

!!! tip

    详细的统计信息包含：ID/level/rank，mode，time/est，solved_bv/bv/bvs，ce/ces，cl/cls，l/fl/r/d，path，op/is，ioe/iome，qg/rqp，corr/thrp，stnb。

- 分享录像链接自动解析功能：该功能在提取到`http://tapsss.com`与`post=`关键词后自动触发。 :material-circle:{.green_circle}

!!! warning

    由于自动推送的访问流量过于庞大，小鱼暂未设置自动推送的功能，推送录像自动解析功能需要结合群中的**自动推送机器人**一起使用。

### 对战机器人

- 查询对战机器人状态：包含信息为`对战等级(含当前等级完成度)`，`胜负场数(含胜率)`，与`最近一盘战况`。 :material-account: :material-account-group: :material-circle:{.green_circle}

    === "中文指令"

        ```tex
        对战机器人
        ```

    === "英文指令"

        ```tex
        autopvp
        ```

- 自动推送对战机器人状态：每天 00:00:00 进行推送，误差为 30 秒。 :material-account-group: :material-fish:{.blue_fish}

!!! tip

    如果最近一盘对战机器人被打败，小鱼会**自动**膜拜战胜对战机器人的玩家。

!!! warning

    由于联萌的访问限制，对战机器人被分成了另外的一个项目，项目地址请点击[这里](https://github.com/T0nyX1ang/mswar-bot-autopvp)。对战机器人和小鱼是不同的项目，请务必加以区分。

## 娱乐功能

- 打招呼功能: 根据当前的时间，小鱼会给出不同的问候语句。 :material-account: :material-account-group: :material-circle:{.green_circle}

    === "中文指令"

        ```tex
        小鱼
        ```

    === "英文指令"

        ```tex
        greet
        ```

!!! tip

    戳一戳小鱼，也会给出与打招呼相同的反馈。

- 膜佬功能：包含了多样的膜佬形式(包括动图)和随机的膜佬语句。 :material-account: :material-account-group: :material-circle:{.green_circle}

    === "中文指令"

        === "膜拜一次"

            ```tex
            膜$名字$
            ```

        === "连续膜拜两次"

            ```tex
            狂膜$名字$
            ```

    === "英文指令"

        === "膜拜一次"

            ```tex
            praise$name$
            ```

        === "连续膜拜两次"

            ```tex
            admire$name$
            ```

!!! tip

    膜佬指令的参数可为空，此时会默认用`大佬`作为参数。

    用于复读的膜佬语句**不会**出现动图。

- 加油功能：包含了少量的加油形式(包括动图)和随机的加油语句。 :material-account: :material-account-group: :material-circle:{.green_circle}

    === "中文指令"

        === "常规版本"

            ```tex
            加油 $名字$
            ```

        === "匹配结尾版"

            ```tex
            $名字$加油
            ```

    === "英文指令"

        ```tex
        cheer $name$
        ```

!!! tip

    加油指令的参数可为空，此时会默认用`大佬`作为参数。

- 复读功能：如果群内有五条呈**等差数列**的消息(不包含小鱼在内)，小鱼会复读等差数列的下一项，相同的消息**只会**复读一次。 :material-account-group: :material-circle:{.green_circle}

!!! tip

    为了增强小鱼复读的趣味性，小鱼还学会了**打断复读**和**变形复读**这两个技能。

    打断复读：小鱼有5%的概率强行打断复读，此时会重置相应的复读计数器。如果复读的句子前两个字是`打断`，小鱼会自动在句子前加上一个`打断`。

    变形复读：小鱼有5%的概率随机倒装句子中的某一部分**或**随机替换句子中的某个QQ表情**，此时会重置相应的复读计数器，增量复读部分参与这个功能。

    由于小鱼不会发送红包，小鱼会将复读的红包信息修改为`我发了一个[xx红包]，请下载最新版扫雷联萌领取~`，红包的标题与复读红包的标题一致。

!!! warning

    复读功能目前完全支持复读图片，但存在复读动图时无法自动播放动图的问题。

    复读功能的优先级**最低**，只有在其它指令均未被匹配时，才会触发。

    变形复读中出现的三种形式是互斥的。

- 设置复读屏蔽词：小鱼不会复读在屏蔽列表中的词汇。 :material-account-group: :material-circle:{.red_circle}

    === "中文指令"

        === "新增"

            ```tex
            复读屏蔽词 + $屏蔽词$
            ```

        === "移除"

            ```tex
            复读屏蔽词 - $屏蔽词$
            ```

    === "英文指令"

        === "新增"

            ```tex
            blockword + $word$
            ```

        === "移除"

            ```tex
            blockword - $word$
            ```

!!! warning

    不推荐设置过多的屏蔽词，可能会导致性能问题。

- 设置复读参数：设置复读的`变形概率`(0-100 整数)与`打断概率`(0-100 整数)。 :material-account-group: :material-circle:{.red_circle}

    === "中文指令"

        ```tex
        复读参数 $变形概率$ $打断概率$
        ```

    === "英文指令"

        ```tex
        repeaterparam $mutate-prob$ $cut-in-prob$
        ```

- 查看复读状态：显示当前的`变形概率`与`打断概率`。 :material-account-group: :material-circle:{.red_circle}

    === "中文指令"

        ```tex
        复读状态
        ```

    === "英文指令"

        ```tex
        repeaterstatus
        ```

- 小黑屋功能：在小鱼为管理员时，禁言进入小黑屋的用户一段时间(以分钟为单位)。 :material-account-group: :material-circle:{.yellow_circle}

    === "中文指令"

        ```tex
        进入小黑屋 $时长$
        ```

    === "英文指令"

        ```tex
        blackroom $duration$
        ```

!!! tip

    允许设定的时间范围是 1 分钟至 43200 分钟(即 1 个月)，如果设定时间不在此范围内，禁言时间将会自动调整为 10 分钟。

- 随机数功能: 生成`m`与`n`之间`c`个随机整数。 :material-account: :material-account-group: :material-circle:{.green_circle}

    === "中文指令"

        === "不重复"

            ```tex
            随机数 $m$ $n$ $c$
            ```

        === "可重复"

            ```tex
            随机数 $m$ $n$ $c$ r
            ```

        === "升序"

            ```tex
            随机数 $m$ $n$ $c$ a
            ```

        === "降序"

            ```tex
            随机数 $m$ $n$ $c$ d
            ```

    === "英文指令"

        === "不重复"

            ```tex
            randi $m$ $n$ $c$
            ```

        === "可重复"

            ```tex
            randi $m$ $n$ $c$ r
            ```

        === "升序"

            ```tex
            randi $m$ $n$ $c$ a
            ```

        === "降序"

            ```tex
            randi $m$ $n$ $c$ d
            ```

!!! tip

    最多生成 10 个随机数，最少生成一个，如果参数`c`超出范围，将只生成一个随机数，所有附加参数可以叠加使用，升序排列优先级高于降序排列。

    随机数生成采用`Python`自带的`random.sample`，不保证效率，数据范围充分大。

!!! warning

    此部分代码即将重构，指令说明可能不具备时效性。

## 算 42 点

### 规则及说明

- 算 42 点小游戏：每日 8-23 点 42:42 自动触发。 :material-fish:{.blue_fish}

- 42 点游戏规则(暂定):

  - 每日 8-23 时的 42 分 42 秒, 会给出 5 个位于 0 至 13 之间的整数，玩家需要将这五个整数(可以调换顺序)通过四则运算与括号相连，使得结果等于 42(有`0.25%`的概率随机为`24-60`中的某个数);
  - 回答时以"calc42"或"42 点"开头，加入空格，并给出算式;
  - 将根据每个问题解的个数决定结算时间，5 个解对应 3 分钟的结算时间，15 分钟封顶;
  - 在游戏结束前 1 分钟，小鱼会进行提醒，并发送当前问题的求解结果;
  - 示例：(问题) 1 3 3 8 2，(正确的回答) calc42/42 点 (1 + 3 + 3) \* (8 - 2)，(错误的回答) calc422^8!3&3=1。

- 关于等价解的说明:

  - 四则运算的性质得出的等价是等价解，即满足交换律，结合律与分配律;
  - 中间结果出现 0，可以利用加减移动到式子的任何地方，即 $(a + 0) \times b = a \times (b + 0) = a \times b + 0$;
  - 中间结果出现 1，可以利用乘除移动到式子的任何地方，即 $(a + b) \times 1 = a \times 1 + b = a + b \times 1$;
  - $a + b = c$ 时，$(a + b) / c$，$c / (a + b)$，$(c - b) / a$，$a / (c - b)$，$(c - a) / b$，$b / (c - a)$ 等价;
  - 等值子式的交换等价;
  - $2 \times 2$ 与 $2 + 2$ 等价，$4 / 2$ 与 $4 - 2$ 等价。

- 关于得分的说明:

  - 每题的得分计算公式为 $10 \times n^{2-m} + 5 - 5 \times m$，其中 $m$ 为"当前总时间/总限时"，$n$ 为"当前解数/总解数";
  - 如果题目被完全求解(AK)，求解该题目全员额外加 10 分;
  - 首杀玩家额外加 5 分，最后一个解玩家额外加 $10 \times n^{2-m} \times (1 - \frac{1}{N})$ 分，其中 $N$ 为总解数;
  - 如果题目多于一半的解均被某名玩家求出，该名玩家额外加(该玩家给出的解数)分;
  - 统计完所有得分后，将得分取整，作为玩家的本题得分。

- 关于成就的说明:
  - 每局 42 点结束后，将给予表现出色的玩家一些成就;
  - F(First blood)指拿到首杀;
  - V(Victory)指获得游戏胜利;
  - H(Half AK)指获得半数 AK;
  - 成就可以叠加获取，且仅供娱乐。

!!! tip

    42 点游戏的核心部分已经分离该项目，转为独立开发状态，详见[这里](https://pypi.org/project/42Points/)。

### 相关指令

- 回答 42 点题目。 :material-account-group: :material-circle:{.green_circle}

    === "中文指令"

        ```tex
        42点 $算式$
        ```

    === "英文指令"

        ```tex
        calc42 $expr$
        ```

- 显示 42 点规则(即此节内容)。 :material-account: :material-account-group: :material-circle:{.green_circle}

    === "中文指令"

        ```tex
        42点说明
        ```

    === "英文指令"

        ```tex
        guide42
        ```

- 显示 42 点游戏得分。 :material-account-group: :material-circle:{.green_circle}

    === "中文指令 1"

        ```tex
        42点积分
        ```

    === "中文指令 2"

        ```tex
        42点得分
        ```

    === "英文指令"

        ```tex
        score42
        ```

- 显示 42 点游戏排行。 :material-account-group: :material-circle:{.green_circle}

    === "中文指令 1"

        ```tex
        42点排名
        ```

    === "中文指令 2"

        ```tex
        42点排行
        ```

    === "英文指令"

        ```tex
        rank42
        ```

- 显示 42 点游戏今日得分排行。 :material-account-group: :material-circle:{.green_circle}

    === "中文指令 1"

        ```tex
        42点今日排名
        ```

    === "中文指令 2"

        ```tex
        42点今日排行
        ```

    === "英文指令"

        ```tex
        dailyrank42
        ```

- 手动生成/取消 42 点(或随机生成 24-60 之间的其它点数)题目。 :material-account-group: :material-circle:{.green_circle}

    === "中文指令"

        === "生成"

            ```tex
            手动42点 +
            ```

        === "随机生成"

            ```tex
            手动42点 ++
            ```

        === "取消"

            ```tex
            手动42点 -
            ```

    === "英文指令"

        === "生成"

            ```tex
            manual42 +
            ```

        === "随机生成"

            ```tex
            manual42 ++
            ```

        === "取消"

            ```tex
            manual42 -
            ```

!!! warning

    任何人都可以在 42 点开始以前生成题目，只有生成题目的玩家可以取消 42 点题目。如果是每小时固定的 42 点，**无人(包括超级用户)可以取消**该题目。手动生成的 42 点计算得分，但**不加入**玩家总分中。

## 其它功能

- B 站直播订阅/取消订阅/查看订阅。 :material-account-group: :material-circle:{.green_circle}

    === "中文指令"

        === "订阅"

            ```tex
            订阅用户 + $B站UID$
            ```

        === "取消订阅"

            ```tex
            订阅用户 - $B站UID$
            ```

    === "英文指令"

        === "订阅"

            ```tex
            subscribe + $BUID$
            ```

        === "取消订阅"

            ```tex
            subscribe - $BUID$
            ```

- B 站直播推送：小鱼每隔 20 秒查询订阅用户名单中的所有用户，如果某个用户处于直播状态，小鱼将会发送 TA 的直播间地址。 :material-account-group: :material-fish:{.blue_fish}

!!! warning

    该功能根据订阅名单构造了若干队列，每次查询队首用户状态，并将其移至队尾。需要注意，这种方式会相当耗费流量，且有被风控的风险，请谨慎决定其开启状态。

- 本地数据库存档：将小鱼的当前状态写入本地数据库。 :material-circle:{.red_circle} :material-account: :material-account-group:

    === "中文指令"

        ```tex
        存档
        ```

    === "英文指令"

        ```tex
        save
        ```

- 自动写入数据库：小鱼会从 00:30:00 开始，每隔 2 小时将当前状态写入本地数据库。 :material-fish:{.blue_fish} :material-account: :material-account-group:
