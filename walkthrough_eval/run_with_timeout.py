"""Run a script against a given code folder, with a 60s timeout + retry on each
Gemini call. Transport only: the prompt and everything else are that folder's code.
Usage: run_with_timeout.py <code_dir> <script.py> [args...]"""
import runpy
import sys
import time

code_dir, script = sys.argv[1], sys.argv[2]
sys.argv = [script] + sys.argv[3:]
sys.path.insert(0, code_dir)

import explainer                                   # noqa: E402  (from code_dir)
from google.genai import types                     # noqa: E402


def _get_client():
    if explainer._client is None:
        explainer._client = explainer.genai.Client(
            api_key=explainer._find_api_key(),
            http_options=types.HttpOptions(
                timeout=60_000,
                retry_options=types.HttpRetryOptions(attempts=3, initial_delay=2, max_delay=8)),
        )
    return explainer._client


_orig_generate = explainer._generate


def _generate(level, facts):
    for attempt in range(1, 4):
        try:
            return _orig_generate(level, facts)
        except Exception as err:
            print(f"[timeout-wrapper] attempt {attempt} failed: {err!r}", flush=True)
            if attempt == 3:
                raise
            time.sleep(10)


explainer._get_client = _get_client
explainer._generate = _generate
print(f"[timeout-wrapper] explainer from {explainer.__file__}", flush=True)
runpy.run_path(script, run_name="__main__")
