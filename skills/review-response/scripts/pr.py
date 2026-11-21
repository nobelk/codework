#!/usr/bin/env python3
"""GitHub plumbing for the review-response skill. Standard library plus the `gh` CLI.

  pr.py fetch [PR-URL | PR-number] [--out FILE]
      Print one JSON snapshot of the PR: metadata, review threads with their
      resolution state, review summaries, conversation comments, and Jira-key
      candidates. With no argument, uses the current branch's PR.

  pr.py reply <PR-URL | PR-number> <replies.json> (--expect-head SHA | --dry-run)
      Post replies. replies.json is a list of
        {"reply_to": <thread root_comment_id>, "seen_thread_version": "<version at fetch>", "body": "..."}
        {"conversation": true, "body": "..."}        # one top-level PR comment
      Hold a missing, resolved, incomplete, or changed thread. Skip a reply
      already present. The result
      lists each target under posted / skipped / held / failed (--dry-run: would_post).

  pr.py body <PR-URL | PR-number> <section.md> [--dry-run]
      Replace (or append) the <!-- review-response --> block of the PR description
      with the contents of section.md, leaving the rest of the description as written.

Exit status: 0 on success, 1 when a write failed, 2 when the PR cannot be resolved.
"""

import argparse
import hashlib
import json
import re
import subprocess
import sys

PR_URL = re.compile(r"^https?://([^/]+)/([^/]+)/([^/]+)/pull/(\d+)")
TICKET = re.compile(r"\b[A-Z][A-Z0-9]+-\d+\b")
PLACEHOLDER = re.compile(r"<sha[:>]")  # <sha> or <sha:name>, left unfilled
OID = re.compile(r"[0-9a-f]{40}|[0-9a-f]{64}")
BLOCK_START = "<!-- review-response:start -->"
BLOCK_END = "<!-- review-response:end -->"

THREAD_FIELDS = """
fragment ThreadFields on PullRequestReviewThread {
  id isResolved isOutdated path line originalLine startLine
  resolvedBy{login}
  comments(first:100){
    totalCount
    nodes{fullDatabaseId author{login __typename} body createdAt updatedAt url diffHunk}
  }
}
"""

QUERY = """
query($owner:String!,$repo:String!,$n:Int!,$cursor:String){
  viewer{login}
  repository(owner:$owner,name:$repo){
    pullRequest(number:$n){
      number url title body state isDraft isCrossRepository
      author{login}
      headRefName headRefOid baseRefName
      headRepository{nameWithOwner}
      commits(last:100){nodes{commit{oid message}}}
      reviewThreads(first:50,after:$cursor){
        pageInfo{hasNextPage endCursor}
        nodes{...ThreadFields}
      }
    }
  }
}
""" + THREAD_FIELDS

CURRENT_THREAD_QUERY = """
query($owner:String!,$repo:String!,$n:Int!,$id:ID!){
  repository(owner:$owner,name:$repo){
    pullRequest(number:$n){headRefOid state}
  }
  node(id:$id){... on PullRequestReviewThread{...ThreadFields}}
}
""" + THREAD_FIELDS


class GhError(Exception):
    pass


def gh(args, stdin=None):
    proc = subprocess.run(["gh", *args], input=stdin, capture_output=True, text=True)
    if proc.returncode != 0:
        raise GhError(proc.stderr.strip() or proc.stdout.strip() or f"gh {args[0]} failed")
    return proc.stdout


def resolve(pr_arg):
    """Return (host, owner, repo, number) for a PR URL, a PR number, or the current branch."""
    match = PR_URL.match(pr_arg or "")
    if not match:
        view = ["pr", "view", "--json", "url", "--jq", ".url"]
        if pr_arg:
            view.insert(2, pr_arg)
        try:
            match = PR_URL.match(gh(view).strip())
        except GhError as err:
            print(f"cannot resolve the pull request: {err}", file=sys.stderr)
            sys.exit(2)
        if not match:
            print("cannot resolve the pull request: gh returned no PR url", file=sys.stderr)
            sys.exit(2)
    host, owner, repo, number = match.groups()
    return host, owner, repo, int(number)


def rest_list(host, path):
    """Every item of a paginated REST list endpoint."""
    out = gh(["api", "--hostname", host, "--paginate", path, "--jq", ".[] | tojson"])
    return [json.loads(line) for line in out.splitlines() if line.strip()]


