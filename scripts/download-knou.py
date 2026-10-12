"""Download a KNOU lecture by watching its requests in a logged-in Chrome window."""

from __future__ import annotations

import argparse
import base64
import json
import os
from itertools import count
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import time
from urllib.parse import parse_qs, unquote, urlparse

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Page, Response
from playwright.sync_api import sync_playwright


DEFAULT_PAGE = "https://ucampus.knou.ac.kr/ekp/user/study/retrieveUSTStudy.do"
PROFILE_DIR = Path(os.environ["LOCALAPPDATA"]) / "UniversityKNOU" / "ChromeProfile"
DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parent / "downloads"
LECTURE_TITLE = re.compile(r"^(\d{1,3})\s*강\s*[.．:：-]?\s*(\S.{0,100})$")


def safe_filename(name: str) -> str:
    """Turn a lecture title into a Windows-safe MP4 filename."""
    if name.lower().endswith(".mp4"):
        name = name[:-4]
    stem = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", name).strip().rstrip(" .")
    if not stem or stem.upper() in {
        "CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)),
        *(f"LPT{i}" for i in range(1, 10)),
    }:
        raise ValueError("사용할 수 없는 파일명입니다.")
    return f"{stem}.mp4"


def normalize_lecture_title(text: str) -> str | None:
    match = LECTURE_TITLE.fullmatch(" ".join(text.split()))
    if not match:
        return None
    return f"{int(match.group(1))}강. {match.group(2).strip()}"


def page_lecture_title(page: Page) -> str | None:
    """Use the selected lesson, or an unambiguous visible lesson title."""
    selected: set[str] = set()
    visible: set[str] = set()
    for frame in page.frames:
        try:
            texts = frame.evaluate("""() => {
                const active = '[aria-current="page"], [aria-current="true"], '
                    + '[aria-selected="true"], li.active, li.selected, li.current, '
                    + 'li.on, .lecture.active, .lecture.selected, .lecture.on';
                const selected = [...document.querySelectorAll(active)]
                    .filter(el => el.getClientRects().length)
                    .map(el => el.innerText || '');
                const visible = (document.body?.innerText || '').split('\\n');
                return {selected, visible};
            }""")
        except PlaywrightError:
            continue
        if not isinstance(texts, dict):
            continue
        for text in texts.get("selected") or []:
            if not isinstance(text, str):
                continue
            title = normalize_lecture_title(text)
            if title:
                selected.add(title)
        for text in texts.get("visible") or []:
            if not isinstance(text, str):
                continue
            title = normalize_lecture_title(text)
            if title:
                visible.add(title)
    if len(selected) == 1:
        return next(iter(selected))
    if not selected and len(visible) == 1:
        return next(iter(visible))
    return None


def source_filename(url: str) -> str:
    """Use the source MP4 basename above playlist.m3u8, if it is available."""
    source = unquote(PurePosixPath(urlparse(url).path).parent.name)
    if not source.lower().endswith(".mp4"):
        return "lecture.mp4"
    try:
        return safe_filename(source[:-4])
    except ValueError:
        return "lecture.mp4"


def destination(path_text: str | None, filename: str) -> Path:
    if not path_text:
        folder = DEFAULT_OUTPUT_DIR
    else:
        path = Path(path_text).expanduser()
        if path.is_dir() or not path.suffix:
            folder = path
        elif path.suffix.lower() == ".mp4":
            return path.resolve()
        else:
            raise ValueError("저장 경로는 폴더 또는 .mp4 파일이어야 합니다.")

    folder = folder.resolve()
    stem = Path(filename).stem
    for number in count():
        suffix = "" if number == 0 else f"_{number}"
        candidate = folder / f"{stem}{suffix}.mp4"
        partial = candidate.with_name(candidate.stem + ".part.mp4")
        if not candidate.exists() and not partial.exists():
            return candidate


def playlist_expired(url: str) -> bool:
    token = parse_qs(urlparse(url).query).get("token", [None])[0]
    if not token:
        return False
    try:
        payload = token.split(".")[1]
        payload += "=" * (-len(payload) % 4)
        claims = json.loads(base64.urlsafe_b64decode(payload))
        return int(claims["exp"]) <= time.time()
    except (IndexError, KeyError, TypeError, ValueError):
        return False


