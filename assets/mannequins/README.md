# 预置模特图（FASHN Try-On 用）

共 **6 张**：女/男 × 高挑 / 标准 / 丰满。

| 文件 | 说明 |
|------|------|
| `female_tall.jpg` | 女 · 高挑 |
| `female_average.jpg` | 女 · 标准 |
| `female_curvy.jpg` | 女 · 丰满 |
| `male_tall.jpg` | 男 · 高挑 |
| `male_average.jpg` | 男 · 标准 |
| `male_curvy.jpg` | 男 · 丰满 |

## 没有 FASHN API Key 也能演示

应用内置 **6 张 Unsplash 占位图 URL**，步骤 2 可直接预览，**无需 Key、无需生成**。

若要离线 / 不用外网，可下载到本目录（仍不需要 FASHN Key）：

```bash
.venv/bin/python scripts/download_mannequin_placeholders.py
```

## 正式模特图（需 `FASHN_API_KEY`，可选）

用 FASHN **model-create** 按 prompt 生成更统一的打底模特：

```bash
.venv/bin/python scripts/generate_mannequin_assets.py
```

只生成一张示例：

```bash
.venv/bin/python scripts/generate_mannequin_assets.py --only 女,标准
```

强制覆盖已有文件：

```bash
.venv/bin/python scripts/generate_mannequin_assets.py --force
```

生成后把 `assets/mannequins/*.jpg` 提交进仓库，演示时 **不再调用 model-create**，只走 tryon-v1.6 叠衣服，省额度也更稳。

Prompt 模板见 `fitentropy/mannequin_assets.py` 中的 `model_create_prompt()`。
