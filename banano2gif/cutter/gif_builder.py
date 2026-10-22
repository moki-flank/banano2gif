# -*- coding: utf-8 -*-
"""
GIF 动图合成器：
将有序帧序列打包为高质量、平滑、无限循环的 GIF 动图。
"""

import os
from typing import List, Union
from PIL import Image


def build_gif(
    frames: List[Union[str, Image.Image]],
    output_path: str = "output.gif",
    duration_ms: int = 180,
    loop: int = 0,
) -> str:
    """
    合成 GIF 动图。
    frames: 图片路径列表或 PIL.Image 对象列表
    output_path: 保存的 GIF 文件路径
    duration_ms: 单帧展示毫秒数 (推荐 150ms ~ 220ms)
    loop: 0 为无限循环播放
    """
    if not frames:
        raise ValueError("帧列表为空，无法合成 GIF")

    images: List[Image.Image] = []
    for f in frames:
        if isinstance(f, str):
            images.append(Image.open(f).convert("RGB"))
        else:
            images.append(f.convert("RGB"))

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    images[0].save(
        output_path,
        save_all=True,
        append_images=images[1:],
        duration=duration_ms,
        loop=loop,
        optimize=True,
    )
    return output_path
