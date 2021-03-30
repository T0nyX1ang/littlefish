// .vuepress/config.js
module.exports = {
  base: '/littlefish/',
  title: 'littlefish',
  description: 'A bot for minesweeper league.',
  locale: {
    '/': {
      'lang': 'zh-CN'
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
          { text: '更新日志', link: '/misc/changelog' }
        ]
      }
    ],
    sidebar: 'auto',
    lastUpdated: '最后更新于',
    smoothScroll: true,
    repo: 'T0nyX1ang/littlefish',
    repoLabel: 'Github',
    docsDir: 'docs',
    editLinks: true,
    editLinkText: '编辑此页面'
  },
  plugins: [
    '@vuepress/back-to-top',
    'vuepress-plugin-mathjax',
    {
      target: 'svg',
      macros: {
        '*': '\\times',
      },
    }
  ]
}
