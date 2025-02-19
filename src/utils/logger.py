import os
import sys
from datetime import datetime
from loguru import logger

def setup_logger():
    """ロガーの初期設定を行う"""
    try:
        # ログファイルのパスを設定
        log_dir = os.path.abspath("logs")
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, f"audio_converter_{datetime.now().strftime('%Y%m%d')}.log")
        
        # ロガーの設定
        config = {
            "handlers": [
                {
                    "sink": sys.stdout,
                    "format": "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
                    "catch": True,
                },
                {
                    "sink": log_file,
                    "format": "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
                    "rotation": "1 day",
                    "retention": "7 days",
                    "compression": "zip",
                    "encoding": "utf-8",
                    "catch": True,
                },
            ],
        }
        
        # 既存のハンドラーを削除
        logger.remove()
        
        # 新しい設定を適用
        for handler in config["handlers"]:
            logger.add(**handler)
        
        logger.info("ロガーの初期化が完了しました")
        return logger
        
    except Exception as e:
        print(f"ロガーの初期化中にエラーが発生しました: {str(e)}")
        # 最低限のロガー設定を適用
        logger.remove()
        logger.add(sys.stdout, catch=True)
        return logger

# グローバルなロガーインスタンスを作成
logger = setup_logger() 