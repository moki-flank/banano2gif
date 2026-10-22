# -*- coding: utf-8 -*-
"""
HrioAPI 官方 SDK 内置封装模块
无需额外安装外部依赖，内置支持 https://hrioapi.hrio.site 平台各图像大模型调用。
"""

import os
import json
import base64
import urllib.request
import urllib.error
from typing import Optional, Dict, Any, Tuple, List

DEFAULT_BASE_URL = "https://hrioapi.hrio.site/v1"
OFFICIAL_WEBSITE = "https://hrioapi.hrio.site"


class HrioAPIError(Exception):
    """HrioAPI 平台请求异常"""
    pass


class HrioClient:
    """
    轻量自包含 HrioAPI 客户端。
    支持传入 api_key，若未传则自动读取环境变量 HRIO_API_KEY。
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 180,
    ):
        self.api_key = (api_key or os.environ.get("HRIO_API_KEY", "")).strip()
        self.base_url = (base_url or os.environ.get("HRIO_BASE_URL", DEFAULT_BASE_URL)).rstrip("/")
        self.timeout = timeout

        if not self.api_key:
            # 尝试检测本地是否有默认配置
            pass

    def check_auth(self):
        if not self.api_key:
            raise HrioAPIError(
                f"\n[错误] 未检测到有效的 API Key！\n"
                f"请前往官方网站注册并获取您的 API Key: {OFFICIAL_WEBSITE}\n"
                f"使用方式：\n"
                f"  1. 环境变量配置：export HRIO_API_KEY=\"sk-xxxx\" (Linux/Mac) 或 set HRIO_API_KEY=\"sk-xxxx\" (Windows)\n"
                f"  2. 代码传参配置：client = HrioClient(api_key=\"sk-xxxx\")\n"
                f"  3. 命令行参数：python -m banano2gif.cli --key \"sk-xxxx\"\n"
            )

    def generate_image(
        self,
        model: str,
        prompt: str,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        调用图像生成接口。
        支持 gemini-nano-banana-2.1、gpt-image-2、gemini-3.1-flash-image 等模型。
        """
        self.check_auth()

        url = f"{self.base_url}/images/generations"
        payload = {
            "model": model,
            "prompt": prompt,
            "n": 1,
            "size": "1024x1024",
            **(parameters or {}),
        }

        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data_bytes,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
                "User-Agent": "banano2gif-sdk/1.0",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                resp_text = resp.read().decode("utf-8")
                return json.loads(resp_text)
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="ignore")
            raise HrioAPIError(
                f"HTTP 请求失败 ({e.code}): {err_body}\n"
                f"请检查 Key 余额或前往官网管理：{OFFICIAL_WEBSITE}"
            ) from e
        except Exception as e:
            raise HrioAPIError(f"请求失败: {e}") from e

    def extract_image_bytes_or_url(self, resp_data: Dict[str, Any]) -> Tuple[Optional[str], Optional[bytes]]:
        """
        从响应体中解析图片 URL 或 Base64 图片二进制。
        """
        if not isinstance(resp_data, dict):
            return None, None

        # 1. 尝试 data 列表
        items = resp_data.get("data")
        if isinstance(items, list) and items:
            first = items[0]
            if isinstance(first, dict):
                if first.get("url"):
                    return first["url"], None
                if first.get("b64_json"):
                    return None, base64.b64decode(first["b64_json"])

        # 2. 递归查找 url 字段
        for k in ("url", "image_url", "output_url"):
            val = resp_data.get(k)
            if isinstance(val, str) and val.startswith(("http://", "https://")):
                return val, None

        return None, None
