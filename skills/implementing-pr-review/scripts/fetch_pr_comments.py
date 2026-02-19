#!/usr/bin/env python3
"""
Fetch PR review comments from a GitHub Pull Request.

Usage:
    fetch_pr_comments.py <PR_URL>
    fetch_pr_comments.py <OWNER/REPO> <PR_NUMBER>

Examples:
    fetch_pr_comments.py https://github.com/owner/repo/pull/42
    fetch_pr_comments.py owner/repo 42

Output (JSON):
    {
      "pr": { "title": "...", "url": "...", "body": "..." },
      "review_comments": [
        {
          "id": 123,
          "author": "reviewer",
          "path": "src/foo.py",
          "line": 10,
          "body": "Consider using ...",
          "diff_hunk": "@@ -8,6 +8,7 @@\\n ...",
          "outdated": false,
          "resolved": false,
          "replies": [
            { "id": 124, "author": "dev", "body": "fixed by abc1234" }
          ]
        }
      ],
      "issue_comments": [
        {
          "id": 456,
          "author": "reviewer",
          "body": "Overall this looks good but ..."
        }
      ]
    }

review_comments contains only top-level comments (no replies).
Replies are nested under the parent comment's "replies" key.
"outdated" is true when position is null (the diff has moved past the comment).
"resolved" is true when the review thread has been marked resolved on GitHub.

Requires: gh CLI (https://cli.github.com/) authenticated with repo access.
"""

import json
import re
import subprocess
import sys


def run_gh(args: list[str]) -> dict | list:
    """Run a gh CLI command and return parsed JSON output."""
    result = subprocess.run(
        ["gh"] + args,
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


def parse_pr_ref(args: list[str]) -> tuple[str, str]:
    """Parse CLI args into (owner/repo, pr_number) strings."""
    if len(args) == 1:
        # URL format: https://github.com/owner/repo/pull/42
        url = args[0]
        m = re.match(r"https://github\.com/([^/]+/[^/]+)/pull/(\d+)", url)
        if not m:
            print(f"Error: Cannot parse PR URL: {url}", file=sys.stderr)
            sys.exit(1)
        return m.group(1), m.group(2)
    elif len(args) == 2:
        return args[0], args[1]
    else:
        print(__doc__, file=sys.stderr)
        sys.exit(1)


def fetch_resolved_thread_ids(owner: str, repo: str, number: int) -> set[int]:
    """Return the databaseIds of top-level comments in resolved threads.

    Uses the GraphQL API because the REST API does not expose thread resolution.
    Handles pagination so PRs with many threads are covered.
    """
    query = """
query($owner: String!, $repo: String!, $number: Int!, $cursor: String) {
  repository(owner: $owner, name: $repo) {
    pullRequest(number: $number) {
      reviewThreads(first: 100, after: $cursor) {
        nodes {
          isResolved
          comments(first: 1) {
            nodes { databaseId }
          }
        }
        pageInfo { hasNextPage endCursor }
      }
    }
  }
}
""".strip()

    resolved: set[int] = set()
    cursor = None

    while True:
        variables = {"owner": owner, "repo": repo, "number": number, "cursor": cursor}
        body = json.dumps({"query": query, "variables": variables})
        raw = subprocess.run(
            ["gh", "api", "graphql", "--input", "-"],
            input=body,
            capture_output=True,
            text=True,
            check=True,
        )
        result = json.loads(raw.stdout)
        threads = (
            result["data"]["repository"]["pullRequest"]["reviewThreads"]
        )
        for thread in threads["nodes"]:
            if thread["isResolved"]:
                comments = thread["comments"]["nodes"]
                if comments:
                    resolved.add(comments[0]["databaseId"])

        page_info = threads["pageInfo"]
        if not page_info["hasNextPage"]:
            break
        cursor = page_info["endCursor"]

    return resolved


def fetch_pr_comments(repo: str, number: str) -> dict:
    """Fetch PR metadata and all comments."""
    owner, repo_name = repo.split("/", 1)

    # PR metadata
    pr_data = run_gh([
        "api", f"repos/{repo}/pulls/{number}",
        "--jq", "{title: .title, url: .html_url, body: .body}",
    ])

    # Thread resolution status (requires GraphQL)
    resolved_ids = fetch_resolved_thread_ids(owner, repo_name, int(number))

    # Inline review comments (includes both top-level and replies)
    raw_review = run_gh(["api", f"repos/{repo}/pulls/{number}/comments", "--paginate", "--slurp"])

    # Separate top-level comments from replies
    top_level: dict[int, dict] = {}
    replies: dict[int, list] = {}
    for c in raw_review:
        parent_id = c.get("in_reply_to_id")
        if parent_id is None:
            top_level[c["id"]] = c
            replies.setdefault(c["id"], [])
        else:
            replies.setdefault(parent_id, []).append({
                "id": c["id"],
                "author": c["user"]["login"],
                "body": c["body"],
            })

    review_comments = [
        {
            "id": c["id"],
            "author": c["user"]["login"],
            "path": c["path"],
            "line": c.get("line") or c.get("original_line"),
            "body": c["body"],
            "diff_hunk": c.get("diff_hunk", ""),
            # position is null when the surrounding diff has changed (outdated comment)
            "outdated": c.get("position") is None,
            # resolved threads should not be actioned
            "resolved": c["id"] in resolved_ids,
            "replies": replies.get(c["id"], []),
        }
        for c in top_level.values()
    ]

    # General PR issue comments (timeline comments, not inline)
    raw_issue = run_gh(["api", f"repos/{repo}/issues/{number}/comments", "--paginate", "--slurp"])
    issue_comments = [
        {
            "id": c["id"],
            "author": c["user"]["login"],
            "body": c["body"],
        }
        for c in raw_issue
    ]

    return {
        "pr": pr_data,
        "review_comments": review_comments,
        "issue_comments": issue_comments,
    }


def main() -> None:
    args = sys.argv[1:]
    if not args:
        print(__doc__, file=sys.stderr)
        sys.exit(1)

    repo, number = parse_pr_ref(args)
    data = fetch_pr_comments(repo, number)
    print(json.dumps(data, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
