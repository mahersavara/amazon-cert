# Floci — AWS giả lập local

Cấu hình: [`floci/compose.yaml`](../floci/compose.yaml) · Floci 2.3.0 · chỉ nghe trên 127.0.0.1.

## Bật / tắt
```bash
docker compose -f floci/compose.yaml up -d     # bật (cần Docker Desktop đang chạy)
docker compose -f floci/compose.yaml down      # tắt, giữ dữ liệu
docker compose -f floci/compose.yaml down -v   # tắt + xoá sạch dữ liệu
```

## Trỏ AWS CLI vào Floci (chỉ cửa sổ hiện tại)
- PowerShell: `. .\floci\floci-env.ps1`
- Git Bash: `source floci/floci-env.sh` và thêm `export MSYS_NO_PATHCONV=1` (nếu không, Git Bash biến `/aws/service/...` thành đường dẫn Windows).

Credential là `test`/`test`. Không chạy các script này trong cửa sổ đang dùng AWS thật.

## Cổng
| Cổng | Dùng cho |
|---|---|
| 4566 | Mọi API AWS. Gõ `http://127.0.0.1` không có cổng sẽ bị từ chối |
| 4500 | Web console: http://localhost:4500/console/aws (hoặc mở http://localhost:4566/_floci/ui để tự chuyển hướng) |
| 7001–7020 | RDS (Endpoint.Port trong `describe-db-instances`; kết nối `localhost:<port>`) |
| 8080–8089 | Listener ALB/NLB — tạo listener trên các cổng này để gọi từ máy |

## Đã kiểm tra (2026-10-20)
S3, SQS, DynamoDB, STS, EC2 (`run-instances` ra container thật), RDS MySQL (cổng 7001 kết nối được), web console. ALB/ASG chưa test.

## Lưu ý
- Container Floci có quyền điều khiển Docker trên máy (mount Docker socket).
- AMI: lấy từ SSM `/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64`.
- Không mô phỏng: EFS mount, NAT/peering/VPN, Windows.
