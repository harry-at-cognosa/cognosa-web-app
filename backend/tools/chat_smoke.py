"""Command-line smoke test for the chat service (conversation mode).

Run from `backend/` with the project venv, with the chat service running:

    ../venv/bin/python -m tools.chat_smoke --user NAME --password PASSWORD
    ../venv/bin/python -m tools.chat_smoke --as-user NAME            # local dev only
    ../venv/bin/python -m tools.chat_smoke --as-user NAME --other-user NAME2 --outsider NAME3

--user/--password logs in through the web app. --as-user signs a token locally
with the SECRET from backend/.env, so it needs no password but only works on a
machine that holds that file.

--other-user  a second user whose group also has chat: checks that one user
              cannot see, rename or delete another's conversation.
--outsider    a user whose group does not have chat: checks for HTTP 403.

--turns       also run real conversation turns (retrieval and LLM calls):
              a first question, a follow-up that only makes sense in context,
              a stopped answer, a second send refused while one is in flight,
              and two conversations answering at the same time.
              --collection ID, --llm ID, --q1 and --q2 choose what is asked.
              --keep leaves the test conversations in place for inspection.

Exit code 0 when every check passes.
"""
import argparse
import asyncio
import json
import sys
import time
import httpx

CHECKS: list[tuple[bool, str]] = []


def check(ok: bool, text: str) -> bool:
    CHECKS.append((bool(ok), text))
    print(("PASS  " if ok else "FAIL  ") + text)
    return bool(ok)


async def mint_token(user_name: str) -> str:
    from sqlalchemy import select
    from common.sql_db_async import SqlAsyncSession
    from common.sql_models import User
    from cwa_lib.users import get_jwt_strategy
    async with SqlAsyncSession() as session:
        user = (await session.execute(select(User).where(User.user_name == user_name))).scalar_one_or_none()
    if not user:
        sys.exit(f"User not found: {user_name}")
    return await get_jwt_strategy().write_token(user)


async def login(web: str, user: str, password: str) -> str:
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.post(f"{web}/api/v1/auth/jwt/login", data={"username": user, "password": password})
    if r.status_code != 200:
        sys.exit(f"Login failed: HTTP {r.status_code} {r.text[:200]}")
    return r.json()["access_token"]


def client_for(base: str, token: str) -> httpx.AsyncClient:
    return httpx.AsyncClient(base_url=f"{base}/api/v1/chat", headers={"Authorization": f"Bearer {token}"}, timeout=30)


async def send(c: httpx.AsyncClient, conv_id: int, content: str, gllms_id: int,
               stop_after_tokens: int | None = None, show: bool = False) -> dict:
    """Send one message and read the event stream. Returns what was seen:
    http status, statuses, answer text, the final event, and timing."""
    out = {"http": None, "statuses": [], "answer": "", "final": None, "final_event": None,
           "t_start": time.time(), "t_first_token": None, "t_end": None, "tokens": 0}
    async with c.stream("POST", f"/conversations/{conv_id}/messages",
                        json={"content": content, "gllms_id": gllms_id}, timeout=300) as r:
        out["http"] = r.status_code
        if r.status_code != 200:
            out["final"] = (await r.aread()).decode()[:300]
            out["t_end"] = time.time()
            return out
        event = None
        async for line in r.aiter_lines():
            if line.startswith("event: "):
                event = line[7:]
            elif line.startswith("data: "):
                data = json.loads(line[6:])
                if event == "status":
                    out["statuses"].append(data["text"])
                elif event == "token":
                    if out["t_first_token"] is None:
                        out["t_first_token"] = time.time()
                    out["answer"] += data["t"]
                    out["tokens"] += 1
                    if show:
                        print(data["t"], end="", flush=True)
                    if stop_after_tokens and out["tokens"] >= stop_after_tokens:
                        break  # leaving the block closes the stream: this is what Stop does
                elif event in ("done", "error"):
                    out["final"], out["final_event"] = data, event
    if show:
        print()
    out["t_end"] = time.time()
    return out


