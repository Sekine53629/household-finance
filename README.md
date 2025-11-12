# Household Finance Management System

家計の健全化を目的とした、給与予測・キャッシュフロー管理システム

## 概要

このシステムは、以下を目的としたDjangoベースの財務管理アプリケーションです：

- **給与予測**: 手取り給与の正確な予測
- **キャッシュフロー管理**: 収入・支出の追跡と予測
- **デフォルトリスク管理**: クレジットカード・ローンの引落管理
- **バランスシート管理**: 資産・負債の可視化と純資産の推移追跡

## 主な機能

### 1. 給与管理 (salary)
- 給与明細の記録
- 税金・社会保険料の自動計算
- 手取り額の予測
- SmartHR API連携（予定）

### 2. クレジット・ローン管理 (credit)
- クレジットカード利用の記録
- 短期ローン（携帯分割等）の管理
- 引落予定の自動計算
- デフォルトリスク警告

### 3. キャッシュフロー管理 (cashflow)
- 月次キャッシュフロー予測
- 収支バランスの可視化
- リスク分析と改善提案

### 4. バランスシート管理 (balance_sheet)
- 資産・負債の記録
- 純資産の推移追跡
- 財務健全性指標の計算

## セットアップ

### 必要環境
- Python 3.13+
- pip

### インストール手順

1. リポジトリのクローン
```bash
cd C:\Users\imao3\OneDrive\ドキュメント\GitHub\household-finance
```

2. 仮想環境のアクティベート
```bash
# Windows
venv\Scripts\activate
```

3. パッケージのインストール
```bash
pip install -r requirements.txt
```

4. データベースのマイグレーション
```bash
python manage.py migrate
```

5. 開発サーバーの起動
```bash
python manage.py runserver
```

## プロジェクト構造

```
household-finance/
├── config/              # Django設定
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── salary/              # 給与管理アプリ
├── credit/              # クレジット・ローン管理アプリ
├── cashflow/            # キャッシュフロー管理アプリ
├── balance_sheet/       # バランスシート管理アプリ
├── manage.py
├── requirements.txt
└── README.md
```

## 使い方

### CLI経由での操作（開発予定）

```bash
# 給与データの追加
python manage.py add-salary --month 2024-11 --gross 400000

# 給与予測
python manage.py predict-salary 2025-01

# クレジットカード引落予測
python manage.py predict-credit 2025-01

# キャッシュフロー予測
python manage.py cashflow-forecast 2025-01 --months 3

# バランスシート入力
python manage.py bs-add -cash 500000
python manage.py bs-add -loan:house -12000000

# 財務健全性チェック
python manage.py health-check
```

## 開発ロードマップ

### Phase 1: 基盤構築（Week 1-2）
- [x] プロジェクト作成
- [x] アプリケーション構造作成
- [ ] モデル設計・実装
- [ ] 管理コマンド（CLI）実装
- [ ] 基本的なデータ入力・取得

### Phase 2: 予測ロジック実装（Week 2-3）
- [ ] 給与予測アルゴリズム
- [ ] クレジットカード引落予測
- [ ] キャッシュフロー予測
- [ ] デフォルトリスク判定

### Phase 3: API連携（Week 4）
- [ ] SmartHR API調査
- [ ] インポート機能実装
- [ ] 過去データ一括取り込み

### Phase 4: Web UI（Week 5-6）
- [ ] 入力フォーム
- [ ] 月次レポート表示
- [ ] 予測グラフ描画

## 技術スタック

- **Backend**: Django 5.0.1
- **REST API**: Django REST Framework 3.14.0
- **CLI**: Rich 13.7.0
- **API連携**: Requests 2.31.0
- **設定管理**: Python-decouple 3.8
- **データベース**: SQLite（開発）/ PostgreSQL（本番）

## ライセンス

MIT License

## 作者

Yoshihiro Sekine

## 注意事項

- このシステムは個人の家計管理を目的としています
- 給与データや財務情報は機密情報として適切に管理してください
- SmartHR API連携には会社の許可が必要な場合があります
