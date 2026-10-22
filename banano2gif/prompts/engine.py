# -*- coding: utf-8 -*-
"""
banano2gif 提示词工程引擎
支持：
  1. 文生（Text-to-GIF）：纯自然语言描述生成九宫格连续动图
  2. 图生（Image-to-GIF）：基于用户参考图（头像/立绘/照片）保持高一致性角色生成连续动图
彻底去除 1~9 / 01~09 序号，采用纯空间方位映射与微动作渐变闭环。
"""

from typing import Optional, List, Dict

ACTION_PRESETS: Dict[str, Dict[str, str]] = {
    "waving": {
        "title": "挥手打招呼",
        "description": "cheerfully waving hand to say hello",
        "motion": (
            "Top row - left panel: Hand resting near chest, smiling with bright eyes. "
            "Top row - center panel: Right hand starts raising up to shoulder level. "
            "Top row - right panel: Hand raises above shoulder, palm facing forward, fingers open. "
            "Middle row - left panel: Hand tilts 15 degrees to the left in a friendly wave. "
            "Middle row - center panel: Hand reaches maximum left tilt, big cheerful open-mouth smile. "
            "Middle row - right panel: Hand begins waving back toward the right side. "
            "Bottom row - left panel: Hand tilts 15 degrees to the right. "
            "Bottom row - center panel: Hand moves back to upright position, eyes squinting happily. "
            "Bottom row - right panel: Hand gently lowers back toward chest, returning smoothly to starting position for an infinite seamless loop."
        ),
    },
    "petting": {
        "title": "温柔抚摸宠物/猫猫",
        "description": "gently petting and stroking a sitting fluffy pet",
        "motion": (
            "Top row - left panel: Hand hovering slightly above pet's head, pet looking up with curious eyes. "
            "Top row - center panel: Hand lowers closer, fingers gently curling. "
            "Top row - right panel: Hand gently touches the top of pet's head, pet starts squinting happily. "
            "Middle row - left panel: Hand strokes down over the ears, pet closes eyes in comfort. "
            "Middle row - center panel: Hand glides back toward the nape/neck, pet raises chin slightly purring. "
            "Middle row - right panel: Hand glides along upper back, pet stretches neck comfortably. "
            "Bottom row - left panel: Hand reaches mid-back and begins lifting off gently. "
            "Bottom row - center panel: Hand lifts up into the air, pet slowly opens eyes. "
            "Bottom row - right panel: Hand returns to original hovering position above head, pet looks up waiting for next pet, seamlessly connecting to top-left panel."
        ),
    },
    "laughing": {
        "title": "哈哈大笑/欢脱",
        "description": "bursting into joyful laughter with subtle body bounce",
        "motion": (
            "Top row - left panel: Gentle smiling expression, mouth slightly open. "
            "Top row - center panel: Smile widens, head tilts back slightly. "
            "Top row - right panel: Big laughter, eyes closing into joyful arcs, shoulders rising. "
            "Middle row - left panel: Head bobs downward with laughter, hands lightly tapping knees. "
            "Middle row - center panel: Wide open-mouth chuckle, subtle joyful tear in eye corner, chest bouncing. "
            "Middle row - right panel: Head tilts back up laughing heartily, cheeks blushing bright. "
            "Bottom row - left panel: Laughter softens, catching breath with a big beaming grin. "
            "Bottom row - center panel: Head settles back toward center, eyes gently blinking. "
            "Bottom row - right panel: Mouth curves into sweet lingering grin, returning seamlessly to top-left panel."
        ),
    },
    "crying": {
        "title": "委屈哭泣/泪汪汪",
        "description": "tearing up with pouty lips and comical tears stream",
        "motion": (
            "Top row - left panel: Pouty lower lip, eyes glistening with watery tears. "
            "Top row - center panel: Eyes widen, big tear droplets forming at corners. "
            "Top row - right panel: Head tilts slightly down, first tear drops slide down cheeks. "
            "Middle row - left panel: Eyes squeeze shut, comical waterfall tears burst out. "
            "Middle row - center panel: Dramatic weeping with little trembling shoulders. "
            "Middle row - right panel: Tears continue flowing, small handkerchief dab. "
            "Bottom row - left panel: Sniffling, tears slowing down, eyes opening red and watery. "
            "Bottom row - center panel: Wiping tears with sleeve, pouty cute sad expression. "
            "Bottom row - right panel: Trembling soft pout, ready to cry again, looping seamlessly to top-left panel."
        ),
    },
    "heart_wink": {
        "title": "眨眼比心",
        "description": "winking eye and making a cute finger heart gesture",
        "motion": (
            "Top row - left panel: Both eyes open smiling warmly, hands close to chest. "
            "Top row - center panel: Right fingers start forming mini finger-heart shape. "
            "Top row - right panel: Right eye winks closed, small glowing sparkle appears near fingers. "
            "Middle row - left panel: Wink fully held, pink heart icon pops out from fingertips. "
            "Middle row - center panel: Heart icon floats up, sparkling happily, bright cheerful wink. "
            "Middle row - right panel: Heart icon pulses slightly and starts floating away. "
            "Bottom row - left panel: Right eye begins reopening, hands relaxing down. "
            "Bottom row - center panel: Both eyes open, soft warm smile, fingers open naturally. "
            "Bottom row - right panel: Resting cute smile, hands at chest, seamlessly returning to top-left panel."
        ),
    },
    "thumbs_up": {
        "title": "竖起大拇指点赞",
        "description": "enthusiastically giving a thumbs up approval",
        "motion": (
            "Top row - left panel: Standing confidently with pleasant smiling face. "
            "Top row - center panel: Right arm starts raising with closed fist. "
            "Top row - right panel: Thumb pops up firmly, confident wink. "
            "Middle row - left panel: Thumbs up pushed forward toward camera with emphasis. "
            "Middle row - center panel: Big proud beaming smile, sparkling star icon next to thumb. "
            "Middle row - right panel: Thumb wiggles slightly in praise, nod of approval. "
            "Bottom row - left panel: Hand begins relaxing, pulling back slightly. "
            "Bottom row - center panel: Thumb lowers as arm descends. "
            "Bottom row - right panel: Arm returns to natural resting side, returning smoothly to top-left panel."
        ),
    },
}


