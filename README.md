# FitEntropy

> Every morning, your closet is in a state of maximum entropy. **FitEntropy** fixes that.

AI 穿搭助手：根据你的性别、体型、衣橱与场合，生成搭配方案；可选抓取商品页图片并调用 [FASHN](https://docs.fashn.ai/) 做虚拟试穿。

## 功能

- **三步流程**：① 你是谁（性别 + 体型）→ ② 你有什么（衣橱 + 场合 + 预算）→ ③ Reduce Entropy → 搭配卡片
- **LLM 搭配**：OpenAI 或 Qwen（DashScope），`LLM_PROVIDER=auto` 时优先 OpenAI
- **缺件推荐**：搭配中缺少的单品附零售搜索链接
- **虚拟试穿**（可选）：Bright Data 解锁商品页 → 提取主图 → FASHN try-on；预置 6 套模特图（`assets/mannequins/`）

## 环境要求

- Python **3.11+**
- 见 [`requirements.txt`](requirements.txt)

## 快速开始

```bash
git clone https://github.com/Jiao0216/FitEntrophy.git
cd FitEntrophy

python3.11 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# 编辑 .env，至少填写 OPENAI_API_KEY 或 QWEN_API_KEY

# 可选：下载预置模特占位图
python scripts/download_mannequin_placeholders.py

streamlit run app.py
```

浏览器打开 **http://127.0.0.1:8501**。

## 配置说明

复制 [`.env.example`](.env.example) 为 `.env`（勿提交密钥）。

| 变量 | 说明 |
|------|------|
| `OPENAI_API_KEY` | OpenAI API（推荐） |
| `QWEN_API_KEY` | 通义千问（未配置 OpenAI 时使用） |
| `LLM_PROVIDER` | `auto` / `openai` / `qwen` |
| `BRIGHTDATA_API_KEY` | 可选，抓取商品页主图 |
| `FASHN_API_KEY` | 可选，虚拟试穿 |
| `EVEROS_API_KEY` | 可选，长期记忆（EverOS） |

连通性自检：

```bash
python scripts/test_llm_connection.py
python scripts/test_fashn_connection.py   # 需 FASHN_API_KEY
```

## 项目结构

```
app.py                 # Streamlit 主界面
fitentropy/
  config.py            # 环境与衣橱配置
  outfit_agent.py      # LLM 搭配生成
  pipeline.py          # 趋势 + 零售 enrichment
  tryon_service.py     # FASHN 自动试穿
  mannequin_assets.py  # 预置模特图
  ui_theme.py          # 紫色科技风主题
assets/mannequins/     # 预置模特 JPG
scripts/               # 下载占位图、连通性测试等
```

## 演示模式

侧边栏可开启**演示模式**：无需 API Key 即可浏览 UI 与示例搭配。关闭演示模式后需至少配置 **OpenAI 或 Qwen**；Bright Data / FASHN 为增强能力，非硬性要求。

## 仓库名说明

GitHub 仓库名为 **FitEntrophy**（创建时拼写），本地包与产品名为 **FitEntropy**，功能一致。

## License

MIT（如未另行说明，可按需补充）
