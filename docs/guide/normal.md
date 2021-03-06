# 功能与指令
本节仅包含对触发语法的简要介绍，不包含对函数与设计思路的详细说明。以下指令中，`/`表示等价的命令名称，`[ ]`表示简写的参数形式，`|`表示不同的参数选择，请务必注意每个参数与命令之间需要`空格`间隔。扫雷联萌简称为`联萌`，中国扫雷网简称为`雷网`。此外，每个命令有相应的触发权限，这些权限会以如下形式表现:

+   普通用户(小鱼无需权限)即可触发的权限 <Badge text="$" type="tip"/>
+   小鱼为管理员或特殊用户才能触发的权限 <Badge text="#" type="warning"/>
+   超级用户才可触发的权限或广播权限 <Badge text="!" type="error"/>

最后，如无特殊说明，本节中提到的所有指令均需要在群内触发。

## 帮助
+   显示此指南网址。 <Badge text="$" type="tip"/>

```tex
    # 显示本网址
    guide/指南

    # 显示项目github地址
    backupguide/备用链接
```

+   显示联萌安装包下载地址。 <Badge text="$" type="tip"/>

```tex
    getpackage/安装包/安装链接
```

+   显示扫雷指南。 <Badge text="$" type="tip"/>

```tex
    msguide/扫雷指南
```

+   显示联萌推送线。 <Badge text="$" type="tip"/>

```tex
    pushline/推送线
```

> 祝早日达到目标升仙成圣\~

## 雷网相关
+   交给小爆了，小鱼不负责查询雷网了~

## 群组管理功能
+   解析加群申请：将加群用户联萌ID信息公开，并**自动拒绝**不符合加群条件的用户。 <Badge text="#" type="warning"/>
+   欢迎新人。 <Badge text="#" type="warning"/>
+   退群告别。 <Badge text="#" type="warning"/>
+   更新群成员信息。 <Badge text="!" type="error"/>

```tex
    updateuser/更新群成员
```

+   自动更新群成员信息: 小鱼在每天03:00:00每隔4小时自动获取一次群员信息，误差为30秒。 <Badge text="!" type="error"/>

::: tip

有**新用户**加群时，小鱼也会主动获取群员信息。即使群员退群，**其信息也会保留**。

老用户加群与新用户加群会显示**不同的**欢迎语句。

:::

## 联萌信息查询功能

### 今日之星
+   主动查询联萌每日一星。 <Badge text="$" type="tip"/>

```tex
    dailystar/今日之星/联萌每日一星
```

+   主动查询联萌每日一星次数。 <Badge text="$" type="tip"/>

```tex
    dailystarcount/联萌每日一星次数 用户ID
```

+   自动推送联萌每日一星：于每天00:01:30进行推送，误差为30秒，该功能自动触发，广播至小鱼加入的**所有**群中。 <Badge text="!" type="error"/>

### 每日一图
+   主动查询每日一图：图的`大小`，`bv`，`op`，`is`与`第一名成绩`。 <Badge text="$" type="tip"/>

```tex
    dailymap/每日一图
```

+   自动推送每日一图：每天00:03:00进行推送，误差为30秒，该功能自动触发，广播至小鱼加入的**所有**群中。 <Badge text="!" type="error"/>

::: tip

如果每日一图尚未完成，`第一名成绩`会显示为 `inf`。

:::

### 用户扫雷数据
+   按ID查询联萌用户扫雷相关数据：获得用户的`时间记录(含排名)`，`bvs记录(含排名)`，`游戏局数(含开率)`，`当前等级`与`当前排名`。 <Badge text="$" type="tip"/>

```tex
    id/联萌 用户ID
```

+   个人信息查询：本功能需要群主给以查询用户ID命名的头衔，查询结果与上文一致。 <Badge text="$" type="tip"/>

```tex
    personinfo/个人信息/个人成绩
```

::: warning

由于该功能容易刷屏，每个联萌ID**一个小时以内**仅能查询一次，多次查询时小鱼不会回应。

:::

+   按昵称模糊搜索联萌用户：获得用户的`昵称`与`ID`。 <Badge text="$" type="tip"/>

```tex
    search/查询昵称 用户昵称
```

::: tip

