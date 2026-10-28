# AWS local emulators — đánh giá sâu cho mục đích luyện SAA-C03

Date: 2026-10-20 · Nguồn: README/docs từng repo, GitHub API (số liệu lấy 2026-10-20), bài so sánh codenote.net (04/2026), Hacker News thread Floci, blog Mulga (vendor, có xung đột lợi ích).
**Chưa chạy thử tool nào** — mọi đánh giá fidelity dựa trên docs của chính dự án.

## Bối cảnh
LocalStack archive repo GitHub 2026-03, bản mới bắt buộc account + token → hàng loạt emulator miễn phí mới ra đời từ 02–04/2026. Tất cả đều < 9 tháng tuổi, trừ Moto.

## Sức khoẻ repo
| Repo | ★ | Tạo | Release mới nhất | Commit 30 ngày | Contributor | Người đóng góp nhiều nhất | License |
|---|---|---|---|---|---|---|---|
| floci-io/floci | 26,950 | 2026-02 | 2.3.0 (10-15) | 1,356 | ≥99 | hectorvent 17% | MIT |
| ministackorg/ministack | 4,984 | 2026-03 | v1.5.29 (10-17) | 373 | ≥99 | Nahuel990 36% | MIT |
| sivchari/kumo | 1,503 | 2026-02 | v0.32.0 (10-05) | 117 | 20 | sivchari 79% | MIT |
| faiscadev/fakecloud | 757 | 2026-04 | v0.51.0 (10-18) | 815 | 16 | vieiralucas 98.6% | AGPL-3.0 |
| robotocore/robotocore | 334 | 2026-03 | 2026.10.15 | 47 | 6 | JackDanger 99% | MIT |
| localemu/localemu | 200 | 2026-04 | v1.3.2 (10-19) | 3 | 1 | TarekCheikh 100% | Apache-2.0 (fork LocalStack) |
| getmoto/moto | 8,713 | 2013 | 5.2.4 (10-11) | 65 | ≥98 | bblommers 29% | Apache-2.0 |
| localstack/localstack | 65,143 | 2016 | archived | 0 | — | — | — |

Ghi chú tin cậy:
- Floci: HN 292 điểm; bị nghi phần lớn code do AI viết (50k dòng tuần đầu, repo "xuất hiện hoàn chỉnh"); có người báo lỗi fidelity (S3 list sai thứ tự). Nay cộng đồng lớn nhất, commit rất dày.
- fakecloud: 1 người viết ~99% (7,348 commit) → nhịp kiểu AI-assisted; rủi ro bus-factor. AGPL không ảnh hưởng dùng cá nhân.
- LocalEmu: fork từ code LocalStack (LICENSE ghi Atlassian 2016), 1 người, chỉ 14 commit dạng squash release → không audit được lịch sử.
- robotocore: lớp bọc quanh Moto, EC2 "runs no guest OS".

## Fidelity các phần SAA hay hỏi
✅ chạy thật · ⚠️ một phần · ❌ chỉ API/không có · ? docs không nói

| Năng lực | Floci | fakecloud | LocalEmu | MiniStack | kumo | robotocore | Moto | LocalStack Hobby |
|---|---|---|---|---|---|---|---|---|
| EC2 chạy thật (container) | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ? |
| RDS engine thật | ✅ | ✅ (6 engine) | ✅ (bật flag) | ✅ | ❌ | ❌ | ❌ | ❌ |
| ALB chuyển HTTP tới target | ✅ | ✅ + sticky cookie | ? | ⚠️ chỉ ALB→Lambda | ❌ | ? | ❌ | ❌ |
| ASG tự launch instance | ✅ | ✅ | ? | ❌ stub | ❌ | ❌ | ❌ | ❌ |
| EFS mount được | ❌ | ❌ | ? | ❌ | ❌ | ❌ | ❌ | ❌ |
| Security Group lọc gói | ⚠️ bật flag | ❌ | ✅ (tự nhận) | ❌ | ❌ | ❌ | ❌ | ❌ |
| NACL / route / NAT / peering | ❌ | ❌ (chỉ API) | ⚠️ có tutorial NACL, TGW | ❌ | ❌ | ❌ | ❌ | ❌ |
| IAM policy enforce | ❌ | ✅ `--iam soft/strict` | ✅ opt-in | ❌ | ? | ✅ | ❌ | ❌ |
| Lambda/SQS/SNS/StepFn/API GW | ✅ | ✅ | ✅ | ✅ | ⚠️ | ✅ | API mock | ⚠️ |
| Web UI | ✅ built-in | ? | ✅ built-in | ❌ | ❌ | ❌ | ❌ | ❌ |
| Không cần account/token | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |

