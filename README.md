# strands-agents-incident-commander

4 つの AI エージェントが Graph オーケストレーションで協調し、インフラ障害を自律的に **検知 → 分類 → 修復 → 振り返り** する Multi-Agent インシデント対応システムです。

Strands Agents SDK の全機能（Multi-Agent Graph、Hooks、Plugin、Steering、Skills、State）を実践的に活用しています。

以下の Qiita 記事に対応しています。

- [Strands Agents Multi-Agent実践：4つのAIエージェントでインシデント対応を自動化する](https://qiita.com/miruky/items/PLACEHOLDER)

## アーキテクチャ

```
                    ┌──────────┐
  Alert ──────────► │ Monitor  │  メトリクス収集・異常検知
                    └────┬─────┘
                         │
                    ┌────▼─────┐
                    │  Triage  │  重大度分類・根本原因分析
                    └────┬─────┘
                         │
                    ┌────▼─────────┐
                    │ Remediation  │  ランブック実行・復旧（Steering で安全制御）
                    └────┬─────────┘
                         │
                    ┌────▼──────────┐
                    │  Postmortem   │  インシデントレポート生成
                    └───────────────┘
```

各エージェントに共通で **AuditTrailPlugin**（操作記録）と **CostTrackerHook**（コスト追跡）がアタッチされています。

## Strands Agents 機能マッピング

| 機能 | 使用箇所 |
|:--|:--|
| Multi-Agent Graph | `main.py` — GraphBuilder でパイプライン構築 |
| Hooks (HookProvider) | `src/plugins/cost_tracker.py` — AfterModelCallEvent / AfterToolCallEvent |
| Plugin (@hook / @tool) | `src/plugins/audit_trail.py` — BeforeToolCallEvent / AfterToolCallEvent |
| Steering (LLMSteeringHandler) | `src/steering/safety.py` — 修復アクションの安全性チェック |
| Skills (SKILL.md) | `skills/` — ランブック（restart, scale-out, rollback, clear-cache） |
| Custom Tools (@tool) | 各エージェントのファクトリ関数内で定義 |
| State / Shared Data | `Incident` オブジェクトをクロージャで全エージェントに共有 |

## 前提条件

- Python 3.10 以上
- AWS クレデンシャルの設定（Amazon Bedrock へのアクセス）
- Bedrock で Claude Sonnet 4 モデルへのアクセスが有効化されていること

## セットアップ

```bash
git clone https://github.com/miruky/strands-agents-incident-commander.git
cd strands-agents-incident-commander

python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate    # Windows

pip install -r requirements.txt
```

## 実行

```bash
# デフォルト: CPU スパイクシナリオ
python main.py

# シナリオを指定
python main.py cpu_spike          # トラフィック急増による CPU スパイク
python main.py memory_leak        # データベースのメモリリーク
python main.py cascading_failure  # キャッシュクラッシュによる連鎖障害
```

## ディレクトリ構成

```
strands-agents-incident-commander/
├── main.py                          # エントリーポイント（GraphBuilder）
├── requirements.txt
├── src/
│   ├── infrastructure.py            # MockInfrastructure（6サービス構成）
│   ├── incident.py                  # Incident モデル（タイムライン管理）
│   ├── scenarios.py                 # 障害シナリオ定義
│   ├── agents/
│   │   ├── monitor.py               # 監視エージェント
│   │   ├── triage.py                # トリアージエージェント
│   │   ├── remediation.py           # 修復エージェント（Skills + Steering）
│   │   └── postmortem.py            # ポストモーテムエージェント
│   ├── plugins/
│   │   ├── audit_trail.py           # AuditTrailPlugin
│   │   └── cost_tracker.py          # CostTrackerHook
│   └── steering/
│       └── safety.py                # RemediationSafetyHandler
└── skills/
    ├── restart-service/SKILL.md     # 再起動ランブック
    ├── scale-out/SKILL.md           # スケールアウトランブック
    ├── rollback-deploy/SKILL.md     # ロールバックランブック
    └── clear-cache/SKILL.md         # キャッシュクリアランブック
```

## シナリオ

### CPU Spike - Traffic Surge

web-app の CPU が 96% に急上昇。応答時間が 30 倍、エラー率 15%。api-gateway にも波及。

### Memory Leak - Database

postgres-primary のメモリ使用率が 95%。クエリ応答時間 20 倍。web-app の応答にも影響。

### Cascading Failure - Cache Down

redis-cache が完全停止。全リクエストが DB 直撃 → postgres-primary 過負荷 → web-app タイムアウト → api-gateway 障害の連鎖。

## ライセンス

MIT
