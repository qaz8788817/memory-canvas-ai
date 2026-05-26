import customtkinter as ctk
from tkinter import messagebox, filedialog
import json
import os
import platform
from PIL import Image
from google import genai
from google.genai import types
import pydantic

# 系統字型判定
if platform.system() == "Windows":
    main_font_family = "StayHomeWriting"  # 優先套用你的宅在家字動筆
elif platform.system() == "Darwin":
    main_font_family = "PingFang TC"
else:
    main_font_family = "Arial"

ctk.set_appearance_mode("light")

class MemoryCanvasAIApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 紫黃多巴胺配色
        self.bg_purple = "#C69FD5"      # 粉紫背景
        self.text_yellow = "#FDFDC9"    # 奶油黃字
        self.dark_purple = "#4A2E80"    # 深紫容器
        self.bar_bg = "#63439C"         # 軌道底色
        self.macaron_green = "#BAFFC9"  # 成功高亮綠

        self.title("Memory Canvas AI - Travel Diary Wall 🗺️💜")
        self.geometry("1020x620") # 黃金大畫布比例
        self.resizable(False, False)
        self.configure(fg_color=self.bg_purple)

        # 🔑 直接植入你的 Gemini API Key
        MY_GEMINI_KEY = ""

        # 初始化 Gemini 客戶端
        try:
            self.ai_client = genai.Client(api_key=MY_GEMINI_KEY)
        except:
            self.ai_client = None

        self.current_img_path = ""
        self.current_pil_img = None

        self.title_font = ctk.CTkFont(family=main_font_family, size=18, weight="bold")
        self.body_font = ctk.CTkFont(family=main_font_family, size=14)
        self.card_title_font = ctk.CTkFont(family=main_font_family, size=15, weight="bold")
        self.btn_font = ctk.CTkFont(family=main_font_family, size=13, weight="bold")

        self.setup_ui()

    def setup_ui(self):
        # 主雙欄配置外框
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=40) # 左欄：照片載入與預覽
        main_frame.grid_columnconfigure(1, weight=60) # 右欄：AI 多巴胺回憶牆
        main_frame.grid_rowconfigure(0, weight=1)

        # =====================================================================
        # 📸 【左欄】：日常/旅行照片預覽區
        # =====================================================================
        left_column = ctk.CTkFrame(main_frame, fg_color=self.dark_purple, corner_radius=12)
        left_column.grid(row=0, column=0, padx=(0, 10), sticky="nsew", pady=5)

        ctk.CTkLabel(left_column, text="📸 Travel Memory Preview", font=self.title_font, text_color=self.text_yellow).pack(pady=(15, 5))

        # 相片預覽畫布（預設放置一個提示區塊）
        self.preview_frame = ctk.CTkFrame(left_column, fg_color="#361B66", corner_radius=10, height=280)
        self.preview_frame.pack(fill="x", padx=20, pady=10)
        self.preview_frame.pack_propagate(False) # 固定高度
        
        self.lbl_img_render = ctk.CTkLabel(self.preview_frame, text="Click 'Load Image' to start 🖼️", font=self.body_font, text_color="gray")
        self.lbl_img_render.pack(expand=True)

        # 載入與分析按鈕
        btn_load = ctk.CTkButton(
            left_column, text="📁 載入旅行相片", font=self.btn_font, height=35,
            fg_color=self.bg_purple, hover_color="#B58BC4", text_color=self.dark_purple,
            command=self.load_image
        )
        btn_load.pack(fill="x", padx=20, pady=(5, 5))

        self.btn_analyze = ctk.CTkButton(
            left_column, text="🔮 AI 智能看圖說故事", font=self.btn_font, height=40,
            fg_color=self.text_yellow, hover_color="#EBEB9B", text_color=self.dark_purple,
            command=self.start_vision_analysis
        )
        self.btn_analyze.pack(fill="x", padx=20, pady=(5, 15))

        # 顯示原檔名路徑
        self.lbl_path = ctk.CTkLabel(left_column, text="No image loaded", font=self.body_font, text_color="gray", wraplength=320)
        self.lbl_path.pack(padx=20, pady=(0, 15))

        # =====================================================================
        # 📊 【右欄】：AI 多巴胺日記看板 (滾動面板，無邊框報錯參數)
        # =====================================================================
        self.right_column = ctk.CTkFrame(main_frame, fg_color="transparent")
        self.right_column.grid(row=0, column=1, padx=(10, 0), sticky="nsew", pady=5)

        ctk.CTkLabel(self.right_column, text="🗺️ AI Generative Diary Canvas", font=self.title_font, text_color=self.dark_purple).pack(anchor="w", padx=5, pady=(5, 5))

        self.scroll_canvas = ctk.CTkScrollableFrame(self.right_column, fg_color=self.dark_purple, corner_radius=12)
        self.scroll_canvas.pack(fill="both", expand=True)
        self.scroll_canvas._scrollbar.configure(width=0)
        self.scroll_canvas._scrollbar.pack_forget()

        self.lbl_init_tips = ctk.CTkLabel(self.scroll_canvas, text="等待魔法喚醒... 🍃\n上傳照片並點擊分析，自動生成文案、Alt 標籤與新檔名。", font=self.body_font, text_color="gray")
        self.lbl_init_tips.pack(pady=180)

    # --- 📁 圖片載入與縮放渲染技術 ---
    def load_image(self):
        file_path = filedialog.askopenfilename(
            parent=self, 
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.webp *.bmp")]
        )
        if file_path:
            self.current_img_path = file_path
            self.current_pil_img = Image.open(file_path)
            
            # 智慧等比例縮放以符合左欄預覽框 (260x260)
            img_copy = self.current_pil_img.copy()
            img_copy.thumbnail((260, 260), Image.Resampling.LANCZOS)
            
            # 使用 CustomTkinter 的 CTkImage 進行高解析度渲染
            ctk_img = ctk.CTkImage(light_image=img_copy, dark_image=img_copy, size=img_copy.size)
            
            self.lbl_img_render.configure(image=ctk_img, text="")
            self.lbl_img_render.image = ctk_img # 強制維持記憶體引用，避免被回收
            
            # 縮短顯示路徑
            short_path = file_path if len(file_path) <= 40 else f"...{file_path[-37:]}"
            self.lbl_path.configure(text=f"Loaded: {short_path}", text_color=self.text_yellow)

    # --- 🤖 Gemini 2.5 結構化視覺核心 ---
    def start_vision_analysis(self):
        if not self.current_pil_img:
            messagebox.showwarning("Warning", "Please load a travel image first!", parent=self)
            return
        if not self.ai_client:
            messagebox.showerror("API Error", "Gemini Client 未成功初始化，請檢查 API Key。", parent=self)
            return

        self.btn_analyze.configure(state="disabled", text="AI Analyzing... ⏳")
        self.update()

        # 💡 定義絕對不會出錯的 JSON 回傳結構
        class MemoryAnalysisSchema(pydantic.BaseModel):
            推薦智能檔名: str # 格式必須如: hida_no_sato_shirakawago.jpg (全英文底線)
            SEO_Alt標籤: str # 格式如: Hida-no-Sato-9 (專案結構化命名習慣)
            文青手寫風文案: str
            幽默極客風文案: str
            旅遊小助手風文案: str

        try:
            # 發送多模態視覺請求
            response = self.ai_client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[
                    """你是一位充滿生活品味與幽默感的旅遊日記作家。
                    請仔細看這張我旅行拍下的照片，辨識其中的景點、食物、國家或氛圍，並幫我完成以下任務：
                    1. 幫這張相片重新命名，使用全英文小寫、底線連接，並保留合適的副檔名 (例如: hida_no_sato_view.jpg)。
                    2. 產生一組結構化的 SEO Alt 標籤，單字間用連字號隔開並加上流水號 (例如: Hida-no-Sato-9)。
                    3. 用繁體中文撰寫三種不同靈魂的社群文案。
                    必須嚴格遵循指定的 JSON 格式回傳。""",
                    self.current_pil_img
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=MemoryAnalysisSchema,
                    temperature=0.6 # 提高隨機性，讓文案更有創意
                )
            )

            result_json = json.loads(response.text)
            self.render_diary_canvas(result_json)

        except Exception as e:
            messagebox.showerror("Vision Error", f"視覺解析失敗：{str(e)}", parent=self)
        finally:
            self.btn_analyze.configure(state="normal", text="🔮 AI 智能看圖說故事")

    # --- 🎨 渲染多巴胺字卡日記牆 ---
    def render_diary_canvas(self, data):
        for widget in self.scroll_canvas.winfo_children(): widget.destroy()

        # 1. 頂部：檔案重命名與 SEO 標籤卡片 (馬卡龍薄荷綠)
        file_card = ctk.CTkFrame(self.scroll_canvas, fg_color=self.macaron_green, corner_radius=10)
        file_card.pack(fill="x", padx=12, pady=6)

        lbl_f_title = ctk.CTkLabel(file_card, text="⚙️ 智慧自動化檔案管理  ", font=self.card_title_font, text_color=self.dark_purple)
        lbl_f_title.pack(anchor="w", padx=15, pady=(10, 2))

        new_name = data.get("推薦智能檔名", "travel_memory.jpg")
        alt_tag = data.get("SEO_Alt標籤", "Travel-Memory-1")

        lbl_f_info = ctk.CTkLabel(
            file_card, 
            text=f"▫️ 建議新檔名: {new_name}\n▫️ SEO Alt 標籤: <img src=\"...\" alt=\"{alt_tag}\" />  ",
            font=self.body_font, text_color="#1A1A24", justify="left"
        )
        lbl_f_info.pack(anchor="w", padx=15, pady=(2, 5))

        # 一鍵重新命名並另存新檔按鈕
        btn_rename_save = ctk.CTkButton(
            file_card, text="💾 一鍵將相片優化改名另存", font=self.btn_font, height=26, width=200,
            fg_color=self.dark_purple, text_color=self.text_yellow, hover_color="#361B66",
            command=lambda: self.save_smart_image(new_name)
        )
        btn_rename_save.pack(anchor="w", padx=15, pady=(2, 12))

        # 2. 渲染三種靈魂的文案字卡
        copy_styles = [
            ("✍️ 文青手寫風文案", "文青手寫風文案", "#FFB3BA"),  # 櫻花粉
            ("💻 幽默極客風文案", "幽默極客風文案", "#BAE1FF"),  # 天空藍
            ("🎒 旅遊小助手風文案", "旅遊小助手風文案", "#FDFDC9") # 奶油黃
        ]

        for label, json_key, color in copy_styles:
            content = data.get(json_key, "AI 沒能編織出這段文字...")
            
            card = ctk.CTkFrame(self.scroll_canvas, fg_color=color, corner_radius=10)
            card.pack(fill="x", padx=12, pady=6)

            ctk.CTkLabel(card, text=label + "  ", font=self.card_title_font, text_color=self.dark_purple).pack(anchor="w", padx=15, pady=(10, 2))
            
            # 使用唯讀的 Textbox 代替 Label，文字長度再長也能「完美換行且絕不缺字、支援滑鼠選取複製」！
            txt_copy = ctk.CTkTextbox(
                card, height=75, fg_color="transparent", text_color="#1A1A24",
                font=self.body_font, wrap="char"
            )
            txt_copy.pack(fill="x", padx=10, pady=(0, 5))
            txt_copy.insert("1.0", content)
            txt_copy.configure(state="disabled")

    # --- 💾 Pillow 實體影像優化改名另存流水線 ---
    def save_smart_image(self, suggested_name):
        if not self.current_pil_img: return
        
        # 彈出視窗讓使用者確認要把新圖片存在哪
        save_path = filedialog.asksaveasfilename(
            parent=self,
            initialfile=suggested_name,
            filetypes=[("JPEG Image", "*.jpg"), ("PNG Image", "*.png"), ("WebP Image", "*.webp")]
        )
        if save_path:
            try:
                # 確保如果是 JPG，自動過濾掉透明度通道防崩潰
                save_img = self.current_pil_img.copy()
                if save_path.lower().endswith((".jpg", ".jpeg")) and save_img.mode in ("RGBA", "P"):
                    save_img = save_img.convert("RGB")
                
                save_img.save(save_path)
                messagebox.showinfo("Saved 🎉", f"相片已成功以智慧檔名另存新檔：\n{os.path.basename(save_path)}", parent=self)
            except Exception as e:
                messagebox.showerror("Save Error", f"存檔失敗：{e}", parent=self)


if __name__ == "__main__":
    app = MemoryCanvasAIApp()
    app.mainloop()