def is_bot(login, kind):
    return kind == "Bot" or (login or "").endswith("[bot]")


def conversation_comments(host, path):
    return [{
        "id": c["id"],
        "author": (c.get("user") or {}).get("login"),
        "is_bot": is_bot((c.get("user") or {}).get("login"), (c.get("user") or {}).get("type")),
        "body": c.get("body") or "",
        "created_at": c.get("created_at"),
        "url": c.get("html_url"),
    } for c in rest_list(host, path)]


def ticket_candidates(pr, commits):
    """Jira-style keys in priority order: branch, title, body, commit messages."""
    seen, found = set(), []
    sources = [
        ("branch", pr["headRefName"].upper()),  # branch names are often lowercased
        ("title", pr["title"]),
        ("body", pr["body"] or ""),
        ("commits", "\n".join(commits)),
    ]
    for source, text in sources:
        for key in TICKET.findall(text):
            if key not in seen:
                seen.add(key)
                found.append({"key": key, "source": source})
    return found


def thread_snapshot(node):
    comments = [{
        "id": int(c["fullDatabaseId"]) if c["fullDatabaseId"] is not None else None,
        "author": (c["author"] or {}).get("login"),
        "is_bot": is_bot((c["author"] or {}).get("login"), (c["author"] or {}).get("__typename")),
        "body": c["body"],
        "created_at": c["createdAt"],
        "updated_at": c["updatedAt"],
        "url": c["url"],
    } for c in node["comments"]["nodes"]]
    if not comments:
        return None
    count = node["comments"]["totalCount"]
    version = None
    # A push may change line anchors even when the conversation is unchanged.
    if count == len(comments):
        content = json.dumps([node["id"], comments], sort_keys=True).encode("utf-8")
        version = hashlib.sha256(content).hexdigest()
    return {
        "node_id": node["id"],
        "root_comment_id": comments[0]["id"],
        "path": node["path"],
        "line": node["line"] or node["originalLine"],
        "start_line": node["startLine"],
        "is_resolved": node["isResolved"],
        "is_outdated": node["isOutdated"],
        "resolved_by": (node["resolvedBy"] or {}).get("login"),
        "comment_count": count,
        "thread_version": version,
        "diff_hunk": node["comments"]["nodes"][0]["diffHunk"],
        "url": comments[0]["url"],
        "comments": comments,
    }


def fetch(host, owner, repo, number):
    threads, cursor, pr, viewer = [], None, None, None
    while True:
        args = ["api", "graphql", "--hostname", host, "-f", f"query={QUERY}",
                "-F", f"owner={owner}", "-F", f"repo={repo}", "-F", f"n={number}"]
        if cursor:
            args += ["-f", f"cursor={cursor}"]
        data = json.loads(gh(args))["data"]
        viewer = data["viewer"]["login"]
        pr = (data["repository"] or {}).get("pullRequest")
        if pr is None:
            raise GhError(f"no pull request #{number} in {owner}/{repo}")
        page = pr["reviewThreads"]
        for node in page["nodes"]:
            thread = thread_snapshot(node)
            if thread is not None:
                threads.append(thread)
        if not page["pageInfo"]["hasNextPage"]:
            break
        cursor = page["pageInfo"]["endCursor"]

    base = f"repos/{owner}/{repo}"
    reviews = [{
        "id": r["id"],
        "author": (r.get("user") or {}).get("login"),
        "is_bot": is_bot((r.get("user") or {}).get("login"), (r.get("user") or {}).get("type")),
        "state": r["state"],
        "body": r.get("body") or "",
        "submitted_at": r.get("submitted_at"),
        "commit_id": r.get("commit_id"),
        "url": r.get("html_url"),
    } for r in rest_list(host, f"{base}/pulls/{number}/reviews") if r["state"] != "PENDING"]
    conversation = conversation_comments(host, f"{base}/issues/{number}/comments")

    commits = [n["commit"]["message"] for n in pr["commits"]["nodes"]]
    unresolved = [t for t in threads if not t["is_resolved"]]
    return {
        "pr": {
            "host": host, "owner": owner, "repo": repo, "number": number,
            "url": pr["url"], "title": pr["title"], "body": pr["body"],
            "state": pr["state"], "is_draft": pr["isDraft"],
            "author": (pr["author"] or {}).get("login"),
            "head_ref": pr["headRefName"], "head_oid": pr["headRefOid"],
            "head_repo": (pr["headRepository"] or {}).get("nameWithOwner"),
            "base_ref": pr["baseRefName"], "is_fork": pr["isCrossRepository"],
        },
        "viewer": viewer,
        "ticket_candidates": ticket_candidates(pr, commits),
        "counts": {
            "threads": len(threads),
            "unresolved": len(unresolved),
            "unresolved_outdated": sum(1 for t in unresolved if t["is_outdated"]),
            "resolved": len(threads) - len(unresolved),
            "reviews_requesting_changes": sum(1 for r in reviews if r["state"] == "CHANGES_REQUESTED"),
            # Review summaries and top-level comments worth reading: not empty, not a bot's, not the author's own.
            "comments_outside_threads": sum(
                1 for c in reviews + conversation
                if c["body"].strip() and not c["is_bot"] and c["author"] != (pr["author"] or {}).get("login")),
        },
        "threads": threads,
        "reviews": reviews,
        "conversation": conversation,
    }


