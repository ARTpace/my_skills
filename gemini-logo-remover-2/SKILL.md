---
name: gemini-logo-remover
description: 使用 OpenCV 图像修复移除 Gemini 标志、水印或 AI 生成的图片标记。当用户要求移除 Gemini 标志、AI 水印或图片中的任何标志/水印时使用此技能。
---

# Gemini 标志移除器

使用图像修复从 AI 生成的图片中移除 Gemini 标志和水印。

## 设置

```bash
pip install opencv-python numpy pillow --break-system-packages
```

## 用法

### 按坐标

```python
import cv2
import numpy as np

def remove_region(input_path, output_path, x1, y1, x2, y2, radius=5):
    """使用图像修复移除矩形区域。"""
    img = cv2.imread(input_path)
    h, w = img.shape[:2]
    
    mask = np.zeros((h, w), dtype=np.uint8)
    cv2.rectangle(mask, (x1, y1), (x2, y2), 255, -1)
    
    result = cv2.inpaint(img, mask, radius, cv2.INPAINT_TELEA)
    cv2.imwrite(output_path, result)

# 示例：移除坐标处的区域
remove_region('/mnt/user-data/uploads/img.png', 
              '/mnt/user-data/outputs/clean.png',
              x1=700, y1=650, x2=800, y2=720)
```

### 按角落

```python
def remove_corner_logo(input_path, output_path, corner='bottom_right', 
                       w_ratio=0.1, h_ratio=0.1, padding=10):
    """从角落移除标志。corner: top_left, top_right, bottom_left, bottom_right"""
    img = cv2.imread(input_path)
    h, w = img.shape[:2]
    
    lw, lh = int(w * w_ratio), int(h * h_ratio)
    
    coords = {
        'bottom_right': (w - lw - padding, h - lh - padding, w - padding, h - padding),
        'bottom_left': (padding, h - lh - padding, lw + padding, h - padding),
        'top_right': (w - lw - padding, padding, w - padding, lh + padding),
        'top_left': (padding, padding, lw + padding, lh + padding)
    }
    x1, y1, x2, y2 = coords[corner]
    
    mask = np.zeros((h, w), dtype=np.uint8)
    cv2.rectangle(mask, (x1, y1), (x2, y2), 255, -1)
    
    result = cv2.inpaint(img, mask, 5, cv2.INPAINT_TELEA)
    cv2.imwrite(output_path, result)

# 示例：移除右下角标志
remove_corner_logo('/mnt/user-data/uploads/img.png',
                   '/mnt/user-data/outputs/no_logo.png',
                   corner='bottom_right', w_ratio=0.08, h_ratio=0.08)
```

### 查找坐标

```python
img = cv2.imread(input_path)
h, w = img.shape[:2]
print(f"尺寸: {w}x{h}")

# Gemini 星形标志通常位于图片右下角稍微内侧
# 一般坐标：x1=w-150, y1=h-100, x2=w-130, y2=h-55
# 精确位置因图片而异，需要调整
```

## 输出

始终保存到 `/mnt/user-data/outputs/` 并使用 `present_files` 工具。

## 注意

- 图像修复对具有均匀背景的小区域效果最好
- Gemini 标志通常在右下角
- 根据实际标志位置和大小调整坐标/比例
