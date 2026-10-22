# -*- coding: utf-8 -*-
"""
banano2gif 核心流水线引擎
全面支持：
  1. 文生动图 (Text-to-GIF)
  2. 图生动图 (Image-to-GIF / 参考图生图)
  3. 视频转动图 (Video-to-GIF)
  4. 多种动图格式导出 (GIF / WebP)
"""

import os
import urllib.request
from typing import Optional, Dict, Any, List, Union, Tuple
from PIL import Image

from .sdk.client import HrioClient, DEFAULT_BASE_URL, OFFICIAL_WEBSITE
from .prompts.engine import build_prompt, ACTION_PRESETS
from .cutter.slicer import slice_grid
from .cutter.gif_builder import build_gif
from .cutter.video_to_gif import convert_video_to_gif

DEFAULT_MODEL = "gemini-nano-banana-2.1"


class Banano2Gif:
    """
    banano2gif 多模态动图生成引擎
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = DEFAULT_MODEL,
    ):
        self.client = HrioClient(api_key=api_key, base_url=base_url)
        self.model = model

    def text_to_gif(
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
        【文生动图】输入自然语言描述，生成九宫格并合成无缝循环 GIF。
        """
        return self._generate_from_prompt(
            prompt=prompt,
            images=None,
            preset=preset,
            style=style,
            output_dir=output_dir,
            gif_filename=gif_filename,
            duration_ms=duration_ms,
            crop_size=crop_size,
            mode="text_to_gif",
        )

    def image_to_gif(
        self,
        image_path: str,
        prompt: str = "gently waving and smiling happily",
        preset: Optional[str] = None,
        style: str = "Preserve original character art style, high quality render",
        output_dir: str = "output",
        gif_filename: str = "image_animation.gif",
        duration_ms: int = 180,
        crop_size: int = 320,
    ) -> Dict[str, Any]:
        """
        【图生动图 / 参考图生图】输入角色参考图与动作描述，高度锁脸/锁特征生成连续动图。
        """
        if not os.path.isfile(image_path) and not image_path.startswith(("http://", "https://")):
            raise FileNotFoundError(f"未找到参考图片文件: {image_path}")

        return self._generate_from_prompt(
            prompt=prompt,
            images=[image_path],
            preset=preset,
            style=style,
            output_dir=output_dir,
            gif_filename=gif_filename,
            duration_ms=duration_ms,
            crop_size=crop_size,
            mode="image_to_gif",
        )

    def video_to_gif(
        self,
        video_path: str,
        output_path: str = "output/video_animation.gif",
        fps: int = 10,
        max_duration_sec: float = 4.0,
        target_size: Optional[Tuple[int, int]] = (320, 320),
    ) -> Dict[str, Any]:
        """
        【视频生 / 视频转动图】将任意格式视频转换为表情包 GIF 或 WebP。
        """
        print(f"[banano2gif] 正在转换视频: {video_path} -> {output_path}...")
        res_path = convert_video_to_gif(
            video_path=video_path,
            output_gif_path=output_path,
            fps=fps,
            max_duration_sec=max_duration_sec,
            target_size=target_size,
        )
        return {
            "ok": True,
            "mode": "video_to_gif",
            "gif_path": res_path,
            "video_input": video_path,
        }

    def _generate_from_prompt(
        self,
        prompt: str,
        images: Optional[List[str]],
        preset: Optional[str],
        style: str,
        output_dir: str,
        gif_filename: str,
        duration_ms: int,
        crop_size: int,
        mode: str,
    ) -> Dict[str, Any]:
        os.makedirs(output_dir, exist_ok=True)
        grid_save_path = os.path.join(output_dir, "grid.jpg")
        frames_dir = os.path.join(output_dir, "frames")
        gif_save_path = os.path.join(output_dir, gif_filename)

        # 1. 提示词构建（去序号、微动作空间排布）
        full_prompt = build_prompt(
            subject_and_action=prompt,
            preset=preset,
            style=style,
            has_reference_image=bool(images),
        )

        print(f"[banano2gif] 模式: {mode}")
        print(f"[banano2gif] 1. 请求大模型生图 (模型: {self.model})...")
        if images:
            print(f"[banano2gif] 参考图: {images}")

        # 2. 调用 SDK 生成九宫格图
        resp = self.client.generate_image(self.model, full_prompt, images=images)
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

        # 3. 高精度切图（去白边、零抖动）
        print(f"[banano2gif] 2. 正在进行高精度九宫格切割...")
        frames = slice_grid(grid_save_path, output_dir=frames_dir, crop_size=crop_size)

        # 4. 合成 GIF
        print(f"[banano2gif] 3. 正在合成平滑动图 ({duration_ms}ms/帧)...")
        gif_path = build_gif(frames, output_path=gif_save_path, duration_ms=duration_ms)

        # 同时可导出带 Alpha / 24位的 WebP 动图
        webp_save_path = os.path.splitext(gif_save_path)[0] + ".webp"
        build_gif(frames, output_path=webp_save_path, duration_ms=duration_ms)

        return {
            "ok": True,
            "mode": mode,
            "gif_path": gif_path,
            "webp_path": webp_save_path,
            "grid_image": grid_save_path,
            "frames_dir": frames_dir,
            "total_frames": len(frames),
            "prompt": full_prompt,
            "official_website": OFFICIAL_WEBSITE,
        }


def banano2gif(
    prompt: Optional[str] = None,
    image_path: Optional[str] = None,
    video_path: Optional[str] = None,
    preset: Optional[str] = None,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    model: str = DEFAULT_MODEL,
    style: str = "High-end 3D animation render, soft ambient lighting, clean pastel background, Pop Mart collectible figurine style",
    output_dir: str = "output",
    duration_ms: int = 180,
) -> Dict[str, Any]:
    """
    智能统一接口：自动根据传入参数分流执行 文生图 / 图生图 / 视频转动图。
    """
    app = Banano2Gif(api_key=api_key, base_url=base_url, model=model)

    if video_path:
        out_gif = os.path.join(output_dir, "video_animation.gif")
        return app.video_to_gif(video_path=video_path, output_path=out_gif)

    if image_path:
        act_prompt = prompt or "gently waving and smiling happily"
        return app.image_to_gif(
            image_path=image_path,
            prompt=act_prompt,
            preset=preset,
            style=style,
            output_dir=output_dir,
            duration_ms=duration_ms,
        )

    act_prompt = prompt or "A cute 3D character smiling warmly"
    return app.text_to_gif(
        prompt=act_prompt,
        preset=preset,
        style=style,
        output_dir=output_dir,
        duration_ms=duration_ms,
    )