如果使用`search %`命令，将模糊搜索前十玩家. 模糊搜索最多查询`10`名玩家。

:::

+   排名比较功能：比较两个ID的排名。 <Badge text="$" type="tip"/>

```tex
    battle/对战 ID1 ID2
```

### 排行榜
+   主动获取联萌每个等级的人数与总计人数, 并比较与上周的人数变化。 <Badge text="$" type="tip"/>

```tex
    level
```

+   自动推送联萌每个等级的人数与总计人数：每周一00:00:00进行推送，误差为30秒，该功能自动触发，广播至小鱼加入的**所有**群中。 <Badge text="!" type="error"/>
+   经典模式排行榜查询：包含用户的`排名`，`昵称`，`ID`与`成绩`。 <Badge text="$" type="tip"/>

```tex
    # 总时间排行榜/总bvs排行榜(无需参数)
    rank/排名 [t]ime/时间|[b]vs/3bvs 查询页码

    # 时间排行榜/bvs排行榜
    rank/排名 [t]ime/时间|[b]vs/3bvs 查询页码 [a]ll/全部|[n]f/盲扫|[f]l/标旗 [a]ll/全部|[i]nt/初级|[b]eg/中级|[e]xp/高级 

    # 无尽排行榜
    rank/排名 [e]ndless/无尽 查询页码

    # 无猜排行榜
    rank/排名 [n]onguessing/无猜 查询页码

    # 雷币排行榜
    rank/排名 c[o]in/coins/财富 查询页码

    # 乱斗排行榜
    rank/排名 [c]haos/乱斗 查询页码

    # 进步排行榜    
    rank/排名 [a]dvance/进步 查询页码

    # 人气排行榜
    rank/排名 [v]isit/人气 查询页码
```

::: tip

查询的每一页会显示10名用户，例如第1页有排行榜1-10名的用户，第2页有排行榜11-20名的用户，以此类推。

:::

### 录像解析

+   录像数据解析功能：包含扫雷局面的信息以及用户的操作信息，基本与电脑端`arbiter`的计数器的统计信息保持一致。 <Badge text="$" type="tip"/>

```tex
    # 根据[录像ID]解析
    analyze/分析 [r]ecord/录像 录像ID 

    # 根据[发帖ID]解析          
    analyze/分析 [p]ost/帖子 帖子ID           
```

::: tip

详细的统计信息包含：ID/level/rank，mode，time/est，solved_bv/bv/bvs，ce/ces，cl/cls，l/fl/r/d，path，op/is，ioe/iome，qg/rqp，corr/thrp，stnb。

:::

+   分享录像链接自动解析功能：该功能在提取到`http://tapsss.com`与`post=`关键词后自动触发。 <Badge text="$" type="tip"/>

::: warning

由于自动推送的访问流量过于庞大，小鱼暂未设置自动推送的功能，推送录像自动解析功能需要结合群中的**自动推送机器人**一起使用。

:::

### 对战机器人
+   查询对战机器人状态：包含的`对战等级(含当前等级完成度)`，`胜负场数(含胜率)`，与`最近一盘战况`。 <Badge text="$" type="tip"/>

```tex
    autopvp/对战机器人
```

+   自动推送对战机器人状态：每天00:00:00进行推送，误差为30秒，该功能自动触发，广播至小鱼加入的**所有**群中。 <Badge text="!" type="error"/>

::: tip

如果最近一盘对战机器人被打败，小鱼会**自动**膜拜战胜对战机器人的玩家。

:::

::: warning