def post(host, path, body):
    out = gh(["api", "--hostname", host, "--method", "POST", path, "--input", "-"],
             stdin=json.dumps({"body": body}))
    return json.loads(out).get("html_url")


def require_reviewed_head(actual_head, state, expected_head):
    if expected_head and actual_head != expected_head:
        raise GhError(f"PR head is {actual_head}, expected {expected_head}")
    if expected_head and state.upper() != "OPEN":
        raise GhError("pull request is no longer open")


def git_oid(value):
    if not OID.fullmatch(value):
        raise argparse.ArgumentTypeError("expected a full Git commit SHA")
    return value


def load_replies(path):
    with open(path, encoding="utf-8") as handle:
        replies = json.load(handle)
    if not isinstance(replies, list):
        raise GhError("expected a list of replies")
    targets = set()
    for number, item in enumerate(replies, 1):
        if not isinstance(item, dict):
            raise GhError(f"reply {number} must be an object")
        body = item.get("body")
        if not isinstance(body, str) or not body.strip() or PLACEHOLDER.search(body):
            raise GhError(f"reply {number} must have a nonempty body with no commit placeholders")
        reply_to = item.get("reply_to")
        if item.get("conversation") is True and "reply_to" not in item:
            target = "conversation"
        elif "conversation" not in item and type(reply_to) is int and reply_to > 0:
            target = reply_to
        else:
            raise GhError(f"reply {number} must name exactly one thread or conversation target")
        if target in targets:
            raise GhError(f"reply {number} repeats target {target}")
        targets.add(target)
    return replies


def current_thread(host, owner, repo, number, node_id, expected_head):
    args = ["api", "graphql", "--hostname", host, "-f", f"query={CURRENT_THREAD_QUERY}",
            "-F", f"owner={owner}", "-F", f"repo={repo}", "-F", f"n={number}", "-f", f"id={node_id}"]
    data = json.loads(gh(args))["data"]
    pr = (data["repository"] or {}).get("pullRequest")
    if pr is None:
        raise GhError("pull request is no longer available")
    require_reviewed_head(pr["headRefOid"], pr["state"], expected_head)
    return thread_snapshot(data["node"]) if data["node"] else None


