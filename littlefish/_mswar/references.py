"""
References of data received from minesweeper app.

Please use it as a dictionary.
"""

from collections import defaultdict

level_ref = {-1: '雷帝', 0: '-', 1: 'E', 2: 'D', 3: 'C', 4: 'B', 5: 'A', 6: 'S', 7: 'SS', 8: 'SSS', 9: '★', 10: '★★'}

sex_ref = {0: '', 1: 'GG', 2: 'mm'}

type_ref = {
    'time': 0,
    '时间': 0,
    't': 0,
    'bvs': 1,
    '3bvs': 1,
    'b': 1,
    'endless': 2,
    '无尽': 2,
    'e': 2,
    'nonguessing': 3,
    '无猜': 3,
    'n': 3,
    'coin': 4,
    'coins': 4,
    '财富': 4,
    'o': 4,
    'chaos': 5,
    '乱斗': 5,
    'c': 5,
    'advance': 6,
    '进步': 6,
    'a': 6,
    'visit': 7,
    '人气': 7,
    'v': 7,
}

style_ref = defaultdict(lambda: -1, {
    'all': -1,
    '全部': -1,
    'a': -1,
    'nf': 0,
    '盲扫': 0,
    'fl': 1,
    '标旗': 1,
    'f': 1,
})

mode_ref = defaultdict(lambda: 4, {
    'all': 4,
    '全部': 4,
    'a': 4,
    'beg': 1,
    '初级': 1,
    'b': 1,
    'int': 2,
    '中级': 2,
    'i': 2,
    'exp': 3,
    '高级': 3,
    'e': 3,
})
