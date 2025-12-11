
import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk, ImageOps, ImageDraw
import os
import math
from typing import Optional, Dict, Any

class ImageViewer(ctk.CTkFrame):
    """
    Gelişmiş resim görüntüleyici bileşeni.
    - Şeffaflık için dumanlı cam (checkerboard) arka planı
    - Fare imlecine doğru yakınlaştırma
    - Klavye kısayolları
    - Gelişmiş tema desteği
    """
    def __init__(self, master, file_path=None, **kwargs):
        super().__init__(master, **kwargs)
        
        # Durum Değişkenleri
        self.file_path = file_path
        self.content_modified = False
        self.original_image = None
        self.displayed_image = None
        self.rotation = 0
        self.zoom_scale = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self.is_dragging = False
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        self.fit_to_window = True
        self.checkerboard_image = self._create_checkerboard_pattern()
        
        # Performans Yönetimi
        self.is_interacting = False
        self._hq_render_job = None
        
        # Grid Yapılandırması
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        
        # --- 1. Resim Alanı (Canvas) ---
        self.canvas = tk.Canvas(
            self, 
            bg="#1e1e1e", 
            highlightthickness=0, 
            bd=0
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")
        
        # --- 2. Araç Çubuğu (Toolbar) ---
        self.toolbar = ctk.CTkFrame(self, height=40, corner_radius=0, fg_color=("gray90", "#2b2b2b"))
        self.toolbar.grid(row=1, column=0, sticky="ew")
        
        # Buton referanslarını sakla (tema güncellemesi için)
        self.toolbar_buttons = []
        
        self._add_btn("Original", "1:1", self.reset_view)
        self._add_btn("Fit", "↔", self.toggle_fit)
        
        self._create_separator()
        
        self._add_btn("Zoom In", "+", self.zoom_in)
        self._add_btn("Zoom Out", "-", self.zoom_out)
        
        self._create_separator()
        
        self._add_btn("Rotate Left", "⟲", self.rotate_left)
        self._add_btn("Rotate Right", "⟳", self.rotate_right)
        
        # Bilgi Etiketi
        self.info_label = ctk.CTkLabel(self.toolbar, text="", font=("Segoe UI", 12))
        self.info_label.pack(side="right", padx=15)

        # --- Olay Bağlayıcıları ---
        self.canvas.bind("<Configure>", self.on_resize)
        
        # Mouse
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)   # Windows
        self.canvas.bind("<Button-4>", self.on_mouse_wheel)     # Linux Up
        self.canvas.bind("<Button-5>", self.on_mouse_wheel)     # Linux Down
        self.canvas.bind("<ButtonPress-1>", self.on_drag_start)
        self.canvas.bind("<B1-Motion>", self.on_drag_motion)
        self.canvas.bind("<ButtonRelease-1>", self.on_drag_end)
        
        # Odaklanma (Klavye kısayolları için gerekli)
        self.canvas.bind("<Enter>", lambda e: self.canvas.focus_set())
        
        # Klavye Kısayolları
        self.canvas.bind("<plus>", lambda e: self.zoom_in())
        self.canvas.bind("<minus>", lambda e: self.zoom_out())
        self.canvas.bind("<equal>", lambda e: self.zoom_in()) # Shift gerektirmeyen artı
        self.canvas.bind("<r>", lambda e: self.rotate_right())
        self.canvas.bind("<l>", lambda e: self.rotate_left())
        self.canvas.bind("<f>", lambda e: self.toggle_fit())
        self.canvas.bind("<0>", lambda e: self.reset_view())
        
        # Yön tuşları ile kaydırma
        self.canvas.bind("<Left>", lambda e: self._pan_keyboard(-20, 0))
        self.canvas.bind("<Right>", lambda e: self._pan_keyboard(20, 0))
        self.canvas.bind("<Up>", lambda e: self._pan_keyboard(0, -20))
        self.canvas.bind("<Down>", lambda e: self._pan_keyboard(0, 20))

        if file_path:
            self.load_file(file_path)

    def _create_checkerboard_pattern(self):
        """Şeffaflık için gri/koyu gri dama tahtası deseni oluşturur."""
        size = 20
        image = Image.new("RGB", (size * 2, size * 2), "#2b2b2b")
        draw = ImageDraw.Draw(image)
        draw.rectangle([0, 0, size, size], fill="#1e1e1e")
        draw.rectangle([size, size, size * 2, size * 2], fill="#1e1e1e")
        return ImageTk.PhotoImage(image)

    def _add_btn(self, tooltip, text, command):
        btn = ctk.CTkButton(
            self.toolbar, 
            text=text, 
            width=30, 
            height=30,
            corner_radius=5,
            fg_color="transparent",
            hover_color=("gray75", "#3a3a3a"),
            text_color=("gray10", "gray90"),
            font=("Segoe UI", 14, "bold"),
            command=command
        )
        btn.pack(side="left", padx=2, pady=5)
        self.toolbar_buttons.append(btn)
        return btn

    def _create_separator(self):
        sep = ctk.CTkFrame(self.toolbar, width=2, height=20, fg_color=("gray70", "gray40"))
        sep.pack(side="left", padx=5, pady=10)

    def load_file(self, file_path: str):
        try:
            self.file_path = file_path
            self.original_image = Image.open(file_path)
            self.original_image = ImageOps.exif_transpose(self.original_image)
            self.reset_view()
        except Exception as e:
            print(f"Error loading image: {e}")
            self._show_error(str(e))

    def _show_error(self, message):
        self.canvas.delete("all")
        self.canvas.create_text(
            self.canvas.winfo_width()//2, 
            self.canvas.winfo_height()//2, 
            text=f"Hata:\n{message}", 
            fill="red", font=("Segoe UI", 12)
        )

    def _update_display(self, fast_mode=False):
        """
        Resmi ekrana çizer.
        fast_mode=True ise daha hızlı (ancak düşük kaliteli) bir yeniden boyutlandırma kullanır.
        """
        if not self.original_image: return
        
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w <= 1 or h <= 1: return

        # 1. Döndürme (Döndürme işlemi pahalıdır, o yüzden orijinali döndürüp cachelemek daha iyi olabilir ama
        # şimdilik anlık yapıyoruz. Fast mode'da bile bu gerekli.)
        if self.rotation % 360 != 0:
            image = self.original_image.rotate(self.rotation, expand=True)
        else:
            image = self.original_image

        orig_w, orig_h = image.size
        
        # 2. Ölçekleme
        if self.fit_to_window:
            ratio = min(w / orig_w, h / orig_h)
            self.zoom_scale = ratio
        
        target_w = max(1, int(orig_w * self.zoom_scale))
        target_h = max(1, int(orig_h * self.zoom_scale))

        # 3. Resize ve Render
        # EĞER fast_mode ise veya çok büyükse NEAREST/BILINEAR kullan.
        # Değilse ve stabil durumdaysa LANCZOS kullan.
        
        if fast_mode:
            method = Image.Resampling.NEAREST
        else:
            # Sadece makul boyutlarda Lanczos kullan, çok büyük zoomlarda yine nearest daha iyi
            method = Image.Resampling.LANCZOS if self.zoom_scale < 3.0 else Image.Resampling.NEAREST

        resized = image.resize((target_w, target_h), method)
        
        self.displayed_image = ImageTk.PhotoImage(resized)
        
        # 4. Canvas Çizimi
        self.canvas.delete("all")
        
        center_x = w // 2 + self.pan_x
        center_y = h // 2 + self.pan_y
        
        self.canvas.create_image(center_x, center_y, anchor="center", image=self.displayed_image)
        
        self._update_info_label(orig_w, orig_h)
        
        # Eğer hızlı modda çizildiyse, kısa bir süre sonra kaliteli çizim için zamanla
        if fast_mode:
            self._schedule_hq_render()

    def _schedule_hq_render(self):
        """Etkileşim bittikten sonra yüksek kaliteli render işlemini zamanlar."""
        if self._hq_render_job:
            self.after_cancel(self._hq_render_job)
        self._hq_render_job = self.after(500, lambda: self._update_display(fast_mode=False))

    def _update_info_label(self, w, h):
        file_size = ""
        if self.file_path and os.path.exists(self.file_path):
            s = os.path.getsize(self.file_path)
            file_size = f"{s/1024:.1f} KB" if s < 1024*1024 else f"{s/(1024*1024):.1f} MB"
            
        zoom = int(self.zoom_scale * 100)
        state_icons = []
        if self.fit_to_window: state_icons.append("↔")
        if self.rotation != 0: state_icons.append(f"↻{self.rotation}°")
        
        state_str = " ".join(state_icons)
        self.info_label.configure(text=f"{w}x{h} ({file_size}) | {zoom}% {state_str}")

    def on_resize(self, event):
        # Resize sırasında da fast mode kullan
        if hasattr(self, '_resize_job'):
            self.after_cancel(self._resize_job)
        self._resize_job = self.after(50, lambda: self._update_display(fast_mode=True))

    def on_mouse_wheel(self, event):
        """Fare imlecine doğru yakınlaştırma mantığı."""
        if self.fit_to_window:
            self.fit_to_window = False

        # Zoom faktörü
        if event.delta: # Windows
            factor = 1.1 if event.delta > 0 else 0.9
        elif event.num == 4: # Linux Up
            factor = 1.1
        elif event.num == 5: # Linux Down
            factor = 0.9
        else:
            return

        old_scale = self.zoom_scale
        new_scale = old_scale * factor
        
        # Limitler
        if not (0.01 < new_scale < 50.0):
            return

        # Fare imlecinin konumu (Canvas merkezine göre değil, sol üste göre event.x/y geliyor)
        # Mevcut pan değerlerini de hesaba katarak farenin resim üzerindeki "göreli" konumunu bulmalıyız.
        
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        
        # Fare konumu (Canvas koordinatları)
        mouse_x = event.x
        mouse_y = event.y
        
        # Mevcut merkez
        center_x = w // 2 + self.pan_x
        center_y = h // 2 + self.pan_y
        
        # Farenin merkeze uzaklığı
        offset_x = mouse_x - center_x
        offset_y = mouse_y - center_y
        
        # Yeni pan değerlerini hesapla:
        # Farenin altındaki nokta sabit kalmalı.
        # Yeni offset = Eski offset * factor
        # Fare konumu = Yeni merkez + Yeni offset
        # Yeni merkez = Fare konumu - (Eski offset * factor)
        
        new_pan_x = mouse_x - (w // 2) - (offset_x * factor)
        new_pan_y = mouse_y - (h // 2) - (offset_y * factor)
        
        self.pan_x = new_pan_x
        self.pan_y = new_pan_y
        self.zoom_scale = new_scale
        
        # Hızlı render (Fast Mode = True)
        self._update_display(fast_mode=True)

    def _pan_keyboard(self, dx, dy):
        self.fit_to_window = False
        self.pan_x -= dx
        self.pan_y -= dy
        self._update_display(fast_mode=True)

    def on_drag_start(self, event):
        self.canvas.focus_set() # Tıklayınca odaklan
        if self.fit_to_window: return
        self.is_dragging = True
        self.last_mouse_x = event.x
        self.last_mouse_y = event.y
        self.canvas.configure(cursor="fleur")

    def on_drag_motion(self, event):
        if not self.is_dragging: return
        self.pan_x += event.x - self.last_mouse_x
        self.pan_y += event.y - self.last_mouse_y
        self.last_mouse_x = event.x
        self.last_mouse_y = event.y
        self._update_display(fast_mode=True) # Sürüklerken hızlı mod

    def on_drag_end(self, event):
        self.is_dragging = False
        self.canvas.configure(cursor="arrow")
        # Sürükleme bitince kaliteli render yap
        self._schedule_hq_render()

    # Komutlar
    def zoom_in(self):
        self.fit_to_window = False
        # Merkezden zoom
        self.zoom_scale *= 1.2
        # Pan'ı da ölçekle ki merkez kaysın (merkezi zoom'da pan değişmez ama hissi korur)
        self._update_display() # Buton tıklamaları tekil olay olduğu için normal render yeterli olabilir, ama soft his için fast mode da olur.
        # Butonlar için şimdilik normal render bırakabiliriz veya kullanıcı seri tıklarsa diye fast mode yapabiliriz.
        # Tutarlılık için fast mode yapmayalım, tek tık donma yapmaz. Seri tıklanırsa belki.

    def zoom_out(self):
        self.fit_to_window = False
        self.zoom_scale /= 1.2
        self._update_display()

    def rotate_left(self):
        self.rotation = (self.rotation + 90) % 360
        self._update_display()

    def rotate_right(self):
        self.rotation = (self.rotation - 90) % 360
        self._update_display()

    def reset_view(self):
        self.fit_to_window = False
        self.rotation = 0
        self.zoom_scale = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self._update_display()

    def toggle_fit(self):
        self.fit_to_window = not self.fit_to_window
        self.pan_x = 0
        self.pan_y = 0
        self._update_display()

    def apply_theme(self, theme: Dict[str, Any]):
        bg = theme.get("editor_bg", "#1e1e1e")
        fg = theme.get("fg", "#d4d4d4")
        menu_bg = theme.get("menu_bg", "#2b2b2b")
        menu_hover = theme.get("menu_hover", "#3a3a3a")
        
        self.configure(fg_color=bg)
        self.canvas.configure(bg=bg)
        self.toolbar.configure(fg_color=menu_bg)
        self.info_label.configure(text_color=fg)
        
        for btn in self.toolbar_buttons:
            btn.configure(
                text_color=fg, 
                hover_color=menu_hover
            )

    # Uyumluluk
    def save_file(self): return True
    def set_lexer_from_file(self, f): pass
    def toggle_line_numbers(self, show=None): pass
    def toggle_minimap(self, show=None): pass
    def toggle_word_wrap(self, enable=None): pass
    def get_view_states(self): return {}
    def duplicate_line(self): pass
    def move_line_up(self): pass
    def move_line_down(self): pass
    def delete_line(self): pass
    def join_lines(self): pass