def reply(host, owner, repo, number, replies, dry_run, expected_head):
    snapshot = fetch(host, owner, repo, number)
    require_reviewed_head(snapshot["pr"]["head_oid"], snapshot["pr"]["state"], expected_head)
    viewer = snapshot["viewer"]
    by_root = {t["root_comment_id"]: t for t in snapshot["threads"]}
    base = f"repos/{owner}/{repo}"
    conversation_path = f"{base}/issues/{number}/comments"
    conversation = snapshot["conversation"]
    result = {"posted": [], "would_post": [], "skipped": [], "held": [], "failed": []}

    for item in replies:
        body = item["body"].strip()
        target = "conversation" if item.get("conversation") else item.get("reply_to")
        entry = {"target": target}
        thread = by_root.get(target)
        if not dry_run:
            try:
                if target == "conversation":
                    conversation = conversation_comments(host, conversation_path)
                    pr = json.loads(gh(["api", "--hostname", host, f"{base}/pulls/{number}"]))
                    require_reviewed_head(pr["head"]["sha"], pr["state"], expected_head)
                elif thread:
                    thread = current_thread(host, owner, repo, number, thread["node_id"], expected_head)
            except GhError as err:
                result["failed"].append({**entry, "error": str(err), "remaining_replies_stopped": True})
                break

        if target == "conversation":
            dup = next((c for c in conversation
                        if c["author"] == viewer and c["body"].strip() == body), None)
            if dup:
                result["skipped"].append({**entry, "reason": "already posted", "url": dup["url"]})
                continue
            path = conversation_path
        else:
            if thread is None:
                result["held"].append({**entry, "reason": "thread is missing"})
                continue
            last = thread["comments"][-1]
            if thread["is_resolved"]:
                result["held"].append({**entry, "reason": "thread resolved since the snapshot"})
                continue
            if not thread["thread_version"]:
                result["held"].append({**entry, "reason": "thread could not be read in full"})
                continue
            if last["author"] == viewer and last["body"].strip() == body:
                result["skipped"].append({**entry, "reason": "already posted", "url": last["url"]})
                continue
            if thread["thread_version"] != item.get("seen_thread_version"):
                result["held"].append({**entry, "reason": "thread changed since the snapshot",
                                       "latest": f'{last["author"]}: {last["body"][:200]}'})
                continue
            path = f"{base}/pulls/{number}/comments/{target}/replies"

        if dry_run:
            result["would_post"].append(entry)
            continue
        try:
            result["posted"].append({**entry, "url": post(host, path, body)})
        except GhError as err:
            result["failed"].append({**entry, "error": str(err)})
    return result


def splice(body, section):
    """The PR description with its review-response block replaced, or appended."""
    block = f"{BLOCK_START}\n{section.strip()}\n{BLOCK_END}"
    start = body.find(BLOCK_START)
    end = body.find(BLOCK_END, start + len(BLOCK_START)) if start != -1 else -1
    if start != -1 and end > start:
        return body[:start] + block + body[end + len(BLOCK_END):]
    return (body.rstrip() + "\n\n" if body.strip() else "") + block + "\n"


def update_body(host, owner, repo, number, section, dry_run, expected_head):
    path = f"repos/{owner}/{repo}/pulls/{number}"
    pr = json.loads(gh(["api", "--hostname", host, path]))
    require_reviewed_head(pr["head"]["sha"], pr["state"], expected_head)
    current = pr["body"] or ""
    new = splice(current, section)
    if dry_run or new == current:
        return {"changed": new != current, "dry_run": dry_run, "body": new}
    out = gh(["api", "--hostname", host, "--method", "PATCH", path, "--input", "-"],
             stdin=json.dumps({"body": new}))
    return {"changed": True, "url": json.loads(out).get("html_url")}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    p_fetch = sub.add_parser("fetch")
    p_fetch.add_argument("pr", nargs="?")
    p_fetch.add_argument("--out")
    p_reply = sub.add_parser("reply")
    p_reply.add_argument("pr")
    p_reply.add_argument("replies")
    p_body = sub.add_parser("body")
    p_body.add_argument("pr")
    p_body.add_argument("section")
    for write_parser in (p_reply, p_body):
        mode = write_parser.add_mutually_exclusive_group(required=True)
        mode.add_argument("--dry-run", action="store_true")
        mode.add_argument("--expect-head", metavar="SHA", type=git_oid)
    args = parser.parse_args()

    target = resolve(args.pr)
    try:
        if args.command == "fetch":
            text = json.dumps(fetch(*target), indent=2)
            if args.out:
                with open(args.out, "w", encoding="utf-8") as handle:
                    handle.write(text + "\n")
                snapshot = json.loads(text)
                print(json.dumps({"out": args.out, "pr": snapshot["pr"]["url"],
                                  "viewer": snapshot["viewer"], "counts": snapshot["counts"],
                                  "ticket_candidates": snapshot["ticket_candidates"]}, indent=2))
            else:
                print(text)
        elif args.command == "reply":
            replies = load_replies(args.replies)
            result = reply(*target, replies, args.dry_run, args.expect_head)
            print(json.dumps(result, indent=2))
            sys.exit(1 if result["failed"] else 0)
        else:
            with open(args.section, encoding="utf-8") as handle:
                result = update_body(*target, handle.read(), args.dry_run, args.expect_head)
            print(json.dumps(result, indent=2))
    except (GhError, OSError, ValueError) as err:
        print(f"gh failed: {err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