def build_generic_motion_flow(subject: str, action: str) -> str:
    """自动生成 9 帧微幅渐变描述（纯方位映射）"""
    return (
        f"Top row - left panel: {subject} in starting pose, beginning {action}. "
        f"Top row - center panel: {subject} makes subtle preparatory motion, body shifts slightly. "
        f"Top row - right panel: {subject} initiates first micro-movement of {action}. "
        f"Middle row - left panel: {subject} smoothly advances movement halfway through motion arc. "
        f"Middle row - center panel: {subject} reaches the peak keyframe expression and maximum extension of {action}. "
        f"Middle row - right panel: {subject} maintains peak excitement with subtle micro-bounce. "
        f"Bottom row - left panel: {subject} begins smooth recovery motion, relaxing muscles. "
        f"Bottom row - center panel: {subject} returns closer to starting position, breathing naturally. "
        f"Bottom row - right panel: {subject} settles back to original starting pose, ready to seamlessly loop back into top-left panel."
    )


def build_prompt(
    subject_and_action: str,
    preset: Optional[str] = None,
    style: str = "High-end 3D animation render, soft ambient lighting, clean pastel background, Pop Mart collectible figurine style",
    custom_motion: Optional[str] = None,
    has_reference_image: bool = False,
) -> str:
    """
    生成符合 banano2gif 规范的连续帧提示词：
    - 支持文生图与参考图生图（图生图）
    - 绝无任何 1~9 / 01~09 等数字序号
    - 强制机位锁定 (LOCKED CAMERA)
    - 强制微动作首尾闭环 (SEAMLESS LOOP)
    - 严格负向过滤各种水印、数字角标与文字
    """
    if custom_motion:
        motion_desc = custom_motion
    elif preset and preset in ACTION_PRESETS:
        p = ACTION_PRESETS[preset]
        subject_and_action = f"{subject_and_action}, {p['description']}"
        motion_desc = p["motion"]
    else:
        motion_desc = build_generic_motion_flow(subject_and_action, "the smooth looping action")

    reference_anchor = ""
    if has_reference_image:
        reference_anchor = (
            "REFERENCE CHARACTER LOCK: Maintain exact, strict identity consistency with the character/subject in the provided reference image. "
            "Preserve identical facial features, eye shape, hairstyle, hair color, clothing style, key accessories, and aesthetic identity across all 9 panels. "
        )

    prompt = (
        f"A clean 3x3 animation contact sheet grid consisting of exactly 9 sequential square panels showing ONE continuous, smooth micro-motion cycle: "
        f"{reference_anchor}"
        f"{subject_and_action}. "
        f"CRITICAL MOTION RULES: "
        f"1. LOCKED CAMERA: Absolutely static camera, identical distance, identical zoom, static background. The main body of the character stays in the exact same physical coordinates across all 9 panels. "
        f"2. SEQUENTIAL MICRO-MOTION FLOW (Spatial Order: Top row left-to-right, Middle row left-to-right, Bottom row left-to-right): "
        f"{motion_desc} "
        f"LAYOUT: Equal 3x3 grid separated by thin, clean, solid white borders. "
        f"STRICT NEGATIVE CONSTRAINT: ABSOLUTELY NO numbers, NO digits, NO frame index watermark (such as 01, 02... 09, 1, 2... 9), NO text, NO labels, NO logos, NO captions anywhere in the image. Every panel must contain 100% pure visual artwork. "
        f"STYLE: {style}."
    )
    return prompt
