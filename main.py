"""
====================================================================
  TIKTOK & YOUTUBE TO MP3 320KBPS DOWNLOADER (CLI TOOL)
  Hỗ trợ tải âm thanh chất lượng cao 320kbps từ YouTube, TikTok & nhiều nền tảng
====================================================================
"""

import os
import sys
import argparse
import subprocess

# Configure UTF-8 encoding for Windows terminals
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.progress import (
    Progress,
    SpinnerColumn,
    BarColumn,
    TextColumn,
    DownloadColumn,
    TransferSpeedColumn,
    TimeRemainingColumn,
)
from rich.prompt import Prompt, Confirm

from downloader import MediaDownloader, format_bytes, format_duration
from config import (
    DEFAULT_DOWNLOAD_DIR,
    DEFAULT_QUALITY,
    AVAILABLE_QUALITIES,
    DEFAULT_EMBED_THUMBNAIL,
    SUPPORTED_PLATFORMS,
)

console = Console()


def print_banner():
    """Print a sleek, modern banner"""
    banner_text = Text()
    banner_text.append("╔═══════════════════════════════════════════════════════════════╗\n", style="bold cyan")
    banner_text.append("║           🎵 MP3 320KBPS DOWNLOADER - YOUTUBE & TIKTOK        ║\n", style="bold magenta")
    banner_text.append("╚═══════════════════════════════════════════════════════════════╝", style="bold cyan")

    sub_text = Text("⚡ Tải âm thanh chuẩn 320kbps cực nét • Tự động gắn ảnh bìa & ID3 tags", style="dim italic")

    console.print(Panel(
        Text.assemble(banner_text, "\n\n", sub_text, justify="center"),
        border_style="bright_blue",
        padding=(1, 2),
    ))


def open_folder(folder_path: str):
    """Open folder in Windows Explorer or default file manager"""
    abs_path = os.path.abspath(folder_path)
    os.makedirs(abs_path, exist_ok=True)
    try:
        if sys.platform == "win32":
            os.startfile(abs_path)
        elif sys.platform == "darwin":
            subprocess.run(["open", abs_path])
        else:
            subprocess.run(["xdg-open", abs_path])
        console.print(f"[green]✓ Đã mở thư mục:[/green] [underline]{abs_path}[/underline]")
    except Exception as e:
        console.print(f"[yellow]! Không thể tự động mở thư mục: {e}[/yellow]")
        console.print(f"[dim]Đường dẫn thư mục: {abs_path}[/dim]")


def choose_download_dir(current_dir: str) -> str:
    """Let the user keep the current destination or choose another folder."""
    if not Confirm.ask(
        f"Lưu vào thư mục hiện tại ({os.path.abspath(current_dir)})?",
        default=True,
    ):
        selected_dir = Prompt.ask("Nhập đường dẫn thư mục muốn lưu", default=current_dir).strip().strip('"')
        if selected_dir:
            try:
                os.makedirs(selected_dir, exist_ok=True)
                return selected_dir
            except OSError as exc:
                console.print(f"[red]Không thể tạo/mở thư mục '{selected_dir}': {exc}[/red]")
                console.print("[yellow]Sẽ tiếp tục dùng thư mục lưu hiện tại.[/yellow]")
    return current_dir


