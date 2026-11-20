"""Budgets, limits and model choices. Every number here is referenced by an ADR."""
import os

# ADR-002 / ADR-009: bounded loops
MAX_BUILD_ATTEMPTS = 3          # stage 3 -> 4b retries before giving up
MAX_DESIGN_ESCALATIONS = 1      # same failure twice -> back to stage 2, at most once
MAX_STAGE_TRIES = 2             # stages 1, 2, 4a: one retry with the gate's feedback
MAX_REVIEW_ROUNDS = 2           # ADR-002: at most two review rounds

# ADR-009: per-agent step limits and per-run token ceiling (calibrate after first run)
STEP_LIMITS = {
    'analyst': int(os.environ.get('AUTOSE_STEPS_ANALYST', 25)),
    'test_author': int(os.environ.get('AUTOSE_STEPS_TEST_AUTHOR', 25)),
    'builder': int(os.environ.get('AUTOSE_STEPS_BUILDER', 35)),
    'reviewer': int(os.environ.get('AUTOSE_STEPS_REVIEWER', 30)),
}
RUN_TOKEN_CAP = int(os.environ.get('AUTOSE_TOKEN_CAP', 3_000_000))
COMMAND_TIMEOUT = 120            # seconds per shell command an agent runs
CI_WAIT_SECONDS = 1800           # stage 5: max wait for the dispatched CI run

# ADR-006: free tiers, two model families. gemini-2.5-flash was closed to new keys
# (404 on the first real run, 2026-11-20), so the default moved to gemini-3.8-flash.
BUILD_MODEL = os.environ.get('AUTOSE_BUILD_MODEL', 'gemini/gemini-3.8-flash')
REVIEW_MODELS = [m.strip() for m in os.environ.get(
    'AUTOSE_REVIEW_MODELS',
    'github/openai/gpt-4.1-mini,groq/llama-3.3-70b-versatile',
).split(',') if m.strip()]

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