async def run_turns(c: httpx.AsyncClient, args, collections: list, llms: list) -> None:
    gvdbs_id = args.collection or collections[0]["gvdbs_id"]
    gllms_id = args.llm or llms[0]["gllms_id"]
    name = next((x["gvdbs_name"] for x in collections if x["gvdbs_id"] == gvdbs_id), "?")
    llm_name = next((x["gllms_name"] for x in llms if x["gllms_id"] == gllms_id), "?")
    print(f"\n--- turns on collection {gvdbs_id} ({name}) with LLM {gllms_id} ({llm_name}) ---")
    created = []

    async def new_conv() -> int:
        r = await c.post("/conversations", json={"gvdbs_id": gvdbs_id, "gllms_id": gllms_id})
        created.append(r.json()["conv_id"])
        return created[-1]

    try:
        # 1. first question
        conv_id = await new_conv()
        print(f"Q1: {args.q1}")
        t1 = await send(c, conv_id, args.q1, gllms_id, show=True)
        ok = check(t1["http"] == 200 and t1["final_event"] == "done" and len(t1["answer"]) > 20,
                   f"first question streams an answer ({len(t1['answer'])} chars in {t1['tokens']} pieces, "
                   f"first piece after {((t1['t_first_token'] or t1['t_end']) - t1['t_start']):.1f}s, "
                   f"total {(t1['t_end'] - t1['t_start']):.1f}s)")
        if not ok:
            print("      ", t1["final"])
            return
        check(t1["final"]["retrieval_query"] == args.q1, "first turn searches the question as typed (no rewrite)")
        check(t1["final"]["title"] == args.q1[:35].rstrip(), f"title set from the first message: {t1['final']['title']!r}")

        # 2. follow-up that needs the context
        print(f"Q2: {args.q2}")
        t2 = await send(c, conv_id, args.q2, gllms_id, show=True)
        rq = (t2["final"] or {}).get("retrieval_query") if t2["final_event"] == "done" else None
        check(t2["final_event"] == "done" and len(t2["answer"]) > 20, "follow-up streams an answer")
        check(bool(rq) and rq != args.q2, f"follow-up was rewritten before searching:\n         {rq!r}")
        check("Understanding the question..." in t2["statuses"], "rewrite step ran on the follow-up")

        r = await c.get(f"/conversations/{conv_id}")
        msgs = r.json()["messages"]
        check([m["role"] for m in msgs] == ["user", "assistant", "user", "assistant"]
              and [m["seqn"] for m in msgs] == [1, 2, 3, 4]
              and all(m["status"] == "complete" for m in msgs),
              "stored: four messages in order, all complete")
        a2 = msgs[3]
        check(a2["retrieval_query"] == rq and (a2["tokens_in"] or 0) > 0 and (a2["tokens_out"] or 0) > 0
              and (a2["seconds"] or 0) > 0, f"answer row carries the search query, token counts "
              f"({a2['tokens_in']} in / {a2['tokens_out']} out) and time ({a2['seconds']}s)")
        check(msgs[1]["content"] == t1["answer"], "stored answer equals what was streamed")

        # 3. stop mid-answer
        t3 = await send(c, conv_id, args.q1, gllms_id, stop_after_tokens=3)
        await asyncio.sleep(2.5)  # the service saves the partial answer after noticing the close
        msgs = (await c.get(f"/conversations/{conv_id}")).json()["messages"]
        last = msgs[-1]
        check(last["role"] == "assistant" and last["status"] == "stopped" and len(last["content"]) > 0,
              f"closing the stream leaves a 'stopped' answer with the partial text ({len(last['content'])} chars, "
              f"{len(t3['answer'])} received before closing)")

        # 4. a second send while one is in flight is refused; the conversation works again afterwards
        first = asyncio.create_task(send(c, conv_id, args.q2, gllms_id))
        await asyncio.sleep(0.7)
        second = await send(c, conv_id, "second message while busy", gllms_id)
        check(second["http"] == 409, f"second send during an answer is refused (HTTP {second['http']})")
        f = await first
        check(f["final_event"] == "done", "the answer in flight still completes")

        # 5. two conversations at the same time
        ca, cb = await new_conv(), await new_conv()
        ra, rb = await asyncio.gather(send(c, ca, args.q1, gllms_id), send(c, cb, args.q1, gllms_id))
        both = ra["final_event"] == "done" and rb["final_event"] == "done"
        dur_a, dur_b = ra["t_end"] - ra["t_start"], rb["t_end"] - rb["t_start"]
        wall = max(ra["t_end"], rb["t_end"]) - min(ra["t_start"], rb["t_start"])
        # Run one after the other they would take dur_a + dur_b; together, about the longer one.
        check(both and wall < 0.8 * (dur_a + dur_b),
              f"two conversations answer concurrently (A {dur_a:.1f}s, B {dur_b:.1f}s, "
              f"both done in {wall:.1f}s)")
    finally:
        if args.keep:
            print(f"      kept conversations: {created}")
        else:
            for conv_id in created:
                await c.delete(f"/conversations/{conv_id}")


