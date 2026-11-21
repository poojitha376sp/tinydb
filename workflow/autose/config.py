"""Budgets, limits and model choices. Every number here is referenced by an ADR."""
import os

# ADR-002 / ADR-009: bounded loops
MAX_BUILD_ATTEMPTS = 3          # stage 3 -> 4b retries before giving up
MAX_DESIGN_ESCALATIONS = 1      # same failure twice -> back to stage 2, at most once
MAX_TEST_REPAIRS = 1            # same test failure twice -> Test Author may fix its test, once
MAX_STAGE_TRIES = 2             # stages 1, 2, 4a: one retry with the gate's feedback
MAX_REVIEW_ROUNDS = 2           # ADR-002: at most two review rounds

# ADR-009: per-agent step limits and per-run token ceiling (calibrate after first run)
STEP_LIMITS = {
    'analyst': int(os.environ.get('AUTOSE_STEPS_ANALYST', 25)),
    'test_author': int(os.environ.get('AUTOSE_STEPS_TEST_AUTHOR', 25)),
    'builder': int(os.environ.get('AUTOSE_STEPS_BUILDER', 35)),
    # 20 suited Groq's 8000 tokens/min; on NVIDIA, Nemotron used all 20 checking and wrote no
    # verdict (E1, 21 Nov). The Gemini baseline never used more than 12, so 40 changes only E1-B.
    'reviewer': int(os.environ.get('AUTOSE_STEPS_REVIEWER', 40)),
}
RUN_TOKEN_CAP = int(os.environ.get('AUTOSE_TOKEN_CAP', 3_000_000))
COMMAND_TIMEOUT = 120            # seconds per shell command an agent runs
CI_WAIT_SECONDS = 1800           # stage 5: max wait for the dispatched CI run

# ADR-006: free tiers, two model families. gemini-2.5-flash was closed to new keys
# (404 on the first real run, 2026-11-20), so the default moved to gemini-3.8-flash.
# Run 3 (same day) lost its hour to 503 "high demand" on gemini-3.8-flash, so the build roles
# now take a fallback chain too; a busy model hands over to the next one (agents.FallbackModel).
# Run 4 showed the free tier allows only 20 requests/day and 5/minute per Flash model, so the
# chain lists every free Google model on the key; busy ones are skipped and used-up ones dropped.
# Free limits on the key (AI Studio, 2026-11-20): Flash Lite 15 RPM / 500 RPD, Flash 5 RPM / 20 RPD,
# Gemma 4 30 RPM but only 16K tokens/min (one agent call is often larger), so Flash Lite leads and
# Gemma is the last resort. All are Google models, so the Reviewer stays another family.
BUILD_MODELS = [m.strip() for m in os.environ.get(
    'AUTOSE_BUILD_MODELS',
    'gemini/gemini-3.5-flash-lite,gemini/gemini-3.1-flash-lite,gemini/gemini-flash-lite-latest,gemini/gemini-3-flash-preview,gemini/gemini-3.8-flash,gemini/gemini-3.7-flash,gemini/gemma-4-31b-it',
).split(',') if m.strip()]
BUILD_MODEL = BUILD_MODELS[0]
GEMINI_THINKING = os.environ.get('AUTOSE_GEMINI_THINKING', 'low')
# Run 5: GitHub Models answered every request with a bare "OK" (HTTP 200) on this account, and
# Groq had retired llama-3.3-70b. A probe found gpt-oss-120b and qwen3.8-27b on Groq, both with
# 1000 requests/day but 8000 tokens/minute; neither is a Google model (ADR-008 independence).
# 21 Nov: Groq's daily token quota ran out for both models halfway through E1. Cerebras needs a
# payment method and NVIDIA's free API had retired gpt-oss, so a probe of NVIDIA's free models
# picked Nemotron 3 Ultra (fast, correct action format, not Google), then Mistral Large 4 and
# MiniMax M3.1 Flash. Groq stays last in case its daily quota has come back.
REVIEW_MODELS = [m.strip() for m in os.environ.get(
    'AUTOSE_REVIEW_MODELS',
    'nvidia_nim/nvidia/nemotron-3-ultra-550b-a55b,nvidia_nim/mistralai/mistral-large-4-1t-a52b,'
    'nvidia_nim/minimaxai/minimax-m3.1-flash,groq/openai/gpt-oss-120b',
).split(',') if m.strip()]
# Per-request input budget (tokens) for models with small free limits; see agents.fit_messages.
CONTEXT_BUDGET = {'groq/': int(os.environ.get('AUTOSE_GROQ_BUDGET', 5000)),
                  'nvidia_nim/': int(os.environ.get('AUTOSE_NVIDIA_BUDGET', 20000))}
BUDGET_MAX_OUTPUT = 2500

# ADR-010: trigger label and labels the workflow sets
TRIGGER_LABEL = 'autose'
LABEL_READY = 'ready-for-human'
LABEL_NEEDS_HUMAN = 'needs-human'
LABEL_FAILED = 'autose-failed'

# Files the agents never see (ADR-003, ADR-005): workflow code, prompts,
# experiment material and results stay outside every agent sandbox.
SANDBOX_EXCLUDE = {
    '.git', '.github', 'workflow', 'architecture', 'experiment', 'results',
    'README.md', 'report.pdf', 'demo.mp4', '.pytest_cache', '.mypy_cache',
    '__pycache__', '_autose_out', 'ARCHITECTURE.md',
}
