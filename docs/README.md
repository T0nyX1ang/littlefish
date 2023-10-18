# 小鱼

小鱼是一个基于[NoneBot2](https://v2.nonebot.dev/)和[go-cqhttp](http://docs.go-cqhttp.org/)的异步 IO 机器人，用于[扫雷联萌](http://tapsss.com)(原扫雷大作战)的相关信息查询和各种各样的娱乐操作。如果小鱼已经部署在你所在的群里，你可能需要阅读[功能与指令](./guide/normal.md)这一节；如果你希望将小鱼部署在某些群里，你可能需要阅读[配置与部署](./guide/advanced.md)这一节。此外，你可以通过站内搜索或导航栏以进一步了解本项目。

祝你使用愉快 ^\_^ !

## 特点

- 良好的项目结构: 小鱼的代码分为了用户指令的表层和核心逻辑的里层两部分，满足了松耦合的特性。
- 高效的访问: 小鱼的所有网络访问代码是异步的，且数据库相对高效，保证了用户响应效率。
- 丰富的功能: 小鱼集成了大量扫雷联萌的接口，内置了大量娱乐指令，且尽可能保持高效更新。

## 协议

- 本项目基于`AGPL 3.0`开源, 详细的协议见[这里](http://www.gnu.org/licenses/agpl-3.0.html)。

## 鸣谢

- 雷网 [17373](https://github.com/hxtscjk17373) 的小爆，分担了雷网查询的任务。
- 雷网 [13688](https://github.com/darknessgod) 的[小喵](https://github.com/darknessgod/littlemeow/wiki/%E5%B0%8F%E5%96%B5%E4%BD%BF%E7%94%A8%E5%B8%AE%E5%8A%A9%EF%BC%88%E6%9C%80%E5%90%8E%E6%9B%B4%E6%96%B0%E4%BA%8E2020%E5%B9%B44%E6%9C%886%E6%97%A5%EF%BC%89)——本项目的灵感来源。
- 雷网 [14491](https://github.com/teleportor) 对于 42 点等价解提供的技术支持以及对联萌大表的开发工作。
- 扫雷联萌萌主(开发者)夜夜通宵对项目的包容。
- [CryptoFucker](https://github.com/P4nda0s/CryptoFucker)：一款可以 hook 安卓应用加密方式和密码的 Xposed 插件。
- [Fiddler](https://www.telerik.com/fiddler) + [HTTPCanary](https://github.com/MegatronKing/HttpCanary)：用于网络抓包的软件。
- [FDex2](https://bbs.pediy.com/thread-224105.htm)：用于安卓应用的脱壳的 Xposed 插件。
- [jadx](https://github.com/skylot/jadx)：用于 dex 形式文件的反编译软件。
- [Genymotion](https://www.genymotion.com/)：运行安卓应用的虚拟机软件。
- [bilibili_api](https://github.com/Passkou/bilibili_api)：用于 B 站直播推送。
- And you ~
