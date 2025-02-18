import os
import sys
import traceback

# プロジェクトのルートディレクトリをPythonパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from src.ui.main_window import MainWindow
from src.utils.logger import logger

def main():
    """アプリケーションのメインエントリーポイント"""
    try:
        print("デバッグ: アプリケーション起動開始")
        print(f"デバッグ: 現在の作業ディレクトリ: {os.getcwd()}")
        print(f"デバッグ: プロジェクトルート: {project_root}")
        
        # 必要なディレクトリの作成
        os.makedirs("logs", exist_ok=True)
        print("デバッグ: logsディレクトリを作成しました")
        
        # アプリケーションの起動
        logger.info("アプリケーションを起動します")
        print("デバッグ: MainWindowを初期化します")
        app = MainWindow()
        print("デバッグ: MainWindow初期化完了")
        app.mainloop()
        
    except Exception as e:
        print(f"エラー発生: {str(e)}")
        print("スタックトレース:")
        traceback.print_exc()
        logger.error(f"予期せぬエラーが発生しました: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 