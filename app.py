from pathlib import Path
import subprocess
import threading
import queue
import shutil
import sys

from PIL import Image, ImageSequence
import customtkinter as ctk
from tkinter import filedialog, messagebox

try:
    import pillow_avif  # Optional: pip install pillow-avif-plugin
except ImportError:
    pillow_avif = None


IMAGE_INPUT_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff", ".tif",
    ".gif", ".avif", ".ico", ".ppm", ".pgm", ".pbm"
}

VIDEO_INPUT_EXTENSIONS = {
    ".mp4", ".mov", ".mkv", ".avi", ".webm", ".flv", ".wmv",
    ".m4v", ".mpeg", ".mpg", ".3gp", ".ts", ".mts", ".m2ts"
}

IMAGE_FORMATS = ["WEBP", "JPEG", "PNG", "AVIF", "BMP", "TIFF"]
VIDEO_FORMATS = ["mp4", "webm", "mkv", "mov", "avi", "custom"]
VIDEO_PRESETS = ["ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow", "slower", "veryslow"]
VIDEO_SCALES = ["Original", "2160p", "1440p", "1080p", "720p", "480p", "360p"]


class AssetConverterApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Asset Converter - Images & Videos")
        self.geometry("1120x760")
        self.minsize(980, 680)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.queue = queue.Queue()
        self.is_running = False
        self.active_worker = None

        # Image variables
        self.image_input_folder = ctk.StringVar()
        self.image_output_folder = ctk.StringVar()
        self.image_output_format = ctk.StringVar(value="WEBP")
        self.image_quality = ctk.IntVar(value=90)
        self.image_lossless = ctk.BooleanVar(value=False)
        self.image_overwrite = ctk.BooleanVar(value=False)
        self.image_keep_structure = ctk.BooleanVar(value=True)
        self.image_resize_enabled = ctk.BooleanVar(value=False)
        self.image_max_width = ctk.StringVar(value="1920")

        # Video variables
        self.video_input_folder = ctk.StringVar()
        self.video_output_folder = ctk.StringVar()
        self.video_output_format = ctk.StringVar(value="mp4")
        self.video_custom_extension = ctk.StringVar(value="mp4")
        self.video_codec_mode = ctk.StringVar(value="Auto")
        self.video_crf = ctk.IntVar(value=28)
        self.video_preset = ctk.StringVar(value="medium")
        self.video_scale = ctk.StringVar(value="Original")
        self.video_audio_bitrate = ctk.StringVar(value="128k")
        self.video_overwrite = ctk.BooleanVar(value=False)
        self.video_keep_structure = ctk.BooleanVar(value=True)
        self.video_strip_audio = ctk.BooleanVar(value=False)

        self.reset_counts()
        self.build_ui()
        self.after(100, self.process_queue)

    def reset_counts(self):
        self.total_count = 0
        self.success_count = 0
        self.skipped_count = 0
        self.failed_count = 0

    def build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, corner_radius=0)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="Asset Converter",
            font=ctk.CTkFont(size=28, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=28, pady=(22, 4))

        ctk.CTkLabel(
            header,
            text="Bulk convert & compress gambar dan video secara recursive untuk asset web portfolio.",
            font=ctk.CTkFont(size=14),
            text_color="gray75"
        ).grid(row=1, column=0, sticky="w", padx=28, pady=(0, 22))

        self.tabs = ctk.CTkTabview(self, corner_radius=18)
        self.tabs.grid(row=1, column=0, sticky="nsew", padx=18, pady=16)
        self.tabs.add("Images")
        self.tabs.add("Videos")

        self.build_image_tab(self.tabs.tab("Images"))
        self.build_video_tab(self.tabs.tab("Videos"))

    def build_image_tab(self, parent):
        parent.grid_columnconfigure(0, weight=0)
        parent.grid_columnconfigure(1, weight=1)
        parent.grid_rowconfigure(0, weight=1)

        left = ctk.CTkScrollableFrame(parent, width=360, corner_radius=18)
        left.grid(row=0, column=0, sticky="nsw", padx=(8, 14), pady=8)

        right = ctk.CTkFrame(parent, corner_radius=18)
        right.grid(row=0, column=1, sticky="nsew", padx=(0, 8), pady=8)

        self.build_image_settings(left)
        self.build_log_panel(right, "image")

    def build_image_settings(self, parent):
        ctk.CTkLabel(parent, text="Image Settings", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", padx=16, pady=(14, 10))

        self.path_picker(parent, "Input Folder", self.image_input_folder, self.choose_image_input).pack(fill="x", padx=16, pady=(0, 10))
        self.path_picker(parent, "Output Folder", self.image_output_folder, self.choose_image_output).pack(fill="x", padx=16, pady=(0, 12))

        ctk.CTkLabel(parent, text="Output Format", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=16, pady=(0, 5))
        self.image_format_menu = ctk.CTkOptionMenu(
            parent,
            values=IMAGE_FORMATS,
            variable=self.image_output_format,
            command=lambda _: self.on_image_format_change()
        )
        self.image_format_menu.pack(fill="x", padx=16, pady=(0, 12))

        quality_row = ctk.CTkFrame(parent, fg_color="transparent")
        quality_row.pack(fill="x", padx=16, pady=(0, 2))
        self.image_quality_title = ctk.CTkLabel(quality_row, text="Quality", font=ctk.CTkFont(size=14, weight="bold"))
        self.image_quality_title.pack(side="left")
        self.image_quality_value = ctk.CTkLabel(quality_row, textvariable=self.image_quality, font=ctk.CTkFont(size=14, weight="bold"))
        self.image_quality_value.pack(side="right")

        self.image_quality_slider = ctk.CTkSlider(parent, from_=1, to=100, number_of_steps=99, variable=self.image_quality)
        self.image_quality_slider.pack(fill="x", padx=16, pady=(0, 10))

        self.image_lossless_check = ctk.CTkCheckBox(
            parent,
            text="Lossless jika format mendukung",
            variable=self.image_lossless,
            command=self.on_image_format_change
        )
        self.image_lossless_check.pack(anchor="w", padx=16, pady=5)

        self.image_keep_structure_check = ctk.CTkCheckBox(parent, text="Pertahankan struktur folder", variable=self.image_keep_structure)
        self.image_keep_structure_check.pack(anchor="w", padx=16, pady=5)

        self.image_overwrite_check = ctk.CTkCheckBox(parent, text="Overwrite jika file sudah ada", variable=self.image_overwrite)
        self.image_overwrite_check.pack(anchor="w", padx=16, pady=5)

        self.image_resize_check = ctk.CTkCheckBox(
            parent,
            text="Resize max width",
            variable=self.image_resize_enabled,
            command=self.toggle_image_resize
        )
        self.image_resize_check.pack(anchor="w", padx=16, pady=(10, 6))

        resize_row = ctk.CTkFrame(parent, fg_color="transparent")
        resize_row.pack(fill="x", padx=16, pady=(0, 10))
        resize_row.grid_columnconfigure(0, weight=0)
        resize_row.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            resize_row,
            text="Max width",
            anchor="w"
        ).grid(row=0, column=0, sticky="w", padx=(0, 12))

        self.image_max_width_entry = ctk.CTkEntry(
            resize_row,
            textvariable=self.image_max_width,
            height=34,
            placeholder_text="1920"
        )
        self.image_max_width_entry.grid(row=0, column=1, sticky="ew")
        self.toggle_image_resize()

        self.image_start_button = ctk.CTkButton(
            parent,
            text="Start Image Convert",
            height=46,
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self.start_image_conversion
        )
        self.image_start_button.pack(fill="x", padx=16, pady=(8, 8))

        ctk.CTkButton(parent, text="Clear Log", height=38, fg_color="gray25", hover_color="gray30", command=self.clear_log).pack(fill="x", padx=16, pady=(0, 14))

        self.on_image_format_change()

    def build_video_tab(self, parent):
        parent.grid_columnconfigure(0, weight=0)
        parent.grid_columnconfigure(1, weight=1)
        parent.grid_rowconfigure(0, weight=1)

        left = ctk.CTkScrollableFrame(parent, width=390, corner_radius=18)
        left.grid(row=0, column=0, sticky="nsw", padx=(8, 14), pady=8)

        right = ctk.CTkFrame(parent, corner_radius=18)
        right.grid(row=0, column=1, sticky="nsew", padx=(0, 12), pady=12)

        self.build_video_settings(left)
        self.build_log_panel(right, "video")

    def build_video_settings(self, parent):
        ctk.CTkLabel(parent, text="Video Settings", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", padx=16, pady=(14, 10))

        self.path_picker(parent, "Input Folder", self.video_input_folder, self.choose_video_input).pack(fill="x", padx=20, pady=(0, 14))
        self.path_picker(parent, "Output Folder", self.video_output_folder, self.choose_video_output).pack(fill="x", padx=20, pady=(0, 18))

        format_row = ctk.CTkFrame(parent, fg_color="transparent")
        format_row.pack(fill="x", padx=20, pady=(0, 12))
        format_row.grid_columnconfigure(0, weight=1)
        format_row.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(format_row, text="Format", font=ctk.CTkFont(size=13, weight="bold")).grid(row=0, column=0, sticky="w", pady=(0, 5))
        ctk.CTkLabel(format_row, text="Custom Ext", font=ctk.CTkFont(size=13, weight="bold")).grid(row=0, column=1, sticky="w", padx=(10, 0), pady=(0, 5))

        self.video_format_menu = ctk.CTkOptionMenu(
            format_row,
            values=VIDEO_FORMATS,
            variable=self.video_output_format,
            command=lambda _: self.on_video_format_change()
        )
        self.video_format_menu.grid(row=1, column=0, sticky="ew")

        self.video_custom_entry = ctk.CTkEntry(format_row, textvariable=self.video_custom_extension, placeholder_text="contoh: m4v")
        self.video_custom_entry.grid(row=1, column=1, sticky="ew", padx=(10, 0))

        ctk.CTkLabel(parent, text="Codec", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=20, pady=(0, 6))
        self.video_codec_menu = ctk.CTkOptionMenu(
            parent,
            values=["Auto", "H.264", "H.265", "VP9", "AV1", "MPEG-4"],
            variable=self.video_codec_mode
        )
        self.video_codec_menu.pack(fill="x", padx=20, pady=(0, 14))

        crf_row = ctk.CTkFrame(parent, fg_color="transparent")
        crf_row.pack(fill="x", padx=20, pady=(0, 4))
        ctk.CTkLabel(crf_row, text="CRF / Compression", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left")
        ctk.CTkLabel(crf_row, textvariable=self.video_crf, font=ctk.CTkFont(size=14, weight="bold")).pack(side="right")

        self.video_crf_slider = ctk.CTkSlider(parent, from_=18, to=40, number_of_steps=22, variable=self.video_crf)
        self.video_crf_slider.pack(fill="x", padx=20, pady=(0, 6))
        ctk.CTkLabel(parent, text="CRF kecil = kualitas lebih tinggi, file lebih besar. CRF besar = lebih kecil.", text_color="gray65", font=ctk.CTkFont(size=11)).pack(anchor="w", padx=20, pady=(0, 14))

        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=(0, 14))
        row.grid_columnconfigure(0, weight=1)
        row.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(row, text="Preset", font=ctk.CTkFont(size=13, weight="bold")).grid(row=0, column=0, sticky="w", pady=(0, 5))
        ctk.CTkLabel(row, text="Scale", font=ctk.CTkFont(size=13, weight="bold")).grid(row=0, column=1, sticky="w", padx=(10, 0), pady=(0, 5))
        ctk.CTkOptionMenu(row, values=VIDEO_PRESETS, variable=self.video_preset).grid(row=1, column=0, sticky="ew")
        ctk.CTkOptionMenu(row, values=VIDEO_SCALES, variable=self.video_scale).grid(row=1, column=1, sticky="ew", padx=(10, 0))

        audio_row = ctk.CTkFrame(parent, fg_color="transparent")
        audio_row.pack(fill="x", padx=20, pady=(0, 14))
        ctk.CTkLabel(audio_row, text="Audio bitrate:").pack(side="left")
        ctk.CTkEntry(audio_row, textvariable=self.video_audio_bitrate, width=110).pack(side="right")

        ctk.CTkCheckBox(parent, text="Pertahankan struktur folder", variable=self.video_keep_structure).pack(anchor="w", padx=20, pady=7)
        ctk.CTkCheckBox(parent, text="Overwrite jika file sudah ada", variable=self.video_overwrite).pack(anchor="w", padx=20, pady=7)
        ctk.CTkCheckBox(parent, text="Hapus audio / mute", variable=self.video_strip_audio).pack(anchor="w", padx=20, pady=7)

        ctk.CTkLabel(
            parent,
            text="Butuh FFmpeg. Cek dengan command: ffmpeg -version. Rekomendasi web: MP4 H.264 CRF 23–28 atau WebM VP9 CRF 28–34.",
            text_color="gray65",
            font=ctk.CTkFont(size=12),
            wraplength=335,
            justify="left"
        ).pack(anchor="w", padx=20, pady=(10, 16))

        self.video_start_button = ctk.CTkButton(
            parent,
            text="Start Video Convert",
            height=46,
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self.start_video_conversion
        )
        self.video_start_button.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkButton(parent, text="Clear Log", height=40, fg_color="gray25", hover_color="gray30", command=self.clear_log).pack(fill="x", padx=20)
        self.on_video_format_change()

    def path_picker(self, parent, label, variable, command):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(frame, text=label, font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 6))
        ctk.CTkEntry(frame, textvariable=variable, height=38).grid(row=1, column=0, sticky="ew", padx=(0, 8))
        ctk.CTkButton(frame, text="Browse", width=86, height=38, command=command).grid(row=1, column=1)
        return frame

    def build_log_panel(self, parent, prefix):
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(4, weight=0)
        parent.grid_rowconfigure(5, weight=1)

        stats = ctk.CTkFrame(parent, fg_color="transparent")
        stats.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 12))
        stats.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.total_card = self.create_stat_card(stats, "Total", "0", 0)
        self.success_card = self.create_stat_card(stats, "Success", "0", 1)
        self.skipped_card = self.create_stat_card(stats, "Skipped", "0", 2)
        self.failed_card = self.create_stat_card(stats, "Failed", "0", 3)

        self.status_label = ctk.CTkLabel(parent, text="Ready", anchor="w", font=ctk.CTkFont(size=13), text_color="gray75")
        self.status_label.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 6))

        self.progress = ctk.CTkProgressBar(parent, height=14)
        self.progress.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 16))
        self.progress.set(0)

        ctk.CTkLabel(parent, text="Log", font=ctk.CTkFont(size=16, weight="bold")).grid(row=3, column=0, sticky="nw", padx=20, pady=(0, 0))

        self.log_text = ctk.CTkTextbox(
            parent,
            corner_radius=14,
            font=ctk.CTkFont(size=12),
            height=170
        )
        self.log_text.grid(row=4, column=0, sticky="ew", padx=20, pady=(24, 20))

    def create_stat_card(self, parent, title, value, column):
        card = ctk.CTkFrame(parent, corner_radius=14)
        card.grid(row=0, column=column, sticky="ew", padx=6)

        ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=12), text_color="gray70").pack(anchor="w", padx=14, pady=(12, 0))
        label_value = ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=24, weight="bold"))
        label_value.pack(anchor="w", padx=14, pady=(0, 12))
        return label_value

    # Folder pickers
    def choose_image_input(self):
        folder = filedialog.askdirectory(title="Pilih folder gambar")
        if folder:
            self.image_input_folder.set(folder)
            if not self.image_output_folder.get():
                path = Path(folder)
                self.image_output_folder.set(str(path.parent / f"{path.name}_converted_images"))

    def choose_image_output(self):
        folder = filedialog.askdirectory(title="Pilih folder output gambar")
        if folder:
            self.image_output_folder.set(folder)

    def choose_video_input(self):
        folder = filedialog.askdirectory(title="Pilih folder video")
        if folder:
            self.video_input_folder.set(folder)
            if not self.video_output_folder.get():
                path = Path(folder)
                self.video_output_folder.set(str(path.parent / f"{path.name}_converted_videos"))

    def choose_video_output(self):
        folder = filedialog.askdirectory(title="Pilih folder output video")
        if folder:
            self.video_output_folder.set(folder)

    # UI helpers
    def clear_log(self):
        self.log_text.delete("1.0", "end")

    def log(self, message):
        self.log_text.insert("end", str(message) + "\n")
        self.log_text.see("end")

    def set_running_state(self, running, button):
        self.is_running = running
        state = "disabled" if running else "normal"
        self.image_start_button.configure(state=state)
        self.video_start_button.configure(state=state)
        if running:
            button.configure(text="Processing...")
        else:
            self.image_start_button.configure(text="Start Image Convert")
            self.video_start_button.configure(text="Start Video Convert")

    def update_stats(self):
        self.total_card.configure(text=str(self.total_count))
        self.success_card.configure(text=str(self.success_count))
        self.skipped_card.configure(text=str(self.skipped_count))
        self.failed_card.configure(text=str(self.failed_count))

    def toggle_image_resize(self):
        if hasattr(self, "image_max_width_entry"):
            state = "normal" if self.image_resize_enabled.get() else "disabled"
            self.image_max_width_entry.configure(state=state)

    def on_image_format_change(self):
        fmt = self.image_output_format.get().upper()
        lossless_supported = fmt in {"WEBP", "PNG", "TIFF"}
        quality_supported = fmt in {"WEBP", "JPEG", "AVIF", "TIFF"}

        if not lossless_supported:
            self.image_lossless.set(False)
            self.image_lossless_check.configure(state="disabled")
        else:
            self.image_lossless_check.configure(state="normal")

        if self.image_lossless.get() or not quality_supported:
            self.image_quality_slider.configure(state="disabled")
            self.image_quality_title.configure(text_color="gray50")
            self.image_quality_value.configure(text_color="gray50")
        else:
            self.image_quality_slider.configure(state="normal")
            self.image_quality_title.configure(text_color="white")
            self.image_quality_value.configure(text_color="white")

    def on_video_format_change(self):
        if self.video_output_format.get() == "custom":
            self.video_custom_entry.configure(state="normal")
        else:
            self.video_custom_entry.configure(state="disabled")

    # Image conversion
    def start_image_conversion(self):
        if self.is_running:
            return

        input_path = Path(self.image_input_folder.get().strip())
        output_path = Path(self.image_output_folder.get().strip())

        if not input_path.exists() or not input_path.is_dir():
            messagebox.showerror("Error", "Input folder gambar tidak valid.")
            return
        if not str(output_path):
            messagebox.showerror("Error", "Output folder gambar belum dipilih.")
            return

        self.reset_for_start(self.image_start_button)
        self.active_worker = threading.Thread(target=self.convert_images_worker, args=(input_path, output_path), daemon=True)
        self.active_worker.start()

    def convert_images_worker(self, input_root, output_root):
        try:
            image_files = [p for p in input_root.rglob("*") if p.is_file() and p.suffix.lower() in IMAGE_INPUT_EXTENSIONS]
            total = len(image_files)
            self.queue.put(("total", total))
            self.queue.put(("log", f"Total gambar ditemukan: {total}"))

            if total == 0:
                self.queue.put(("done", "Image conversion selesai."))
                return

            output_ext = self.image_output_extension()

            for index, image_path in enumerate(image_files, start=1):
                try:
                    if self.image_keep_structure.get():
                        relative_path = image_path.relative_to(input_root)
                        output_path = output_root / relative_path.with_suffix(output_ext)
                    else:
                        output_path = self.unique_flat_output_path(output_root, image_path.stem, output_ext)

                    if output_path.exists() and not self.image_overwrite.get():
                        self.queue.put(("skipped",))
                        self.queue.put(("log", f"SKIP: {output_path}"))
                    else:
                        output_path.parent.mkdir(parents=True, exist_ok=True)
                        self.convert_single_image(image_path, output_path)
                        self.queue.put(("success",))
                        self.queue.put(("log", f"OK: {image_path} -> {output_path}"))

                except Exception as exc:
                    self.queue.put(("failed",))
                    self.queue.put(("log", f"ERROR: {image_path} -> {exc}"))

                self.queue.put(("progress", index, total))

            self.queue.put(("summary",))
            self.queue.put(("done", "Image conversion selesai."))
        except Exception as exc:
            self.queue.put(("log", f"FATAL ERROR: {exc}"))
            self.queue.put(("done", "Image conversion gagal."))

    def image_output_extension(self):
        fmt = self.image_output_format.get().upper()
        return {
            "JPEG": ".jpg",
            "PNG": ".png",
            "WEBP": ".webp",
            "AVIF": ".avif",
            "BMP": ".bmp",
            "TIFF": ".tiff",
        }.get(fmt, ".webp")

    def convert_single_image(self, input_path, output_path):
        fmt = self.image_output_format.get().upper()
        quality = int(self.image_quality.get())
        lossless = bool(self.image_lossless.get())

        with Image.open(input_path) as img:
            if getattr(img, "is_animated", False):
                img = next(ImageSequence.Iterator(img)).copy()

            img = self.apply_image_resize(img)
            img = self.prepare_image_mode(img, fmt)

            save_options = self.build_image_save_options(fmt, quality, lossless)
            img.save(output_path, fmt, **save_options)

    def apply_image_resize(self, img):
        if not self.image_resize_enabled.get():
            return img

        try:
            max_width = int(self.image_max_width.get())
        except ValueError:
            max_width = 0

        if max_width <= 0 or img.width <= max_width:
            return img

        ratio = max_width / img.width
        new_height = max(1, int(img.height * ratio))
        return img.resize((max_width, new_height), Image.Resampling.LANCZOS)

    def prepare_image_mode(self, img, fmt):
        has_alpha = "A" in img.getbands() or img.mode in ("LA", "PA")

        if fmt in {"JPEG", "BMP"}:
            if has_alpha:
                background = Image.new("RGB", img.size, (255, 255, 255))
                background.paste(img.convert("RGBA"), mask=img.convert("RGBA").split()[-1])
                return background
            return img.convert("RGB")

        if fmt in {"WEBP", "PNG", "AVIF", "TIFF"}:
            return img.convert("RGBA") if has_alpha else img.convert("RGB")

        return img.convert("RGB")

    def build_image_save_options(self, fmt, quality, lossless):
        if fmt == "WEBP":
            options = {"method": 6}
            if lossless:
                options["lossless"] = True
            else:
                options["quality"] = quality
            return options

        if fmt == "JPEG":
            return {"quality": quality, "optimize": True, "progressive": True}

        if fmt == "PNG":
            return {"optimize": True, "compress_level": 9}

        if fmt == "AVIF":
            return {"quality": quality}

        if fmt == "TIFF":
            return {"compression": "tiff_lzw"}

        if fmt == "BMP":
            return {}

        return {}

    # Video conversion
    def start_video_conversion(self):
        if self.is_running:
            return

        if not shutil.which("ffmpeg"):
            messagebox.showerror("FFmpeg tidak ditemukan", "FFmpeg belum terinstall atau belum masuk PATH. Coba cek di terminal: ffmpeg -version")
            return

        input_path = Path(self.video_input_folder.get().strip())
        output_path = Path(self.video_output_folder.get().strip())

        if not input_path.exists() or not input_path.is_dir():
            messagebox.showerror("Error", "Input folder video tidak valid.")
            return
        if not str(output_path):
            messagebox.showerror("Error", "Output folder video belum dipilih.")
            return

        self.reset_for_start(self.video_start_button)
        self.active_worker = threading.Thread(target=self.convert_videos_worker, args=(input_path, output_path), daemon=True)
        self.active_worker.start()

    def convert_videos_worker(self, input_root, output_root):
        try:
            video_files = [p for p in input_root.rglob("*") if p.is_file() and p.suffix.lower() in VIDEO_INPUT_EXTENSIONS]
            total = len(video_files)
            self.queue.put(("total", total))
            self.queue.put(("log", f"Total video ditemukan: {total}"))

            if total == 0:
                self.queue.put(("done", "Video conversion selesai."))
                return

            output_ext = self.video_output_extension()

            for index, video_path in enumerate(video_files, start=1):
                try:
                    if self.video_keep_structure.get():
                        relative_path = video_path.relative_to(input_root)
                        output_path = output_root / relative_path.with_suffix(output_ext)
                    else:
                        output_path = self.unique_flat_output_path(output_root, video_path.stem, output_ext)

                    if output_path.exists() and not self.video_overwrite.get():
                        self.queue.put(("skipped",))
                        self.queue.put(("log", f"SKIP: {output_path}"))
                    else:
                        output_path.parent.mkdir(parents=True, exist_ok=True)
                        cmd = self.build_ffmpeg_command(video_path, output_path)
                        self.queue.put(("log", "RUN: " + " ".join(f'\"{part}\"' if " " in str(part) else str(part) for part in cmd)))
                        self.run_ffmpeg(cmd)
                        self.queue.put(("success",))
                        self.queue.put(("log", f"OK: {video_path} -> {output_path}"))

                except Exception as exc:
                    self.queue.put(("failed",))
                    self.queue.put(("log", f"ERROR: {video_path} -> {exc}"))

                self.queue.put(("progress", index, total))

            self.queue.put(("summary",))
            self.queue.put(("done", "Video conversion selesai."))
        except Exception as exc:
            self.queue.put(("log", f"FATAL ERROR: {exc}"))
            self.queue.put(("done", "Video conversion gagal."))

    def video_output_extension(self):
        fmt = self.video_output_format.get().strip().lower()
        if fmt == "custom":
            custom = self.video_custom_extension.get().strip().lower().lstrip(".")
            return f".{custom or 'mp4'}"
        return f".{fmt}"

    def build_ffmpeg_command(self, input_path, output_path):
        overwrite_flag = "-y" if self.video_overwrite.get() else "-n"
        codec, audio_codec = self.resolve_video_codecs(output_path.suffix.lower())

        cmd = ["ffmpeg", overwrite_flag, "-i", str(input_path)]

        vf = self.resolve_scale_filter()
        if vf:
            cmd += ["-vf", vf]

        cmd += ["-c:v", codec]

        codec_mode = self.video_codec_mode.get()
        crf = str(int(self.video_crf.get()))

        if codec in {"libx264", "libx265"}:
            cmd += ["-preset", self.video_preset.get(), "-crf", crf]
            if output_path.suffix.lower() in {".mp4", ".mov", ".m4v"}:
                cmd += ["-pix_fmt", "yuv420p", "-movflags", "+faststart"]
        elif codec == "libvpx-vp9":
            cmd += ["-b:v", "0", "-crf", crf]
        elif codec == "libaom-av1":
            cmd += ["-crf", crf, "-b:v", "0", "-cpu-used", "6"]
        elif codec == "mpeg4":
            qscale = max(2, min(31, int(int(self.video_crf.get()) / 1.3)))
            cmd += ["-q:v", str(qscale)]

        if self.video_strip_audio.get():
            cmd += ["-an"]
        else:
            cmd += ["-c:a", audio_codec]
            if audio_codec != "copy":
                cmd += ["-b:a", self.video_audio_bitrate.get().strip() or "128k"]

        cmd += [str(output_path)]
        return cmd

    def resolve_video_codecs(self, output_suffix):
        selected = self.video_codec_mode.get()

        if selected == "H.264":
            return "libx264", "aac" if output_suffix != ".webm" else "libopus"
        if selected == "H.265":
            return "libx265", "aac" if output_suffix != ".webm" else "libopus"
        if selected == "VP9":
            return "libvpx-vp9", "libopus"
        if selected == "AV1":
            return "libaom-av1", "libopus" if output_suffix == ".webm" else "aac"
        if selected == "MPEG-4":
            return "mpeg4", "mp3" if output_suffix == ".avi" else "aac"

        # Auto defaults per container
        if output_suffix == ".webm":
            return "libvpx-vp9", "libopus"
        if output_suffix == ".avi":
            return "mpeg4", "mp3"
        return "libx264", "aac"

    def resolve_scale_filter(self):
        scale = self.video_scale.get()
        if scale == "Original":
            return None
        heights = {
            "2160p": 2160,
            "1440p": 1440,
            "1080p": 1080,
            "720p": 720,
            "480p": 480,
            "360p": 360,
        }
        h = heights.get(scale)
        if not h:
            return None
        return f"scale=-2:'min({h},ih)'"

    def run_ffmpeg(self, cmd):
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform.startswith("win") else 0
        )

        last_lines = []
        if process.stdout:
            for line in process.stdout:
                line = line.strip()
                if not line:
                    continue
                last_lines.append(line)
                if len(last_lines) > 8:
                    last_lines.pop(0)

        return_code = process.wait()
        if return_code != 0:
            details = "\n".join(last_lines[-5:])
            raise RuntimeError(f"FFmpeg gagal dengan exit code {return_code}. Detail:\n{details}")

    # Shared helpers
    def reset_for_start(self, active_button):
        self.reset_counts()
        self.update_stats()
        self.progress.set(0)
        self.status_label.configure(text="Scanning files...")
        self.set_running_state(True, active_button)

    def unique_flat_output_path(self, output_root, stem, extension):
        output_root.mkdir(parents=True, exist_ok=True)
        candidate = output_root / f"{stem}{extension}"
        if self.image_overwrite.get() or self.video_overwrite.get() or not candidate.exists():
            return candidate

        counter = 1
        while True:
            candidate = output_root / f"{stem}_{counter}{extension}"
            if not candidate.exists():
                return candidate
            counter += 1

    def process_queue(self):
        try:
            while True:
                item = self.queue.get_nowait()
                event = item[0]

                if event == "log":
                    self.log(item[1])

                elif event == "total":
                    self.total_count = item[1]
                    self.update_stats()

                elif event == "success":
                    self.success_count += 1
                    self.update_stats()

                elif event == "skipped":
                    self.skipped_count += 1
                    self.update_stats()

                elif event == "failed":
                    self.failed_count += 1
                    self.update_stats()

                elif event == "progress":
                    current, total = item[1], item[2]
                    self.progress.set(current / total if total else 0)
                    self.status_label.configure(text=f"Processing {current}/{total}")

                elif event == "summary":
                    self.log("")
                    self.log("=== SUMMARY ===")
                    self.log(f"Total   : {self.total_count}")
                    self.log(f"Success : {self.success_count}")
                    self.log(f"Skipped : {self.skipped_count}")
                    self.log(f"Failed  : {self.failed_count}")

                elif event == "done":
                    self.set_running_state(False, self.image_start_button)
                    self.status_label.configure(text="Done")
                    messagebox.showinfo("Selesai", item[1])

        except queue.Empty:
            pass

        self.after(100, self.process_queue)


if __name__ == "__main__":
    app = AssetConverterApp()
    app.mainloop()
