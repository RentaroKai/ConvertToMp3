import tkinter as tk
from tkinter import ttk
from typing import Callable, List, Optional
import os
from tkinterdnd2 import DND_FILES, TkinterDnD

class DragDropFrame(ttk.Frame):
    """ドラッグ＆ドロップ領域のフレーム"""

    def __init__(
        self,
        master: tk.Misc,
        on_files_dropped: Callable[[List[str]], None],
        *args,
        **kwargs
    ):
        super().__init__(master, *args, **kwargs)
        self.on_files_dropped = on_files_dropped

        # ドロップ領域のラベル
        self.drop_label = ttk.Label(
            self,
            text="ここにオーディオファイル（MOV→MP4変換もサポート）をドラッグ＆ドロップしてください",
            padding=20
        )
        self.drop_label.pack(expand=True, fill="both")

        # ドラッグ＆ドロップのバインド
        self.drop_label.drop_target_register(DND_FILES)
        self.drop_label.dnd_bind('<<Drop>>', self._on_drop)
        self.drop_label.bind('<Enter>', self._on_drag_enter)
        self.drop_label.bind('<Leave>', self._on_drag_leave)

    def _on_drop(self, event) -> None:
        """ファイルがドロップされた時の処理"""
        print("\nデバッグ: ファイルがドロップされました")
        print(f"デバッグ: 生のイベントデータ: {event.data}")

        try:
            # ドロップされたファイルのパスを取得
            # 波括弧で囲まれたパス全体を取得
            file_paths = []
            current_path = ""
            in_braces = False

            for char in event.data:
                if char == '{':
                    in_braces = True
                elif char == '}':
                    in_braces = False
                    if current_path:
                        file_paths.append(current_path)
                        current_path = ""
                elif in_braces:
                    current_path += char
                elif char.isspace() and not in_braces:
                    if current_path:
                        file_paths.append(current_path)
                        current_path = ""
                else:
                    current_path += char

            if current_path:  # 最後のパスを追加
                file_paths.append(current_path)

            print(f"デバッグ: パース後のパス: {file_paths}")

            # パスの正規化
            file_paths = [os.path.normpath(path) for path in file_paths]
            print(f"デバッグ: 正規化後のパス: {file_paths}")

            # コールバックを呼び出し
            self.on_files_dropped(file_paths)

        except Exception as e:
            print(f"エラー: ドロップ処理中にエラーが発生: {str(e)}")
            raise
        finally:
            # 見た目を元に戻す
            self.drop_label.configure(background="")

    def _on_drag_enter(self, event) -> None:
        """ドラッグが領域に入った時の処理"""
        print("デバッグ: ドラッグが領域に入りました")
        self.drop_label.configure(background="lightblue")

    def _on_drag_leave(self, event) -> None:
        """ドラッグが領域から出た時の処理"""
        print("デバッグ: ドラッグが領域から出ました")
        self.drop_label.configure(background="")

