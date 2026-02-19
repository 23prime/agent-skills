#!/usr/bin/env python3
"""
Post a new comment on a PR (used when responding to issue-level comments,
which do not support threaded replies via the GitHub REST API).

Usage:
    post_pr_comment.py <owner/repo> <pr_number> <message>

Examples:
    post_pr_comment.py owner/repo 42 "> @alice: your comment\n\nfixed by abc1234"
    post_pr_comment.py owner/repo 42 "> @alice: your comment\n\nNo change: reason here"

Requires: gh CLI authenticated with repo access.
"""

import json
import subprocess
import sys


def main() -> None:
    if len(sys.argv) != 4:
        print(__doc__, file=sys.stderr)
        sys.exit(1)

    repo, pr_number, message = sys.argv[1], sys.argv[2], sys.argv[3]

    result = subprocess.run(
        [
            "gh", "api",
            f"repos/{repo}/issues/{pr_number}/comments",
            "--method", "POST",
            "--raw-field", f"body={message}",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    data = json.loads(result.stdout)
    print(json.dumps({"id": data["id"], "url": data["html_url"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
