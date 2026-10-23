# -*- coding: utf-8 -*-
"""
九宫格高精度自适应切割器：
全面支持 1024x1024、2048x2048、4096x4096 (4K) 等任意超高分辨率九宫格！
动态计算单元格中心与裁切范围，完美规避分割线，零白边、零抖动。
"""

import os
from typing import List, Tuple, Union, Optional
from PIL import Image

from .matting import remove_background


def slice_grid(
    image_input: Union[str, Image.Image],
    output_dir: Optional[str] = None,
    crop_size: Optional[int] = None,
    export_size: Optional[int] = None,
    transparent: bool = False,
) -> List[Image.Image]:
    """
    将 3x3 九宫格图片切割为 9 张独立图像（原生支持 4K 超高分）。
    
    参数：
      image_input: 图片文件路径或 PIL.Image 对象
      output_dir: 若传入路径，则自动将 9 帧保存为 frame_01.png ~ frame_09.png
      crop_size: 每帧裁切的正方形边长。若为 None 则自适应按比例（约占单元格 93.75%）裁切，
                 如 1024 图裁 320px，4K 图 (4096) 裁 1280px 原生超高清
      export_size: 最终导出目标尺寸。若指定（如 320），则通过 Lanczos 算法超采样缩放，
                   保持 4K 的极致锐度与细节的同时压缩体积；若为 None 则保留原分辨率
      transparent: 是否自动去除纯色背景，输出含 Alpha 通道的透明图
    """
    if isinstance(image_input, str):
        im = Image.open(image_input).convert("RGB")
    else:
        im = image_input.convert("RGB")

    width, height = im.size

    # 自适应步长与中心点计算（支持 1024、2048、4096 或任意分辨率）
    step_x = width / 3.0
    step_y = height / 3.0
    cell_centers_x = [step_x * 0.5, step_x * 1.5, step_x * 2.5]
    cell_centers_y = [step_y * 0.5, step_y * 1.5, step_y * 2.5]

    # 动态自适应裁切尺寸：取单元格宽度的 93.75%，确保四周预留足够的安全边距避开分割线
    if crop_size is None or crop_size <= 0:
        crop_size = int(round(min(step_x, step_y) * 0.9375))

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

            if transparent:
                frame = remove_background(frame)

            # 若指定了目标导出尺寸，进行高质量超采样缩放
            if export_size and export_size > 0 and (frame.width != export_size or frame.height != export_size):
                frame = frame.resize((export_size, export_size), Image.Resampling.LANCZOS)

            frames.append(frame)

            if output_dir:
                save_path = os.path.join(output_dir, f"frame_{frame_idx:02d}.png")
                frame.save(save_path)

            frame_idx += 1

    return frames
