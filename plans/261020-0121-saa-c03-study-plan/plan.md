# SAA-C03 study plan (20/10 → thi ~13/11/2026)

Status: draft · Owner: user · Hạn promo: thi xong ≤ 16/11 (an toàn)

## Mục tiêu
- Đậu SAA-C03 (≥720) lần đầu, trong cửa sổ Pearson Global Retake (giá $82.50).
- Tiêu chí sẵn sàng: Tutorials Dojo (TD) timed mode ≥ 80% ở 2 đề liên tiếp + đề official 20 câu ≥ 85%.

## Giả định
- Thời gian học: ~2h/ngày thường, ~4h/ngày cuối tuần → ~50–55h tổng.
- Ngày thi đề xuất: Thứ 6 13/11 (Metaserv HN) → còn 16/11 làm dự phòng dời lịch.

## Đánh giá nền tảng
| Đã mạnh (ôn nhanh) | Thiếu / hay sai với dân K8s-DevOps |
|---|---|
| EC2, ECR, EKS, ELB cơ bản, Route 53 (record), ACM/TLS, IaC | VPC sâu: NAT GW vs NAT instance, VPC endpoint (gateway vs interface), peering vs Transit Gateway, VPN vs Direct Connect, NACL vs SG |
| | Route 53 routing policies (failover, latency, geolocation, geoproximity, weighted), CloudFront (OAC, signed URL), Global Accelerator |
| | IAM policy evaluation, SCP/Organizations, cross-account role, KMS (CMK, envelope), Secrets Manager vs Parameter Store, WAF/Shield, Cognito |
| | Storage: S3 classes + lifecycle + replication + Object Lock, EBS gp3/io2, EFS vs FSx (Windows/Lustre/ONTAP), Storage Gateway |
| | DB: RDS Multi-AZ vs Read Replica, Aurora (Global, Serverless), DynamoDB (DAX, Global Tables, on-demand), ElastiCache, Redshift |
| | Decoupling/serverless: SQS (FIFO, DLQ, visibility), SNS fan-out, EventBridge, Kinesis (Streams vs Firehose), Lambda, API Gateway, Step Functions |
| | DR (backup-restore, pilot light, warm standby, active-active), Auto Scaling policies |
| | Cost: Savings Plans vs RI vs Spot, S3 Intelligent-Tiering, Compute Optimizer |
| | Migration/analytics: DMS/SCT, DataSync, Snow family, Athena, Glue, Lake Formation |

Bẫy chính: đề ưu tiên **managed/serverless, "least operational overhead"**. Đừng chọn tự dựng (K8s trên EC2, cron trên EC2...) khi có service managed.

## Lịch
| Tuần | Ngày | Nội dung | Đầu ra |
|---|---|---|---|
| 0 | 20–21/10 | Đề chẩn đoán: official 20 câu (Skill Builder, free) + TD sampler 30 câu (free). Xin ESL +30. Đặt lịch thi. | Điểm gốc, danh sách domain yếu |
| 1 | 22–26/10 | Networking + Security (VPC, hybrid, Route 53, CloudFront, IAM, KMS, WAF) | TD section-based: Secure ≥ 75% |
| 2 | 27/10–2/11 | Storage + Database | TD section-based: Resilient / High-Perf ≥ 75% |
| 3 | 3–8/11 | Decoupling, serverless, DR, cost, migration, analytics | TD section-based: Cost ≥ 75% |
| 4 | 9–12/11 | TD timed full đề (1 đề/ngày) + review mọi câu sai, ghi lỗi vào notes | 2 đề liên tiếp ≥ 80% |
| — | 13/11 | Thi | |

Không đạt ngưỡng ở tuần 4 → dời lịch sang 14–16/11 (≥24h báo trước).

## Tài liệu
- Bắt buộc: Tutorials Dojo SAA practice exams ($14.99) + cheat sheets (free).
- Bắt buộc: AWS Official Practice Question Set SAA-C03 (free, Skill Builder).
- Tuỳ chọn (học theo chủ đề yếu, không xem hết): Cantrill SAA ($40) hoặc khoá Stephane Maarek (Udemy).
- Tham khảo: exam guide + in-scope services list (docs.aws.amazon.com SAA-C03).
- Lab nhanh (chỉ phần chưa làm): VPC endpoint + S3, SQS + Lambda, RDS Multi-AZ failover, CloudFront + S3 OAC. Bật Budgets alert trước.

## Rủi ro
- Hết slot Hà Nội gần hạn → đặt lịch sớm.
- Ít thời gian hơn giả định → bỏ khoá video, chỉ dùng TD review mode + cheat sheets.

## Câu hỏi mở
- Số giờ học thực tế mỗi ngày?
- Thi tại trung tâm hay online (OnVUE)?
