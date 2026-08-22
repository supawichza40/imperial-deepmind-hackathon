# Gemma 4 on-device — practical reference (verified 2026-08-22)

> **MEASURED CORRECTION (22 Aug 2026, 12:15):** the performance figures below were
> derived from published sources and are **wrong for this team's M1/16GB machine**.
> Actual measured rate on `gemma4:latest`: **4.74 tokens/s**, plus a 65-second cold load —
> roughly 10x slower than the 50-80 tok/s estimated here.
> See [`notes/MEASURED-on-device-reality.md`](../notes/MEASURED-on-device-reality.md)
> before planning any on-device demo. Also note `gemma4:latest` and `gemma4:e4b` are the
> same model (blob `c6eb396dbd59`).



**Yes, Gemma 4 is real and current.** Google DeepMind shipped it on **April 2, 2026**, built "from Gemini 3 research and technology" — this is not the Gemma 3 family. ([DeepMind](https://deepmind.google/models/gemma/gemma-4/), [Google blog](https://blog.google/innovation-and-ai/technology/developers-tools/gemma-4/)) Everything below is Gemma 4 unless a section explicitly says otherwise (some specialized weights — MedGemma, EmbeddingGemma, ShieldGemma — are **still on Gemma 3**, see §2).

---

## 0. Fastest path to a working local model in 10 minutes

Use **Ollama** — one binary, one command, auto-detects your hardware backend (Metal on Mac, CUDA on Nvidia, CPU fallback).

```bash
# 1. Install Ollama if you don't have it (macOS: brew, or the .app from ollama.com)
brew install ollama
ollama serve &     # skip if the menu-bar app is already running

# 2. Pull + run the small edge model (fastest, works on any hackathon laptop)
ollama run gemma4:e2b

# One-shot (no interactive prompt), good for testing in a script:
ollama run gemma4 "What makes a sourdough starter bubbly?"
```

`ollama run gemma4` with no tag pulls the default **E4B** variant. Tags confirmed live on the model page: `gemma4:e2b`, `gemma4:e4b`, `gemma4:12b`, `gemma4:26b` (MoE), `gemma4:31b`. ([ollama.com/library/gemma4](https://ollama.com/library/gemma4), [DeepMind download panel](https://deepmind.google/models/gemma/gemma-4/)) Exact `.gguf` download sizes weren't confirmable from the official page in this pass — third-party guides report the default E4B pull at ~9.6 GB — treat that figure as **UNVERIFIED** and let `ollama pull` tell you the real number.

If you're on an **M1 Mac** specifically, jump to §4 first — `e2b` is the realistic choice, not `e4b` if RAM is 8 GB.

---

## 1. Gemma 4 model family

Five sizes, all instruction-tuned (`-it`) and base checkpoints available, all natively multimodal to some degree. Source: [official model card](https://ai.google.dev/gemma/docs/core/model_card_4).

### Dense models

| Property | E2B | E4B | 12B Unified | 31B Dense |
|---|---|---|---|---|
| Params | 2.3B effective (5.1B incl. embeddings) | 4.5B effective (8B incl. embeddings) | 11.95B | 30.7B |
| Layers | 35 | 42 | 48 | 60 |
| Context length | 128K | 128K | 256K | 256K |
| Vocab | 262K | 262K | 262K | 262K |
| Modalities | Text, Image, Audio | Text, Image, Audio | Text, Image, Audio | Text, Image (no audio) |
| Vision encoder | ~150M params | ~150M params | none (encoder-free) | ~550M params |
| Audio encoder | ~300M params | ~300M params | none (encoder-free) | — |

### Mixture-of-Experts model

| Property | 26B A4B MoE |
|---|---|
| Total params | 25.2B (only **3.8B active** per token — 8 of 128 experts + 1 shared) |
| Layers | 30 |
| Context length | 256K |
| Modalities | Text, Image |
| Vision encoder | ~550M params |

The "E" in E2B/E4B = "effective" parameters (Per-Layer Embeddings keep per-token lookup tables outside the active compute path). The 12B "Unified" model drops dedicated vision/audio encoders entirely — raw patches/waveforms project straight into the LLM embedding space. The two larger dense/MoE models (26B, 31B) additionally handle **video up to 60 seconds**; E2B/E4B/12B add **native audio input** via conformer-style encoders. ([Google blog](https://blog.google/innovation-and-ai/technology/developers-tools/gemma-4/), [model card](https://ai.google.dev/gemma/docs/core/model_card_4))

**License:** Gemma 4 is released under **Apache 2.0** — the first time the Gemma family has used a fully standard open-source license rather than Google's custom Gemma Terms of Use. No usage-restriction carve-outs, no redistribution limits, commercial use is unrestricted. ([Google blog](https://blog.google/innovation-and-ai/technology/developers-tools/gemma-4/), [Google Open Source blog](https://opensource.googleblog.com/2026/03/gemma-4-expanding-the-gemmaverse-with-apache-20.html))

**Quantization:** Google ships official **Quantization-Aware Training (QAT)** checkpoints (not just post-hoc PTQ) for all five sizes, in several download flavors — `-qat-q4_0-gguf` (llama.cpp/LM Studio), `-qat-w4a16-ct` (vLLM/SGLang), `-qat-mobile-ct`/`-qat-mobile-transformers` (mobile), and unquantized QAT weights for custom conversion (e.g. to MLX) plus a matching draft/assistant model for speculative decoding. Collection: [huggingface.co/collections/google/gemma-4-qat-q4-0](https://huggingface.co/collections/google/gemma-4-qat-q4-0). ([ai.google.dev/gemma/docs/core](https://ai.google.dev/gemma/docs/core))

**Reasoning ("thinking mode"):** every size is a configurable reasoner. Put the `<|think|>` token at the start of the system prompt to force step-by-step reasoning before the answer; omit it to answer directly. Libraries like Transformers/llama.cpp handle this via the chat template so you rarely hand-write the tokens. ([model card, Best Practices §2](https://ai.google.dev/gemma/docs/core/model_card_4))

Benchmark headlines circulating post-launch (third-party aggregation, **not independently re-verified here**, treat as reported): 31B scoring ~89% on AIME-2026 math and ranking #3 on an open-source Arena leaderboard at ~1452 Elo. ([labellerr.com summary](https://www.labellerr.com/blog/gemma-4-open-weight-ai-model-overview/) — UNVERIFIED beyond this secondary source.)

---

## 2. Specialized weights — honest status check

The keynote description mentions "specialized medical/multimodal weights." As of today (2026-08-22), **none of Google's specialized Gemma variants have been re-based on Gemma 4 yet** — they're all still Gemma 3-generation:

| Model | Purpose | Base generation | Where to get it |
|---|---|---|---|
| **MedGemma** | Medical text + image understanding | **Gemma 3** (4B multimodal, 27B text-only and multimodal) | [huggingface.co/google/medgemma-4b-it](https://huggingface.co/google/medgemma-4b-it), [github.com/Google-Health/medgemma](https://github.com/Google-Health/medgemma) |
| **EmbeddingGemma** | 100+ language text embeddings, Matryoshka 768→128 dims, 2K context, <200MB RAM | **Gemma 3** | [huggingface.co/google/embeddinggemma-300m](https://huggingface.co/google/embeddinggemma-300m) (308M params) |
| **ShieldGemma 2** | Image/text safety classifier | **Gemma 3** | [huggingface.co/collections/google/shieldgemma-release](https://huggingface.co/collections/google/shieldgemma-release) (4B) |

A community discussion asking whether MedGemma will move to Gemma 4 is open and unanswered as of this writing — treat any "MedGemma-4" claim as **false** until Google actually ships one. ([github.com/google-deepmind/gemma discussion #630](https://github.com/google-deepmind/gemma/discussions/630))

For **code**: search did not surface a dedicated "CodeGemma-4" — Gemma 4's base models are themselves pitched as strong at coding/tool-use out of the box, so there may be no separate code-specialized checkpoint this generation. Treat as **UNVERIFIED absence**, not confirmed non-existence.

Practical implication for the hackathon: if you need a medical/safety/embedding specialist today, you'll be mixing generations — e.g. Gemma 4 E4B as your agent brain + EmbeddingGemma (Gemma 3-based) for retrieval embeddings. That's fine; they're independent checkpoints, just don't expect one unified Gemma-4 chat template across all of them (EmbeddingGemma isn't a chat model anyway).

One extra find, not requested but worth flagging: a **"DiffusionGemma"** collection appeared alongside the official Gemma 4 collection on Hugging Face ([huggingface.co/collections/google/gemma-4](https://huggingface.co/collections/google/gemma-4)). Not investigated further — **UNVERIFIED**, likely an image-diffusion variant, out of scope for a text/agent build.

---

## 3. How to run it today — ranked by realistic time-to-first-token on a laptop

| Rank | Method | Best for | Command |
|---|---|---|---|
| 1 | **Ollama** | Zero-setup CLI, any OS, auto backend detection | `ollama run gemma4:e2b` |
| 2 | **MLX** (Apple Silicon only) | Fastest on M-series Macs specifically | see below |
| 3 | **llama.cpp / GGUF** (LM Studio uses this under the hood) | Fine-grained control, same GGUF works everywhere | see below |
| 4 | **LM Studio** | GUI, non-terminal teammates | search "gemma-4" in-app |
| 5 | **Hugging Face transformers** | Python integration, fine-tuning, custom pipelines | see below |
| 6 | **LiteRT-LM / MediaPipe** | Android/iOS/edge deployment, not desktop iteration | see §7 |
| 7 | **Google AI Edge Gallery app** | No-code phone demo | Play Store / App Store |

### Ollama
```bash
ollama run gemma4:e2b      # smallest, fastest first token
ollama run gemma4:e4b      # default multimodal, laptop-friendly
ollama run gemma4:12b
ollama run gemma4:26b      # MoE, 3.8B active params — fast for its quality
ollama run gemma4:31b      # flagship dense
```
([ollama.com/library/gemma4](https://ollama.com/library/gemma4))

### MLX (Apple Silicon — fastest path on a Mac)
```bash
pip install mlx mlx-lm mlx-vlm

mlx_lm.generate --model mlx-community/gemma-4-e2b-it-4bit --prompt "Who are you?"
# or, in Python:
python -c "
from mlx_lm import load, generate
model, tokenizer = load('mlx-community/gemma-4-e4b-it-4bit')
print(generate(model, tokenizer, prompt='Explain quantum computing simply', max_tokens=256, verbose=True))
"
```
MLX support is officially documented by Google, and `mlx-community` maintains quantized MLX conversions of all five sizes. ([ai.google.dev/gemma/docs/integrations/mlx](https://ai.google.dev/gemma/docs/integrations/mlx))

### llama.cpp / GGUF
```bash
# Unsloth maintains ready GGUFs for every size:
# huggingface.co/unsloth/gemma-4-E2B-it-GGUF (also E4B, 12b, 26B-A4B, 31B)
./llama-cli -hf unsloth/gemma-4-E2B-it-GGUF -p "Hello"
```
Unsloth recommends 8-bit GGUF for the small models and Dynamic 4-bit for the larger ones. ([unsloth.ai/docs/models/gemma-4](https://unsloth.ai/docs/models/gemma-4))

### Hugging Face transformers
```python
from transformers import AutoProcessor, AutoModelForCausalLM
import torch

model_id = "google/gemma-4-E4B-it"
processor = AutoProcessor.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=torch.bfloat16, device_map="auto")
```
Day-one support confirmed for Transformers, TRL, Transformers.js, and Candle. ([blog.google gemma-4 post](https://blog.google/innovation-and-ai/technology/developers-tools/gemma-4/), [huggingface.co/google/gemma-4-E4B-it](https://huggingface.co/google/gemma-4-E4B-it))

### LM Studio
Search "gemma-4" inside the app, or browse [lmstudio.ai/models/gemma-4](https://lmstudio.ai/models/gemma-4). GUI wrapper over llama.cpp — same GGUF ecosystem as above.

---

## 4. THE M1 MAC CONSTRAINT — what actually fits

Honest read for an **8-core Apple M1, CPU-treated-as-default, modest RAM**:

**Use E2B, or E4B if you have 16 GB unified memory. Do not attempt 26B/31B on this machine.**

- **M1 8 GB → `gemma4:e2b` at Q4.** A third-party hardware decision-tree benchmark (post-launch, dated after April 2026) puts this at **~50–80 tok/s** — but that number assumes the normal path: Ollama/llama.cpp/MLX default to the M1's **Metal GPU**, not pure CPU. ([sudoall.com decision tree](https://sudoall.com/gemma-4-31b-apple-silicon-local-guide/))
- **M1/M2 16 GB → `gemma4:e4b` (safe) or `gemma4:26b` MoE (tight, only 3.8B active so it's lighter than its 25B total suggests)**, same source: E4B ~40–60 tok/s, 26B-A4B ~15–25 tok/s.
- A separate benchmark index cites a much lower **~12 tok/s for "M1"** with no model/quant specified — this smells like a genuinely CPU-only (no Metal) number, or a bigger model than E2B. Flagging the discrepancy rather than picking one: **if you disable/can't use Metal (e.g. inside a sandboxed CPU-only container), expect roughly 10x slower than the Metal numbers above.** ([llmcheck.net benchmarks](https://llmcheck.net/benchmarks) — UNVERIFIED methodology)
- For reference, human reading speed is ~4–5 tok/s, so even the pessimistic 12 tok/s figure is still usable for an interactive chat demo — it's the *reasoning-heavy, long-context, or 31B-class* workloads that will feel painful on an M1.

**Bottom line for this teammate's machine:** `ollama run gemma4:e2b` (or `e4b` if RAM allows) is realistically usable at real-time chat speed via Metal. If the demo needs 26B/31B-tier reasoning quality, don't fight the hardware — **fall back to the Gemini API for that specific step** and keep Gemma 4 E2B/E4B for the offline/privacy-demo parts of the pitch (see tradeoff table, §8).

Note this doesn't conflict with the "no GPU-intensive ML on this Mac" household rule — that rule is about *training*, not inference. Running a 2–4B quantized model through Metal for chat inference is normal, low-power CPU/GPU work a MacBook does fine; it's fine-tuning/pretraining that needs the Kaggle T4 offload (see §6).

---

## 5. Function calling / tool use

Gemma 4 supports **native structured tool calls**, not just prompted JSON. The chat template has dedicated special tokens for tool declarations, calls, and responses — this is new/changed from Gemma 3 (which used plain `system`/`user`/`model` turns without this). ([ai.google.dev/gemma/docs/capabilities/text/function-calling-gemma4](https://ai.google.dev/gemma/docs/capabilities/text/function-calling-gemma4))

**Python usage** — pass `tools=` straight into the chat template:
```python
text = processor.apply_chat_template(messages, tools=tools, tokenize=False, add_generation_prompt=True)
inputs = processor(text=text, return_tensors="pt").to(model.device)
out = model.generate(**inputs, max_new_tokens=128)
```

**What the model actually emits under the hood** (decoded with special tokens visible):
```
<|turn>system
You are a helpful assistant.<|tool>declaration:get_current_weather{description:"Gets the current weather in a given location.",parameters:{...},required:["location"],type:"OBJECT"}<tool|><turn|>
<|turn>user
Hey, what's the weather in Tokyo right now?<turn|>
<|turn>model
<|tool_call>call:get_current_weather{location:"Tokyo, JP"}<tool_call|><|tool_response>response:get_current_weather{temperature:15,weather:"sunny"}<tool_response|>The current weather in Tokyo is 15 degrees Celsius and sunny.<turn|>
```
In practice you never hand-write this — Transformers' `apply_chat_template(tools=...)` and llama.cpp both generate/parse it for you. Message history is a list of dicts with `role`, `content`, and (for the assistant turn) `tool_calls` / `tool_responses` keys, matching OpenAI-style function-calling shape. ([same doc](https://ai.google.dev/gemma/docs/capabilities/text/function-calling-gemma4))

**Serving with vLLM:** pass `--chat-template examples/tool_chat_template_gemma4.jinja` so the server applies the same special-token format. ([vLLM forum thread](https://discuss.vllm.ai/t/what-is-the-correct-chat-template-when-serving-gemma4/2606) — community source, secondary confirmation only.)

Runnable notebook: [github.com/google-gemma/cookbook — function-calling-gemma4.ipynb](https://github.com/google-gemma/cookbook/blob/main/docs/capabilities/text/function-calling-gemma4.ipynb) (also opens directly in Colab/Kaggle/Vertex from the official docs page).

---

## 6. Fine-tuning fast — LoRA/QLoRA on a free T4

**What fits on a free Colab/Kaggle T4 (16 GB VRAM) in under 2 hours: E2B and E4B, comfortably.** 26B-A4B and 31B need an A100-class GPU (Colab Pro / paid tier) — don't attempt those on the free T4 today. ([ideas2it.com](https://www.ideas2it.com/blogs/fine-tune-gemma-4-e2b-unsloth), [unsloth.ai/docs/models/gemma-4](https://unsloth.ai/docs/models/gemma-4))

- **LoRA** trains small adapter matrices; the frozen base stays untouched. **QLoRA** additionally quantizes the frozen base to 4-bit, cutting memory further — full fine-tuning would need 80+ GB, QLoRA gets E4B down to fitting a 16 GB card.
- **Unsloth** provides custom CUDA kernels: reported ~1.5–2x faster training and ~30–60% less VRAM than vanilla PEFT/Flash-Attention-2, at no accuracy cost. Official Gemma 4 GGUF/LoRA docs: [unsloth.ai/docs/models/gemma-4](https://unsloth.ai/docs/models/gemma-4). Free ready-to-run notebook: [Unsloth Studio Colab](https://colab.research.google.com/github/unslothai/unsloth/blob/main/studio/Unsloth_Studio_Colab.ipynb).
- A ~100-conversation synthetic/domain dataset, rank-16 LoRA adapters, trains in **well under 20 minutes on a T4** for narrow domain adaptation — illustrative figure from a third-party walkthrough, not a guarantee for your dataset/task. ([ideas2it.com](https://www.ideas2it.com/blogs/fine-tune-gemma-4-e2b-unsloth))

**Recipe (E4B, Kaggle T4):**
```python
pip install unsloth
from unsloth import FastLanguageModel
model, tokenizer = FastLanguageModel.from_pretrained("unsloth/gemma-4-E4B-it", load_in_4bit=True, max_seq_length=4096)
model = FastLanguageModel.get_peft_model(model, r=16, lora_alpha=16, target_modules=["q_proj","k_proj","v_proj","o_proj"])
# then train with TRL's SFTTrainer on your hackathon dataset
```
This is a standard Unsloth pattern (module names may need adjusting to Gemma 4's actual layer names — check the model's config before running); route the actual GPU job through the team's existing **Kaggle T4 pipeline** (`~/.claude/gpu-pipeline/`) rather than the M1 CPU, per the standing local-machine rule. After training, export to GGUF and serve through Ollama/llama.cpp for the demo.

---

## 7. On-device deployment targets

**Android** — two paths:
- **LiteRT-LM** (Kotlin/C++/Python APIs) — the direct low-level runtime. CLI quick start:
  ```bash
  uv tool install litert-lm
  litert-lm run --from-huggingface-repo=litert-community/gemma-4-E2B-it-litert-lm gemma-4-E2B-it.litertlm --prompt="What is the capital of France?"
  ```
  ([developers.google.com/edge/litert-lm/models/gemma-4](https://developers.google.com/edge/litert-lm/models/gemma-4))
- **ML Kit GenAI Prompt API** — higher-level, production-oriented Android integration; **Android Studio "Agent Mode"** now runs on Gemma 4 locally for in-IDE dev assistance. ([android-developers blog, March 2026](http://android-developers.googleblog.com/2026/03/gemma-4-new-standard-for-local-agentic-intelligence.html))
- A new **Multi-Token Prediction (MTP)** feature gives up to 2.2x decode speedup on mobile GPU and up to 1.5x on mobile CPU — recommended for E4B on CPU, selectively for E2B. ([LiteRT-LM Gemma 4 page](https://developers.google.com/edge/litert-lm/models/gemma-4))

**iOS** — LiteRT-LM Swift API (same runtime family as Android), plus the **Google AI Edge Gallery** app on the [App Store](https://apps.apple.com/us/app/google-ai-edge-gallery/id6749645337) for a no-code on-device demo running E2B/E4B with the new "Agent Skills" — multi-step autonomous on-device agent workflows (query external info, generate visualizations, chain to other local models like TTS/image-gen). ([developers.googleblog.com Agent Skills post](https://developers.googleblog.com/bring-state-of-the-art-agentic-skills-to-the-edge-with-gemma-4/))

**Web** — **Transformers.js v4** (Feb 2026, rewritten runtime in C++ with a WebGPU backend, reported 3–10x faster than v3) runs Gemma 4 text generation directly in-browser via WebGPU/ONNX Runtime, no server round-trip. Live demo: [huggingface.co/spaces/webml-community/Gemma-4-WebGPU](https://huggingface.co/spaces/webml-community/Gemma-4-WebGPU). Caveat from the write-ups: **vision (image) input is not yet supported in the browser path** — text-only for now. ([pyimagesearch.com](https://pyimagesearch.com/2026/07/27/running-gemma-4-in-the-browser-with-transformers-js-and-webgpu/), [daily.dev](https://daily.dev/posts/running-gemma-4-in-the-browser-with-transformers-js-and-webgpu-dso1tayuq) — third-party sources, dated after launch, cross-check before relying on this for a demo). MediaPipe's web GenAI task (`@mediapipe/tasks-genai` + WebGPU delegate) is the alternative path but its documented Gemma optimization target in the sources found was Gemma 3n E2B/E4B specifically — **full Gemma 4 parity on MediaPipe-web is UNVERIFIED**, prefer Transformers.js for a browser demo today.

---

## 8. Gemma 4 local vs Gemini API — the honest tradeoff

| Dimension | Gemma 4 local (E2B/E4B on your laptop) | Gemini API (e.g. Gemini 3 Flash) |
|---|---|---|
| **Quality** | Good for chat/coding/tool-use; genuinely strong for its size, but a 2–4B model is not frontier-tier reasoning. 31B is competitive with mid-tier closed models per third-party leaderboard reports, but you can't run 31B well on an M1. | Higher ceiling, especially for hard multi-step reasoning and long-tail knowledge. |
| **Latency** | Depends entirely on your hardware/quant (see §4) — can be very fast (Metal-accelerated E2B) or sluggish (CPU-only, bigger model). No network hop. | ~0.9–1.1s time-to-first-token reported for Flash-tier models via API benchmarking; ~206 tok/s generation for Flash reasoning vs ~35 tok/s for Gemma 4 31B reasoning on comparable API infra. Adds a network round-trip and is subject to conference-wifi flakiness. ([artificialanalysis.ai comparisons](https://artificialanalysis.ai/models/comparisons/gemma-4-31b-vs-gemini-3-flash-reasoning)) |
| **Cost** | Zero marginal cost after download — hardware you already own. | Metered per token; reported reseller pricing has Gemma 4 (self-hosted or via API resellers) around $0.13–0.17/1M tokens vs $0.43–1.31/1M for comparable Gemini Flash tiers — but that's *API* pricing for Gemma, not your local electricity cost, which is effectively free for a demo. |
| **Privacy** | Data never leaves the device — this is literally the keynote's pitch ("privacy-first offline workflows"). | Data is sent to Google's servers. |
| **Offline** | Fully works with zero connectivity — huge advantage on flaky hackathon venue wifi. | Hard-dependent on internet; a dead connection kills the demo outright. |
| **Demo risk** | Risk is thermal throttling / slow tok/s / OOM on stage if you reach for a model too big for the hardware. No external dependency to fail. | Risk is rate limiting, API outage, or wifi dropping mid-pitch — but consistent quality/speed when it works. |

**Recommendation for today's brief specifically:** since the keynote is about local-first/on-device agents, the on-brand move is to demo the **golden path fully offline on Gemma 4 E2B/E4B** (fast, private, no wifi dependency — literally proves the keynote's thesis live), while keeping a Gemini API call wired in as a silent fallback/backup for any step that needs more reasoning headroom than the small local model can deliver, in case a judge pushes on a harder question. This is standard "golden path + safe fallback" demo engineering, not a compromise of the local-first story — you just don't advertise the fallback exists unless asked.

---

## Sources index
- [DeepMind — Gemma 4](https://deepmind.google/models/gemma/gemma-4/)
- [Google blog — Gemma 4 announcement](https://blog.google/innovation-and-ai/technology/developers-tools/gemma-4/)
- [ai.google.dev — Gemma 4 model overview](https://ai.google.dev/gemma/docs/core)
- [ai.google.dev — Gemma 4 model card](https://ai.google.dev/gemma/docs/core/model_card_4)
- [ai.google.dev — Gemma releases changelog](https://ai.google.dev/gemma/docs/releases)
- [ai.google.dev — Gemma 4 function calling](https://ai.google.dev/gemma/docs/capabilities/text/function-calling-gemma4)
- [ai.google.dev — Gemma + MLX](https://ai.google.dev/gemma/docs/integrations/mlx)
- [Google AI Edge — LiteRT-LM Gemma 4](https://developers.google.com/edge/litert-lm/models/gemma-4)
- [Google Developers blog — Agent Skills / AI Edge Gallery](https://developers.googleblog.com/bring-state-of-the-art-agentic-skills-to-the-edge-with-gemma-4/)
- [Google Open Source blog — Apache 2.0 license](https://opensource.googleblog.com/2026/03/gemma-4-expanding-the-gemmaverse-with-apache-20.html)
- [Hugging Face — google/gemma-4-E4B-it](https://huggingface.co/google/gemma-4-E4B-it)
- [Hugging Face — Gemma 4 collection](https://huggingface.co/collections/google/gemma-4)
- [Hugging Face — google/medgemma-4b-it](https://huggingface.co/google/medgemma-4b-it)
- [Hugging Face — google/embeddinggemma-300m](https://huggingface.co/google/embeddinggemma-300m)
- [Hugging Face — ShieldGemma release](https://huggingface.co/collections/google/shieldgemma-release)
- [Ollama — gemma4 library page](https://ollama.com/library/gemma4)
- [Unsloth — Gemma 4 docs](https://unsloth.ai/docs/models/gemma-4)
- [artificialanalysis.ai — Gemma 4 31B vs Gemini 3 Flash](https://artificialanalysis.ai/models/comparisons/gemma-4-31b-vs-gemini-3-flash-reasoning)
- Third-party, cross-checked but not primary: [sudoall.com Apple Silicon guide](https://sudoall.com/gemma-4-31b-apple-silicon-local-guide/), [llmcheck.net benchmarks](https://llmcheck.net/benchmarks), [ideas2it.com Unsloth fine-tuning guide](https://www.ideas2it.com/blogs/fine-tune-gemma-4-e2b-unsloth), [pyimagesearch.com browser guide](https://pyimagesearch.com/2026/07/27/running-gemma-4-in-the-browser-with-transformers-js-and-webgpu/)