def download_single_url(
    url: str,
    output_dir: str = DEFAULT_DOWNLOAD_DIR,
    quality: str = DEFAULT_QUALITY,
    embed_thumbnail: bool = DEFAULT_EMBED_THUMBNAIL,
) -> bool:
    """Download single URL with rich UI feedback"""
    url = url.strip()
    if not url:
        return False

    console.print()
    with console.status("[bold cyan]🔍 Đang phân tích liên kết và lấy thông tin video...[/bold cyan]", spinner="dots"):
        try:
            downloader_preview = MediaDownloader(output_dir=output_dir, quality=quality, embed_thumbnail=embed_thumbnail)
            info = downloader_preview.get_info(url)
        except Exception as e:
            console.print(Panel(
                f"[bold red]❌ Lỗi khi phân tích liên kết:[/bold red]\n{str(e)}\n\n"
                "[yellow]Gợi ý:[/yellow]\n"
                "• Kiểm tra lại đường dẫn xem có chính xác không.\n"
                "• Đảm bảo video không ở chế độ riêng tư hoặc bị xóa.\n"
                "• Hỗ trợ: YouTube video, Shorts, TikTok video, Photo slide, v.v.",
                title="Lỗi tải thông tin",
                border_style="red",
            ))
            return False

    # Display video information card
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Key", style="bold cyan")
    table.add_column("Value", style="bright_white")

    title = info.get("title", "N/A")
    uploader = info.get("uploader", "N/A")
    duration = info.get("formatted_duration", "N/A")
    extractor = info.get("extractor", "N/A")

    table.add_row("🎬 Tiêu đề:", title)
    table.add_row("👤 Kênh / Tác giả:", uploader)
    table.add_row("⏱️ Thời lượng:", duration)
    table.add_row("🌐 Nền tảng:", extractor)
    table.add_row("🎧 Định dạng xuất:", f"MP3 [bold green]{quality} kbps[/bold green] (Stereo)")
    table.add_row("🖼️ Ảnh bìa album:", "Có (Tự động nhúng vào MP3)" if embed_thumbnail else "Không")

    console.print(Panel(table, title="[bold green]THÔNG TIN VIDEO[/bold green]", border_style="green"))

    # Prepare Progress bar
    progress = Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(bar_width=40, style="cyan", complete_style="bold green"),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        DownloadColumn(),
        TransferSpeedColumn(),
        TimeRemainingColumn(),
        console=console,
    )

    download_task = progress.add_task("Đang tải dữ liệu...", total=100)
    current_status = {"text": "Đang chuẩn bị..."}

    def on_progress(p):
        percent = p.get("percent", 0)
        downloaded = p.get("downloaded", 0)
        total = p.get("total", 0)
        progress.update(
            download_task,
            completed=downloaded,
            total=total if total > 0 else 100,
            description="Đang tải luồng âm thanh...",
        )

    def on_status(msg):
        current_status["text"] = msg
        progress.update(download_task, description=f"[bold yellow]{msg}[/bold yellow]")

    downloader = MediaDownloader(
        output_dir=output_dir,
        quality=quality,
        embed_thumbnail=embed_thumbnail,
        on_progress=on_progress,
        on_status=on_status,
    )

    try:
        with progress:
            result = downloader.download(url)
    except Exception as e:
        console.print(Panel(
            f"[bold red]❌ Lỗi khi tải hoặc chuyển đổi:[/bold red]\n{str(e)}",
            title="Thất bại",
            border_style="red",
        ))
        return False

    # Download success summary
    summary_table = Table(show_header=False, box=None, padding=(0, 2))
    summary_table.add_column("Key", style="bold green")
    summary_table.add_column("Value", style="bright_white")

    summary_table.add_row("✓ Trạng thái:", "[bold green]Thành công 100%[/bold green]")
    summary_table.add_row("📁 Tên file:", result.get("file_name", "N/A"))
    summary_table.add_row("💾 Dung lượng:", result.get("formatted_size", "N/A"))
    summary_table.add_row("🎧 Chất lượng:", result.get("quality", f"{quality} kbps"))
    summary_table.add_row("⏱️ Thời gian xử lý:", f"{result.get('elapsed', 0):.1f} giây")
    summary_table.add_row("📍 Thư mục lưu:", os.path.abspath(output_dir))

    console.print(Panel(
        summary_table,
        title="[bold green]🎉 HOÀN TẤT TẢI VỀ & CHUYỂN ĐỔI MP3[/bold green]",
        border_style="bold green",
    ))
    return True


def batch_download(
    urls: list,
    output_dir: str = DEFAULT_DOWNLOAD_DIR,
    quality: str = DEFAULT_QUALITY,
    embed_thumbnail: bool = DEFAULT_EMBED_THUMBNAIL,
):
    """Download a list of URLs with summary statistics"""
    total = len(urls)
    if total == 0:
        console.print("[yellow]! Không có liên kết nào để tải.[/yellow]")
        return

    console.print(f"\n[bold cyan]🚀 Bắt đầu tải {total} liên kết...[/bold cyan]")
    success_count = 0
    fail_count = 0

    for idx, url in enumerate(urls, 1):
        console.print(f"\n[bold magenta]━━━ [{idx}/{total}] Đang xử lý: {url} ━━━[/bold magenta]")
        ok = download_single_url(url, output_dir=output_dir, quality=quality, embed_thumbnail=embed_thumbnail)
        if ok:
            success_count += 1
        else:
            fail_count += 1

    console.print(Panel(
        f"[bold green]✓ Thành công: {success_count}/{total}[/bold green]\n"
        f"[bold red]✗ Thất bại: {fail_count}/{total}[/bold red]\n"
        f"[cyan]📁 Thư mục lưu:[/cyan] {os.path.abspath(output_dir)}",
        title="TỔNG KẾT DANH SÁCH TẢI",
        border_style="cyan",
    ))


