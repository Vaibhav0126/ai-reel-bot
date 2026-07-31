from __future__ import annotations

import time
from collections.abc import Callable
from pathlib import Path

import httpx

from .config import INSTAGRAM_ACCESS_TOKEN, INSTAGRAM_USER_ID

# Instagram Login tokens (IGAA…) use graph.instagram.com + public video_url.
# Facebook Page tokens (EAA…) use graph.facebook.com + resumable rupload.
FB_GRAPH = "https://graph.facebook.com/v21.0"
IG_GRAPH = "https://graph.instagram.com/v21.0"


class InstagramConfigError(RuntimeError):
    pass


def _require_creds() -> tuple[str, str]:
    if not INSTAGRAM_USER_ID or not INSTAGRAM_ACCESS_TOKEN:
        raise InstagramConfigError(
            "Missing INSTAGRAM_USER_ID or INSTAGRAM_ACCESS_TOKEN in bot/.env."
        )
    return INSTAGRAM_USER_ID, INSTAGRAM_ACCESS_TOKEN


def _is_instagram_login_token(token: str) -> bool:
    return token.startswith("IG")


def _graph_base(token: str) -> str:
    return IG_GRAPH if _is_instagram_login_token(token) else FB_GRAPH


def _host_on_pixeldrain(client: httpx.Client, video_path: Path) -> str:
    """Direct MP4 URL without Cloudflare bot challenge pages."""
    with video_path.open("rb") as f:
        resp = client.post(
            "https://pixeldrain.com/api/file",
            files={"file": (video_path.name, f, "video/mp4")},
        )
    if resp.status_code >= 400:
        raise RuntimeError(f"pixeldrain upload failed: {resp.status_code} {resp.text[:300]}")
    file_id = resp.json().get("id")
    if not file_id:
        raise RuntimeError(f"pixeldrain returned no id: {resp.text[:300]}")
    return f"https://pixeldrain.com/api/file/{file_id}"


def _host_on_litterbox(client: httpx.Client, video_path: Path) -> str:
    with video_path.open("rb") as f:
        resp = client.post(
            "https://litterbox.catbox.moe/resources/internals/api.php",
            data={"reqtype": "fileupload", "time": "1h"},
            files={"fileToUpload": (video_path.name, f, "video/mp4")},
        )
    if resp.status_code >= 400 or not resp.text.startswith("https://"):
        raise RuntimeError(f"litterbox upload failed: {resp.status_code} {resp.text[:300]}")
    return resp.text.strip()


def _host_video_publicly(client: httpx.Client, video_path: Path) -> tuple[str, Callable[[], None]]:
    """
    Instagram Login cannot use Meta resumable upload; Meta must fetch a public HTTPS URL.
    Prefer hosts that serve raw bytes (no JS/bot challenge).
    """
    errors: list[str] = []
    for name, fn in (
        ("pixeldrain", _host_on_pixeldrain),
        ("litterbox", _host_on_litterbox),
    ):
        try:
            url = fn(client, video_path)
            # Verify Meta-like fetch: direct bytes, video content-type
            probe = client.get(url, headers={"Range": "bytes=0-1023"}, follow_redirects=True)
            ctype = (probe.headers.get("content-type") or "").lower()
            if probe.status_code >= 400 or "text/html" in ctype:
                raise RuntimeError(
                    f"hosted URL not downloadable as video "
                    f"(status={probe.status_code}, content-type={ctype})"
                )
            print(f"   Public video URL ready via {name}")
            return url, (lambda: None)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{name}: {exc}")

    raise RuntimeError(
        "Could not host video at a Meta-fetchable URL.\n"
        + "\n".join(errors)
        + "\n\nBest fix: use a Facebook Page access token (EAA…) so the bot can "
        "upload the file directly without a public URL. See bot/README.md."
    )


def _wait_for_container(client: httpx.Client, graph: str, creation_id: str, token: str) -> None:
    """
    Poll until FINISHED. Meta sometimes returns a transient ERROR before FINISHED,
    so keep polling briefly after ERROR instead of failing immediately.
    """
    status = "IN_PROGRESS"
    last_body = ""
    error_streak = 0
    for _ in range(60):
        st = client.get(
            f"{graph}/{creation_id}",
            params={"fields": "status_code,status", "access_token": token},
        )
        if st.status_code >= 400:
            # Instagram Login sometimes rejects `status`; retry with status_code only.
            st = client.get(
                f"{graph}/{creation_id}",
                params={"fields": "status_code", "access_token": token},
            )
            if st.status_code >= 400:
                raise RuntimeError(f"Container status check failed: {st.status_code} {st.text}")
        payload = st.json()
        last_body = st.text
        status = payload.get("status_code", "IN_PROGRESS")
        if status == "FINISHED":
            return
        if status in {"ERROR", "EXPIRED"}:
            error_streak += 1
            # Community reports: ERROR can flip to FINISHED shortly after.
            if error_streak >= 4 or status == "EXPIRED":
                detail = payload.get("status") or last_body
                raise RuntimeError(
                    f"Container not ready (status={status}). Detail: {detail}\n"
                    "If this keeps happening with an IGAA token, switch to a Facebook "
                    "Page token (EAA…) so local MP4s upload via resumable rupload."
                )
        else:
            error_streak = 0
        time.sleep(5)


