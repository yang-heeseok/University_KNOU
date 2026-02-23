#!/usr/bin/env python3
"""
동영상 다운로더 GUI (tkinter)
===============================
YouTube, Vimeo, X, Instagram 등 1800+ 사이트 지원
실행: python yt_downloader_gui.py
"""

import argparse
import queue
import re
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
from pathlib import Path

# 같은 디렉터리의 yt_downloader 모듈 임포트
sys.path.insert(0, str(Path(__file__).parent))
from yt_downloader import (
    YTDownloader, DownloadCancelled, ProgressHook, fix_korean_filename,
)


# ── stdout 리다이렉트 ──────────────────────────────────────────

ANSI_RE = re.compile(r"\033\[[0-9;]*m")


class QueueWriter:
    """sys.stdout 대체: ANSI 코드 제거 후 Queue에 전달."""

    def __init__(self, msg_queue: queue.Queue):
        self.queue = msg_queue

    def write(self, text: str):
        clean = ANSI_RE.sub("", text).strip()
        if clean:
            self.queue.put({"type": "log", "text": clean})

    def flush(self):
        pass


# ── GUI용 진행률 훅 ────────────────────────────────────────────

class GUIProgressHook:
    """ProgressHook 대신 구조화된 진행률을 Queue에 전달."""

    def __init__(self, msg_queue: queue.Queue):
        self.queue = msg_queue

    def __call__(self, d: dict):
        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            downloaded = d.get("downloaded_bytes", 0)
            speed = d.get("speed")
            eta = d.get("eta")
            pct = (downloaded / total) if total > 0 else 0
            self.queue.put({
                "type": "progress",
                "percent": pct,
                "speed": speed,
                "eta": eta,
            })
        elif d["status"] == "finished":
            filesize = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            self.queue.put({"type": "download_finished", "filesize": filesize})

    def postprocessor_hook(self, d: dict):
        """후처리(MP3 변환 등) 상태를 Queue에 전달."""
        pp = d.get("postprocessor", "")
        label = "MP3 변환" if "Audio" in pp else pp
        if d["status"] == "started":
            self.queue.put({"type": "pp_started", "label": label})
        elif d["status"] == "finished":
            self.queue.put({"type": "pp_finished", "label": label})


# ── 메인 GUI 클래스 ───────────────────────────────────────────

class YTDownloaderGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Video Downloader (yt-dlp)")
        self.root.geometry("700x720")
        self.root.minsize(600, 600)

        self.msg_queue: queue.Queue = queue.Queue()
        self.cancel_event = threading.Event()
        self.worker_thread: threading.Thread | None = None

        self._build_ui()
        self._poll_queue()

    # ── UI 구성 ─────────────────────────────────────────────

    def _build_ui(self):
        pad = {"padx": 8, "pady": 4}

        # ── URL 입력 ────────────────────────────────────────
        frm_url = ttk.LabelFrame(self.root, text="URL 입력 (YouTube, Vimeo, X, Instagram 등)")
        frm_url.pack(fill=tk.X, **pad)

        self.url_var = tk.StringVar()
        ttk.Entry(frm_url, textvariable=self.url_var).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 4), pady=6,
        )
        ttk.Button(frm_url, text="붙여넣기", width=9, command=self._on_paste).pack(
            side=tk.LEFT, padx=2, pady=6,
        )
        ttk.Button(frm_url, text="초기화", width=7, command=lambda: self.url_var.set("")).pack(
            side=tk.LEFT, padx=(2, 8), pady=6,
        )

        # ── 옵션 ────────────────────────────────────────────
        frm_opt = ttk.LabelFrame(self.root, text="옵션")
        frm_opt.pack(fill=tk.X, **pad)

        opt_row = ttk.Frame(frm_opt)
        opt_row.pack(fill=tk.X, padx=8, pady=6)

        self.mp3_var = tk.BooleanVar()
        self.subs_var = tk.BooleanVar()
        self.thumb_var = tk.BooleanVar()
        self.meta_var = tk.BooleanVar()

        ttk.Checkbutton(opt_row, text="MP3 변환", variable=self.mp3_var).pack(side=tk.LEFT, padx=(0, 12))
        ttk.Checkbutton(opt_row, text="자막", variable=self.subs_var).pack(side=tk.LEFT, padx=(0, 12))
        ttk.Checkbutton(opt_row, text="썸네일", variable=self.thumb_var).pack(side=tk.LEFT, padx=(0, 12))
        ttk.Checkbutton(opt_row, text="메타데이터", variable=self.meta_var).pack(side=tk.LEFT, padx=(0, 24))

        ttk.Label(opt_row, text="화질:").pack(side=tk.LEFT, padx=(0, 4))
        self.quality_var = tk.StringVar(value="best")
        ttk.Combobox(
            opt_row, textvariable=self.quality_var, width=8, state="readonly",
            values=["best", "2160", "1080", "720", "480", "360"],
        ).pack(side=tk.LEFT)

        # 브라우저 쿠키 (로그인 필요 사이트용)
        ttk.Label(opt_row, text="  쿠키:").pack(side=tk.LEFT, padx=(12, 4))
        self.cookies_var = tk.StringVar(value="없음")
        ttk.Combobox(
            opt_row, textvariable=self.cookies_var, width=9, state="readonly",
            values=["없음", "chrome", "edge", "firefox", "safari"],
        ).pack(side=tk.LEFT)

        # ── 저장 경로 ───────────────────────────────────────
        frm_out = ttk.LabelFrame(self.root, text="저장 경로")
        frm_out.pack(fill=tk.X, **pad)

        self.output_var = tk.StringVar(value="./downloads")
        ttk.Entry(frm_out, textvariable=self.output_var).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 4), pady=6,
        )
        ttk.Button(frm_out, text="찾아보기", width=9, command=self._on_browse).pack(
            side=tk.LEFT, padx=(2, 8), pady=6,
        )

        # ── 배치 모드 ───────────────────────────────────────
        frm_batch = ttk.LabelFrame(self.root, text="배치 모드 (여러 URL, 한 줄에 하나)")
        frm_batch.pack(fill=tk.X, **pad)

        batch_inner = ttk.Frame(frm_batch)
        batch_inner.pack(fill=tk.X, padx=8, pady=6)

        self.batch_text = tk.Text(batch_inner, height=4, wrap=tk.WORD)
        self.batch_text.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))

        btn_col = ttk.Frame(batch_inner)
        btn_col.pack(side=tk.LEFT, fill=tk.Y)
        ttk.Button(btn_col, text="파일\n불러오기", width=9, command=self._on_load_batch).pack(pady=(0, 4))
        ttk.Button(btn_col, text="비우기", width=9, command=lambda: self.batch_text.delete("1.0", tk.END)).pack()

        # ── 실행 버튼 ───────────────────────────────────────
        frm_actions = ttk.Frame(self.root)
        frm_actions.pack(fill=tk.X, **pad)

        self.btn_download = ttk.Button(
            frm_actions, text="▶  다운로드", command=self._on_download,
        )
        self.btn_download.pack(side=tk.LEFT, padx=(8, 4), ipady=4)

        self.btn_channel = ttk.Button(
            frm_actions, text="📂  채널 백업", command=self._on_channel_backup,
        )
        self.btn_channel.pack(side=tk.LEFT, padx=4, ipady=4)

        self.btn_stop = ttk.Button(
            frm_actions, text="⏹  중지", command=self._on_stop, state=tk.DISABLED,
        )
        self.btn_stop.pack(side=tk.LEFT, padx=4, ipady=4)

        # ── 진행률 ──────────────────────────────────────────
        frm_prog = ttk.LabelFrame(self.root, text="진행률")
        frm_prog.pack(fill=tk.X, **pad)

        self.progress_bar = ttk.Progressbar(
            frm_prog, orient=tk.HORIZONTAL, mode="determinate", maximum=100,
        )
        self.progress_bar.pack(fill=tk.X, padx=8, pady=(6, 2))

        self.status_var = tk.StringVar(value="대기 중")
        ttk.Label(frm_prog, textvariable=self.status_var).pack(
            anchor=tk.W, padx=8, pady=(0, 6),
        )

        # ── 로그 ────────────────────────────────────────────
        frm_log = ttk.LabelFrame(self.root, text="다운로드 로그")
        frm_log.pack(fill=tk.BOTH, expand=True, **pad)

        self.log_text = scrolledtext.ScrolledText(
            frm_log, height=10, state=tk.DISABLED, wrap=tk.WORD,
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)

    # ── 이벤트 핸들러 ──────────────────────────────────────

    def _on_paste(self):
        try:
            text = self.root.clipboard_get()
            self.url_var.set(text.strip())
        except tk.TclError:
            pass

    def _on_browse(self):
        path = filedialog.askdirectory()
        if path:
            self.output_var.set(path)

    def _on_load_batch(self):
        path = filedialog.askopenfilename(
            filetypes=[("텍스트 파일", "*.txt"), ("모든 파일", "*.*")],
        )
        if path:
            content = Path(path).read_text(encoding="utf-8")
            self.batch_text.delete("1.0", tk.END)
            self.batch_text.insert("1.0", content)

    def _on_download(self):
        """다운로드 시작 (단일/배치)."""
        urls = self._collect_urls()
        if not urls:
            self._append_log("[오류] URL을 입력해주세요.")
            return
        self._start_worker(urls, channel_mode=False)

    def _on_channel_backup(self):
        """채널 전체 백업 시작."""
        url = self.url_var.get().strip()
        if not url:
            self._append_log("[오류] 채널 URL을 입력해주세요.")
            return
        self._start_worker([url], channel_mode=True)

    def _on_stop(self):
        """다운로드 중지."""
        self.cancel_event.set()
        self.status_var.set("중지 요청됨... 현재 영상 완료 후 중지됩니다.")

    def _collect_urls(self) -> list[str]:
        """URL 입력창 + 배치 텍스트에서 URL 목록 수집."""
        urls: list[str] = []
        main_url = self.url_var.get().strip()
        if main_url:
            urls.append(main_url)

        batch_content = self.batch_text.get("1.0", tk.END).strip()
        if batch_content:
            for line in batch_content.splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    urls.append(line)
        return urls

    # ── 워커 스레드 ─────────────────────────────────────────

    def _start_worker(self, urls: list[str], channel_mode: bool):
        """워커 스레드를 시작하고 UI를 다운로드 모드로 전환."""
        if self.worker_thread and self.worker_thread.is_alive():
            self._append_log("[경고] 이미 다운로드가 진행 중입니다.")
            return

        self.cancel_event.clear()
        self.progress_bar["value"] = 0
        self.status_var.set("시작 중...")
        self.btn_download.config(state=tk.DISABLED)
        self.btn_channel.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)

        self.worker_thread = threading.Thread(
            target=self._run_worker,
            args=(urls, channel_mode),
            daemon=True,
        )
        self.worker_thread.start()

    def _run_worker(self, urls: list[str], channel_mode: bool):
        """워커 스레드: 다운로드 실행, 메시지를 Queue로 전달."""
        old_stdout = sys.stdout
        sys.stdout = QueueWriter(self.msg_queue)

        try:
            args = self._build_namespace()
            downloader = YTDownloader(
                args,
                status_callback=lambda msg: self.msg_queue.put(msg),
                cancel_event=self.cancel_event,
            )
            gui_hook = GUIProgressHook(self.msg_queue)
            downloader.progress = gui_hook
            downloader.pp_hook = gui_hook.postprocessor_hook

            if channel_mode:
                downloader.download_channel(urls[0])
            else:
                for url in urls:
                    downloader.download_url(url)

            downloader.print_summary()
        except DownloadCancelled:
            self.msg_queue.put({"type": "log", "text": "다운로드가 취소되었습니다."})
        except Exception as e:
            self.msg_queue.put({"type": "log", "text": f"[오류] {e}"})
        finally:
            sys.stdout = old_stdout
            self.msg_queue.put({"type": "done"})

    def _build_namespace(self) -> argparse.Namespace:
        """GUI 위젯 상태로 argparse.Namespace 생성."""
        cookies = self.cookies_var.get()
        return argparse.Namespace(
            url=self.url_var.get().strip() or None,
            batch=None,
            output=self.output_var.get(),
            mp3=self.mp3_var.get(),
            audio_quality=192,
            quality=self.quality_var.get(),
            subs=self.subs_var.get(),
            thumbnail=self.thumb_var.get(),
            metadata=self.meta_var.get(),
            cookies_from_browser=cookies if cookies != "없음" else None,
            channel=False,
            info=False,
        )

    # ── Queue 폴링 ──────────────────────────────────────────

    def _poll_queue(self):
        """100ms 간격으로 Queue를 확인하고 UI 업데이트."""
        while True:
            try:
                msg = self.msg_queue.get_nowait()
            except queue.Empty:
                break

            msg_type = msg.get("type")

            if msg_type == "progress":
                pct = msg["percent"] * 100
                self.progress_bar["value"] = pct
                speed = msg.get("speed")
                eta = msg.get("eta")
                speed_str = f"{speed / 1024 / 1024:.1f}MB/s" if speed else "---"
                eta_str = f"{eta}s" if eta else "---"
                self.status_var.set(f"{pct:.0f}%  |  {speed_str}  |  ETA {eta_str}")

            elif msg_type == "download_finished":
                size = msg.get("filesize", 0)
                size_str = f"{size / 1024 / 1024:.1f}MB" if size else ""
                self._append_log(f"  다운로드 완료 ({size_str})")
                self.progress_bar["value"] = 100

            elif msg_type == "pp_started":
                self.progress_bar.config(mode="indeterminate")
                self.progress_bar.start(30)
                self.status_var.set(f"{msg['label']} 중...")

            elif msg_type == "pp_finished":
                self.progress_bar.stop()
                self.progress_bar.config(mode="determinate")
                self.progress_bar["value"] = 100
                self.status_var.set(f"{msg['label']} 완료")
                self._append_log(f"  {msg['label']} 완료")

            elif msg_type == "log":
                self._append_log(msg["text"])

            elif msg_type == "video_start":
                self.progress_bar["value"] = 0
                self.status_var.set(f"다운로드 중: {msg['title']}")

            elif msg_type in ("playlist_progress", "channel_progress"):
                cur = msg["current"]
                tot = msg["total"]
                self.status_var.set(
                    f"[{cur}/{tot}] {msg['title']}"
                )

            elif msg_type == "channel_info":
                self._append_log(
                    f"채널: {msg['channel']}  |  총 {msg['total']}개 영상"
                )

            elif msg_type == "done":
                self.btn_download.config(state=tk.NORMAL)
                self.btn_channel.config(state=tk.NORMAL)
                self.btn_stop.config(state=tk.DISABLED)
                self.progress_bar["value"] = 0
                self.status_var.set("완료")
                self._append_log("=" * 50)

        self.root.after(100, self._poll_queue)

    # ── 유틸 ────────────────────────────────────────────────

    def _append_log(self, text: str):
        """로그 텍스트 영역에 메시지 추가."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, text + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)


# ── 메인 ────────────────────────────────────────────────────────

def main():
    root = tk.Tk()
    YTDownloaderGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
