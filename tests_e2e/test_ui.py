"""Python Playwright end-to-end coverage for the server-rendered UI."""

from __future__ import annotations

import json
import re
from typing import Any

from playwright.sync_api import Page, expect

CREATED_PROMPT = {
    "id": "playwright-prompt-1",
    "text": "Draft a release note with rollout risks and rollback steps.",
    "target_model": "gpt-4.1",
    "submitter_tag": None,
    "created_at": "2026-04-19T00:00:00Z",
}

SUCCESSFUL_EVALUATION = {
    "id": "playwright-evaluation-1",
    "prompt_id": CREATED_PROMPT["id"],
    "llm_provider": "none",
    "rationale": "The prompt is clear, structured, and requests concrete operational detail.",
    "scores": {
        "total_score": 86,
        "clarity": 91,
        "correctness": 88,
        "information_density": 84,
        "hallucination_risk": 19,
        "redundancy": 14,
    },
    "created_at": "2026-04-19T00:00:01Z",
}


def _install_fetch_stub(
    page: Page,
    *,
    block_create: bool = False,
    evaluation_status: int = 200,
    evaluation_payload: dict[str, Any] | None = None,
) -> None:
    """Install a deterministic browser-side fetch stub for editor API calls."""

    evaluation_payload = evaluation_payload or SUCCESSFUL_EVALUATION
    script = f"""
    (() => {{
      const originalFetch = window.fetch.bind(window);
      const createdPrompt = {json.dumps(CREATED_PROMPT)};
      const evaluationPayload = {json.dumps(evaluation_payload)};

      window.__createRequestCount = 0;
      window.__releaseCreate = null;

      window.fetch = async (input, init) => {{
        const url = typeof input === "string" ? input : input.url;
        const method = init?.method || (typeof input === "object" && input.method) || "GET";

        if (url.endsWith("/api/v1/prompts") && method === "POST") {{
          window.__createRequestCount += 1;
          if ({str(block_create).lower()}) {{
            await new Promise((resolve) => {{
              window.__releaseCreate = resolve;
            }});
          }}

          return new Response(JSON.stringify(createdPrompt), {{
            status: 201,
            headers: {{ "Content-Type": "application/json" }},
          }});
        }}

        if (url.endsWith("/api/v1/prompts/{CREATED_PROMPT['id']}/evaluate") && method === "POST") {{
          return new Response(JSON.stringify(evaluationPayload), {{
            status: {evaluation_status},
            headers: {{ "Content-Type": "application/json" }},
          }});
        }}

        return originalFetch(input, init);
      }};
    }})();
    """
    page.add_init_script(script=script)


def test_landing_page_links_to_editor(page: Page) -> None:
    """The landing page should route users into the editor."""

    page.goto("/")

    expect(page.get_by_role("heading", level=1)).to_contain_text("Know where a prompt will fail")
    expect(page.get_by_role("link", name="Open Editor")).to_have_attribute("href", "/editor")

    page.get_by_role("link", name="Open Editor").click()
    expect(page).to_have_url(re.compile(r".*/editor$"))
    expect(page.locator("#check-button")).to_be_visible()


def test_editor_page_renders_and_updates_preview(page: Page, mock_editor_cdn: None) -> None:
    """The editor page should render and update the preview as text changes."""

    page.goto("/editor")

    expect(page.get_by_text("Markdown")).to_be_visible()
    expect(page.get_by_text("Preview")).to_be_visible()
    expect(page.locator("#text-hidden")).to_have_value("")
    expect(page.get_by_label("Markdown editor")).to_be_visible()

    page.get_by_label("Markdown editor").fill("# Prompt\n\nWrite a concise launch summary.")
    expect(page.locator("#preview-content")).to_contain_text("Prompt")
    expect(page.locator("#preview-content")).to_contain_text("Write a concise launch summary.")


def test_editor_success_flow_shows_loading_and_results(page: Page, mock_editor_cdn: None) -> None:
    """Successful evaluation should show loading state, then render the returned results."""
    _install_fetch_stub(page, block_create=True)

    page.goto("/editor")
    page.get_by_label("Markdown editor").fill(CREATED_PROMPT["text"])
    page.locator("#target-model").fill(CREATED_PROMPT["target_model"])

    submit = page.locator("#check-button")
    submit.click()

    expect(page.locator("#loading-state")).to_be_visible()
    expect(submit).to_be_disabled()

    page.evaluate("window.__releaseCreate()")

    expect(page.locator("#results-container")).to_contain_text("Total score")
    expect(page.locator("#results-container")).to_contain_text("86")
    expect(page.locator("#results-container")).to_contain_text(CREATED_PROMPT["target_model"])
    expect(page.locator("#results-container")).to_contain_text("none")
    expect(page.locator("#results-container")).to_contain_text(SUCCESSFUL_EVALUATION["rationale"])
    expect(page.locator("#loading-state")).to_be_hidden()
    expect(submit).to_be_enabled()


def test_editor_failure_shows_error_and_recovers_button(page: Page, mock_editor_cdn: None) -> None:
    """Evaluation failures should surface a user-visible error and reset UI state."""

    page.route(
        "**/api/v1/prompts",
        lambda route: route.fulfill(
            status=201, content_type="application/json", json=CREATED_PROMPT
        ),
    )
    page.route(
        f"**/api/v1/prompts/{CREATED_PROMPT['id']}/evaluate",
        lambda route: route.fulfill(
            status=502,
            content_type="application/json",
            json={"detail": "Evaluator unavailable"},
        ),
    )

    page.goto("/editor")
    page.get_by_label("Markdown editor").fill(CREATED_PROMPT["text"])

    submit = page.locator("#check-button")
    submit.click()

    expect(page.locator("#error-banner")).to_contain_text("Evaluator unavailable")
    expect(page.locator("#results-container")).to_be_hidden()
    expect(page.locator("#loading-state")).to_be_hidden()
    expect(submit).to_be_enabled()


def test_editor_rejects_duplicate_submit_while_request_in_flight(
    page: Page,
    mock_editor_cdn: None,
) -> None:
    """A second click during an in-flight submission should not create a second request."""
    _install_fetch_stub(page, block_create=True)

    page.goto("/editor")
    page.get_by_label("Markdown editor").fill(CREATED_PROMPT["text"])

    submit = page.locator("#check-button")
    submit.click()

    expect(page.locator("#loading-state")).to_be_visible()
    expect(submit).to_be_disabled()

    page.evaluate("document.getElementById('editor-form').requestSubmit()")
    page.evaluate("window.__releaseCreate()")

    # Wait for the full flow to complete, then verify only one create request was made.
    expect(page.locator("#results-container")).to_contain_text("Total score")
    assert page.evaluate("window.__createRequestCount") == 1
