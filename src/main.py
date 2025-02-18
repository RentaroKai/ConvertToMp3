import os
import sys

# プロジェクトのルートディレクトリをPythonパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from src.ui.main_window import MainWindow
from src.utils.logger import logger

def main():
    """アプリケーションのメインエントリーポイント"""
    try:
        # 必要なディレクトリの作成
        os.makedirs("logs", exist_ok=True)
        
        # アプリケーションの起動
        logger.info("アプリケーションを起動します")
        app = MainWindow()
        app.mainloop()
        
    except Exception as e:
        logger.error(f"予期せぬエラーが発生しました: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 