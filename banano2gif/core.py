# -*- coding: utf-8 -*-
"""
banano2gif 核心调度器
串联：提示词构建（去序号/锁机位） -> SDK 请求大模型生图 -> 高精度裁切 -> GIF 动图合成。
"""

import os
import urllib.request
from typing import Optional, Dict, Any, List
from PIL import Image

from .sdk.client import HrioClient, DEFAULT_BASE_URL, OFFICIAL_WEBSITE
from .prompts.engine import build_prompt, ACTION_PRESETS
from .cutter.slicer import slice_grid
from .cutter.gif_builder import build_gif

DEFAULT_MODEL = "gemini-nano-banana-2.1"


class Banano2Gif:
    """
    banano2gif 动图生成引擎
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = DEFAULT_MODEL,
    ):
        self.client = HrioClient(api_key=api_key, base_url=base_url)
        self.model = model

    def create(
        self,
        prompt: str,
        preset: Optional[str] = None,
        style: str = "High-end 3D animation render, soft ambient lighting, clean pastel background, Pop Mart collectible figurine style",
        output_dir: str = "output",
        gif_filename: str = "animation.gif",
        duration_ms: int = 180,
        crop_size: int = 320,
    ) -> Dict[str, Any]:
        """
        全流程一键生成动态 GIF 表情包。
        """
        os.makedirs(output_dir, exist_ok=True)
        grid_save_path = os.path.join(output_dir, "grid.jpg")
        frames_dir = os.path.join(output_dir, "frames")
        gif_save_path = os.path.join(output_dir, gif_filename)

        # 1. 构建严格去序号、微动作连续的提示词
        full_prompt = build_prompt(subject_and_action=prompt, preset=preset, style=style)
        print(f"[banano2gif] 1. 发起模型生图请求 (模型: {self.model})...")
        print(f"[banano2gif] 提示词: {full_prompt[:120]}...")

        # 2. 调用 SDK 生成九宫格图片
        resp = self.client.generate_image(self.model, full_prompt)
        img_url, img_bytes = self.client.extract_image_bytes_or_url(resp)

        if img_bytes:
            with open(grid_save_path, "wb") as f:
                f.write(img_bytes)
        elif img_url:
            req = urllib.request.Request(img_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as s, open(grid_save_path, "wb") as f:
                f.write(s.read())
        else:
            raise RuntimeError(f"未能从模型返回中提取有效图片数据: {resp}")

        print(f"[banano2gif] 九宫格原图已保存: {grid_save_path}")

        # 3. 精准中心裁切出 9 张序列帧（去白边、零抖动）
        print(f"[banano2gif] 2. 正在进行高精度九宫格切割...")
        frames = slice_grid(grid_save_path, output_dir=frames_dir, crop_size=crop_size)
        print(f"[banano2gif] 已成功切割 {len(frames)} 帧至: {frames_dir}")

        # 4. 合成平滑无限循环 GIF
        print(f"[banano2gif] 3. 正在合成平滑动图 GIF ({duration_ms}ms/帧)...")
        gif_path = build_gif(frames, output_path=gif_save_path, duration_ms=duration_ms)
        print(f"[banano2gif] GIF 动图制作成功: {gif_path}")

        return {
            "ok": True,
            "gif_path": gif_path,
            "grid_image": grid_save_path,
            "frames_dir": frames_dir,
            "total_frames": len(frames),
            "prompt": full_prompt,
            "official_website": OFFICIAL_WEBSITE,
        }


def banano2gif(
    prompt: str,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    model: str = DEFAULT_MODEL,
    preset: Optional[str] = None,
    style: str = "High-end 3D animation render, soft ambient lighting, clean pastel background, Pop Mart collectible figurine style",
    output_dir: str = "output",
    duration_ms: int = 180,
) -> Dict[str, Any]:
    """
    一键函数接口
    """
    app = Banano2Gif(api_key=api_key, base_url=base_url, model=model)
    return app.create(
        prompt=prompt,
        preset=preset,
        style=style,
        output_dir=output_dir,
        duration_ms=duration_ms,
    )
