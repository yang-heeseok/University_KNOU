#!/usr/bin/env python3
"""
동영상 다운로더 (yt-dlp 기반)
=====================================
YouTube, Vimeo, Twitter/X, Instagram, Twitch, Naver TV, Kakao TV 등
yt-dlp가 지원하는 모든 사이트의 영상을 다운로드할 수 있습니다.
전체 지원 사이트: https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md

사용법:
    # 단일 영상 다운로드 (최고화질)
    python yt_downloader.py "https://www.youtube.com/watch?v=xxxxx"
    python yt_downloader.py "https://vimeo.com/123456789"
    python yt_downloader.py "https://x.com/user/status/123456"

    # MP3로 변환 다운로드
    python yt_downloader.py "URL" --mp3

    # 재생목록 전체 다운로드
    python yt_downloader.py "https://www.youtube.com/playlist?list=xxxxx"

    # 화질 지정
    python yt_downloader.py "URL" --quality 720

    # 자막 포함 다운로드
    python yt_downloader.py "URL" --subs

    # URL 목록 파일로 일괄 다운로드 (사이트 혼합 가능)
    python yt_downloader.py --batch urls.txt

    # 썸네일 저장
    python yt_downloader.py "URL" --thumbnail

    # 채널/계정 전체 백업 (날짜별 폴더 자동 정리)
    python yt_downloader.py "https://www.youtube.com/@채널명" --channel

    # 로그인 필요 사이트 (브라우저 쿠키 활용)
    python yt_downloader.py "URL" --cookies-from-browser chrome
    python yt_downloader.py "URL" --cookies-from-browser edge

    # 복합 사용 예시
    python yt_downloader.py "URL" --mp3 --output ./lectures --subs --thumbnail

    # GUI 실행
    python yt_downloader_gui.py

필수 패키지:
    pip install yt-dlp

선택 패키지 (MP3 변환 시):
    ffmpeg 설치 필요 (https://ffmpeg.org/download.html)
"""

import argparse
import io
import os
import re
import sys
import json
import time
import unicodedata
from datetime import datetime
from pathlib import Path

# Windows cp949 콘솔에서 유니코드(이모지, 특수문자) 출력 보장
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

try:
    import yt_dlp
except ImportError:
    print("[오류] yt-dlp가 설치되어 있지 않습니다.")
    print("       설치: pip install yt-dlp")
    sys.exit(1)

import shutil


# ── 외부 도구 경로 자동 감지 ─────────────────────────────────────

def _find_in_known_paths(exe_name: str) -> str | None:
    """PATH에 없는 실행 파일을 알려진 Windows 설치 경로에서 탐색."""
    if shutil.which(exe_name):
        return None  # PATH에 있으므로 별도 지정 불필요

    candidates = [
        Path.home() / "AppData/Local/Microsoft/WinGet/Links",
        Path.home() / "AppData/Local/Microsoft/WinGet/Packages",
        Path.home() / ".deno/bin",
        Path("C:/ProgramData/chocolatey/bin"),
        Path("C:/ffmpeg/bin"),
    ]
    for base in candidates:
        if not base.exists():
            continue
        exe = base / exe_name
        if exe.exists():
            return str(base)
        for exe in base.rglob(exe_name):
            return str(exe.parent)
    return None


def _ensure_path():
    """ffmpeg, deno 등 외부 도구의 경로를 PATH에 추가."""
    additions = []
    for exe in ("ffmpeg.exe", "deno.exe"):
        loc = _find_in_known_paths(exe)
        if loc and loc not in os.environ.get("PATH", ""):
            additions.append(loc)
    if additions:
        os.environ["PATH"] = os.pathsep.join(additions) + os.pathsep + os.environ.get("PATH", "")


_ensure_path()


# ── 한글 제목 보정 ──────────────────────────────────────────────

