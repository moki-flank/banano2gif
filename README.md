# banano2gif 🍌➡️🎞️

> **全能 AI 表情包与动态帧生成引擎**  
> 支持【**文生动图**、**图生动图（垫图/参考图锁脸）**、**视频转动图**】全模态！  
> 默认内置官方原生 SDK，开箱即用。彻底去除数字角标，精准对齐切帧，合成丝滑无缝循环 GIF / WebP。

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8%2B-brightgreen.svg)](https://www.python.org/)
[![API Platform](https://img.shields.io/badge/API%20Platform-HrioAPI-orange.svg)](https://hrioapi.hrio.site)

---

## 🌟 效果展示 (Demo Showcase)

| 1. AI 渲染九宫格原图 (1024x1024 纯净无角标) | 2. 自动高精度裁切后合成的丝滑无缝 GIF (180ms/帧) |
| :---: | :---: |
| <img src="examples/sample_grid.jpg" width="380" alt="九宫格原图" /> | <img src="examples/sample_playing_cat.gif" width="320" alt="无缝循环动图" /> |

---

## 🔑 获取 API Key

本项目默认内置封装了轻量级原生 SDK，直连 **HrioAPI** 官方平台（全面接入 `gemini-nano-banana-2.1`、`gpt-image-2`、`gemini-3.1-flash-image` 等主流多模态生图大模型）：

1. 前往官方网站注册登录：👉 **[https://hrioapi.hrio.site](https://hrioapi.hrio.site)**
2. 进入用户后台创建并复制您的专属 API Key (`sk-xxxxxxxx`)。
3. 配置环境变量或直接在命令行中传入：
   ```bash
   # Linux / macOS
   export HRIO_API_KEY="sk-xxxxxxxx"

   # Windows (CMD)
   set HRIO_API_KEY=sk-xxxxxxxx

   # Windows (PowerShell)
   $env:HRIO_API_KEY="sk-xxxxxxxx"
   ```

---

## 🚀 三大核心生成模式 (All-in-One Multimodal)

### 1. 📝 文生动图 (Text-to-GIF)
输入纯文本提示词或选用内置预设，AI 自动根据 9 帧微幅渐变机理生成连续无缝的九宫格并切片合成动图。
```bash
python main.py "可爱的3D柴犬戴着红色围巾" --preset waving
```

### 2. 🖼️ 图生动图 / 参考图生图 (Image-to-GIF)
传入用户的头像、照片或立绘作为**参考图（垫图）**，在保持角色面部、五官、发型与穿搭高度一致的前提下，生成专属动态表情包！
```bash
python main.py "温柔地向镜头挥手打招呼" --image "avatar.jpg" --preset waving
```

### 3. 🎥 视频转动图 (Video-to-GIF)
支持 MP4、MOV、WebM、AVI 等任意格式视频，自动采样关键帧并进行中心正方形裁切，直接转换为高画质轻量表情包（支持 GIF 与 WebP 双格式输出）。
```bash
python main.py --video "dance.mp4" --fps 10 --out output
```

---

## ✨ 核心亮点

- 🎯 **彻底去除数字序号（No 1~9 Numbers）**：
  - 彻底抛弃易诱导 AI 渲染角标的 `1, 2, 3...` / `01, 02...` 编号；
  - 采用严密的**纯空间方位排布（Top-left, Middle-center, Bottom-right...）**与强制负向约束，生成 100% 纯净无水印原画。
- 📐 **工业级高精度定点裁切（Precision Slicing）**：
  - 实测剖析 1024×1024 图像的分割白线位置（X=341/682, Y=341/684），运用**中心对称定点裁切法（320×320）**；
  - 完美剔除所有分割白边，保证 9 帧画面中心同轴、零镜头抖动。
- 🎞️ **多种动图格式导出（GIF + WebP）**：
  - 同时输出标准通用的 `.gif` 与画质更高、体积更小的现代动态 `.webp`。
- 📦 **内置官方 SDK，开箱即用**：
  - 内置封装完整的 HrioClient，无需额外寻找或安装外部包。

---

## 💻 快速安装与使用

### 1. 安装依赖
```bash
git clone https://github.com/moki-flank/banano2gif.git
cd banano2gif
pip install -r requirements.txt
```

### 2. 命令行使用示例

```bash
# 查看所有支持的内置微动作预设
python main.py --list-presets

# 示例 1: 文生图（使用摸摸头预设）
python main.py "萌系Q版小女孩摸摸白猫的头" --preset petting --duration 180

# 示例 2: 图生图（传入参考头像保持角色一致）
python main.py "灿烂地哈哈大笑" --image "my_avatar.png" --preset laughing

# 示例 3: 视频直转动图
python main.py --video "cat_video.mp4" --fps 10
```

### 3. Python 代码集成

```python
from banano2gif import banano2gif

# 1. 文生动图
res1 = banano2gif(prompt="宇航员在月球表面跳舞", preset="waving")

# 2. 图生动图（垫图保持人设一致）
res2 = banano2gif(image_path="avatar.jpg", prompt="眨眼比心", preset="heart_wink")

# 3. 视频转动图
res3 = banano2gif(video_path="input.mp4")

print("生成的动图路径:", res2["gif_path"])
print("生成的WebP路径:", res2["webp_path"])
```

---

## 📚 内置常用微动作预设列表

| 预设代码 (`--preset`) | 动作名称 | 动作循环逻辑与幅度 |
| :--- | :--- | :--- |
| `waving` | **挥手打招呼** | 手臂从胸前抬起 -> 掌心向前左右摆动 15° -> 欢快微笑 -> 降回胸前闭环循环 |
| `petting` | **温柔抚摸宠物** | 手掌凌空逼近 -> 掌心触碰额头 -> 顺滑抚摸至后颈/背部 -> 猫咪眯眼仰头享受 -> 归位闭环 |
| `laughing` | **哈哈大笑/欢脱** | 微笑挑眉 -> 仰头放声大笑 -> 肩膀微微颤动欢脱 -> 缓和回笑闭环 |
| `crying` | **委屈哭泣/泪目** | 憋嘴泛泪 -> 泪珠滑落 -> 爆出动漫瀑布泪花 -> 抽泣擦泪闭环 |
| `heart_wink` | **眨眼比心** | 灿烂微笑 -> 右眼眨眼 Wink -> 手指搓出爱心光波飘起 -> 归位闭环 |
| `thumbs_up` | **竖大拇指点赞** | 握拳抬臂 -> 伸出大拇指向前挺进点赞 -> 闪烁星芒好评 -> 缓缓收回闭环 |

---

## 📄 开源许可证

本项目基于 [MIT License](LICENSE) 开源协议。欢迎 Star 与 PR！