async def run(args) -> int:
    if args.as_user:
        token = await mint_token(args.as_user)
    else:
        token = await login(args.web, args.user, args.password)

    async with httpx.AsyncClient(base_url=f"{args.base}/api/v1/chat", timeout=30) as anon:
        r = await anon.get("/options")
        check(r.status_code == 401, f"no token is refused (HTTP {r.status_code})")

    async with client_for(args.base, token) as c:
        r = await c.get("/options")
        if not check(r.status_code == 200, f"GET /options (HTTP {r.status_code})"):
            print(r.text[:300])
            return 1
        options = r.json()
        collections, llms = options["collections"], options["llms"]
        print(f"      collections: {[(x['gvdbs_id'], x['gvdbs_name']) for x in collections]}")
        print(f"      llms: {[(x['gllms_id'], x['gllms_name']) for x in llms]}")
        if not check(bool(collections) and bool(llms), "the group has at least one collection and one LLM"):
            return 1
        gvdbs_id, gllms_id = collections[0]["gvdbs_id"], llms[0]["gllms_id"]

        r = await c.post("/conversations", json={"gvdbs_id": gvdbs_id, "gllms_id": gllms_id})
        check(r.status_code == 201, f"create conversation (HTTP {r.status_code})")
        conv = r.json()
        conv_id = conv["conv_id"]
        check(conv["gvdbs_id"] == gvdbs_id and conv["filters"] is None, "created with the collection and no filters")

        r = await c.post("/conversations", json={"gvdbs_id": 10 ** 9, "gllms_id": gllms_id})
        check(r.status_code == 400, f"unknown collection is refused (HTTP {r.status_code})")
        r = await c.post("/conversations", json={"gvdbs_id": gvdbs_id, "gllms_id": 10 ** 9})
        check(r.status_code == 400, f"unknown LLM is refused (HTTP {r.status_code})")

        r = await c.get("/conversations")
        check(r.status_code == 200 and any(x["conv_id"] == conv_id for x in r.json()), "conversation appears in the list")

        r = await c.get(f"/conversations/{conv_id}")
        check(r.status_code == 200 and r.json()["messages"] == [], "read conversation: no messages yet")

        r = await c.patch(f"/conversations/{conv_id}", json={"title": "smoke test conversation"})
        check(r.status_code == 200 and r.json()["title"] == "smoke test conversation", "rename conversation")

        if args.other_user:
            async with client_for(args.base, await mint_token(args.other_user)) as other:
                r1 = await other.get(f"/conversations/{conv_id}")
                r2 = await other.patch(f"/conversations/{conv_id}", json={"title": "hijacked"})
                r3 = await other.delete(f"/conversations/{conv_id}")
                r4 = await other.get("/conversations")
                check(r1.status_code == 404 and r2.status_code == 404 and r3.status_code == 404,
                      f"another user cannot read, rename or delete it (HTTP {r1.status_code}/{r2.status_code}/{r3.status_code})")
                check(r4.status_code == 200 and all(x["conv_id"] != conv_id for x in r4.json()),
                      "it is absent from the other user's list")
            r = await c.get(f"/conversations/{conv_id}")
            check(r.status_code == 200 and r.json()["title"] == "smoke test conversation", "and it is unchanged")

        r = await c.delete(f"/conversations/{conv_id}")
        check(r.status_code == 200 and r.json()["success"], "delete conversation")
        r = await c.get(f"/conversations/{conv_id}")
        check(r.status_code == 404, f"deleted conversation is gone (HTTP {r.status_code})")

        if args.turns:
            await run_turns(c, args, collections, llms)

    if args.outsider:
        async with client_for(args.base, await mint_token(args.outsider)) as outsider:
            r1 = await outsider.get("/options")
            r2 = await outsider.get("/conversations")
            r3 = await outsider.post("/conversations", json={"gvdbs_id": gvdbs_id, "gllms_id": gllms_id})
            check(r1.status_code == 403 and r2.status_code == 403 and r3.status_code == 403,
                  f"a user of a group without chat is refused (HTTP {r1.status_code}/{r2.status_code}/{r3.status_code})")

    failed = [text for ok, text in CHECKS if not ok]
    print(f"\n{len(CHECKS) - len(failed)} passed, {len(failed)} failed")
    return 1 if failed else 0


def main():
    parser = argparse.ArgumentParser(description="Chat service smoke test")
    parser.add_argument("--base", default="http://127.0.0.1:8001", help="chat service URL")
    parser.add_argument("--web", default="http://127.0.0.1:8000", help="web app URL (for --user login)")
    parser.add_argument("--user")
    parser.add_argument("--password")
    parser.add_argument("--as-user", help="sign a token locally for this user name (local dev only)")
    parser.add_argument("--other-user", help="second user in a chat-enabled group, for the isolation check")
    parser.add_argument("--outsider", help="user in a group without chat, for the 403 check")
    parser.add_argument("--turns", action="store_true", help="also run real conversation turns")
    parser.add_argument("--collection", type=int, help="gvdbs_id to chat with (default: the first)")
    parser.add_argument("--llm", type=int, help="gllms_id to use (default: the first)")
    parser.add_argument("--q1", default="What topics does this collection cover? Name three.")
    parser.add_argument("--q2", default="Tell me more about the second one.")
    parser.add_argument("--keep", action="store_true", help="do not delete the test conversations")
    args = parser.parse_args()
    if not args.as_user and not (args.user and args.password):
        parser.error("give --user and --password, or --as-user")
    if (args.other_user or args.outsider) and not args.as_user:
        parser.error("--other-user and --outsider need --as-user")
    sys.exit(asyncio.run(run(args)))


if __name__ == "__main__":
    main()
