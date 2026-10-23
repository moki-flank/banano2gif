# -*- coding: utf-8 -*-
"""
banano2gif 核心流水线引擎
全面支持：
  1. 文生动图 (Text-to-GIF)
  2. 图生动图 (Image-to-GIF / 参考图生图)
  3. 动作迁移 (Motion-Transfer / 从GIF、WebP、视频中提取动作迁移到新人设图)
  4. 视频直转动图 (Video-to-GIF)
  5. 智能透明背景化 (Alpha Channel Matting)
"""

import os
import urllib.request
from typing import Optional, Dict, Any, List, Union, Tuple
from PIL import Image

from .sdk.client import HrioClient, DEFAULT_BASE_URL, OFFICIAL_WEBSITE
from .prompts.engine import build_prompt, build_motion_transfer_prompt, ACTION_PRESETS
from .cutter.slicer import slice_grid
from .cutter.gif_builder import build_gif
from .cutter.video_to_gif import convert_video_to_gif
from .cutter.matting import remove_background
from .cutter.motion_extractor import create_motion_guide_grid

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
        style: str = "High-end 3D animation render, soft ambient lighting, clean solid white background, Pop Mart collectible figurine style",
        output_dir: str = "output",
        gif_filename: str = "animation.gif",
        duration_ms: int = 180,
        crop_size: int = 320,
        transparent: bool = False,
    ) -> Dict[str, Any]:
        """【文生动图】输入自然语言描述，生成九宫格并合成无缝循环 GIF。"""
        return self._generate_from_prompt(
            prompt=prompt,
            images=None,
            preset=preset,
            style=style,
            output_dir=output_dir,
            gif_filename=gif_filename,
            duration_ms=duration_ms,
            crop_size=crop_size,
            transparent=transparent,
            mode="text_to_gif",
        )

    def image_to_gif(
        self,
        image_path: str,
        prompt: str = "gently waving and smiling happily",
        preset: Optional[str] = None,
        style: str = "Preserve original character art style, high quality render, clean solid white background",
        output_dir: str = "output",
        gif_filename: str = "image_animation.gif",
        duration_ms: int = 180,
        crop_size: int = 320,
        transparent: bool = False,
    ) -> Dict[str, Any]:
        """【图生动图 / 参考图生图】输入角色参考图与动作描述，高度锁脸/锁特征生成连续动图。"""
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
            transparent=transparent,
            mode="image_to_gif",
        )

    def transfer_motion(
        self,
        source_media: str,
        target_image: str,
        action_hint: str = "transfer the exact 9-step motion and poses from the motion guide to the target character",
        style: str = "Preserve target character art style, high quality render, clean solid white background",
        output_dir: str = "output",
        gif_filename: str = "motion_transfer.gif",
        duration_ms: int = 180,
        crop_size: int = 320,
        transparent: bool = False,
    ) -> Dict[str, Any]:
        """
        【动作生成迁移 (Motion Transfer)】
        1. 从 source_media (.gif, .webp, .mp4) 中抽取 9 帧关键帧拼成 3x3 动作指南
        2. 将 target_image (目标人设) + 动作指南双图喂给模型进行动作迁移
        3. 裁切合成属于新角色的无缝动图
        """
        os.makedirs(output_dir, exist_ok=True)
        if not os.path.isfile(source_media):
            raise FileNotFoundError(f"未找到源动作媒体文件: {source_media}")
        if not os.path.isfile(target_image):
            raise FileNotFoundError(f"未找到目标角色人设图片: {target_image}")

        # 1. 抽取源动作并生成 3x3 动作参考九宫格
        print(f"[banano2gif] 1. 正在从源媒体抽取 9 帧关键动作九宫格: {source_media}...")
        guide_grid_path = os.path.join(output_dir, "motion_guide_grid.jpg")
        create_motion_guide_grid(source_media, output_grid_path=guide_grid_path)

        # 2. 构造动作迁移双图提示词
        full_prompt = build_motion_transfer_prompt(action_hint=action_hint, style=style)
        grid_save_path = os.path.join(output_dir, "transferred_grid.jpg")
        frames_dir = os.path.join(output_dir, "transferred_frames")
        gif_save_path = os.path.join(output_dir, gif_filename)

        print(f"[banano2gif] 2. 发起跨角色动作迁移生图请求 (模型: {self.model})...")
        print(f"[banano2gif] 双参考输入: 目标人设={target_image}, 动作指南={guide_grid_path}")

        # 双图注入：[Image 1: 目标角色, Image 2: 动作九宫格]
        resp = self.client.generate_image(self.model, full_prompt, images=[target_image, guide_grid_path])
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

        # 3. 切割与去底
        print(f"[banano2gif] 3. 正在切帧 (透明去底: {transparent})...")
        frames = slice_grid(grid_save_path, output_dir=frames_dir, crop_size=crop_size, transparent=transparent)

        # 4. 合成
        print(f"[banano2gif] 4. 正在合成动作迁移 GIF / WebP...")
        gif_path = build_gif(frames, output_path=gif_save_path, duration_ms=duration_ms)
        webp_save_path = os.path.splitext(gif_save_path)[0] + ".webp"
        build_gif(frames, output_path=webp_save_path, duration_ms=duration_ms)

        return {
            "ok": True,
            "mode": "motion_transfer",
            "source_media": source_media,
            "target_image": target_image,
            "motion_guide": guide_grid_path,
            "grid_image": grid_save_path,
            "frames_dir": frames_dir,
            "gif_path": gif_path,
            "webp_path": webp_save_path,
            "official_website": OFFICIAL_WEBSITE,
        }

    def video_to_gif(
        self,
        video_path: str,
        output_path: str = "output/video_animation.gif",
        fps: int = 10,
        max_duration_sec: float = 4.0,
        target_size: Optional[Tuple[int, int]] = (320, 320),
    ) -> Dict[str, Any]:
        """【视频生 / 视频转动图】将任意格式视频转换为表情包 GIF 或 WebP。"""
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
        transparent: bool,
        mode: str,
    ) -> Dict[str, Any]:
        os.makedirs(output_dir, exist_ok=True)
        grid_save_path = os.path.join(output_dir, "grid.jpg")
        frames_dir = os.path.join(output_dir, "frames")
        gif_save_path = os.path.join(output_dir, gif_filename)

        full_prompt = build_prompt(
            subject_and_action=prompt,
            preset=preset,
            style=style,
            has_reference_image=bool(images),
        )

        print(f"[banano2gif] 模式: {mode} (透明背景化: {'开启' if transparent else '关闭'})")
        print(f"[banano2gif] 1. 请求大模型生图 (模型: {self.model})...")

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

        print(f"[banano2gif] 2. 正在进行高精度九宫格切割 (智能去底透明化: {transparent})...")
        frames = slice_grid(grid_save_path, output_dir=frames_dir, crop_size=crop_size, transparent=transparent)

        print(f"[banano2gif] 3. 正在合成动图 ({duration_ms}ms/帧)...")
        gif_path = build_gif(frames, output_path=gif_save_path, duration_ms=duration_ms)

        webp_save_path = os.path.splitext(gif_save_path)[0] + ".webp"
        build_gif(frames, output_path=webp_save_path, duration_ms=duration_ms)

        return {
            "ok": True,
            "mode": mode,
            "transparent": transparent,
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
    motion_source: Optional[str] = None,
    preset: Optional[str] = None,
    transparent: bool = False,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    model: str = DEFAULT_MODEL,
    style: str = "High-end 3D animation render, soft ambient lighting, clean solid white background, Pop Mart collectible figurine style",
    output_dir: str = "output",
    duration_ms: int = 180,
) -> Dict[str, Any]:
    """
    智能统一接口：自动根据传入参数分流执行：
      - 动作迁移 (motion_source + image_path)
      - 视频转动图 (video_path)
      - 图生动图 (image_path)
      - 文生动图 (prompt)
    """
    app = Banano2Gif(api_key=api_key, base_url=base_url, model=model)

    if motion_source and image_path:
        # 动作迁移模式
        return app.transfer_motion(
            source_media=motion_source,
            target_image=image_path,
            action_hint=prompt or "transfer the exact 9-step motion and poses from the motion guide to the target character",
            style=style,
            output_dir=output_dir,
            duration_ms=duration_ms,
            transparent=transparent,
        )

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
            transparent=transparent,
        )

    act_prompt = prompt or "A cute 3D character smiling warmly"
    return app.text_to_gif(
        prompt=act_prompt,
        preset=preset,
        style=style,
        output_dir=output_dir,
        duration_ms=duration_ms,
        transparent=transparent,
    )
