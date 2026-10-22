# -*- coding: utf-8 -*-
"""
九宫格高精度切割器：
基于中心对称裁切算法，完美避开 3x3 图像中的分割白线，输出对齐、无白边、无抖动的 9 帧序列。
"""

import os
from typing import List, Tuple, Union, Optional
from PIL import Image


def slice_grid(
    image_input: Union[str, Image.Image],
    output_dir: Optional[str] = None,
    crop_size: int = 320,
) -> List[Image.Image]:
    """
    将 3x3 九宫格图片切割为 9 张独立图像。
    image_input: 图片文件路径或 PIL.Image 对象
    output_dir: 若传入路径，则自动将 9 帧保存为 frame_01.png ~ frame_09.png
    crop_size: 每帧裁切的正方形边长（1024分辨率下推荐 320，安全避开分割线）
    """
    if isinstance(image_input, str):
        im = Image.open(image_input).convert("RGB")
    else:
        im = image_input.convert("RGB")

    width, height = im.size

    # 标准 1024x1024 九宫格实测分割线在 ~341px 与 ~682px 处
    if width == 1024 and height == 1024:
        cell_centers_x = [169.0, 511.5, 854.0]
        cell_centers_y = [169.0, 511.5, 854.0]
    else:
        step_x = width / 3.0
        step_y = height / 3.0
        cell_centers_x = [step_x * 0.5, step_x * 1.5, step_x * 2.5]
        cell_centers_y = [step_y * 0.5, step_y * 1.5, step_y * 2.5]

    crop_half = crop_size // 2
    frames = []

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    frame_idx = 1
    for r in range(3):
        for c in range(3):
            cx = cell_centers_x[c]
            cy = cell_centers_y[r]

            x0 = int(cx - crop_half)
            y0 = int(cy - crop_half)
            x0 = max(0, min(width - crop_size, x0))
            y0 = max(0, min(height - crop_size, y0))
            x1 = x0 + crop_size
            y1 = y0 + crop_size

            frame = im.crop((x0, y0, x1, y1))
            frames.append(frame)

            if output_dir:
                save_path = os.path.join(output_dir, f"frame_{frame_idx:02d}.png")
                frame.save(save_path)

            frame_idx += 1

    return frames
