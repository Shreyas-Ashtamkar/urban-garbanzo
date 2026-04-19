"""Fixtures for Playwright browser tests.

Uses the ``pytest-playwright`` plugin for ``page``, ``context``, and ``browser``
fixtures. Only the live-server bootstrap and CDN-stub helpers are defined here.
"""

from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
from collections.abc import Iterator
from pathlib import Path

import httpx
import pytest
from playwright.sync_api import Page, Playwright, Route

ROOT_DIR = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def playwright() -> Iterator[Playwright]:
    """Start Playwright for the full browser test session."""
    from playwright.sync_api import sync_playwright

    pw = sync_playwright().start()
    yield pw
    pw.stop()


def _free_port() -> int:
    """Reserve an ephemeral localhost port for the test server."""

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        sock.listen(1)
        return int(sock.getsockname()[1])


def _wait_for_server(base_url: str, log_path: Path, timeout: float = 30.0) -> None:
    """Poll the health endpoint until the FastAPI app is accepting requests."""

    deadline = time.time() + timeout
    last_error = "server did not respond"

    with httpx.Client(timeout=1.0) as client:
        while time.time() < deadline:
            try:
                response = client.get(f"{base_url}/health")
                if response.status_code == 200:
                    return
                last_error = f"unexpected status {response.status_code}"
            except httpx.HTTPError as exc:
                last_error = str(exc)
            time.sleep(0.25)

    log_output = log_path.read_text(encoding="utf-8") if log_path.exists() else ""
    raise RuntimeError(f"Timed out waiting for {base_url}: {last_error}\n\n{log_output}")


@pytest.fixture(scope="session")
def live_server_url(tmp_path_factory: pytest.TempPathFactory) -> Iterator[str]:
    """Start the real FastAPI app in a subprocess for browser tests."""

    port = _free_port()
    url = f"http://127.0.0.1:{port}"
    db_dir = tmp_path_factory.mktemp("playwright-db")
    log_dir = tmp_path_factory.mktemp("playwright-log")
    db_path = db_dir / "playwright.sqlite3"
    log_path = log_dir / "uvicorn.log"

    env = os.environ.copy()
    env.update(
        {
            "DATABASE_URL": f"sqlite:///{db_path.as_posix()}",
            "DATABASE_GENERATE_SCHEMAS": "true",
            "LLM_PROVIDER": "none",
            "API_PORT": str(port),
        }
    )

    with log_path.open("w", encoding="utf-8") as log_file:
        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "urban_garbanzo.main:app",
                "--host",
                "127.0.0.1",
                "--port",
                str(port),
            ],
            cwd=ROOT_DIR,
            env=env,
            stdout=log_file,
            stderr=subprocess.STDOUT,
        )

        try:
            _wait_for_server(url, log_path)
            yield url
        finally:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=10)


@pytest.fixture(scope="session")
def base_url(live_server_url: str) -> str:
    """Override pytest-playwright's base_url to point at the live test server."""
    return live_server_url


# ---------------------------------------------------------------------------
# CDN module stubs
# ---------------------------------------------------------------------------


def _module_fulfill(route: Route, body: str) -> None:
    """Return a small JavaScript module for CDN-backed editor imports."""

    route.fulfill(
        status=200,
        content_type="application/javascript",
        headers={
            "access-control-allow-origin": "*",
            "access-control-allow-methods": "GET, OPTIONS",
            "cache-control": "no-store",
        },
        body=body,
    )


@pytest.fixture
def mock_editor_cdn(page: Page) -> None:
    """Stub the CDN modules used by the editor page so tests stay deterministic."""

    def handler(route: Route) -> None:
        url = route.request.url

        if "@codemirror/state@6" in url:
            _module_fulfill(
                route,
                """
export class EditorState {
  constructor(config = {}) {
    this.doc = config.doc || "";
    this.extensions = config.extensions || [];
  }

  static create(config = {}) {
    return new EditorState(config);
  }
}
""",
            )
            return

        if "@codemirror/view@6" in url:
            _module_fulfill(
                route,
                """
export const keymap = { of: (value) => value };
export const lineNumbers = () => ({ type: "lineNumbers" });
export const highlightActiveLine = () => ({ type: "highlightActiveLine" });

export class EditorView {
  static lineWrapping = { type: "lineWrapping" };

  static updateListener = {
    of(listener) {
      return { __updateListener: listener };
    },
  };

  constructor({ state, parent }) {
    this.state = {
      ...state,
      doc: {
        toString: () => state.doc || "",
      },
    };

    this.__listener = null;
    for (const extension of state.extensions || []) {
      if (extension && typeof extension === "object" && "__updateListener" in extension) {
        this.__listener = extension.__updateListener;
      }
    }

    const editor = document.createElement("textarea");
    editor.setAttribute("aria-label", "Markdown editor");
    editor.value = state.doc || "";
    editor.className = "playwright-editor-stub";
    parent.appendChild(editor);

    editor.addEventListener("input", () => {
      const nextValue = editor.value;
      this.state.doc = {
        toString: () => nextValue,
      };

      if (this.__listener) {
        this.__listener({
          docChanged: true,
          state: this.state,
        });
      }
    });
  }
}
""",
            )
            return

        if "@codemirror/commands@6" in url:
            _module_fulfill(
                route,
                """
export const defaultKeymap = [];
export const historyKeymap = [];
export const history = () => ({ type: "history" });
""",
            )
            return

        if "@codemirror/lang-markdown@6" in url:
            _module_fulfill(route, 'export const markdown = () => ({ type: "markdown" });')
            return

        if "@codemirror/theme-one-dark@6" in url:
            _module_fulfill(route, 'export const oneDark = { type: "oneDark" };')
            return

        if "marked@12" in url:
            _module_fulfill(
                route,
                """
function escapeHtml(text) {
  return String(text)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\"/g, "&quot;");
}

export const marked = {
  parse(text) {
    const escaped = escapeHtml(text).replace(/\\n/g, "<br>");
    return escaped ? "<p>" + escaped + "</p>" : "";
  },
};
""",
            )
            return

        route.abort()

    page.route("https://esm.sh/**", handler)
