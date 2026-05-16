# Agent Forge Hackathon — Deploy FitEntropy on Zeabur

Live demo requirement: project must be **deployed and reachable on the web** before **4:30 PM** submission.

## 1. Claim credits (before deploy)

| Partner | Link / code |
|---------|-------------|
| Zeabur | https://zeabur.com/events?code=BUILDER0516 |
| Bright Data | https://get.brightdata.com/aibuilders10 |
| Qwen Cloud | https://tinyurl.com/qwencloudcredits |
| Qoder | https://tinyurl.com/qodercredits |
| Nosana | https://www.theaibuilders.dev/nosanacredits |
| Butterbase (optional) | Code `FUN0516` at https://dashboard.butterbase.ai/billing |

## 2. Push code to GitHub

```bash
cd /path/to/FitEntrophy-main
git init
git add app.py fitentropy/ assets/ Dockerfile requirements.txt .streamlit/ .env.example .dockerignore
git commit -m "Agent Forge: FitEntropy Zeabur deploy"
git branch -M main
git remote add origin https://github.com/Jiao0216/FitEntrophy.git
git push -u origin main
```

If the repo already exists, use `git pull` first or push to a new branch.

## 3. Deploy on Zeabur (Docker)

1. Open https://zeabur.com and sign in (use **BUILDER0516** for hackathon credits).
2. **New Project** → **Deploy New Service** → **GitHub** → select `FitEntrophy`.
3. Zeabur detects `Dockerfile` automatically (Streamlit on port `${PORT}`, default 8080).
4. Open the service → **Variables** → add secrets from `.env.example`:

| Variable | Required for live demo | Notes |
|----------|----------------------|--------|
| `QWEN_API_KEY` | Yes (or `OPENAI_API_KEY`) | Outfit generation |
| `LLM_PROVIDER` | Optional | `auto` (default) |
| `BRIGHTDATA_API_KEY` | Recommended | Trend scrape + product images |
| `BRIGHTDATA_ZONE` | Optional | `web_unlocker1` |
| `FASHN_API_KEY` | Optional | Virtual try-on |
| `EVEROS_API_KEY` | Optional | Evermind memory |
| `EVEROS_USER_ID` | Optional | e.g. `agent-forge-demo` |
| `DEMO_MODE` | Optional | `demo` = always mock; `auto` = mock when no LLM key |

5. **Networking** → enable **Public** → copy the `*.zeabur.app` URL.
6. Wait for build to finish (green). Open the URL — you should see FitEntropy.

**Judges with no keys:** leave `DEMO_MODE=demo` or omit LLM keys; enable **Demo Mode** in the sidebar for mock outfits + try-on samples.

## 4. Verify locally (optional)

```bash
docker build -t fitentropy .
docker run --rm -p 8080:8080 -e PORT=8080 -e DEMO_MODE=demo fitentropy
# Open http://localhost:8080
```

## 5. Submit

- Form: https://tinyurl.com/agentforgesubmit (deadline **4:30 PM**)
- Include: live Zeabur URL, GitHub repo, stack used (AgentField, Qwen, Bright Data, FASHN, EverOS, Zeabur)

## Stack mapping (for judges)

| Hackathon partner | FitEntropy usage |
|-------------------|------------------|
| **AgentField** | `fitentropy/outfit_agent.py` — `@outfit_agent.reasoner` mesh entry |
| **Qwen Cloud** | `fitentropy/qwen_client.py` — outfit JSON generation |
| **Bright Data** | `brightdata_client.py` — trends + retail page unlock |
| **Evermind / EverOS** | `evermind_memory.py` — style memory |
| **Actionbook** | `actionbook_client.py` — optional CLI hints (`ACTIONBOOK_CLI_HINTS=1`) |
| **Zeabur** | This Dockerfile + public URL |
