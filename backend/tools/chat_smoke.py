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

Exit code 0 when every check passes.
"""
import argparse
import asyncio
import sys
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
    args = parser.parse_args()
    if not args.as_user and not (args.user and args.password):
        parser.error("give --user and --password, or --as-user")
    if (args.other_user or args.outsider) and not args.as_user:
        parser.error("--other-user and --outsider need --as-user")
    sys.exit(asyncio.run(run(args)))


if __name__ == "__main__":
    main()