由于联萌的访问限制，对战机器人被分成了另外的一个项目，项目地址请点击[这里](https://github.com/T0nyX1ang/mswar-bot-autopvp)。对战机器人和小鱼是不同的项目，请务必加以区分。

:::

## 娱乐功能
+   打招呼功能: 根据当前的时间，小鱼会给出不同的问候语句。 <Badge text="$" type="tip"/>

```tex
    greet/小鱼
```

::: tip

戳一戳小鱼，也会给出与打招呼相同的反馈。

:::

+   膜佬功能：包含了多样的膜佬形式(包括动图)和随机的膜佬语句。 <Badge text="$" type="tip"/>

```tex
    # 空泛膜拜
    praise/膜/膜拜

    # 用于复读的空泛膜拜(会连续膜两次)         
    admire/狂膜

    # 定向膜拜            
    praise/膜/膜拜 大佬的名字

    # 用于复读的定向膜拜(会连续膜两次)  
    admire/狂膜 大佬的名字
```

::: tip

用于复读的膜佬语句**不会**出现动图。

:::

+   加油功能：包含了少量的加油形式(包括动图)和随机的加油语句。 <Badge text="$" type="tip"/>
```tex
    # 空泛加油
    cheer/加油

    # 定向加油         
    cheer/加油 大佬的名字

    # 定向加油(匹配结尾版, 优先级低)
    xx加油
```

+   复读功能：如果群内有五条呈**等差数列**的消息(不包含小鱼在内)，小鱼会复读等差数列的下一项，相同的消息**只会**复读一次。 <Badge text="$" type="tip"/>

::: tip

打断复读：小鱼有5%的概率强行打断复读，此时会重置相应的复读计数器。如果复读的句子前两个字是`打断`，小鱼会自动在句子前加上一个`打断`。

变形复读：小鱼有5%的概率随机倒装句子中的某一部分/随机替换句子中的某个QQ表情/将句子中的`一`字替换为`二`至`九`中的某个数字，此时会重置相应的复读计数器，增量复读部分参与这个功能。

由于不会发送红包，小鱼会将复读的红包信息修改为`我发了一个[雷币红包]，请下载最新版扫雷联萌领取~`。

:::

::: warning

复读功能目前完全支持复读图片，但存在复读动图时无法自动播放动图的问题。

复读功能的优先级**最低**，只有在其它指令均未被匹配时，才会触发。

变形复读中出现的三种形式是互斥的。

:::

+   设置复读屏蔽词：小鱼不会复读在屏蔽列表中的词汇。 <Badge text="!" type="error"/>

```tex
    blockword/复读屏蔽词 +/- 待新增/移除的屏蔽词
```

::: warning

不推荐设置过多的屏蔽词，可能会导致性能问题。

:::

+   设置复读参数：设置复读的`变形概率`与`打断概率`。 <Badge text="!" type="error"/>
```tex
    repeaterparam/复读参数 变形概率(0-100整数) 打断概率(0-100整数)
```

+   查看复读状态：显示当前的`变形概率`与`打断概率`。 <Badge text="!" type="error"/>
```tex
    repeaterstatus/复读状态
```

+   小黑屋功能：在小鱼为管理员时，禁言进入小黑屋的用户一段时间。 <Badge text="#" type="warning"/>

```tex
    # 进入自定义时间段的小黑屋
    blackroom/进入小黑屋 时间(以分钟为单位)
```

::: tip

允许设定的时间范围是1分钟\~43200分钟(即1个月)，如果设定时间不在此范围内，禁言时间将会自动调整为10分钟。

:::

+   随机数功能: 生成可重复/不可重复的随机数。 <Badge text="$" type="tip"/>

```tex
    # 生成 [m, n] 之间的c个随机整数，不重复
    randi/随机数 m n c

    # 生成 [m, n] 之间的c个随机整数，可重复
    randi/随机数 m n c r

    # 生成 [m, n] 之间的c个随机整数，升序排列
    randi/随机数 m n c a

    # 生成 [m, n] 之间的c个随机整数，降序排列
    randi/随机数 m n c d
```

::: tip

最多生成10个随机数，最少生成一个，如果参数`c`超出范围，将只生成一个随机数，所有附加参数可以叠加使用，升序排列优先级高于降序排列。

随机数生成采用`Python`自带的`random.sample`，不保证效率，数据范围充分大。

:::

## 算42点

### 规则及说明
+   算42点小游戏：每日8-23点42:42自动触发，广播至小鱼加入的**所有**群中。 <Badge text="!" type="error"/>

+   42点游戏规则(暂定): 
    +   每日8-23时的42分42秒, 会给出5个位于0至13之间的整数，玩家需要将这五个整数(可以调换顺序)通过四则运算与括号相连，使得结果等于42(有`0.25%`的概率随机为`24-60`中的某个数);
    +   回答时以"calc42"或"42点"开头，加入空格，并给出算式;
    +   将根据每个问题解的个数决定结算时间，5个解对应3分钟的结算时间，15分钟封顶;
    +   在游戏结束前1分钟，小鱼会进行提醒，并发送当前问题的求解结果;
    +   示例：(问题) 1 3 3 8 2，(正确的回答) calc42/42点 (1 +   3 +   3) * (8 -   2)，(错误的回答) calc422^8!3&3=1。

+   关于等价解的说明: 
    +   四则运算的性质得出的等价是等价解，即满足交换律，结合律与分配律;
    +   中间结果出现0，可以利用加减移动到式子的任何地方，即 $(a + 0) \times b = a \times (b + 0) = a \times b + 0$;
    +   中间结果出现1，可以利用乘除移动到式子的任何地方，即 $(a + b) \times 1 = a \times 1 + b = a + b \times 1$;
    +   $a + b = c$ 时，$(a + b) / c$，$c / (a + b)$，$(c - b) / a$，$a / (c - b)$，$(c - a) / b$，$b / (c - a)$ 等价;
    +   等值子式的交换等价;
    +   $2 \times 2$ 与 $2 + 2$ 等价，$4 / 2$ 与 $4 - 2$ 等价。

+   关于得分的说明:
    +   每题的得分计算公式为 $\left[10 \times n^{2-m}\right] + 5 - 5 \times \left[m\right]$，其中 $m$ 为"当前总时间/总限时"，$n$ 为"当前解数/总解数";
    +   如果题目被完全求解(AK)，求解该题目全员额外加10分;
    +   首杀玩家额外加5分，最后一个解玩家额外加 $\left[10 \times n^{2-m} \times (1 - \frac{1}{N}) \right]$ 分，其中 $N$ 为总解数;
    +   如果题目多于一半的解均被某名玩家求出，该名玩家额外加(该玩家给出的解数)分;
    +   显示积分时会进行归一化。

+   关于成就的说明:
    +   每局42点结束后，将给予表现出色的玩家一些成就;
    +   F(First blood)指拿到首杀;
    +   V(Victory)指获得游戏胜利;
    +   H(Half AK)指获得半数AK;
    +   成就可以叠加获取，且仅供娱乐。

::: tip

42点游戏的核心部分已经分离该项目，转为独立开发状态，详见[这里](https://pypi.org/project/42Points/)。

:::

### 相关指令
+   回答42点题目。 <Badge text="$" type="tip"/>

```tex
    calc42/42点
```

+   显示42点规则。 <Badge text="$" type="tip"/>

```tex
    guide42/42点说明
```

+   显示42点游戏得分。 <Badge text="$" type="tip"/>
```tex
    score42/42点积分/42点得分
```

+   显示42点游戏排行。 <Badge text="$" type="tip"/>
```tex
    rank42/42点排名/42点排行
```

+   手动生成42点(或其它点数)题目。 <Badge text="#" type="warning"/>
```tex
    # 生成42点
    manual42 +

    # 生成24-60点
    manual42 ++
```

+   手动取消42点题目。 <Badge text="#" type="warning"/>
```tex
    manual42 -
```

::: warning

任何人都可以在42点开始以前生成题目，只有生成题目的玩家可以取消42点题目。如果是每小时固定的42点，**无人(包括超级用户)可以取消**该题目。手动生成的42点计算得分，但**不加入**玩家总分中。

:::

## 其它功能
+   B站直播推送：小鱼会在每天8-24点，每隔20秒查询订阅用户名单中的所有用户，如果某个用户处于直播状态，小鱼将会发送TA的直播间地址。 <Badge text="!" type="error"/>

```tex
    subscribe/订阅用户 +/- 用户B站UID
```

::: warning

该功能根据订阅名单构造了一个队列，每次查询队首用户状态，并将其移至队尾。需要注意，这种方式可能会相当耗费流量，同时查询有被风控的风险(目前的线性查询方式会适当降低风险)，请谨慎决定其开启状态。

:::

+   本地数据库存档：将小鱼的当前状态写入本地数据库。 <Badge text="!" type="error"/>
```tex
    save/存档
```

+   自动写入数据库：小鱼会从00:30:00开始，每隔2小时将当前状态写入本地数据库。 <Badge text="!" type="error"/>