def ffmpeg_download(url: str, headers: dict[str, str], output: Path) -> None:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("FFmpeg를 찾을 수 없습니다. PATH를 확인하세요.")
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        raise FileExistsError(f"이미 파일이 있습니다: {output}")
    partial = output.with_name(output.stem + ".part.mp4")
    if partial.exists():
        raise FileExistsError(f"이전 임시 파일이 있습니다: {partial}")

    command = [ffmpeg, "-hide_banner", "-loglevel", "quiet", "-nostdin"]
    if headers.get("user-agent"):
        command += ["-user_agent", headers["user-agent"]]
    if headers.get("referer"):
        command += ["-referer", headers["referer"]]
    extra = []
    for name in ("cookie", "origin", "authorization"):
        value = headers.get(name)
        if value and "\r" not in value and "\n" not in value:
            extra.append(f"{name.title()}: {value}\r\n")
    if extra:
        command += ["-headers", "".join(extra)]
    command += ["-i", url, "-c", "copy", "-n", "-progress", "pipe:1", "-nostats", str(partial)]

    print(f"저장 중: {output}", flush=True)
    try:
        with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                              text=True, encoding="utf-8", errors="replace") as process:
            assert process.stdout is not None
            last_time = ""
            for line in process.stdout:
                if line.startswith("out_time="):
                    current = line.split("=", 1)[1].strip()
                    if current != last_time:
                        print(f"\r처리된 영상: {current}", end="", flush=True)
                        last_time = current
            code = process.wait()
        print()
        if code != 0:
            raise RuntimeError(
                f"FFmpeg가 종료 코드 {code}로 실패했습니다. 인증 또는 영상 형식을 확인하세요."
            )
        partial.replace(output)
    except BaseException:
        partial.unlink(missing_ok=True)
        raise
    print(f"저장 완료: {output}")


def main() -> int:
    parser = argparse.ArgumentParser(description="KNOU 로그인 후 재생한 강의를 MP4로 저장합니다.")
    parser.add_argument("--page-url", default=DEFAULT_PAGE, help="열 KNOU 페이지")
    parser.add_argument("--output", help="저장 폴더 또는 .mp4 파일 경로")
    parser.add_argument("--title", help="자동으로 강의 제목을 찾지 못할 때 사용할 파일명")
    parser.add_argument("--transcribe", action="store_true", help="다운로드 후 한국어 TXT/SRT 전사")
    args = parser.parse_args()
    destination(args.output, "lecture.mp4")  # Validate the requested path early.
    if args.title:
        safe_filename(args.title)

    if urlparse(args.page_url).hostname != "ucampus.knou.ac.kr":
        parser.error("--page-url은 ucampus.knou.ac.kr 주소여야 합니다.")
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    captured: list[tuple[str, dict[str, str], Response]] = []
    with sync_playwright() as playwright:
        try:
            context = playwright.chromium.launch_persistent_context(
                str(PROFILE_DIR), channel="chrome", headless=False,
                accept_downloads=False,
            )
        except PlaywrightError as exc:
            raise RuntimeError(
                "별도 Chrome 창을 열지 못했습니다. 이전 다운로드 창을 닫고 다시 실행하세요."
            ) from exc
        try:
            def is_playlist_response(response: Response) -> bool:
                parsed = urlparse(response.url)
                return (parsed.hostname == "sdnw.knou.ac.kr" and
                        parsed.path.endswith("/playlist.m3u8") and
                        response.status == 200 and not playlist_expired(response.url))

            def on_response(response: Response) -> None:
                if not is_playlist_response(response):
                    return
                try:
                    headers = response.request.all_headers()
                except PlaywrightError:
                    headers = {}
                captured.append((response.url, headers, response))

            context.on("response", on_response)
            page = context.pages[0] if context.pages else context.new_page()
            try:
                page.goto(args.page_url, wait_until="domcontentloaded", timeout=30000)
            except PlaywrightError:
                print("페이지가 바로 열리지 않았습니다. Chrome 창에서 KNOU로 이동하세요.")
            print("Chrome 창에서 KNOU에 로그인하고 원하는 강의를 재생하세요.")
            print("영상 요청을 감지하면 자동으로 다운로드합니다. 취소: Ctrl+C")
            if not captured:
                try:
                    response = context.wait_for_event(
                        "response", predicate=is_playlist_response, timeout=30 * 60 * 1000,
                    )
                    if not captured:
                        on_response(response)
                except PlaywrightError as exc:
                    raise TimeoutError(
                        "새 playlist.m3u8 요청을 찾지 못했습니다. 강의를 재생했는지 확인하세요."
                    ) from exc
            if not captured:
                raise TimeoutError("30분 동안 새 playlist.m3u8 요청을 찾지 못했습니다.")
            url, headers, response = captured[-1]
            filename = source_filename(url)
            if args.title:
                filename = safe_filename(args.title)
            else:
                try:
                    response_page = response.request.frame.page
                except (PlaywrightError, AttributeError):
                    response_page = page
                title = page_lecture_title(response_page)
                if title:
                    filename = safe_filename(title)
                else:
                    print("강의 제목을 확인하지 못해 원본 파일명을 사용합니다. ",
                          "원하는 이름은 --title로 지정할 수 있습니다.")
            output = destination(args.output, filename)
            ffmpeg_download(url, headers, output)
        finally:
            context.close()
    if args.transcribe:
        from knou_transcribe import transcribe
        transcribe(output)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (KeyboardInterrupt, OSError, RuntimeError, TimeoutError, ValueError) as exc:
        print(f"오류: {exc}", file=sys.stderr)
        raise SystemExit(1) from None
