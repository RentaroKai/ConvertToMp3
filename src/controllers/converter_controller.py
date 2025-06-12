from typing import List, Dict, Optional, Callable
from ..services.ffmpeg_wrapper import FFmpegWrapper
from ..services.file_handler import FileHandler
from ..utils.logger import logger
from ..utils.config_loader import config

class ConverterController:
    """オーディオ変換を制御するコントローラー"""

    def __init__(self):
        self.ffmpeg = FFmpegWrapper()
        self.file_handler = FileHandler()
        self.progress_callback: Optional[Callable[[str, float], None]] = None
        self.quality_preset = "normal"  # デフォルトの品質設定

    def set_progress_callback(self, callback: Callable[[str, float], None]) -> None:
        """進捗コールバックを設定"""
        self.progress_callback = callback

    def set_quality_preset(self, preset: str) -> None:
        """品質設定を設定"""
        self.quality_preset = preset

    def convert_files(self, file_paths: List[str], output_format: str) -> List[Dict[str, str]]:
        """複数のファイルを変換"""
        results = []
        valid_files = self.file_handler.validate_files(file_paths)
        total_files = len(valid_files)

        for i, file_path in enumerate(valid_files, 1):
            try:
                # 進捗を更新
                if self.progress_callback:
                    progress = (i - 1) / total_files * 100
                    self.progress_callback(f"ファイルを処理中 ({i}/{total_files}): {file_path}", progress)

                # ファイル情報を取得
                file_info = self.ffmpeg.get_audio_info(file_path)

                # 動画ファイルかどうかに基づいて進捗メッセージを更新
                if file_info.get("is_video", False) and self.progress_callback:
                    if output_format == "mp4":
                        self.progress_callback(f"動画ファイルを変換中 ({i}/{total_files}): {file_path}", progress)
                    else:
                        self.progress_callback(f"動画ファイルから音声を抽出中 ({i}/{total_files}): {file_path}", progress)

                # 出力パスを生成
                output_path = self.file_handler.get_output_path(file_path, output_format)

                # 変換を実行（動画変換 vs 音声変換）
                if output_format == "mp4":
                    converted_path = self.ffmpeg.convert_video(file_path, output_format, output_path, self.quality_preset)
                else:
                    converted_path = self.ffmpeg.convert_audio(file_path, output_format, output_path)

                # 結果を記録
                results.append({
                    "input_path": file_path,
                    "output_path": converted_path,
                    "original_format": file_info["format"],
                    "new_format": output_format,
                    "original_info": file_info,
                    "status": "success"
                })

                # 最終進捗を更新
                if self.progress_callback:
                    progress = i / total_files * 100
                    self.progress_callback(f"ファイルの変換が完了しました ({i}/{total_files})", progress)

            except Exception as e:
                logger.error(f"ファイルの変換中にエラーが発生しました: {str(e)}")
                results.append({
                    "input_path": file_path,
                    "error": str(e),
                    "status": "error"
                })
                continue

        return results

    def get_supported_formats(self) -> List[str]:
        """サポートされている出力フォーマットを取得"""
        return ["mp3", "wav", "mp4"]

    def get_default_format(self) -> str:
        """デフォルトの出力フォーマットを取得"""
        return config.get_default_format()

    def get_format_settings(self, format_type: str) -> Dict[str, str]:
        """指定されたフォーマットの設定を取得"""
        return config.get_format_settings(format_type)