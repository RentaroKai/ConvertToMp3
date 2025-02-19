import os
import sys
import traceback

# プロジェクトのルートディレクトリをPythonパスに追加
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from src.ui.main_window import MainWindow
from src.utils.logger import logger

def main():
    """アプリケーションのメインエントリーポイント"""
    try:
        # 必要なディレクトリの作成
        os.makedirs("logs", exist_ok=True)
        
        # ロガーの初期化確認
        logger.info("アプリケーションを起動します")
        logger.debug(f"現在の作業ディレクトリ: {os.getcwd()}")
        logger.debug(f"プロジェクトルート: {project_root}")
        
        # アプリケーションの起動
        app = MainWindow()
        logger.info("メインウィンドウを初期化しました")
        app.mainloop()
        
    except Exception as e:
        error_msg = f"予期せぬエラーが発生しました: {str(e)}"
        logger.error(error_msg)
        logger.error("スタックトレース:")
        logger.error(traceback.format_exc())
        print(error_msg)
        print("スタックトレース:")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 