---
name: clear-cache
description: キャッシュクリア手順。キャッシュの不整合やメモリ圧迫時に使用する
allowed-tools: clear_cache check_service_status restart_service
---
# キャッシュクリアランブック

キャッシュクリア手順：

1. `check_service_status` でキャッシュサービスの状態を確認する
2. ステータスが down の場合、まず `restart_service` でサービスを起動する
3. `clear_cache` でキャッシュデータをクリアする
4. `check_service_status` でクリア後の状態を確認する
5. キャッシュに依存するサービス（web-app 等）の状態も確認する