class FileListFrame(ttk.Frame):
    """ファイル一覧を表示するフレーム"""

    def __init__(
        self,
        master: tk.Misc,
        on_file_remove: Callable[[str], None],
        *args,
        **kwargs
    ):
        super().__init__(master, *args, **kwargs)
        self.on_file_remove = on_file_remove

        # ファイル一覧のツリービュー
        self.tree = ttk.Treeview(
            self,
            columns=("path", "size", "format"),
            show="headings",
            selectmode="browse"
        )

        # カラムの設定
        self.tree.heading("path", text="ファイル名")
        self.tree.heading("size", text="サイズ")
        self.tree.heading("format", text="形式")

        self.tree.column("path", width=300)
        self.tree.column("size", width=100)
        self.tree.column("format", width=100)

        # スクロールバー
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # 配置
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 右クリックメニュー
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="削除", command=self._remove_selected)

        # 右クリックイベントのバインド
        self.tree.bind("<Button-3>", self._show_context_menu)

    def add_file(self, file_path: str) -> None:
        """ファイルをリストに追加"""
        # ファイル情報を取得
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        file_format = os.path.splitext(file_path)[1].lstrip(".")

        # サイズを適切な単位に変換
        size_str = self._format_size(file_size)

        # ツリービューに追加
        self.tree.insert("", "end", values=(file_name, size_str, file_format), tags=(file_path,))

    def remove_file(self, file_path: str) -> None:
        """ファイルをリストから削除"""
        for item in self.tree.get_children():
            if file_path in self.tree.item(item)["tags"]:
                self.tree.delete(item)
                break

    def clear(self) -> None:
        """リストをクリア"""
        for item in self.tree.get_children():
            self.tree.delete(item)

    def get_files(self) -> List[str]:
        """リストに表示されているファイルのパスを取得"""
        files = []
        for item in self.tree.get_children():
            files.extend(self.tree.item(item)["tags"])
        return files

    def _format_size(self, size: int) -> str:
        """ファイルサイズを適切な単位に変換"""
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    def _show_context_menu(self, event: tk.Event) -> None:
        """右クリックメニューを表示"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def _remove_selected(self) -> None:
        """選択されたファイルを削除"""
        selected = self.tree.selection()
        if selected:
            item = selected[0]
            file_path = self.tree.item(item)["tags"][0]
            self.on_file_remove(file_path)
            self.tree.delete(item)

class FormatSelector(ttk.Frame):
    """出力フォーマット選択フレーム"""

    def __init__(
        self,
        master: tk.Misc,
        formats: List[str],
        default_format: str,
        on_format_change: Callable[[str], None],
        on_quality_change: Optional[Callable[[str], None]] = None,
        on_overwrite_change: Optional[Callable[[bool], None]] = None,
        *args,
        **kwargs
    ):
        super().__init__(master, *args, **kwargs)
        self.on_format_change = on_format_change
        self.on_quality_change = on_quality_change
        self.on_overwrite_change = on_overwrite_change

        # フォーマット選択のラジオボタン
        self.format_var = tk.StringVar(value=default_format)

        # 上部フレーム（フォーマット選択）
        format_frame = ttk.Frame(self)
        format_frame.pack(fill="x", pady=5)

        # ラベル
        ttk.Label(format_frame, text="出力フォーマット:").pack(side="left", padx=5)

        # ラジオボタン
        for fmt in formats:
            rb = ttk.Radiobutton(
                format_frame,
                text=fmt.upper(),
                value=fmt,
                variable=self.format_var,
                command=self._on_format_changed
            )
            rb.pack(side="left", padx=5)

        # MP4品質設定フレーム
        self.quality_frame = ttk.Frame(self)
        self.quality_frame.pack(fill="x", pady=5)

        # 品質設定
        self.quality_var = tk.StringVar(value="medium_compression")

        ttk.Label(self.quality_frame, text="MP4圧縮設定:").pack(side="left", padx=5)

        quality_options = [
            ("まあまあ圧縮", "medium_compression"),
            ("めちゃ圧縮", "high_compression"),
            ("鬼圧縮（激小）", "ultra_compression"),
            ("地獄圧縮（極小）", "hell_compression")
        ]

        for text, value in quality_options:
            rb = ttk.Radiobutton(
                self.quality_frame,
                text=text,
                value=value,
                variable=self.quality_var,
                command=self._on_quality_changed
            )
            rb.pack(side="left", padx=5)

        # 上書きモード設定フレーム
        overwrite_frame = ttk.Frame(self)
        overwrite_frame.pack(fill="x", pady=5)

        # 上書きモードチェックボックス
        self.overwrite_var = tk.BooleanVar(value=False)  # デフォルトはOFF（安全モード）
        
        self.overwrite_checkbox = ttk.Checkbutton(
            overwrite_frame,
            text="上書きモード（元のファイルと同じ名前で保存）",
            variable=self.overwrite_var,
            command=self._on_overwrite_changed
        )
        self.overwrite_checkbox.pack(side="left", padx=5)

        # 警告ラベル
        self.warning_label = ttk.Label(
            overwrite_frame,
            text="⚠️ 注意：元のファイルが上書きされます",
            foreground="red"
        )
        
        # 初期状態でMP4品質設定を隠す
        self._update_quality_visibility()
        # 初期状態で警告ラベルを隠す
        self._update_warning_visibility()

    def get_format(self) -> str:
        """選択されているフォーマットを取得"""
        return self.format_var.get()

    def get_quality_preset(self) -> str:
        """選択されている品質設定を取得"""
        return self.quality_var.get()

    def get_overwrite_mode(self) -> bool:
        """上書きモードの状態を取得"""
        return self.overwrite_var.get()

    def _on_format_changed(self) -> None:
        """フォーマットが変更された時の処理"""
        self._update_quality_visibility()
        self.on_format_change(self.format_var.get())

    def _on_quality_changed(self) -> None:
        """品質設定が変更された時の処理"""
        if self.on_quality_change:
            self.on_quality_change(self.quality_var.get())

    def _on_overwrite_changed(self) -> None:
        """上書きモードが変更された時の処理"""
        self._update_warning_visibility()
        if self.on_overwrite_change:
            self.on_overwrite_change(self.overwrite_var.get())

    def _update_quality_visibility(self) -> None:
        """MP4品質設定の表示/非表示を切り替え"""
        if self.format_var.get() == "mp4":
            self.quality_frame.pack(fill="x", pady=5)
        else:
            self.quality_frame.pack_forget()

    def _update_warning_visibility(self) -> None:
        """警告ラベルの表示/非表示を切り替え"""
        if self.overwrite_var.get():
            self.warning_label.pack(side="left", padx=10)
        else:
            self.warning_label.pack_forget()

class ProgressFrame(ttk.Frame):
    """進捗表示フレーム"""

    def __init__(self, master: tk.Misc, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        # 進捗バー
        self.progress = ttk.Progressbar(
            self,
            orient="horizontal",
            mode="determinate",
            length=400
        )
        self.progress.pack(side="top", fill="x", padx=5, pady=5)

        # 状態ラベル
        self.status_label = ttk.Label(self, text="")
        self.status_label.pack(side="top", fill="x", padx=5)

    def update_progress(self, message: str, value: float) -> None:
        """進捗を更新"""
        self.status_label.configure(text=message)
        self.progress["value"] = value
        self.update_idletasks()

    def reset(self) -> None:
        """進捗表示をリセット"""
        self.status_label.configure(text="")
        self.progress["value"] = 0
        self.update_idletasks()