def interactive_mode():
    """Run interactive menu mode"""
    current_quality = DEFAULT_QUALITY
    current_output_dir = DEFAULT_DOWNLOAD_DIR
    current_embed_cover = DEFAULT_EMBED_THUMBNAIL

    while True:
        console.clear()
        print_banner()

        menu_table = Table(show_header=False, box=None, padding=(0, 2))
        menu_table.add_column("Option", style="bold yellow")
        menu_table.add_column("Description", style="bright_white")

        menu_table.add_row("[1]", "🚀 Tải 1 link (Dán link YouTube, Shorts, TikTok)")
        menu_table.add_row("[2]", "📑 Tải danh sách nhiều link (Nhập liên tục nhiều dòng)")
        menu_table.add_row("[3]", "📂 Tải danh sách từ file [cyan]links.txt[/cyan]")
        menu_table.add_row("[4]", "📁 Mở thư mục chứa file đã tải ([underline]downloads[/underline])")
        menu_table.add_row("[5]", f"⚙️  Cài đặt chất lượng, ảnh bìa & thư mục mặc định [dim](Hiện tại: {current_quality}k, Cover: {'Bật' if current_embed_cover else 'Tắt'})[/dim]")
        menu_table.add_row("[6]", "ℹ️  Xem các nền tảng hỗ trợ")
        menu_table.add_row("[0]", "❌ Thoát chương trình")

        console.print(Panel(menu_table, title="[bold cyan]MENU CHỨC NĂNG[/bold cyan]", border_style="cyan"))

        choice = Prompt.ask("[bold green]👉 Nhập lựa chọn của bạn[/bold green]", choices=["0", "1", "2", "3", "4", "5", "6"], default="1")

        if choice == "0":
            console.print("[cyan]Cảm ơn bạn đã sử dụng MP3 Downloader! Hẹn gặp lại.[/cyan]")
            break

        elif choice == "1":
            download_dir = choose_download_dir(current_output_dir)
            console.print("\n[bold yellow]Dán đường link YouTube hoặc TikTok cần tải:[/bold yellow]")
            url = Prompt.ask("🔗 [bold cyan]URL[/bold cyan]").strip()
            if url:
                success = download_single_url(
                    url,
                    output_dir=download_dir,
                    quality=current_quality,
                    embed_thumbnail=current_embed_cover,
                )
                if success:
                    post_action = Prompt.ask(
                        "\n[bold yellow]Tùy chọn:[/bold yellow] Gõ [bold green]o[/bold green] để mở thư mục, hoặc nhấn [bold cyan]Enter[/bold cyan] để tiếp tục",
                        default="",
                    )
                    if post_action.lower().strip() == "o":
                        open_folder(download_dir)
            else:
                console.print("[yellow]! Bạn chưa nhập link.[/yellow]")
            Prompt.ask("\n[dim]Nhấn Enter để quay lại menu...[/dim]")

        elif choice == "2":
            download_dir = choose_download_dir(current_output_dir)
            console.print("\n[bold yellow]Nhập các đường link (mỗi dòng 1 link). Gõ 'done' hoặc để trống 1 dòng rồi Enter khi nhập xong:[/bold yellow]")
            urls = []
            while True:
                line = input(f"Link #{len(urls) + 1}: ").strip()
                if not line or line.lower() == "done":
                    break
                urls.append(line)

            if urls:
                batch_download(
                    urls,
                    output_dir=download_dir,
                    quality=current_quality,
                    embed_thumbnail=current_embed_cover,
                )
                post_action = Prompt.ask("\nGõ [bold green]o[/bold green] để mở thư mục tải về, hoặc nhấn [bold cyan]Enter[/bold cyan] để tiếp tục", default="")
                if post_action.lower().strip() == "o":
                    open_folder(download_dir)
            else:
                console.print("[yellow]! Không có link nào được nhập.[/yellow]")
            Prompt.ask("\n[dim]Nhấn Enter để quay lại menu...[/dim]")

        elif choice == "3":
            download_dir = choose_download_dir(current_output_dir)
            links_file = os.path.join(os.path.dirname(__file__), "links.txt")
            if not os.path.exists(links_file):
                with open(links_file, "w", encoding="utf-8") as f:
                    f.write("# Dán các đường link YouTube hoặc TikTok vào đây (mỗi dòng 1 link)\n")
                    f.write("# Dòng có dấu # ở đầu sẽ được bỏ qua\n")

            console.print(f"\n[cyan]Đang đọc file:[/cyan] {links_file}")
            urls = []
            with open(links_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        urls.append(line)

            if urls:
                console.print(f"[green]✓ Đã tìm thấy {len(urls)} link trong file links.txt[/green]")
                confirm = Confirm.ask("Bạn có muốn bắt đầu tải tất cả các link này không?", default=True)
                if confirm:
                    batch_download(
                        urls,
                        output_dir=download_dir,
                        quality=current_quality,
                        embed_thumbnail=current_embed_cover,
                    )
                    post_action = Prompt.ask("\nGõ [bold green]o[/bold green] để mở thư mục tải về, hoặc nhấn [bold cyan]Enter[/bold cyan] để tiếp tục", default="")
                    if post_action.lower().strip() == "o":
                        open_folder(download_dir)
            else:
                console.print(f"[yellow]File links.txt đang trống. Hãy mở file [cyan]{links_file}[/cyan] và dán các link vào đó.[/yellow]")
                if Confirm.ask("Bạn có muốn mở file links.txt ngay bây giờ không?", default=True):
                    try:
                        os.startfile(links_file)
                    except Exception:
                        pass
            Prompt.ask("\n[dim]Nhấn Enter để quay lại menu...[/dim]")

        elif choice == "4":
            open_folder(current_output_dir)
            Prompt.ask("\n[dim]Nhấn Enter để quay lại menu...[/dim]")

        elif choice == "5":
            console.print("\n[bold cyan]CÀI ĐẶT CHẤT LƯỢNG VÀ TÙY CHỌN[/bold cyan]")
            new_quality = Prompt.ask(
                "Chọn bitrate MP3 mong muốn",
                choices=AVAILABLE_QUALITIES,
                default=current_quality,
            )
            current_quality = new_quality

            new_cover = Confirm.ask(
                "Tự động tải và nhúng ảnh bìa (thumbnail) vào file MP3?",
                default=current_embed_cover,
            )
            current_embed_cover = new_cover

            custom_dir = Prompt.ask(
                "Thư mục lưu file tải về",
                default=current_output_dir,
            )
            current_output_dir = custom_dir

            console.print(f"[green]✓ Đã cập nhật cài đặt: {current_quality}kbps MP3 | Ảnh bìa: {'Bật' if current_embed_cover else 'Tắt'} | Thư mục: {current_output_dir}[/green]")
            Prompt.ask("\n[dim]Nhấn Enter để quay lại menu...[/dim]")

        elif choice == "6":
            console.print("\n[bold cyan]DANH SÁCH NỀN TẢNG ĐƯỢC HỖ TRỢ:[/bold cyan]")
            for p in SUPPORTED_PLATFORMS:
                console.print(f"  • [green]✓[/green] {p}")
            console.print("\n[dim]Công cụ sử dụng nhân yt-dlp & static-ffmpeg nên hỗ trợ hầu hết các trang video/âm thanh phổ biến hiện nay.[/dim]")
            Prompt.ask("\n[dim]Nhấn Enter để quay lại menu...[/dim]")


def main():
    parser = argparse.ArgumentParser(
        description="🎵 Công cụ tải video từ YouTube, TikTok và chuyển đổi sang MP3 320kbps chất lượng cao.",
        epilog="Ví dụ: python main.py https://www.youtube.com/watch?v=xxxx -q 320",
    )
    parser.add_argument("urls", nargs="*", help="Một hoặc nhiều đường link cần tải")
    parser.add_argument("-o", "--output", default=DEFAULT_DOWNLOAD_DIR, help="Thư mục lưu trữ (mặc định: ./downloads)")
    parser.add_argument("-q", "--quality", choices=AVAILABLE_QUALITIES, default=DEFAULT_QUALITY, help="Chất lượng MP3: 320 (mặc định), 256, 192, 128")
    parser.add_argument("-f", "--file", help="Đọc danh sách link từ file văn bản (.txt)")
    parser.add_argument("--no-cover", action="store_true", help="Không nhúng ảnh thumbnail làm ảnh bìa MP3")
    parser.add_argument("--open", action="store_true", help="Tự động mở thư mục tải về sau khi hoàn tất")
    parser.add_argument("-i", "--interactive", action="store_true", help="Khởi chạy chế độ menu tương tác")

    args = parser.parse_args()

    # Determine execution mode:
    # If no URL, no file, or explicit -i, run interactive mode
    if args.interactive or (not args.urls and not args.file):
        interactive_mode()
        return

    # CLI Arguments mode
    print_banner()

    urls_to_download = list(args.urls) if args.urls else []

    if args.file:
        if os.path.exists(args.file):
            with open(args.file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        urls_to_download.append(line)
        else:
            console.print(f"[bold red]❌ Không tìm thấy file:[/bold red] {args.file}")
            sys.exit(1)

    if not urls_to_download:
        console.print("[yellow]! Không có liên kết nào để tải.[/yellow]")
        sys.exit(0)

    embed_thumbnail = not args.no_cover

    if len(urls_to_download) == 1:
        success = download_single_url(
            urls_to_download[0],
            output_dir=args.output,
            quality=args.quality,
            embed_thumbnail=embed_thumbnail,
        )
    else:
        batch_download(
            urls_to_download,
            output_dir=args.output,
            quality=args.quality,
            embed_thumbnail=embed_thumbnail,
        )

    if args.open:
        open_folder(args.output)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Đã hủy thao tác bởi người dùng.[/yellow]")
        sys.exit(0)
