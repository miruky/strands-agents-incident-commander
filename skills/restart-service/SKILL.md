---
name: restart-service
description: サービスの再起動手順。クラッシュ、メモリリーク、フリーズ時に使用する
allowed-tools: restart_service check_service_status
---
# サービス再起動ランブック

サービスを再起動する際は以下の手順に従ってください：

1. `check_service_status` で対象サービスの現在の状態を確認する
2. `restart_service` でサービスを再起動する
3. 再起動後、`check_service_status` で状態が healthy に回復したことを確認する
4. 回復しない場合は、スケールアウト（scale-out スキル）を検討する
5. 依存サービスの状態も確認する
