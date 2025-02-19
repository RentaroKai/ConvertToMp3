import json
import os
import sys
from typing import Dict, Any
from .logger import logger

class ConfigLoader:
    """設定ファイルを読み込むクラス"""
    
    def _get_base_path(self) -> str:
        """実行ファイルのベースパスを取得"""
        if getattr(sys, 'frozen', False):
            # PyInstallerで実行されている場合
            return os.path.dirname(sys.executable)
        else:
            # 通常のPythonで実行されている場合
            return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    def _normalize_path(self, path: str) -> str:
        """パスを正規化する"""
        return os.path.normpath(path.replace('/', os.sep))
    
    DEFAULT_CONFIG = {
        "ffmpeg": {
            "path": "ffmpeg.exe",  # FFmpegは同じディレクトリに配置
            "default_format": "mp3",
            "mp3": {
                "bitrate": "96k",
                "sample_rate": "44100",
                "channels": "1"
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
        print("デバッグ: ConfigLoaderの初期化開始")
        self.base_path = self._get_base_path()
        print(f"デバッグ: ベースパス: {self.base_path}")
        self.config_path = os.path.normpath(os.path.join(self.base_path, self._normalize_path(config_path)))
        print(f"デバッグ: 設定ファイルのパス: {self.config_path}")
        self.config: Dict[str, Any] = {}
        self.load_config()
    
    def create_default_config(self) -> None:
        """デフォルトの設定ファイルを作成する"""
        try:
            print("デバッグ: デフォルト設定ファイルの作成開始")
            # configディレクトリが存在しない場合は作成
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            print(f"デバッグ: 設定ディレクトリを作成: {os.path.dirname(self.config_path)}")
            
            # FFmpegのパスを絶対パスに変換
            config = self.DEFAULT_CONFIG.copy()
            ffmpeg_path = os.path.normpath(os.path.join(self.base_path, self.DEFAULT_CONFIG["ffmpeg"]["path"]))
            config["ffmpeg"]["path"] = ffmpeg_path
            print(f"デバッグ: FFmpegパスを設定: {ffmpeg_path}")
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            print(f"デバッグ: デフォルト設定ファイルを作成完了: {self.config_path}")
            logger.info(f"デフォルトの設定ファイルを作成しました: {self.config_path}")
            
        except Exception as e:
            print(f"エラー: デフォルト設定ファイルの作成中にエラー発生: {str(e)}")
            logger.error(f"デフォルト設定ファイルの作成中にエラーが発生しました: {str(e)}")
            raise
    
    def load_config(self) -> None:
        """設定ファイルを読み込む"""
        try:
            print(f"デバッグ: 設定ファイルの読み込み開始: {self.config_path}")
            if not os.path.exists(self.config_path):
                print("デバッグ: 設定ファイルが存在しないためデフォルト設定を作成します")
                logger.warning(f"設定ファイルが見つかりません。デフォルト設定で作成します: {self.config_path}")
                self.create_default_config()
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
                # FFmpegのパスが相対パスの場合は絶対パスに変換
                ffmpeg_path = self.config.get("ffmpeg", {}).get("path", "")
                if not os.path.isabs(ffmpeg_path):
                    ffmpeg_path = os.path.normpath(os.path.join(self.base_path, self._normalize_path(ffmpeg_path)))
                    self.config["ffmpeg"]["path"] = ffmpeg_path
                    print(f"デバッグ: FFmpegパスを絶対パスに変換: {ffmpeg_path}")
                print("デバッグ: 設定ファイルの読み込みが完了")
                logger.info("設定ファイルを読み込みました")
        
        except json.JSONDecodeError as e:
            print(f"エラー: 設定ファイルの形式が不正: {str(e)}")
            logger.error(f"設定ファイルの形式が不正です: {str(e)}")
            raise
        
        except Exception as e:
            print(f"エラー: 設定ファイルの読み込み中にエラー発生: {str(e)}")
            logger.error(f"設定ファイルの読み込み中にエラーが発生しました: {str(e)}")
            raise
    
    def get_ffmpeg_path(self) -> str:
        """FFmpegのパスを取得"""
        path = self.config.get("ffmpeg", {}).get("path", "")
        return os.path.normpath(path)
    
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