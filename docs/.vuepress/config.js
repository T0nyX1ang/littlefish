// .vuepress/config.js
module.exports = {
  title: 'littlefish',
  description: '扫雷联萌查询机器人 🐟 小鱼',
  locales: {
    '/': {
      'lang': 'zh-CN',
    }
  },
  themeConfig: {
    activeHeaderLinks: false,
    nav: [
      { text: '主页', link: '/' },
      {
        text: '指南',
        items: [
          { text: '功能与指令', link: '/guide/normal' },
          { text: '配置与部署', link: '/guide/advanced' },
        ]
      },
      {
        text: '了解更多',
        items: [
          { text: '更新日志', link: '/misc/changelog' },
          { text: '参与开发', link: '/misc/contribution'}
        ]
      }
    ],
    locales: {
      '/': {
          lastUpdated: '最后更新于'
      }
    },
    sidebar: 'auto',
    smoothScroll: true,
    repo: 'T0nyX1ang/littlefish',
    repoLabel: 'Github',
    docsDir: 'docs',
    editLinks: true,
    editLinkText: '编辑此页面',
    footer: 'littlefish 🐟 ~ Licensed under AGPL ~ Copyright © 2020-2021 Tony Xiang'
  },
  plugins: [
    '@vuepress/back-to-top',
    'vuepress-plugin-reading-progress',
    [
      'vuepress-plugin-mathjax', { target: 'svg' }
    ],
    [
      '@vuepress/last-updated',
      {
        dateOptions:{
          hour12: false,
          timeZone: 'Asia/Shanghai',
          timeStyle: 'long',
          dateStyle: 'long'
        }
      }
    ]
  ]
}
