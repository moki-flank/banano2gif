# banano2gif 🍌➡️🎞️

> **全能 AI 表情包与动态帧生成引擎**  
> 支持【**文生动图**、**图生动图（垫图/参考图锁脸）**、**视频转动图**】全模态！  
> 原生支持【**8-bit Alpha 完整半透明通道 WebP 与透明 GIF**】智能去底！  
> 默认内置官方原生 SDK，开箱即用。彻底去除数字角标，精准对齐切帧，合成丝滑无缝循环动图。

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8%2B-brightgreen.svg)](https://www.python.org/)
[![API Platform](https://img.shields.io/badge/API%20Platform-HrioAPI-orange.svg)](https://hrioapi.hrio.site)

---

## 🌟 效果展示 (Demo Showcase)

| 1. AI 渲染九宫格原图 (1024x1024 纯净无角标) | 2. 智能去底透明背景循环动图 (支持 WebP / GIF) |
| :---: | :---: |
| <img src="examples/sample_grid.jpg" width="380" alt="九宫格原图" /> | <img src="examples/sample_crying_transparent.gif" width="300" alt="透明背景无缝循环动图" /> |

---

## 🔑 获取 API Key

本项目默认内置封装了轻量级原生 SDK，直连 **HrioAPI** 官方平台（全面接入 `gemini-nano-banana-2.1`、`gpt-image-2` 等主流多模态生图大模型）：

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

## 🚀 三大核心生成模式 + 智能透明化

### 1. 📝 文生动图 (Text-to-GIF)
输入纯文本提示词或选用内置预设，AI 自动根据 9 帧微幅渐变机理生成连续无缝的九宫格并切片合成动图。
```bash
python main.py "可爱的3D柴犬戴着红色围巾" --preset waving
```

### 2. 🖼️ 图生动图 / 参考图生图 (Image-to-GIF)
传入用户的头像、照片或立绘作为**参考图（垫图）**，在保持角色面部、五官、发型与穿搭高度一致的前提下，生成专属动态表情包！
```bash
python main.py "委屈哭泣流眼泪" --image "avatar.png" --preset crying
```

### 3. 👻 一键透明背景去底化 (`--transparent`)
加上 `--transparent` 参数，算法将通过**外边缘泛洪填充 (Exterior Boundary BFS)** 自动提取背景并生成 Alpha 通道，**100% 保护角色体内的白色衣服、高光与发夹不被误扣**：
- **WebP 格式**：支持**完整的 8-bit Alpha 通道（256 级半透明羽化抗锯齿）**，边缘如丝般顺滑，文件体积轻量，特别适合现代即时通信软件与网页展示。
- **GIF 格式**：自动映射透明调色板并配置 `disposal=2`，杜绝传统透明 GIF 的层叠残影问题。
```bash
python main.py "可爱的二次元少女挥手" --preset waving --transparent
```

### 4. 🎥 视频转动图 (Video-to-GIF)
支持 MP4、MOV、WebM、AVI 等任意格式视频，自动采样关键帧并进行中心正方形裁切，直接转换为高画质轻量表情包。
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
- 🎞️ **全透明与多格式支持（Transparent WebP + GIF）**：
  - 同时导出支持透明背景的 `.webp` 与 `.gif`。
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

# 示例 1: 文生图并开启透明背景
python main.py "萌系Q版小女孩摸摸白猫的头" --preset petting --transparent

# 示例 2: 图生图（传入参考头像保持人设一致并去底）
python main.py "委屈哭泣" --image "avatar.png" --preset crying --transparent

# 示例 3: 视频直转动图
python main.py --video "cat_video.mp4" --fps 10
```

### 3. Python 代码集成

```python
from banano2gif import banano2gif

# 开启 transparent=True 即可获得透明背景动图
result = banano2gif(
    image_path="avatar.png",
    prompt="委屈哭泣揉眼睛",
    preset="crying",
    transparent=True,       # 开启智能透明背景
    duration_ms=180,
    api_key="sk-xxxx",
)

print("透明 GIF 动图:", result["gif_path"])
print("透明 WebP 动图 (8位Alpha):", result["webp_path"])
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
