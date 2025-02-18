# AudioConverter

オーディオファイルをドラッグ＆ドロップでMP3またはWAVに変換するシンプルなツールです

## 機能

- ドラッグ＆ドロップでファイルを受け取り（最大20ファイル）
- MP3またはWAVフォーマットへの変換
- シンプルで使いやすいインターフェース
- 詳細なログ出力

## 必要要件

- Python 3.8以上
- FFmpeg（ミニマル版）
- Windows 10/11

## セットアップ


1. リポジトリをクローン：
```bash
git clone https://github.com/yourusername/AudioConverter.git
cd AudioConverter
```

2. 必要なパッケージをインストール：
```bash
pip install -r requirements.txt
```

3. FFmpegをセットアップ：
   - `resources/ffmpeg`ディレクトリにFFmpegのミニマル版を配置してください。

## 使用方法

1. `src/main.py`を実行してアプリケーションを起動
2. 変換したいオーディオファイルをウィンドウにドラッグ＆ドロップ
3. 出力フォーマット（MP3またはWAV）を選択
4. 「変換開始」ボタンをクリック

## ログ

変換ログは`logs`ディレクトリに保存されます。ログは7日間保持され、1ファイルあたり最大10MBまで記録されます。

## ライセンスと謝辞

このプロジェクトは以下のオープンソースソフトウェアを使用しています：

### FFmpeg
- **ライセンス**: LGPL v2.1+
- **著作権表示**: This software uses code of [FFmpeg](http://ffmpeg.org) licensed under the LGPLv2.1 and its source can be downloaded [here](https://ffmpeg.org/download.html)
- **用途**: オーディオファイルの変換処理に使用

FFmpegのライセンスの詳細については[FFmpeg License and Legal Considerations](https://ffmpeg.org/legal.html)をご確認ください。 