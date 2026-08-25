#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成应用图标（纯标准库，无需 PIL / PyQt5）。

设计：蓝底圆角方块 + 同心圆环（目标）+ 白色向下箭头与托盘（下载符号）。

用法: python3 tools/gen_icon.py <输出路径>
"""
import math
import struct
import sys
import zlib


def _png_chunk(tag, data):
    chunk = tag + data
    return struct.pack(">I", len(data)) + chunk + struct.pack(">I", zlib.crc32(chunk))


def _write_png(path, width, height, rows):
    raw = b"".join(b"\x00" + row for row in rows)
    data = (
        b"\x89PNG\r\n\x1a\n"
        + _png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
        + _png_chunk(b"IDAT", zlib.compress(raw, 9))
        + _png_chunk(b"IEND", b"")
    )
    with open(path, "wb") as fh:
        fh.write(data)


def _in_rect(x, y, x0, y0, x1, y1):
    return x0 <= x <= x1 and y0 <= y <= y1


def _in_circle(x, y, cx, cy, r):
    return (x - cx) ** 2 + (y - cy) ** 2 <= r * r


def _in_rounded_rect(x, y, x0, y0, x1, y1, r):
    if not _in_rect(x, y, x0, y0, x1, y1):
        return False
    cx0, cy0 = x0 + r, y0 + r
    cx1, cy1 = x1 - r, y1 - r
    if x < cx0 and y < cy0 and not _in_circle(x, y, cx0, cy0, r):
        return False
    if x > cx1 and y < cy0 and not _in_circle(x, y, cx1, cy0, r):
        return False
    if x < cx0 and y > cy1 and not _in_circle(x, y, cx0, cy1, r):
        return False
    if x > cx1 and y > cy1 and not _in_circle(x, y, cx1, cy1, r):
        return False
    return True


def _sign(p1, p2, p3):
    return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])


def _in_triangle(pt, a, b, c):
    d1 = _sign(pt, a, b)
    d2 = _sign(pt, b, c)
    d3 = _sign(pt, c, a)
    has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
    has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
    return not (has_neg and has_pos)


def _lerp(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def sample(x, y, s):
    """返回像素 (x, y) 的 RGBA，坐标基于边长 s。"""
    top = (30, 136, 229)
    bottom = (13, 71, 161)
    white = (255, 255, 255)
    light = (144, 202, 249)
    green = (67, 160, 71)

    if not _in_rounded_rect(x, y, 0.03 * s, 0.03 * s, 0.97 * s, 0.97 * s, 0.13 * s):
        return (0, 0, 0, 0)

    t = (y - 0.03 * s) / (0.94 * s)
    t = max(0.0, min(1.0, t))
    color = _lerp(top, bottom, t)

    # 同心圆环（目标）
    cx, cy = 0.5 * s, 0.46 * s
    d = math.hypot(x - cx, y - cy)
    if 0.13 * s <= d <= 0.23 * s:
        color = light

    # 箭头杆
    if _in_rect(x, y, 0.455 * s, 0.28 * s, 0.545 * s, 0.60 * s):
        color = white
    # 箭头头部（向下三角）
    if _in_triangle(
        (x, y),
        (0.5 * s, 0.78 * s),
        (0.36 * s, 0.58 * s),
        (0.64 * s, 0.58 * s),
    ):
        color = white
    # 托盘
    if _in_rect(x, y, 0.30 * s, 0.80 * s, 0.70 * s, 0.86 * s):
        color = white
    # 状态绿点（托盘右端）
    if _in_circle(x, y, 0.66 * s, 0.83 * s, 0.035 * s):
        color = green

    return (color[0], color[1], color[2], 255)


def render(path, size=256, ss=4):
    rows = []
    for py in range(size):
        row = bytearray()
        for px in range(size):
            r = g = b = a = 0
            for sy in range(ss):
                for sx in range(ss):
                    yy = py + (sy + 0.5) / ss
                    xx = px + (sx + 0.5) / ss
                    pr, pg, pb, pa = sample(xx, yy, size)
                    r += pr * pa
                    g += pg * pa
                    b += pb * pa
                    a += pa
            n = ss * ss
            if a == 0:
                row += b"\x00\x00\x00\x00"
            else:
                row += bytes((r // a, g // a, b // a, a // n))
        rows.append(bytes(row))
    _write_png(path, size, size, rows)
    print("图标已生成：{}".format(path))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 tools/gen_icon.py <输出路径>")
        sys.exit(1)
    render(sys.argv[1])