def fix_korean_filename(title: str) -> str:
    """한글 깨짐 보정 및 파일명에 사용 불가한 문자 제거."""
    # NFC 정규화 (macOS 등에서 자모 분리 현상 방지)
    title = unicodedata.normalize("NFC", title)

    # mojibake 복구 시도: latin-1 로 잘못 디코딩된 UTF-8 복원
    try:
        recovered = title.encode("latin-1").decode("utf-8")
        # 복원 결과에 한글이 있으면 채택
        if re.search(r"[가-힣]", recovered):
            title = recovered
    except (UnicodeDecodeError, UnicodeEncodeError):
        pass

    # Windows 파일명 금지 문자 제거
    title = re.sub(r'[<>:"/\\|?*]', "", title)
    # 연속 공백/점 정리
    title = re.sub(r"\s+", " ", title).strip(". ")
    return title


# ── 진행률 훅 ───────────────────────────────────────────────────

class ProgressHook:
    """다운로드 진행률을 컬러 프로그레스바로 표시."""

    BAR_LEN = 40
    _SPIN = ["|", "/", "-", "\\"]

    def __init__(self):
        self._spin_idx = 0
        self._pp_start: float | None = None

    def __call__(self, d: dict):
        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            downloaded = d.get("downloaded_bytes", 0)
            speed = d.get("speed")
            eta = d.get("eta")

            if total > 0:
                pct = downloaded / total
                filled = int(self.BAR_LEN * pct)
                bar = "█" * filled + "░" * (self.BAR_LEN - filled)
            else:
                bar = "?" * self.BAR_LEN
                pct = 0

            speed_str = f"{speed / 1024 / 1024:.1f}MB/s" if speed else "---"
            eta_str = f"{eta}s" if eta else "---"

            sys.stdout.write(
                f"\r  [\033[36m{bar}\033[0m] "
                f"{pct:6.1%}  {speed_str}  ETA {eta_str}   "
            )
            sys.stdout.flush()

        elif d["status"] == "finished":
            sys.stdout.write("\r" + " " * 80 + "\r")
            filesize = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            size_str = (
                f"{filesize / 1024 / 1024:.1f}MB" if filesize else "완료"
            )
            print(f"  \033[32m✓ 다운로드 완료\033[0m ({size_str})")

    def _pp_label(self, pp: str) -> str:
        if "Audio" in pp:
            return "MP3 변환"
        if "EmbedSub" in pp:
            return "자막 내장"
        if "EmbedThumbnail" in pp:
            return "썸네일 내장"
        if "Metadata" in pp:
            return "메타데이터 기록"
        return pp

    def postprocessor_hook(self, d: dict):
        """후처리(MP3 변환, 자막 내장 등) 상태 표시 (경과 시간 포함)."""
        pp = d.get("postprocessor", "")
        label = self._pp_label(pp)
        if d["status"] == "started":
            self._pp_start = time.time()
            spin = self._SPIN[self._spin_idx % len(self._SPIN)]
            self._spin_idx += 1
            sys.stdout.write(f"\r  \033[33m{spin} {label} 중...\033[0m   ")
            sys.stdout.flush()
        elif d["status"] == "finished":
            elapsed = ""
            if self._pp_start:
                secs = time.time() - self._pp_start
                elapsed = f" ({secs:.0f}초)"
                self._pp_start = None
            sys.stdout.write("\r" + " " * 80 + "\r")
            print(f"  \033[32m✓ {label} 완료\033[0m{elapsed}")


# ── 다운로드 이력 관리 ──────────────────────────────────────────

class DownloadArchive:
    """다운로드한 영상 ID를 기록하여 중복 방지."""

    def __init__(self, archive_path: str):
        self.path = Path(archive_path)
        self._ids: set[str] = set()
        if self.path.exists():
            self._ids = set(self.path.read_text(encoding="utf-8").splitlines())

    def contains(self, video_id: str) -> bool:
        return video_id in self._ids

    def add(self, video_id: str):
        self._ids.add(video_id)
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(video_id + "\n")


# ── 메인 다운로더 ──────────────────────────────────────────────

