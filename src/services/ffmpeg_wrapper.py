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
        
        # コマンドを構築
        command = [
            self.ffmpeg_path,
            "-i", input_path,
            "-vn",  # 映像を無視（動画ファイルの場合）
            "-y"  # 既存ファイルを上書き
        ]
        
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
    
    def get_audio_info(self, file_path: str) -> Dict[str, str]:
        """オーディオファイルの情報を取得"""
        if not os.path.exists(file_path):
            logger.error(f"ファイルが見つかりません: {file_path}")
            raise FileNotFoundError(f"ファイルが見つかりません: {file_path}")
        
        try:
            result = subprocess.run(
                [
                    self.ffmpeg_path,
                    "-i", file_path
                ],
                capture_output=True,
                text=True
            )
            
            # FFmpegは情報を標準エラーに出力する
            output = result.stderr
            
            # 基本的な情報を抽出
            info = {
                "format": "unknown",
                "duration": "unknown",
                "bitrate": "unknown",
                "channels": "unknown",
                "sample_rate": "unknown"
            }
            
            # 出力から情報を解析
            if "Audio: " in output:
                audio_line = [line for line in output.split('\n') if "Audio: " in line][0]
                info["format"] = audio_line.split("Audio: ")[1].split(",")[0]
                
                if "Hz" in audio_line:
                    info["sample_rate"] = audio_line.split("Hz")[0].split()[-1]
                
                if "stereo" in audio_line:
                    info["channels"] = "2"
                elif "mono" in audio_line:
                    info["channels"] = "1"
            
            if "Duration: " in output:
                duration_line = output.split("Duration: ")[1].split(",")[0]
                info["duration"] = duration_line.strip()
            
            if "bitrate: " in output:
                bitrate_line = output.split("bitrate: ")[1].split()[0]
                info["bitrate"] = bitrate_line
            
            return info
        
        except Exception as e:
            logger.error(f"ファイル情報の取得中にエラーが発生しました: {str(e)}")
            raise 