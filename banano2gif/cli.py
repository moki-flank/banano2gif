# -*- coding: utf-8 -*-
import argparse
import sys
import os

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from banano2gif import Banano2Gif, ACTION_PRESETS, OFFICIAL_WEBSITE, DEFAULT_BASE_URL, DEFAULT_MODEL


def main():
    parser = argparse.ArgumentParser(
        description="banano2gif: 支持 4K 超高分、文生、图生、视频生、动作迁移、智能透明背景的 AI 动图引擎",
        epilog=f"获取官方 API Key 请访问: {OFFICIAL_WEBSITE}",
    )
    parser.add_argument("prompt", nargs="?", default="", help="动作或表情包描述（选填）")
    parser.add_argument("--image", default="", help="【图生/动作迁移】目标角色人设参考图路径或 URL (进行锁脸/锁人设)")
    parser.add_argument("--motion-source", default="", help="【动作迁移】提供动作模板来源的动图/视频文件 (.gif, .webp, .mp4)，从中抽取动作九宫格迁移给 --image 目标角色")
    parser.add_argument("--video", default="", help="【视频生动图】传入本地视频文件路径 (.mp4, .mov 等) 直接转为表情包 GIF/WebP")
    parser.add_argument("--preset", choices=list(ACTION_PRESETS.keys()), help="选择内置微动作模板 (waving, petting, laughing, crying, heart_wink, thumbs_up)")
    parser.add_argument("--list-presets", action="store_true", help="查看所有支持的内置动作模板")
    parser.add_argument("--4k", action="store_true", dest="is_4k", help="【4K 超高清规格】开启 4096x4096 极致九宫格生图与高精度自适应切图")
    parser.add_argument("--export-size", type=int, default=None, help="导出动图单帧尺寸（如 320 或 480，适合表情包体积限制；不传则保持原生分辨率）")
    parser.add_argument("--transparent", action="store_true", help="【智能去底】自动识别外围纯色背景并透明化（输出含 Alpha 通道的高清透明 WebP 与 GIF）")
    parser.add_argument("--style", default="High-end 3D animation render, soft ambient lighting, clean solid white background, Pop Mart collectible figurine style", help="画面风格")
    parser.add_argument("--key", default="", help=f"HrioAPI Key (未指定则读取环境变量 HRIO_API_KEY，可在 {OFFICIAL_WEBSITE} 获取)")
    parser.add_argument("--base-url", default="", help=f"API 基址 (默认: {DEFAULT_BASE_URL})")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"生图模型 (默认: {DEFAULT_MODEL})")
    parser.add_argument("--duration", type=int, default=180, help="每帧毫秒数 (默认 180ms)")
    parser.add_argument("--fps", type=int, default=10, help="视频转动图时的采样帧率 (默认 10 FPS)")
    parser.add_argument("--out", default="output", help="产物输出目录 (默认 output/)")

    args = parser.parse_args()

    if args.list_presets:
        print("\n=== banano2gif 内置微动作预设 ===")
        for k, v in ACTION_PRESETS.items():
            print(f"  * {k:12s} - {v['title']} ({v['description']})")
        print(f"\n使用示例: python main.py \"可爱的柴犬\" --preset waving --4k --transparent\n")
        return

    app = Banano2Gif(
        api_key=args.key,
        base_url=args.base_url,
        model=args.model,
    )

    try:
        # 模式 1: 动作生成迁移 (Motion Transfer)
        if args.motion_source and args.image:
            res = app.transfer_motion(
                source_media=args.motion_source,
                target_image=args.image,
                action_hint=args.prompt or "transfer the exact 9-step motion and poses from the motion guide to the target character",
                style=args.style,
                output_dir=args.out,
                duration_ms=args.duration,
                transparent=args.transparent,
                is_4k=args.is_4k,
                export_size=args.export_size,
            )
            print("\n" + "=" * 50)
            print("🎉 动作迁移大功告成！")
            print(f"🎥 源动作媒体: {res['source_media']}")
            print(f"🖼️ 目标角色图: {res['target_image']}")
            print(f"📐 抽取的动作九宫格指南: {res['motion_guide']}")
            print(f"📁 生成的迁移九宫格:     {res['grid_image']}")
            print(f"✨ 最终迁移 GIF 动图:   {res['gif_path']}")
            print(f"🌐 最终迁移 WebP 动图:  {res.get('webp_path')}")
            print(f"💎 4K 超高规格: {'已开启' if args.is_4k else '标准规格'}")
            print(f"🔍 透明化去底: {'已开启' if args.transparent else '未开启'}")
            print("=" * 50 + "\n")
            return

        # 模式 2: 纯视频转动图 (Video-to-GIF)
        if args.video:
            out_file = os.path.join(args.out, "video_animation.gif")
            res = app.video_to_gif(video_path=args.video, output_path=out_file, fps=args.fps)
            print("\n" + "=" * 50)
            print("🎉 视频转 GIF 成功！")
            print(f"🎥 输入视频: {res['video_input']}")
            print(f"✨ 最终动图: {res['gif_path']}")
            print("=" * 50 + "\n")
            return

        # 模式 3: 图生动图 (参考图)
        if args.image:
            res = app.image_to_gif(
                image_path=args.image,
                prompt=args.prompt or "smiling and waving happily",
                preset=args.preset,
                style=args.style,
                output_dir=args.out,
                duration_ms=args.duration,
                transparent=args.transparent,
                is_4k=args.is_4k,
                export_size=args.export_size,
            )
            print("\n" + "=" * 50)
            print("🎉 图生动图制作成功！")
            print(f"🖼️ 参考图片: {args.image}")
            print(f"📁 九宫格原图: {res['grid_image']}")
            print(f"✨ GIF 动图:   {res['gif_path']}")
            print(f"🌐 WebP 动图:  {res.get('webp_path')}")
            print(f"💎 4K 规格:    {'4096x4096 (超采样输出)' if args.is_4k else '1024x1024'}")
            print(f"🔍 透明化去底: {'已开启 (含Alpha通道)' if args.transparent else '未开启'}")
            print("=" * 50 + "\n")
            return

        if not args.prompt and not args.preset:
            parser.print_help()
            print(f"\n提示：请输入动作描述，或指定 --image 参考图，或使用 --motion-source 进行动作迁移。\n官方平台与 API Key 获取地址: {OFFICIAL_WEBSITE}\n")
            sys.exit(1)

        # 模式 4: 文生动图
        res = app.text_to_gif(
            prompt=args.prompt,
            preset=args.preset,
            style=args.style,
            output_dir=args.out,
            duration_ms=args.duration,
            transparent=args.transparent,
            is_4k=args.is_4k,
            export_size=args.export_size,
        )
        print("\n" + "=" * 50)
        print("🎉 文生动图制作成功！")
        print(f"📁 九宫格原图: {res['grid_image']}")
        print(f"✨ GIF 动图:   {res['gif_path']}")
        print(f"🌐 WebP 动图:  {res.get('webp_path')}")
        print(f"💎 4K 规格:    {'4096x4096 (超采样输出)' if args.is_4k else '1024x1024'}")
        print(f"🔍 透明化去底: {'已开启 (含Alpha通道)' if args.transparent else '未开启'}")
        print("=" * 50 + "\n")

    except Exception as e:
        print(f"\n[错误] {e}\n", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