class DownloadCancelled(Exception):
    """다운로드 취소 시 발생하는 예외."""
    pass


class YTDownloader:
    def __init__(self, args: argparse.Namespace, status_callback=None, cancel_event=None):
        self.args = args
        self.output_dir = Path(args.output).resolve()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.archive = DownloadArchive(self.output_dir / ".yt_archive")
        self.progress = ProgressHook()
        self.pp_hook = self.progress.postprocessor_hook
        self.status_callback = status_callback or (lambda msg: None)
        self.cancel_event = cancel_event
        self.results: list[dict] = []

    def _check_cancel(self):
        """취소 이벤트 확인. 설정되어 있으면 DownloadCancelled 발생."""
        if self.cancel_event and self.cancel_event.is_set():
            raise DownloadCancelled("사용자에 의해 취소됨")

    # ── yt-dlp 옵션 빌드 ────────────────────────────────────

    def _build_opts(self, playlist_title: str | None = None) -> dict:
        """공통 yt-dlp 옵션 딕셔너리 생성."""
        # 출력 경로 템플릿
        if playlist_title:
            safe_pl = fix_korean_filename(playlist_title)
            outtmpl = str(self.output_dir / safe_pl / "%(title)s.%(ext)s")
        else:
            outtmpl = str(self.output_dir / "%(title)s.%(ext)s")

        opts: dict = {
            "outtmpl": outtmpl,
            "progress_hooks": [self.progress],
            "postprocessor_hooks": [self.pp_hook],
            "restrictfilenames": False,
            "windowsfilenames": True,
            "ignoreerrors": True,
            "no_warnings": False,
            "quiet": False,
            "noprogress": True,  # yt-dlp 자체 진행률 끔 (커스텀 훅 사용)
        }

        # 브라우저 쿠키 (로그인 필요 사이트용)
        cookies_browser = getattr(self.args, "cookies_from_browser", None)
        if cookies_browser:
            opts["cookiesfrombrowser"] = (cookies_browser,)

        # 화질 설정
        if self.args.mp3:
            opts["format"] = "bestaudio/best"
            opts["postprocessors"] = [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": str(self.args.audio_quality),
                }
            ]
        else:
            q = self.args.quality
            aac = getattr(self.args, "aac", False)
            if q == "best":
                opts["format"] = "bestvideo*+bestaudio/best"
            else:
                opts["format"] = (
                    f"bestvideo*[height<={q}]+bestaudio/"
                    f"best[height<={q}]/best"
                )

            if aac:
                # MKV로 병합 → MP4 변환 (영상 복사, 오디오만 AAC 인코딩)
                opts["merge_output_format"] = "mkv"
                opts.setdefault("postprocessors", [])
                opts["postprocessors"].insert(0, {
                    "key": "FFmpegVideoConvertor",
                    "preferedformat": "mp4",
                })
                opts.setdefault("postprocessor_args", {})
                opts["postprocessor_args"]["FFmpegVideoConvertor"] = [
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                ]
            else:
                opts["merge_output_format"] = "mp4"

        # 자막
        if self.args.subs:
            opts["writesubtitles"] = True
            opts["writeautomaticsub"] = True
            opts["subtitleslangs"] = ["ko", "en"]
            opts["subtitlesformat"] = "srt/best"

        # 자막 내장 (영상 파일에 자막 트랙으로 병합)
        embed_subs = getattr(self.args, "embed_subs", False)
        if embed_subs:
            # 자막 내장을 위해 자막 다운로드도 함께 활성화
            opts["writesubtitles"] = True
            opts["writeautomaticsub"] = True
            opts["subtitleslangs"] = ["ko", "en"]
            opts["subtitlesformat"] = "srt/best"
            opts.setdefault("postprocessors", [])
            opts["postprocessors"].append({
                "key": "FFmpegEmbedSubtitle",
                "already_have_subtitle": False,
            })
            # 자막을 MP4 호환 형식(mov_text)으로 변환하며 모든 트랙 포함
            opts.setdefault("postprocessor_args", {})
            opts["postprocessor_args"]["FFmpegEmbedSubtitle"] = [
                "-c:s", "mov_text",
            ]

        # 썸네일
        if self.args.thumbnail:
            opts["writethumbnail"] = True
            opts.setdefault("postprocessors", [])
            opts["postprocessors"].append({"key": "EmbedThumbnail"})

        # 메타데이터
        if self.args.metadata:
            opts.setdefault("postprocessors", [])
            opts["postprocessors"].append({"key": "FFmpegMetadata"})

        return opts

    # ── 단일 URL 다운로드 ───────────────────────────────────

    @staticmethod
    def _detect_site(info: dict) -> str:
        """추출된 메타데이터에서 사이트명을 감지."""
        extractor = info.get("extractor_key") or info.get("extractor") or ""
        if extractor:
            return extractor
        webpage_url = info.get("webpage_url") or ""
        if webpage_url:
            from urllib.parse import urlparse
            return urlparse(webpage_url).netloc
        return "unknown"

    def _extract_opts(self) -> dict:
        """메타데이터 추출용 공통 옵션 (쿠키 포함)."""
        opts = {"quiet": True, "no_warnings": True}
        cookies_browser = getattr(self.args, "cookies_from_browser", None)
        if cookies_browser:
            opts["cookiesfrombrowser"] = (cookies_browser,)
        return opts

    def download_url(self, url: str):
        """URL 하나를 다운로드 (단일 영상 또는 재생목록)."""
        print(f"\n\033[1m▶ URL 분석 중...\033[0m {url}")

        # 먼저 메타데이터 추출
        with yt_dlp.YoutubeDL(self._extract_opts()) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
            except Exception as e:
                print(f"  \033[31m✗ URL 분석 실패:\033[0m {e}")
                return

        if info is None:
            print("  \033[31m✗ 영상 정보를 가져올 수 없습니다.\033[0m")
            return

        site = self._detect_site(info)
        print(f"  \033[1m🌐 사이트:\033[0m {site}")
        self.status_callback({"type": "log", "text": f"사이트 감지: {site}"})

        # 재생목록인지 판별
        if info.get("_type") == "playlist" or "entries" in info:
            self._download_playlist(url, info)
        else:
            self._download_single(url, info)

    def _download_single(self, url: str, info: dict):
        """단일 영상 다운로드."""
        self._check_cancel()
        video_id = info.get("id", "")
        raw_title = info.get("title", "unknown")
        title = fix_korean_filename(raw_title)

        if self.archive.contains(video_id):
            print(f"  ⏭ 이미 다운로드됨 (스킵): {title}")
            return

        duration = info.get("duration", 0)
        dur_str = f"{duration // 60}:{duration % 60:02d}" if duration else "?"
        print(f"  📹 {title}  ({dur_str})")
        self.status_callback({"type": "video_start", "title": title})

        opts = self._build_opts()
        with yt_dlp.YoutubeDL(opts) as ydl:
            try:
                ydl.download([url])
                self.archive.add(video_id)
                self.results.append({"id": video_id, "title": title, "status": "ok"})
            except Exception as e:
                print(f"  \033[31m✗ 다운로드 실패:\033[0m {e}")
                self.results.append(
                    {"id": video_id, "title": title, "status": "error", "error": str(e)}
                )

    def _download_playlist(self, url: str, info: dict):
        """재생목록 전체 다운로드."""
        pl_title = fix_korean_filename(info.get("title", "playlist"))
        entries = list(info.get("entries", []))
        total = len(entries)

        print(f"\n\033[1m📂 재생목록: {pl_title} ({total}개 영상)\033[0m")

        opts = self._build_opts(playlist_title=pl_title)

        for i, entry in enumerate(entries, 1):
            self._check_cancel()
            if entry is None:
                continue
            video_id = entry.get("id", "")
            raw_title = entry.get("title", "unknown")
            title = fix_korean_filename(raw_title)

            if self.archive.contains(video_id):
                print(f"  [{i}/{total}] ⏭ 스킵: {title}")
                continue

            duration = entry.get("duration", 0)
            dur_str = f"{duration // 60}:{duration % 60:02d}" if duration else "?"
            print(f"  [{i}/{total}] 📹 {title}  ({dur_str})")
            self.status_callback({
                "type": "playlist_progress", "current": i, "total": total,
                "title": title,
            })

            with yt_dlp.YoutubeDL(opts) as ydl:
                try:
                    ydl.download([entry.get("url") or entry.get("webpage_url", "")])
                    self.archive.add(video_id)
                    self.results.append(
                        {"id": video_id, "title": title, "status": "ok"}
                    )
                except Exception as e:
                    print(f"  \033[31m✗ 실패:\033[0m {e}")
                    self.results.append(
                        {"id": video_id, "title": title, "status": "error", "error": str(e)}
                    )

        print(f"\n\033[1m📂 재생목록 완료: {pl_title}\033[0m")

    # ── 채널 전체 백업 ────────────────────────────────────────

    def download_channel(self, url: str):
        """채널/계정의 모든 영상을 날짜별 폴더로 백업."""
        print(f"\n\033[1m📡 채널/계정 분석 중...\033[0m {url}")
        self.status_callback({"type": "log", "text": f"채널/계정 분석 중... {url}"})

        # 영상 목록 빠르게 추출 (메타데이터만)
        extract_opts = self._extract_opts()
        extract_opts["extract_flat"] = "in_playlist"
        with yt_dlp.YoutubeDL(extract_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
            except Exception as e:
                print(f"  \033[31m✗ 채널 분석 실패:\033[0m {e}")
                return

        if info is None:
            print("  \033[31m✗ 채널 정보를 가져올 수 없습니다.\033[0m")
            return

        channel_name = fix_korean_filename(
            info.get("channel") or info.get("uploader") or info.get("title", "unknown_channel")
        )
        entries = [e for e in info.get("entries", []) if e is not None]
        total = len(entries)

        # 채널 정보 출력
        print(f"\n{'='*60}")
        print(f"  \033[1m📡 채널:\033[0m {channel_name}")
        print(f"  \033[1m📹 총 영상:\033[0m {total}개")
        print(f"  \033[1m🆔 채널 ID:\033[0m {info.get('channel_id', 'N/A')}")
        print(f"  \033[1m📂 저장 경로:\033[0m {self.output_dir / channel_name}")
        print(f"{'='*60}")
        self.status_callback({
            "type": "channel_info",
            "channel": channel_name, "total": total,
        })

        # 채널 메타데이터 저장
        channel_dir = self.output_dir / channel_name
        channel_dir.mkdir(parents=True, exist_ok=True)

        meta = {
            "channel_name": channel_name,
            "channel_id": info.get("channel_id"),
            "channel_url": info.get("channel_url") or url,
            "total_videos": total,
            "backup_started": datetime.now().isoformat(),
        }
        meta_path = channel_dir / "channel_info.json"
        meta_path.write_text(
            json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        # 날짜별 폴더 출력 템플릿으로 다운로드
        opts = self._build_opts()
        opts["outtmpl"] = str(
            channel_dir / "%(upload_date>%Y-%m)s" / "%(title)s.%(ext)s"
        )

        for i, entry in enumerate(entries, 1):
            self._check_cancel()
            video_id = entry.get("id", "")
            title = fix_korean_filename(entry.get("title", "unknown"))

            if self.archive.contains(video_id):
                print(f"  [{i}/{total}] ⏭ 스킵: {title}")
                continue

            print(f"  [{i}/{total}] 📹 {title}")
            self.status_callback({
                "type": "channel_progress",
                "current": i, "total": total, "title": title,
            })

            video_url = entry.get("url") or entry.get("webpage_url") or ""
            if not video_url:
                print(f"  \033[31m✗ URL 없음 (스킵): {title}\033[0m")
                continue

            with yt_dlp.YoutubeDL(opts) as ydl:
                try:
                    ydl.download([video_url])
                    self.archive.add(video_id)
                    self.results.append(
                        {"id": video_id, "title": title, "status": "ok"}
                    )
                except Exception as e:
                    print(f"  \033[31m✗ 실패:\033[0m {e}")
                    self.results.append(
                        {"id": video_id, "title": title, "status": "error", "error": str(e)}
                    )

        # 완료 시각 기록
        meta["backup_completed"] = datetime.now().isoformat()
        meta["downloaded"] = sum(1 for r in self.results if r["status"] == "ok")
        meta_path.write_text(
            json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"\n\033[1m📡 채널 백업 완료: {channel_name}\033[0m")

    # ── 배치 파일 처리 ──────────────────────────────────────

    def download_batch(self, batch_file: str):
        """텍스트 파일의 URL 목록을 순차 다운로드."""
        path = Path(batch_file)
        if not path.exists():
            print(f"\033[31m✗ 파일을 찾을 수 없습니다: {batch_file}\033[0m")
            return

        urls = [
            line.strip()
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]

        print(f"\n\033[1m📋 배치 다운로드: {len(urls)}개 URL\033[0m")
        for i, url in enumerate(urls, 1):
            print(f"\n{'='*60}")
            print(f"  [{i}/{len(urls)}]")
            self.download_url(url)

    # ── 결과 요약 ───────────────────────────────────────────

    def print_summary(self):
        """다운로드 결과 요약 출력."""
        if not self.results:
            return

        ok = sum(1 for r in self.results if r["status"] == "ok")
        fail = sum(1 for r in self.results if r["status"] == "error")

        print(f"\n{'='*60}")
        print(f"\033[1m📊 다운로드 결과 요약\033[0m")
        print(f"  성공: \033[32m{ok}\033[0m  /  실패: \033[31m{fail}\033[0m")
        print(f"  저장 경로: {self.output_dir}")

        if fail > 0:
            print(f"\n  \033[31m실패 목록:\033[0m")
            for r in self.results:
                if r["status"] == "error":
                    print(f"    - {r['title']}: {r.get('error', '알 수 없는 오류')}")

        # 결과를 JSON 로그로 저장
        log_path = self.output_dir / f"download_log_{datetime.now():%Y%m%d_%H%M%S}.json"
        log_path.write_text(
            json.dumps(self.results, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"  로그 저장: {log_path.name}")


# ── CLI 인자 파싱 ───────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="동영상 다운로더 (yt-dlp 기반, YouTube/Vimeo/X/Instagram 등 1800+ 사이트 지원)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  %(prog)s "https://youtu.be/xxxxx"                     YouTube 영상
  %(prog)s "https://vimeo.com/123456"                    Vimeo 영상
  %(prog)s "https://x.com/user/status/123"               X(Twitter) 영상
  %(prog)s "URL" --mp3                                   MP3 변환
  %(prog)s "https://youtube.com/playlist?list=xxx"       재생목록 전체
  %(prog)s --batch urls.txt --mp3 --output ./music       배치 (사이트 혼합 가능)
  %(prog)s "URL" --quality 720 --subs --thumbnail        720p + 자막 + 썸네일
  %(prog)s "https://youtube.com/@Channel" --channel      채널/계정 전체 백업
  %(prog)s "로그인필요URL" -c chrome                     브라우저 쿠키 인증
        """,
    )

    p.add_argument("url", nargs="?", help="동영상 URL (YouTube, Vimeo, X, Instagram 등)")
    p.add_argument("--batch", "-b", metavar="FILE", help="URL 목록 텍스트 파일")
    p.add_argument("--output", "-o", default="./downloads", help="저장 경로 (기본: ./downloads)")
    p.add_argument("--mp3", action="store_true", help="MP3로 변환 (ffmpeg 필요)")
    p.add_argument("--audio-quality", type=int, default=192, help="MP3 비트레이트 kbps (기본: 192)")
    p.add_argument(
        "--quality", "-q", default="best",
        help="영상 화질: best, 2160, 1080, 720, 480, 360 (기본: best)",
    )
    p.add_argument("--aac", action="store_true", help="AAC 오디오 선택 (Windows 기본 플레이어 호환)")
    p.add_argument("--subs", "-s", action="store_true", help="자막 다운로드 (ko/en)")
    p.add_argument("--embed-subs", action="store_true", help="자막을 영상에 내장 (mp4 자막 트랙)")
    p.add_argument("--thumbnail", "-t", action="store_true", help="썸네일 저장")
    p.add_argument("--metadata", "-m", action="store_true", help="메타데이터 임베드 (ffmpeg 필요)")
    p.add_argument("--channel", action="store_true", help="채널/계정 전체 백업 모드 (날짜별 폴더 정리)")
    p.add_argument(
        "--cookies-from-browser", "-c", metavar="BROWSER",
        help="브라우저 쿠키로 인증 (chrome, edge, firefox, safari 등)",
    )
    p.add_argument("--info", action="store_true", help="다운로드 없이 영상 정보만 출력")

    args = p.parse_args()

    if not args.url and not args.batch:
        p.error("URL 또는 --batch 파일을 지정해주세요.")

    return args


# ── 영상 정보 조회 모드 ─────────────────────────────────────────

def print_info(url: str, cookies_from_browser: str | None = None):
    """다운로드 없이 영상 정보만 출력."""
    print(f"\n\033[1m🔍 영상 정보 조회\033[0m")

    opts = {"quiet": True, "no_warnings": True}
    if cookies_from_browser:
        opts["cookiesfrombrowser"] = (cookies_from_browser,)
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)

    if info is None:
        print("  \033[31m✗ 정보를 가져올 수 없습니다.\033[0m")
        return

    site = info.get("extractor_key") or info.get("extractor") or "unknown"
    print(f"  🌐 사이트: {site}")

    if info.get("_type") == "playlist" or "entries" in info:
        entries = list(info.get("entries", []))
        print(f"  📂 재생목록: {info.get('title', '?')}")
        print(f"  영상 수: {len(entries)}")
        for i, e in enumerate(entries, 1):
            if e is None:
                continue
            dur = e.get("duration", 0)
            dur_str = f"{dur // 60}:{dur % 60:02d}" if dur else "?"
            print(f"    {i:3d}. {fix_korean_filename(e.get('title', '?'))}  ({dur_str})")
    else:
        title = fix_korean_filename(info.get("title", "?"))
        dur = info.get("duration", 0)
        dur_str = f"{dur // 60}:{dur % 60:02d}" if dur else "?"
        print(f"  📹 제목: {title}")
        print(f"  채널: {info.get('channel') or info.get('uploader') or '?'}")
        print(f"  길이: {dur_str}")
        view_count = info.get("view_count")
        if view_count is not None:
            print(f"  조회수: {view_count:,}")
        print(f"  업로드: {info.get('upload_date', '?')}")

        formats = info.get("formats", [])
        resolutions = sorted(
            {f.get("height") for f in formats if f.get("height")}, reverse=True
        )
        print(f"  가용 화질: {', '.join(str(r) + 'p' for r in resolutions)}")


# ── 메인 ────────────────────────────────────────────────────────

def main():
    args = parse_args()

    # 정보 조회 모드
    if args.info and args.url:
        print_info(args.url, getattr(args, "cookies_from_browser", None))
        return

    downloader = YTDownloader(args)

    try:
        if args.channel and args.url:
            downloader.download_channel(args.url)
        elif args.batch:
            downloader.download_batch(args.batch)
        elif args.url:
            downloader.download_url(args.url)
    except DownloadCancelled:
        print("\n\n\033[33m⚠ 다운로드가 취소되었습니다.\033[0m")
    except KeyboardInterrupt:
        print("\n\n\033[33m⚠ 사용자에 의해 중단됨\033[0m")

    downloader.print_summary()


if __name__ == "__main__":
    main()
