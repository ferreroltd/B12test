import hashlib
import hmac
import json
import os
import sys
from datetime import datetime, timezone
from urllib import request

SUBMISSION_URL = "https://b12.io/apply/submission"
SIGNING_SECRET = b"AlsoAppliedToWebPleaseHireMeB12"


def iso_timestamp() -> str:
    now = datetime.now(timezone.utc)
    return now.strftime("%Y-%m-%dT%H:%M:%S.") + f"{now.microsecond // 1000:03d}Z"


def build_payload() -> dict:
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    server = os.environ.get("GITHUB_SERVER_URL", "https://github.com")
    run_id = os.environ.get("GITHUB_RUN_ID", "")

    return {
        "timestamp": iso_timestamp(),
        "name": os.environ["APPLICANT_NAME"],
        "email": os.environ["APPLICANT_EMAIL"],
        "resume_link": os.environ["RESUME_LINK"],
        "repository_link": f"{server}/{repo}" if repo else os.environ["REPOSITORY_LINK"],
        "action_run_link": (
            f"{server}/{repo}/actions/runs/{run_id}"
            if repo and run_id
            else os.environ["ACTION_RUN_LINK"]
        ),
    }


def submit(payload: dict) -> None:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    signature = hmac.new(SIGNING_SECRET, body, hashlib.sha256).hexdigest()

    req = request.Request(
        SUBMISSION_URL,
        data=body,
        headers={
            "Content-Type": "application/json",
            "X-Signature-256": f"sha256={signature}",
        },
        method="POST",
    )
    with request.urlopen(req) as resp:
        response_body = resp.read().decode("utf-8")
        print(f"Status: {resp.status}")
        print(response_body)
        with open("response.json", "w", encoding="utf-8") as f:
            f.write(response_body)


if __name__ == "__main__":
    submit(build_payload())
