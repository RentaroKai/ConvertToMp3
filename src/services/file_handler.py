import os
from typing import List, Set
from ..utils.logger import logger
from ..utils.config_loader import config

class FileHandler:
    """ファイル操作を行うハンドラークラス"""
    
    def __init__(self):
        self.max_files = config.get_app_settings().get("max_files", 20)
        self.supported_formats: Set[str] = {
            # 入力として受け付ける形式
            "mp3", "wav", "aac", "m4a", "wma", "ogg", "flac",
            "mkv", "mp4"  # 動画フォーマットを追加
        }
    
    def validate_files(self, file_paths: List[str]) -> List[str]:
        """ファイルの検証を行い、有効なファイルパスのリストを返す"""
        valid_files = []
        
        if len(file_paths) > self.max_files:
            logger.warning(f"ファイル数が制限を超えています。最初の{self.max_files}個のファイルのみ処理します。")
            file_paths = file_paths[:self.max_files]
        
        for file_path in file_paths:
            try:
                # ファイルの存在確認
                if not os.path.exists(file_path):
                    logger.error(f"ファイルが見つかりません: {file_path}")
                    continue
                
                # ファイル拡張子の確認
                ext = os.path.splitext(file_path)[1].lower().lstrip(".")
                if ext not in self.supported_formats:
                    logger.warning(f"サポートされていないファイル形式です: {file_path}")
                    continue
                
                valid_files.append(file_path)
                logger.info(f"ファイルの検証が完了しました: {file_path}")
            
            except Exception as e:
                logger.error(f"ファイルの検証中にエラーが発生しました: {str(e)}")
                continue
        
        return valid_files
    
    def get_output_path(self, input_path: str, output_format: str) -> str:
        """出力ファイルパスを生成"""
        try:
            directory = os.path.dirname(input_path)
            filename = os.path.splitext(os.path.basename(input_path))[0]
            output_path = os.path.join(directory, f"{filename}_converted.{output_format}")
            
            # 同名ファイルが存在する場合、連番を付与
            counter = 1
            while os.path.exists(output_path):
                output_path = os.path.join(directory, f"{filename}_converted_{counter}.{output_format}")
                counter += 1
            
            return output_path
        
        except Exception as e:
            logger.error(f"出力パスの生成中にエラーが発生しました: {str(e)}")
            raise
    
    def cleanup_temp_files(self, file_paths: List[str]) -> None:
        """一時ファイルの削除"""
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"一時ファイルを削除しました: {file_path}")
            except Exception as e:
                logger.error(f"一時ファイルの削除中にエラーが発生しました: {str(e)}")
                continue 