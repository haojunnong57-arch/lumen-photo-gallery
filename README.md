# Lumen

暗色影院感 + 液态玻璃的个人照片画廊。照片只在本机沙盒里，不联网、不依赖后端。

SwiftUI · SwiftData · Metal · iOS 18+ · 为 120Hz ProMotion 调校。

## 直接安装

1. 下载 `Lumen.ipa`（未签名）
2. 用 **AltStore** / **Sideloadly** 导入，用自己的 Apple ID 签名安装
3. 免费 Apple ID 签名 7 天有效；AltStore 可自动续签

## 从源码构建

```bash
brew install xcodegen
python3 -m pip install --user pillow numpy
python3 scripts/make_icon.py
xcodegen generate
open Lumen.xcodeproj
```

或直接产出未签名 IPA：

```bash
./scripts/build_ipa.sh
# build/Lumen.ipa
```
