# Cantrill labs trên AWS emulator local — research

Date: 2026-10-20 · Scope: `acantril/learn-cantrill-io-labs` (16 lab chính + 22 simple demo) vs LocalStack / Floci / Moto / aws-local-simulator / Flowy.
Method: đọc docs Floci từng service + so CFN resource types trong template lab với danh sách Floci hỗ trợ. **Chưa chạy thử** (Docker daemon máy user đang tắt).

## Công cụ
| Tool | Trạng thái (verified 2026-10-20) | Hợp cho lab SAA? |
|---|---|---|
| Floci | MIT, free, không cần token. GitHub floci-io/floci 27k★, tạo 2026-02, commit hôm nay. 126 service trên `localhost:4566` | **Chọn cái này** nếu dùng emulator |
| LocalStack | Repo GitHub **archived** 2026-03; bản mới bắt buộc account + auth token; còn plan Hobby free (non-commercial) | Được nhưng phiền hơn Floci |
| Moto | Thư viện mock cho unit test (Python) | Không — không phải môi trường lab |
| aws-local-simulator | Repo cá nhân (gugananuvem, 43★), 18 service; bài post Builder Center của community, không phải AWS chính thức | Không — quá nhỏ |
| Flowy | **Không tồn tại — là Floci bị AI tóm tắt ghi sai tên.** Video nguồn (Abhishek Veeramalla, 2026-06-09, ~140k view) có chapter "Getting started with Floci"; trang video nhắc "Floci" 13 lần, không có "Flowy" | Xem Floci |
| MiniStack (thêm) | ministackorg/ministack 5k★, MIT, 60+ service | Phương án dự phòng, chưa đánh giá sâu |
| LocalEmu (thêm) | localemu/localemu 200★, pip install, tự nhận 132 service | Còn quá mới/nhỏ |
| floci-dash (thêm) | ofsazib/floci-dash 59★, giao diện kiểu AWS Console cho Floci | Có ích nếu muốn click như Console; repo nhỏ, chưa kiểm tra |

## Floci làm thật vs chỉ giả API
- Thật: EC2 = Docker container (UserData, SSH, IMDS); RDS = MySQL/Postgres container; Lambda = container runtime thật; ALB forward HTTP tới instance target; ASG reconciler launch/terminate instance; S3 events, DynamoDB Streams → Lambda; SQS/SNS/Step Functions/API GW chạy được.
- Chỉ metadata: EFS (không mount NFS), DMS (không replicate dữ liệu), Transfer Family, FIS, Macie, Control Tower.
- Không emulate: VPC routing, NACL, NAT GW, peering, VPN/TGW data plane. SG filter chỉ khi bật `FLOCI_NETWORK_SECURITY_GROUP_ENFORCEMENT_ENABLED` (không hỗ trợ rootless Docker / Windows containers).
- CFN Floci thiếu: `EC2::VPCCidrBlock` (IPv6), `TransitGateway*`, `NetworkInterface`, `EIPAssociation`, `EFS::*`. Không chạy được AMI Windows.
- Không có AWS Console clone → lab Cantrill hướng dẫn bằng Console phải tự dịch sang CLI/Terraform.

## Bảng lab
✅ chạy được ý chính · ⚠️ chạy một phần · ❌ không đáng làm local

### Lab chính
| Lab | Kết quả | Lý do |
|---|---|---|
| aws-serverless-pet-cuddle-o-tron | ✅ | S3 + Lambda + Step Functions + API GW + SES đều có; email SES không gửi thật |
| aws-elastic-wordpress-evolution | ⚠️ | Stage 1–3 (EC2 + RDS MySQL) + 5 (ALB/ASG) được; Stage 4 EFS ❌; template VPC dùng IPv6 `VPCCidrBlock` → phải tự tạo VPC bằng CLI |
| aws-cognito-web-identity-federation | ⚠️ | Cognito/S3 có, nhưng cần Google OAuth thật; CloudFront chủ yếu control plane |
| aws-codepipeline-catpipeline | ⚠️ | CodeBuild/Deploy/Pipeline/ECR/ECS có; ít liên quan SAA |
| aws-scalable-sysops-using-ssm | ⚠️ | SSM Run Command trên container được; ít liên quan SAA |
| aws-lex-lambda-rds | ❌ | Lex không có |
| aws-pet-rekognition-ecr | ⚠️ | ECR/ECS chạy thật; Rekognition chỉ trả kết quả cố định (stub), không phân tích ảnh |
| aws-dms-database-migration | ❌ | DMS chỉ metadata |
| aws-waf | ❌ | WAF chỉ lưu cấu hình |
| aws-patch-manager | ❌ | Cần Windows AMI + Patch Manager |
| aws-simple-site2site-vpn | ❌ | Không có VPN data plane, thiếu CFN types |
| aws-hybrid-bgpvpn | ❌ | TGW + BGP |
| aws-hybrid-dns | ❌ | Cần routing/DNS giữa VPC |
| aws-hybrid-activedirectory | ❌ | Windows + Directory Service |
| aws-client-vpn | ❌ | Client VPN + Directory Service |

### Simple demos (phân loại theo tên + docs Floci, chưa mở từng lab)
| Demo | Kết quả |
|---|---|
| aws-lambda-s3-events, aws-dynamodb-lambda-trigger, aws-api-gateway | ✅ |
| aws-alb-session-stickiness | ✅ (mọi CFN type được hỗ trợ, ALB có sticky binding) |
| aws-iam-scp-permissions-boundary, aws-systems-manager, aws-cloudtrail-log-file-integrity, aws-s3-object-lambda-access-point | ⚠️ chưa rõ mức enforce |
| aws-efs, aws-lambda-vpc-efs, aws-vpc-ipv6, aws-vpc-flow-logs, aws-global-accelerator, aws-s3-multi-region-access-point, aws-sftp-transfer-family-with-s3, aws-macie, aws-fault-injection-simulator, aws-control-tower, aws-elastic-disaster-recovery, aws-appstream-image, aws-video-on-demand, aws-lambda-xray | ❌ |

## Khuyến nghị
- Floci hợp với phần user còn thiếu về serverless/decoupling: pet-cuddle-o-tron, lambda-s3-events, dynamodb-lambda-trigger, api-gateway, alb-session-stickiness. Free, không sợ bill.
- Networking/HA (VPC endpoint, NAT, peering, TGW, VPN, EFS, WordPress đủ 5 stage) → dùng AWS thật. Free plan tài khoản mới: tới $200 credit, 6 tháng, không bị charge trừ khi nâng lên Paid plan; chưa xác minh EFS/ALB/NAT có trong free plan không.
- Với 3 tuần tới ngày thi: lab là phụ. Ưu tiên Tutorials Dojo. Chỉ làm 2–3 lab ✅; đừng mất thời gian dịch lab hybrid sang local.

## Câu hỏi mở
- Đã chạy thử chưa: chưa. Cần bật Docker Desktop để test Floci + `ALBSTICKINESS.yaml`.
- Free plan có cho EFS / ALB / NAT Gateway không — cần đọc /free/terms/.
- Floci có enforce SCP / permissions boundary khi gọi API không — docs chưa nói rõ.