Không tool nào mount EFS hay emulate đầy đủ routing VPC (NAT, peering, VPN, Direct Connect).

## UI bổ trợ
| Repo | ★ | Ghi chú |
|---|---|---|
| DaviReisVieira/stackport | 162 | Resource browser dùng chung cho MiniStack, Floci, LocalStack, Moto và AWS thật; 28 release, còn active |
| ofsazib/floci-dash | 59 | UI kiểu AWS Console cho Floci; không commit 30 ngày |
| returnvalue/flocidashboard | 22 | Django, chưa có license |
| rcdelacruz/ministack-ui | 2 | Bỏ dở |

## Xếp hạng cho user (luyện SAA, Windows + Docker Desktop)
1. **Floci** — cân bằng nhất: EC2 + RDS + ALB + ASG chạy thật, cộng đồng lớn nhất, có UI. Thiếu IAM enforce và mạng VPC.
2. **fakecloud** — bổ sung tốt nhất cho Floci: IAM `--iam strict` để luyện policy evaluation/least privilege, ALB sticky + ASG thật. Rủi ro: một người maintain.
3. **LocalEmu** — tự nhận đúng phần SAA khó nhất (SG lọc gói, NACL, TGW, IAM least-privilege tutorials, dashboard) nhưng kém tin cậy nhất (1 người, fork LocalStack, 200★). Chỉ thử nếu muốn tutorial mạng, phải tự kiểm chứng.
4. **MiniStack** — tốt cho dev app (RDS/Redis thật), yếu cho SAA (EC2/ASG chỉ stub).
- Loại: kumo, robotocore, Moto (dành cho test code), LocalStack Hobby (thiếu RDS/ELB/ASG/EFS, cần token), aws-local-simulator, "Flowy" (= Floci).
- Phần không emulator nào làm được (EFS, NAT, peering, VPN, TGW thật, Multi-AZ failover) → AWS Free plan.

## Độ phủ lab Cantrill (38 lab) theo từng tool
Không tool nào phủ hết. Dịch vụ không tool nào có: Lex, Directory Service, Client VPN, AppStream, Elastic Disaster Recovery; không tool nào mount EFS, chạy AMI Windows hay VPN/BGP thật.

| Tool | Lab chạy được ý chính | Một phần |
|---|---|---|
| Floci | 5: pet-cuddle-o-tron, api-gateway, dynamodb-lambda-trigger, lambda-s3-events, alb-session-stickiness | wordpress (không EFS), cognito-federation, systems-manager, scalable-sysops, cloudtrail-integrity |
| fakecloud | 6: 5 lab trên + **iam-scp-permissions-boundary** (SCP + permissions boundary enforce thật khi `FAKECLOUD_IAM=strict`) | wordpress, codepipeline (có CodeCommit), lambda-xray |
| LocalEmu | chưa xác minh — danh sách service đầy đủ chỉ có khi chạy `localemu services` | — |
| MiniStack | ≤4 (EC2/ASG chỉ stub → mất alb-session-stickiness) | — |
| AWS Free plan | gần đủ 38 (chưa xác minh dịch vụ nào bị chặn ở Free plan) | — |

Combo khuyến nghị: fakecloud hoặc Floci cho ~6 lab serverless/ALB/IAM + AWS thật cho phần mạng, EFS, hybrid.

## An toàn khi chạy
- EC2/RDS/Lambda chạy thật nghĩa là tool cần quyền điều khiển Docker (mount Docker socket) → container có quyền gần như toàn bộ máy.
- Tool còn rất mới, code phần lớn chưa được audit: pin version cụ thể, dùng image chính thức, credential giả (`test`/`test`), không để AWS credential thật trong env, nên chạy trong WSL2 hoặc VM.

## Câu hỏi mở
- Floci ALB + ASG + EC2 trên Docker Desktop Windows có chạy ổn không — cần test.
- LocalEmu có thật sự lọc gói SG/NACL như README không — cần test.
- LocalStack Hobby: EC2 chạy container thật hay chỉ mock — docs pricing không nói rõ.
