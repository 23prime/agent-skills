#!/usr/bin/env python3
"""
Post a reply to a PR inline review comment.

Usage:
    reply_review_comment.py <owner/repo> <comment_id> <message>

Examples:
    reply_review_comment.py owner/repo 123456 "fixed by abc1234"
    reply_review_comment.py owner/repo 123456 "No change: suggestion uses a removed API"

Requires: gh CLI authenticated with repo access.
"""

import json
import subprocess
import sys


def main() -> None:
    if len(sys.argv) != 4:
        print(__doc__, file=sys.stderr)
        sys.exit(1)

    repo, comment_id, message = sys.argv[1], sys.argv[2], sys.argv[3]

    # Look up the PR number from the comment to build the correct reply endpoint
    meta = subprocess.run(
        ["gh", "api", f"repos/{repo}/pulls/comments/{comment_id}", "--jq", ".pull_request_url"],
        capture_output=True,
        text=True,
        check=True,
    )
    pr_number = meta.stdout.strip().rstrip("/").split("/")[-1]

    result = subprocess.run(
        [
            "gh", "api",
            f"repos/{repo}/pulls/{pr_number}/comments/{comment_id}/replies",
            "--method", "POST",
            "--field", f"body={message}",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    data = json.loads(result.stdout)
    print(json.dumps({"id": data["id"], "url": data["html_url"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
