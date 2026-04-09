---
name: scale-out
description: サービスのスケールアウト手順。高CPU・高トラフィック時に使用する
allowed-tools: scale_service check_service_status
---
# スケールアウトランブック

高負荷時のスケールアウト手順：

1. `check_service_status` で現在の負荷状態を確認する
2. CPU 80-90% の場合、`scale_service` でインスタンスを 3 に増やす
3. CPU 90% 以上の場合、`scale_service` でインスタンスを 5 に増やす
4. スケールアウト後、`check_service_status` で負荷が下がったことを確認する
5. 依存関係にあるサービスへの影響も確認する
