# -*- coding: utf-8 -*-
import argparse
import sys
import os

# 确保在 Windows 控制台输出不因编码报错
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from banano2gif import Banano2Gif, ACTION_PRESETS, OFFICIAL_WEBSITE, DEFAULT_BASE_URL, DEFAULT_MODEL


def main():
    parser = argparse.ArgumentParser(
        description="banano2gif: 基于 AI 九宫格连续序列帧的表情包与平滑动图生成器",
        epilog=f"获取官方 API Key 请访问: {OFFICIAL_WEBSITE}",
    )
    parser.add_argument("prompt", nargs="?", default="", help="表情包主体与动作描述（如：'一只戴耳机的柯基欢快摇尾巴'）")
    parser.add_argument("--preset", choices=list(ACTION_PRESETS.keys()), help="选择内置微动作模板 (waving, petting, laughing, crying, heart_wink, thumbs_up)")
    parser.add_argument("--list-presets", action="store_true", help="查看所有支持的内置动作模板")
    parser.add_argument("--style", default="High-end 3D animation render, soft ambient lighting, clean pastel background, Pop Mart collectible figurine style", help="画面风格")
    parser.add_argument("--key", default="", help=f"HrioAPI Key (未指定则读取环境变量 HRIO_API_KEY，可在 {OFFICIAL_WEBSITE} 获取)")
    parser.add_argument("--base-url", default="", help=f"API 基址 (默认: {DEFAULT_BASE_URL})")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"生图模型 (默认: {DEFAULT_MODEL})")
    parser.add_argument("--duration", type=int, default=180, help="每帧毫秒数 (默认 180ms)")
    parser.add_argument("--out", default="output", help="产物输出目录 (默认 output/)")

    args = parser.parse_args()

    if args.list_presets:
        print("\n=== banano2gif 内置微动作预设 ===")
        for k, v in ACTION_PRESETS.items():
            print(f"  * {k:12s} - {v['title']} ({v['description']})")
        print(f"\n使用示例: python main.py \"可爱的柴犬\" --preset waving\n")
        return

    if not args.prompt and not args.preset:
        parser.print_help()
        print(f"\n提示：请提供动作描述，或使用 --preset 选定预设。\n官方平台与 API Key 获取地址: {OFFICIAL_WEBSITE}\n")
        sys.exit(1)

    prompt = args.prompt or "A cute 3D character"

    app = Banano2Gif(
        api_key=args.key,
        base_url=args.base_url,
        model=args.model,
    )

    try:
        res = app.create(
            prompt=prompt,
            preset=args.preset,
            style=args.style,
            output_dir=args.out,
            duration_ms=args.duration,
        )
        print("\n" + "=" * 50)
        print("生成大功告成！")
        print(f"九宫格原图: {res['grid_image']}")
        print(f"切割序列帧: {res['frames_dir']} (共 {res['total_frames']} 帧)")
        print(f"最终 GIF:   {res['gif_path']}")
        print(f"官网地址:   {res['official_website']}")
        print("=" * 50 + "\n")
    except Exception as e:
        print(f"\n[错误] {e}\n", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
