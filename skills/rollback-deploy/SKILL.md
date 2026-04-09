---
name: rollback-deploy
description: デプロイのロールバック手順。新バージョンデプロイ後の障害時に使用する
allowed-tools: rollback_service check_service_status
---
# ロールバックランブック

デプロイロールバック手順：

1. `check_service_status` で障害の状態を確認する
2. `rollback_service` で前バージョンにロールバックする
3. ロールバック後、`check_service_status` で状態が healthy であることを確認する
4. 回復しない場合は、再起動（restart-service スキル）を検討する
