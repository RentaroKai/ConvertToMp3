import json
import os
from typing import Dict, Any
from .logger import logger

class ConfigLoader:
    """設定ファイルを読み込むクラス"""
    
    DEFAULT_CONFIG = {
        "ffmpeg": {
            "path": "resources/ffmpeg/ffmpeg.exe",
            "default_format": "mp3",
            "mp3": {
                "bitrate": "192k",
                "sample_rate": "44100",
                "channels": "2"
            },
            "wav": {
                "sample_rate": "44100",
                "channels": "2"
            }
        },
        "app": {
            "max_files": 20,
            "log_retention_days": 7,
            "log_max_size_mb": 10
        }
    }
    
    def __init__(self, config_path: str = "config/config.json"):
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        self.load_config()
    
    def create_default_config(self) -> None:
        """デフォルトの設定ファイルを作成する"""
        try:
            # configディレクトリが存在しない場合は作成
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.DEFAULT_CONFIG, f, indent=4, ensure_ascii=False)
            logger.info(f"デフォルトの設定ファイルを作成しました: {self.config_path}")
            
        except Exception as e:
            logger.error(f"デフォルト設定ファイルの作成中にエラーが発生しました: {str(e)}")
            raise
    
    def load_config(self) -> None:
        """設定ファイルを読み込む"""
        try:
            if not os.path.exists(self.config_path):
                logger.warning(f"設定ファイルが見つかりません。デフォルト設定で作成します: {self.config_path}")
                self.create_default_config()
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
                logger.info("設定ファイルを読み込みました")
        
        except json.JSONDecodeError as e:
            logger.error(f"設定ファイルの形式が不正です: {str(e)}")
            raise
        
        except Exception as e:
            logger.error(f"設定ファイルの読み込み中にエラーが発生しました: {str(e)}")
            raise
    
    def get_ffmpeg_path(self) -> str:
        """FFmpegのパスを取得"""
        return self.config.get("ffmpeg", {}).get("path", "")
    
    def get_default_format(self) -> str:
        """デフォルトの出力フォーマットを取得"""
        return self.config.get("ffmpeg", {}).get("default_format", "mp3")
    
    def get_format_settings(self, format_type: str) -> Dict[str, str]:
        """指定されたフォーマットの設定を取得"""
        return self.config.get("ffmpeg", {}).get(format_type, {})
    
    def get_app_settings(self) -> Dict[str, int]:
        """アプリケーションの設定を取得"""
        return self.config.get("app", {})

# グローバルな設定インスタンスを作成
config = ConfigLoader() 