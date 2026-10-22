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
        description="banano2gif: 支持文生、图生(参考图)、视频生多种格式的 AI 连续动图与表情包制作工具",
        epilog=f"获取官方 API Key 请访问: {OFFICIAL_WEBSITE}",
    )
    parser.add_argument("prompt", nargs="?", default="", help="动作或表情包描述（文生图时必填，图生图时选填）")
    parser.add_argument("--image", default="", help="【图生动图】传入参考角色图片文件路径或 URL 进行锁脸/锁特征生成")
    parser.add_argument("--video", default="", help="【视频生动图】传入本地视频文件路径 (.mp4, .mov, .webm 等) 直接转为表情包 GIF/WebP")
    parser.add_argument("--preset", choices=list(ACTION_PRESETS.keys()), help="选择内置微动作模板 (waving, petting, laughing, crying, heart_wink, thumbs_up)")
    parser.add_argument("--list-presets", action="store_true", help="查看所有支持的内置动作模板")
    parser.add_argument("--style", default="High-end 3D animation render, soft ambient lighting, clean pastel background, Pop Mart collectible figurine style", help="画面风格")
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
        print(f"\n使用示例: python main.py \"可爱的柴犬\" --preset waving\n")
        return

    app = Banano2Gif(
        api_key=args.key,
        base_url=args.base_url,
        model=args.model,
    )

    try:
        if args.video:
            # 模式 1: 视频转动图
            out_file = os.path.join(args.out, "video_animation.gif")
            res = app.video_to_gif(video_path=args.video, output_path=out_file, fps=args.fps)
            print("\n" + "=" * 50)
            print("🎉 视频转 GIF 成功！")
            print(f"🎥 输入视频: {res['video_input']}")
            print(f"✨ 最终动图: {res['gif_path']}")
            print("=" * 50 + "\n")
            return

        if args.image:
            # 模式 2: 图生动图 (参考图)
            res = app.image_to_gif(
                image_path=args.image,
                prompt=args.prompt or "smiling and waving happily",
                preset=args.preset,
                style=args.style,
                output_dir=args.out,
                duration_ms=args.duration,
            )
            print("\n" + "=" * 50)
            print("🎉 图生动图制作成功！")
            print(f"🖼️ 参考图片: {args.image}")
            print(f"📁 九宫格原图: {res['grid_image']}")
            print(f"✨ GIF 动图:   {res['gif_path']}")
            print(f"🌐 WebP 动图:  {res.get('webp_path')}")
            print(f"🔑 官网地址:   {res['official_website']}")
            print("=" * 50 + "\n")
            return

        if not args.prompt and not args.preset:
            parser.print_help()
            print(f"\n提示：请输入动作描述，或指定 --image 参考图，或指定 --video 视频文件。\n官方平台与 API Key 获取地址: {OFFICIAL_WEBSITE}\n")
            sys.exit(1)

        # 模式 3: 文生动图
        res = app.text_to_gif(
            prompt=args.prompt,
            preset=args.preset,
            style=args.style,
            output_dir=args.out,
            duration_ms=args.duration,
        )
        print("\n" + "=" * 50)
        print("🎉 文生动图制作成功！")
        print(f"📁 九宫格原图: {res['grid_image']}")
        print(f"✨ GIF 动图:   {res['gif_path']}")
        print(f"🌐 WebP 动图:  {res.get('webp_path')}")
        print(f"🔑 官网地址:   {res['official_website']}")
        print("=" * 50 + "\n")

    except Exception as e:
        print(f"\n[错误] {e}\n", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