def _resolve_user_id(client: httpx.Client, graph: str, token: str, configured_id: str) -> str:
    """Instagram Login tokens should use /me id when available."""
    if not _is_instagram_login_token(token):
        return configured_id
    me = client.get(f"{graph}/me", params={"fields": "id,username", "access_token": token})
    if me.status_code >= 400:
        return configured_id
    me_id = me.json().get("id") or configured_id
    if me_id != configured_id:
        print(f"   Using Instagram Login user id from token (/me): {me_id}")
    return me_id


def _post_reel_resumable(
    client: httpx.Client,
    graph: str,
    user_id: str,
    token: str,
    video_path: Path,
    caption: str,
    share_to_feed: bool,
) -> dict:
    init = client.post(
        f"{graph}/{user_id}/media",
        data={
            "media_type": "REELS",
            "caption": caption,
            "share_to_feed": "true" if share_to_feed else "false",
            "access_token": token,
            "upload_type": "resumable",
        },
    )
    if init.status_code >= 400:
        raise RuntimeError(f"Resumable container create failed: {init.status_code} {init.text}")
    container = init.json()
    creation_id = container.get("id")
    if not creation_id:
        raise RuntimeError(f"No creation id returned: {container}")

    video_bytes = video_path.read_bytes()
    upload_uri = container.get("uri")
    rupload_url = upload_uri or f"https://rupload.facebook.com/ig-api-upload/v21.0/{creation_id}"
    upload = client.post(
        rupload_url,
        headers={
            "Authorization": f"OAuth {token}",
            "offset": "0",
            "file_size": str(len(video_bytes)),
            "Content-Type": "application/octet-stream",
        },
        content=video_bytes,
    )
    if upload.status_code >= 400:
        raise RuntimeError(f"Video upload failed: {upload.status_code} {upload.text}")

    print("   Waiting for Instagram to process the video…")
    _wait_for_container(client, graph, creation_id, token)
    publish = client.post(
        f"{graph}/{user_id}/media_publish",
        data={"creation_id": creation_id, "access_token": token},
    )
    if publish.status_code >= 400:
        raise RuntimeError(f"Publish failed: {publish.status_code} {publish.text}")
    return publish.json()


def _post_reel_via_url(
    client: httpx.Client,
    graph: str,
    user_id: str,
    token: str,
    video_path: Path,
    caption: str,
    share_to_feed: bool,
) -> dict:
    video_url, cleanup = _host_video_publicly(client, video_path)
    try:
        init = client.post(
            f"{graph}/{user_id}/media",
            data={
                "media_type": "REELS",
                "video_url": video_url,
                "caption": caption,
                "share_to_feed": "true" if share_to_feed else "false",
                "access_token": token,
            },
        )
        if init.status_code >= 400:
            raise RuntimeError(
                "Instagram container create failed. "
                f"{init.status_code}: {init.text}\n"
                "Make sure the token includes instagram_business_content_publish."
            )
        creation_id = init.json().get("id")
        if not creation_id:
            raise RuntimeError(f"No creation id returned: {init.text}")

        print("   Waiting for Instagram to process the video…")
        _wait_for_container(client, graph, creation_id, token)
        publish = client.post(
            f"{graph}/{user_id}/media_publish",
            data={"creation_id": creation_id, "access_token": token},
        )
        if publish.status_code >= 400:
            raise RuntimeError(f"Publish failed: {publish.status_code} {publish.text}")
        return publish.json()
    finally:
        cleanup()


def post_reel(video_path: Path, caption: str, share_to_feed: bool = True) -> dict:
    """
    Publish a Reel via Instagram Graph API.
    - Facebook Page token (EAA…): resumable upload (best for local files)
    - Instagram Login token (IGAA…): public video_url (hosts the MP4 briefly)
    """
    configured_id, token = _require_creds()
    video_path = Path(video_path)
    if not video_path.exists():
        raise FileNotFoundError(video_path)

    graph = _graph_base(token)
    ig_login = _is_instagram_login_token(token)

    with httpx.Client(timeout=180, follow_redirects=True) as client:
        user_id = _resolve_user_id(client, graph, token, configured_id)

        if not ig_login:
            return _post_reel_resumable(
                client, graph, user_id, token, video_path, caption, share_to_feed
            )

        # IG Login: try resumable first (sometimes available), then public URL hosts.
        try:
            print("   Trying resumable upload…")
            return _post_reel_resumable(
                client, graph, user_id, token, video_path, caption, share_to_feed
            )
        except Exception as exc:  # noqa: BLE001
            print(f"   Resumable not available ({exc}); using public video URL…")

        return _post_reel_via_url(
            client, graph, user_id, token, video_path, caption, share_to_feed
        )


def can_post() -> bool:
    return bool(INSTAGRAM_USER_ID and INSTAGRAM_ACCESS_TOKEN)
