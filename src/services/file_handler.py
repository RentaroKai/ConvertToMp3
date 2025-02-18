import os
from typing import List, Set
from ..utils.logger import logger
from ..utils.config_loader import config

class FileHandler:
    """ファイル操作を行うハンドラークラス"""
    
    def __init__(self):
        print("デバッグ: FileHandlerの初期化開始")
        self.max_files = config.get_app_settings().get("max_files", 20)
        self.supported_formats: Set[str] = {
            # 入力として受け付ける形式
            "mp3", "wav", "aac", "m4a", "wma", "ogg", "flac",
            "mkv", "mp4"  # 動画フォーマットを追加
        }
        print(f"デバッグ: サポートされているフォーマット: {self.supported_formats}")
    
    def validate_files(self, file_paths: List[str]) -> List[str]:
        """ファイルの検証を行い、有効なファイルパスのリストを返す"""
        valid_files = []
        
        print(f"デバッグ: 検証開始 - 入力ファイル数: {len(file_paths)}")
        if len(file_paths) > self.max_files:
            print(f"警告: ファイル数が制限を超えています（最大{self.max_files}個）")
            logger.warning(f"ファイル数が制限を超えています。最初の{self.max_files}個のファイルのみ処理します。")
            file_paths = file_paths[:self.max_files]
        
        for file_path in file_paths:
            try:
                print(f"\nデバッグ: ファイルの検証: {file_path}")
                # パスの正規化
                normalized_path = os.path.normpath(file_path)
                print(f"デバッグ: 正規化されたパス: {normalized_path}")
                
                # ファイルの存在確認
                if not os.path.exists(normalized_path):
                    print(f"エラー: ファイルが見つかりません: {normalized_path}")
                    logger.error(f"ファイルが見つかりません: {normalized_path}")
                    continue
                
                # ファイル拡張子の確認
                ext = os.path.splitext(normalized_path)[1].lower().lstrip(".")
                print(f"デバッグ: ファイル拡張子: {ext}")
                
                if ext not in self.supported_formats:
                    print(f"警告: サポートされていない形式です: {ext}")
                    logger.warning(f"サポートされていないファイル形式です: {normalized_path}")
                    continue
                
                valid_files.append(normalized_path)
                print(f"デバッグ: ファイルの検証が完了しました: {normalized_path}")
                logger.info(f"ファイルの検証が完了しました: {normalized_path}")
            
            except Exception as e:
                print(f"エラー: ファイルの検証中にエラーが発生: {str(e)}")
                logger.error(f"ファイルの検証中にエラーが発生しました: {str(e)}")
                continue
        
        print(f"\nデバッグ: 検証完了 - 有効なファイル数: {len(valid_files)}")
        return valid_files
    
    def get_output_path(self, input_path: str, output_format: str) -> str:
        """出力ファイルパスを生成"""
        try:
            print(f"デバッグ: 出力パスの生成開始 - 入力: {input_path}")
            directory = os.path.dirname(input_path)
            filename = os.path.splitext(os.path.basename(input_path))[0]
            output_path = os.path.join(directory, f"{filename}_converted.{output_format}")
            print(f"デバッグ: 生成された出力パス: {output_path}")
            
            # 同名ファイルが存在する場合、連番を付与
            counter = 1
            while os.path.exists(output_path):
                print(f"デバッグ: 同名ファイルが存在するため連番を付与: {counter}")
                output_path = os.path.join(directory, f"{filename}_converted_{counter}.{output_format}")
                counter += 1
            
            return output_path
        
        except Exception as e:
            print(f"エラー: 出力パスの生成中にエラーが発生: {str(e)}")
            logger.error(f"出力パスの生成中にエラーが発生しました: {str(e)}")
            raise
    
    def cleanup_temp_files(self, file_paths: List[str]) -> None:
        """一時ファイルの削除"""
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"デバッグ: 一時ファイルを削除: {file_path}")
                    logger.info(f"一時ファイルを削除しました: {file_path}")
            except Exception as e:
                print(f"エラー: 一時ファイルの削除中にエラーが発生: {str(e)}")
                logger.error(f"一時ファイルの削除中にエラーが発生しました: {str(e)}")
                continue 