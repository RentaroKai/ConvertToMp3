import os
import subprocess
from typing import Dict, Optional
from ..utils.logger import logger
from ..utils.config_loader import config

class FFmpegWrapper:
    """FFmpegを実行するためのラッパークラス"""

    def __init__(self):
        print("デバッグ: FFmpegWrapperの初期化開始")
        self.ffmpeg_path = config.get_ffmpeg_path()
        print(f"デバッグ: FFmpegのパス: {self.ffmpeg_path}")
        self._verify_ffmpeg()

    def _verify_ffmpeg(self) -> None:
        """FFmpegが利用可能か確認"""
        print(f"デバッグ: FFmpegの検証開始")
        if not os.path.exists(self.ffmpeg_path):
            print(f"エラー: FFmpegが見つかりません: {self.ffmpeg_path}")
            logger.error(f"FFmpegが見つかりません: {self.ffmpeg_path}")
            raise FileNotFoundError(f"FFmpegが見つかりません: {self.ffmpeg_path}")

        try:
            print("デバッグ: FFmpegバージョンの確認を実行")
            result = subprocess.run(
                [self.ffmpeg_path, "-version"],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                print(f"エラー: FFmpegの実行に失敗: {result.stderr}")
                raise RuntimeError("FFmpegの実行に失敗しました")
            print("デバッグ: FFmpegの検証が完了")
            logger.info("FFmpegの検証が完了しました")
        except Exception as e:
            print(f"エラー: FFmpegの検証中にエラー発生: {str(e)}")
            logger.error(f"FFmpegの検証中にエラーが発生しました: {str(e)}")
            raise

    def convert_audio(
        self,
        input_path: str,
        output_format: str,
        output_path: Optional[str] = None
    ) -> str:
        """オーディオファイルを変換"""
        if not os.path.exists(input_path):
            logger.error(f"入力ファイルが見つかりません: {input_path}")
            raise FileNotFoundError(f"入力ファイルが見つかりません: {input_path}")

        # 出力パスが指定されていない場合、入力ファイルと同じディレクトリに作成
        if output_path is None:
            base_path = os.path.splitext(input_path)[0]
            output_path = f"{base_path}_converted.{output_format}"

        # フォーマット設定を取得
        format_settings = config.get_format_settings(output_format)

        # 入力ファイルの拡張子を取得
        input_ext = os.path.splitext(input_path)[1].lower().lstrip(".")
        is_video = input_ext in ["mp4", "mkv", "mov"]

        # コマンドを構築
        command = [
            self.ffmpeg_path,
            "-i", input_path,
            "-vn",  # 映像を無視（動画ファイルの場合）
            "-y"  # 既存ファイルを上書き
        ]

        # 動画ファイルの場合、音声抽出の最適化設定を追加
        if is_video:
            print(f"デバッグ: 動画ファイルからの音声抽出を実行: {input_path}")
            logger.info(f"動画ファイルからの音声抽出を実行: {input_path}")

        # フォーマット固有の設定を追加
        if output_format == "mp3":
            command.extend([
                "-acodec", "libmp3lame",  # MP3エンコーダーを指定
                "-b:a", format_settings.get("bitrate", "192k"),
                "-ar", format_settings.get("sample_rate", "44100"),
                "-ac", format_settings.get("channels", "2")
            ])
        elif output_format == "wav":
            command.extend([
                "-acodec", "pcm_s16le",  # WAVエンコーダーを指定
                "-ar", format_settings.get("sample_rate", "44100"),
                "-ac", format_settings.get("channels", "2")
            ])

        command.append(output_path)

        logger.info(f"変換を開始: {input_path} -> {output_path}")
        print(f"デバッグ: 実行するコマンド: {' '.join(command)}")
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                logger.error(f"変換中にエラーが発生しました: {result.stderr}")
                raise RuntimeError(f"変換中にエラーが発生しました: {result.stderr}")

            logger.info(f"変換が完了しました: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"変換中にエラーが発生しました: {str(e)}")
            raise

    def convert_video(
        self,
        input_path: str,
        output_format: str,
        output_path: Optional[str] = None,
        quality_preset: str = "normal"
    ) -> str:
        """動画ファイルを変換（mp4への変換用）"""
        if not os.path.exists(input_path):
            logger.error(f"入力ファイルが見つかりません: {input_path}")
            raise FileNotFoundError(f"入力ファイルが見つかりません: {input_path}")

        # 出力パスが指定されていない場合、入力ファイルと同じディレクトリに作成
        if output_path is None:
            base_path = os.path.splitext(input_path)[0]
            output_path = f"{base_path}_converted.{output_format}"

        # フォーマット設定を取得
        format_settings = config.get_format_settings(output_format)

        # 入力ファイルの拡張子を取得
        input_ext = os.path.splitext(input_path)[1].lower().lstrip(".")

        print(f"デバッグ: 動画ファイルの変換を開始: {input_path}")
        logger.info(f"動画ファイルの変換を開始: {input_path}")

        # コマンドを構築
        command = [
            self.ffmpeg_path,
            "-i", input_path,
            "-y"  # 既存ファイルを上書き
        ]

        # フォーマット固有の設定を追加
        if output_format == "mp4":
            command.extend([
                "-c:v", "libx264",  # H.264エンコーダーを指定
                "-c:a", "aac",      # AACオーディオエンコーダーを指定
            ])

            # 品質設定に応じてエンコード設定を調整
            if quality_preset == "high_compression":  # めちゃ圧縮
                command.extend([
                    "-crf", "28",        # 高圧縮（品質は少し下がる）
                    "-preset", "slow",   # 圧縮効率重視
                    "-b:v", "500k",      # 動画ビットレート制限
                    "-b:a", "64k",       # 音声ビットレート制限
                    "-vf", "scale=-2:720"  # 720pにリサイズ
                ])
                print("デバッグ: めちゃ圧縮設定を適用")
            elif quality_preset == "medium_compression":  # まあまあ圧縮
                command.extend([
                    "-crf", "23",        # 中程度の圧縮
                    "-preset", "medium", # バランス重視
                    "-b:v", "1500k",     # 動画ビットレート
                    "-b:a", "128k",      # 音声ビットレート
                ])
                print("デバッグ: まあまあ圧縮設定を適用")
            else:  # デフォルト設定
                command.extend([
                    "-crf", "20",        # 高品質
                    "-preset", "medium",
                    "-b:a", "192k",
                ])
                print("デバッグ: デフォルト設定を適用")

        command.append(output_path)

        logger.info(f"動画変換を開始: {input_path} -> {output_path}")
        print(f"デバッグ: 実行するコマンド: {' '.join(command)}")
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                logger.error(f"動画変換中にエラーが発生しました: {result.stderr}")
                raise RuntimeError(f"動画変換中にエラーが発生しました: {result.stderr}")

            logger.info(f"動画変換が完了しました: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"動画変換中にエラーが発生しました: {str(e)}")
            raise

    def get_audio_info(self, file_path: str) -> Dict[str, str]:
        """オーディオファイルの情報を取得"""
        if not os.path.exists(file_path):
            logger.error(f"ファイルが見つかりません: {file_path}")
            raise FileNotFoundError(f"ファイルが見つかりません: {file_path}")

        try:
            # 入力ファイルの拡張子を取得
            input_ext = os.path.splitext(file_path)[1].lower().lstrip(".")
            is_video = input_ext in ["mp4", "mkv", "mov"]

            print(f"デバッグ: ファイル情報の取得開始: {file_path}")
            result = subprocess.run(
                [
                    self.ffmpeg_path,
                    "-i", file_path
                ],
                capture_output=True,
                text=True
            )

            # FFmpegは情報を標準エラーに出力する
            output = result.stderr if result.stderr else ""

            # 基本的な情報を抽出
            info = {
                "format": "unknown",
                "duration": "unknown",
                "bitrate": "unknown",
                "channels": "unknown",
                "sample_rate": "unknown",
                "is_video": is_video
            }

            # 出力から情報を解析
            if "Audio: " in output:
                print(f"デバッグ: オーディオ情報を検出")
                audio_lines = [line for line in output.split('\n') if "Audio: " in line]
                if audio_lines:
                    audio_line = audio_lines[0]
                    audio_parts = audio_line.split("Audio: ")
                    if len(audio_parts) > 1:
                        format_parts = audio_parts[1].split(",")
                        if format_parts:
                            info["format"] = format_parts[0]

                    if "Hz" in audio_line:
                        try:
                            hz_parts = audio_line.split("Hz")
                            if hz_parts and len(hz_parts) > 0:
                                sample_rate_parts = hz_parts[0].split()
                                if sample_rate_parts:
                                    info["sample_rate"] = sample_rate_parts[-1]
                        except (IndexError, ValueError) as e:
                            print(f"デバッグ: サンプルレート情報の抽出に失敗: {str(e)}")

                    if "stereo" in audio_line:
                        info["channels"] = "2"
                    elif "mono" in audio_line:
                        info["channels"] = "1"
                    elif "channels" in audio_line:
                        try:
                            channel_parts = [part for part in audio_line.split(", ") if "channel" in part]
                            if channel_parts and len(channel_parts) > 0:
                                channel_info = channel_parts[0]
                                channel_value = channel_info.split()
                                if channel_value and len(channel_value) > 0:
                                    info["channels"] = channel_value[0]
                        except (IndexError, ValueError) as e:
                            print(f"デバッグ: チャンネル情報の抽出に失敗: {str(e)}")
            else:
                print(f"デバッグ: オーディオ情報が検出されませんでした")

            if "Duration: " in output:
                print(f"デバッグ: デュレーション情報を検出")
                try:
                    duration_parts = output.split("Duration: ")
                    if len(duration_parts) > 1:
                        duration_line = duration_parts[1].split(",")[0]
                        info["duration"] = duration_line.strip()
                except (IndexError, ValueError) as e:
                    print(f"デバッグ: デュレーション情報の抽出に失敗: {str(e)}")

            if "bitrate: " in output:
                print(f"デバッグ: ビットレート情報を検出")
                try:
                    bitrate_parts = [part for part in output.split() if "kb/s" in part]
                    if bitrate_parts and len(bitrate_parts) > 0:
                        info["bitrate"] = bitrate_parts[0]
                except (IndexError, ValueError) as e:
                    print(f"デバッグ: ビットレート情報の抽出に失敗: {str(e)}")

            print(f"デバッグ: 取得したファイル情報: {info}")
            return info

        except Exception as e:
            logger.error(f"ファイル情報の取得中にエラーが発生しました: {str(e)}")
            print(f"エラー詳細: {str(e)}")
            # エラーが発生しても基本情報を返す
            return {
                "format": "unknown",
                "duration": "unknown",
                "bitrate": "unknown",
                "channels": "unknown",
                "sample_rate": "unknown",
                "is_video": input_ext in ["mp4", "mkv", "mov"]
            }