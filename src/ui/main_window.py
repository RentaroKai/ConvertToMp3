import tkinter as tk
from tkinter import ttk, messagebox
from typing import List
import threading
from tkinterdnd2 import DND_FILES, TkinterDnD
from .components import DragDropFrame, FileListFrame, FormatSelector, ProgressFrame
from ..controllers.converter_controller import ConverterController
from ..utils.logger import logger

class MainWindow(TkinterDnD.Tk):
    """メインウィンドウ"""

    def __init__(self):
        super().__init__()

        # ウィンドウの設定
        self.title("オーディオコンバーター")
        self.geometry("800x600")
        self.minsize(600, 400)

        # コントローラーの初期化
        self.controller = ConverterController()
        self.controller.set_progress_callback(self._update_progress)

        # UIの初期化
        self._init_ui()

    def _init_ui(self) -> None:
        """UIの初期化"""
        # メインフレーム
        main_frame = ttk.Frame(self)
        main_frame.pack(expand=True, fill="both", padx=10, pady=10)

        # ドラッグ＆ドロップエリア
        self.drop_frame = DragDropFrame(
            main_frame,
            on_files_dropped=self._on_files_dropped
        )
        self.drop_frame.pack(fill="x", pady=10)

        # ファイル一覧
        self.file_list = FileListFrame(
            main_frame,
            on_file_remove=self._on_file_removed
        )
        self.file_list.pack(expand=True, fill="both", pady=10)

        # フォーマット選択
        self.format_selector = FormatSelector(
            main_frame,
            formats=self.controller.get_supported_formats(),
            default_format=self.controller.get_default_format(),
            on_format_change=self._on_format_changed,
            on_quality_change=self._on_quality_changed
        )
        self.format_selector.pack(fill="x", pady=10)

        # 進捗表示
        self.progress_frame = ProgressFrame(main_frame)
        self.progress_frame.pack(fill="x", pady=10)

        # 変換ボタン
        self.convert_button = ttk.Button(
            main_frame,
            text="変換開始",
            command=self._start_conversion
        )
        self.convert_button.pack(pady=10)

    def _on_files_dropped(self, file_paths: List[str]) -> None:
        """ファイルがドロップされた時の処理"""
        try:
            for path in file_paths:
                self.file_list.add_file(path)
            logger.info(f"{len(file_paths)}個のファイルが追加されました")
        except Exception as e:
            logger.error(f"ファイルの追加中にエラーが発生しました: {str(e)}")
            messagebox.showerror("エラー", f"ファイルの追加中にエラーが発生しました: {str(e)}")

    def _on_file_removed(self, file_path: str) -> None:
        """ファイルが削除された時の処理"""
        logger.info(f"ファイルが削除されました: {file_path}")

    def _on_format_changed(self, format_type: str) -> None:
        """フォーマットが変更された時の処理"""
        logger.info(f"出力フォーマットが変更されました: {format_type}")
        # ウィンドウタイトルを更新
        if format_type == "mp4":
            self.title("動画コンバーター - MOV→MP4変換")
        else:
            self.title("オーディオコンバーター")

    def _on_quality_changed(self, quality_preset: str) -> None:
        """品質設定が変更された時の処理"""
        logger.info(f"MP4品質設定が変更されました: {quality_preset}")
        self.controller.set_quality_preset(quality_preset)

    def _start_conversion(self) -> None:
        """変換を開始"""
        files = self.file_list.get_files()
        if not files:
            messagebox.showwarning("警告", "変換するファイルが選択されていません")
            return

        # UIを無効化
        self._set_ui_state("disabled")

        # 品質設定を更新
        if self.format_selector.get_format() == "mp4":
            self.controller.set_quality_preset(self.format_selector.get_quality_preset())

        # 変換処理を別スレッドで実行
        thread = threading.Thread(
            target=self._convert_files,
            args=(files, self.format_selector.get_format())
        )
        thread.start()

    def _convert_files(self, files: List[str], output_format: str) -> None:
        """ファイルの変換を実行"""
        try:
            results = self.controller.convert_files(files, output_format)

            # 結果を集計
            success = sum(1 for r in results if r["status"] == "success")
            failed = sum(1 for r in results if r["status"] == "error")
            video_converted = sum(1 for r in results if r["status"] == "success" and
                                 r.get("original_info", {}).get("is_video", False))

            # 完了メッセージを表示
            message = f"変換が完了しました\n成功: {success}件\n失敗: {failed}件\n\n"

            if video_converted > 0:
                if output_format == "mp4":
                    message += f"動画ファイルを変換: {video_converted}件\n\n"
                else:
                    message += f"動画ファイルから音声を抽出: {video_converted}件\n\n"

            # 成功したファイルの出力パスを表示
            if success > 0:
                message += "変換されたファイル:\n"
                for result in results:
                    if result["status"] == "success":
                        message += f"・{result['output_path']}\n"

            if failed > 0:
                message += "\nエラーの詳細はログファイルを確認してください"

            self.after(0, lambda: messagebox.showinfo("完了", message))

            # ファイルリストをクリア
            self.after(0, self.file_list.clear)

        except Exception as e:
            logger.error(f"変換処理中にエラーが発生しました: {str(e)}")
            self.after(0, lambda: messagebox.showerror(
                "エラー",
                f"変換処理中にエラーが発生しました: {str(e)}"
            ))

        finally:
            # UIを有効化
            self.after(0, lambda: self._set_ui_state("normal"))
            # 進捗表示をリセット
            self.after(0, self.progress_frame.reset)

    def _update_progress(self, message: str, value: float) -> None:
        """進捗を更新"""
        self.after(0, lambda: self.progress_frame.update_progress(message, value))

    def _set_ui_state(self, state: str) -> None:
        """UIの状態を設定"""
        # 変換ボタンの状態を変更
        self.convert_button.configure(state=state)

        # フォーマット選択の状態を変更（再帰的に全ての子ウィジェットを処理）
        def update_widget_state(widget):
            try:
                if isinstance(widget, (ttk.Radiobutton, ttk.Label)):
                    widget.configure(state=state)
                for child in widget.winfo_children():
                    update_widget_state(child)
            except:
                pass

        update_widget_state(self.format_selector)

        # ドロップ領域のラベルの状態を変更
        self.drop_frame.drop_label.configure(state=state)