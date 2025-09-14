from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class XboxGame:
    """Xbox Game Passのゲーム情報を表すデータクラス"""

    title: str
    """ゲームのタイトル"""
    description: str
    """ゲームの説明"""
    image_url: str
    """ゲームの画像URL"""

    @staticmethod
    def create(data: dict) -> XboxGame:
        """辞書データからXboxGameインスタンスを生成する。

        Args:
            data (dict): ゲーム情報を含む辞書データ

        Returns:
            XboxGame: 生成されたXboxGameインスタンス
        """

        title = data.get("ProductTitle", None)
        if title is None:
            raise ValueError("ProductTitle is missing in data")

        description = data.get("ProductDescription", "")
        image_title = data.get("ImageTile", {})
        image_url = image_title.get("URI", "")

        return XboxGame(
            title=title,
            description=description,
            image_url=image_url,
        )
