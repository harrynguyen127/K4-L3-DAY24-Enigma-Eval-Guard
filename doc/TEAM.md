# Nhóm thực hiện K4 Track 3A — Enigma

Tên nhóm: **Enigma**.

Repo chung: [K4-L3-DAY24-Enigma-Eval-Guard](https://github.com/harrynguyen127/K4-L3-DAY24-Enigma-Eval-Guard).

Trưởng nhóm/người nộp: **Nguyễn Anh Tuấn — 2A202602700**.

Ngày cập nhật báo cáo: **12/10/2026**, Asia/Ho_Chi_Minh (UTC+07:00). Ngày lab và deadline cụ thể chưa có thông báo lớp trong repo; áp dụng **23:59 ngày diễn ra lab**, trừ khi coach thông báo điều chỉnh theo [SUBMISSION.md](SUBMISSION.md).

Commit dùng để chấm: **chưa chốt bản nộp cuối**. Commit bằng chứng Phase A hiện có là `0ee7c1a74cd449f224f33fe74b6aa8a3398990b4`, thời điểm `2026-10-12T11:47:55+07:00`, thông điệp `feat: complete Phase A evaluation and handoff evidence`. Báo cáo này chưa nằm trong commit đó; Tuấn cập nhật SHA bản cuối khi nộp.

Thông tin thành viên và nhiệm vụ lấy từ `PHAN_CONG_ENIGMA_TEAM.md` (bản cục bộ trong `temp/`), đối chiếu với [đề bài](ASSIGNMENT.md), [bàn giao Phase A](PHASE_A_HANDOFF.md), mã nguồn, artifacts và lịch sử Git. MSSV được giữ đúng như tài liệu phân công. Trạng thái dưới đây phản ánh bằng chứng trong repo tại lần cập nhật này.

## Thành viên và phân công

| STT | Họ và tên | MSSV | Vai trò / công việc thật | Bằng chứng |
|---|---|---|---|---|
| 1 | Nguyễn Anh Tuấn | 2A202602700 | Phụ trách pipeline RAG m1–m5, Phase A/B, báo cáo lỗi và bias; kiểm tra bản tích hợp và nộp link. Đã hoàn thiện Tasks 1–8, 50 answers, batch A/B và hai báo cáo; bàn giao số liệu cho Hưng. | Commit A `0ee7c1a74cd449f224f33fe74b6aa8a3398990b4`; [bàn giao A](PHASE_A_HANDOFF.md), [bàn giao B](PHASE_B_HANDOFF.md); [answers](../artifacts/answers_50q.json), [RAGAS](../artifacts/ragas_50q.json), [judge](../artifacts/judge_results.json), [báo cáo lỗi](reports/failure_clusters.md), [bias](reports/bias_report.md). |
| 2 | Đặng Quang Hưng | 2A20260271 | Phụ trách Phase C Tasks 9a–12, cấu hình Presidio/NeMo, adversarial suite, output guard và latency input layers; tổng hợp blueprint. Đã hoàn thành code Phase C, batch C thật, điền blueprint và đạt 100% tests/checks. | [phase_c_guard.py](../src/phase_c_guard.py); [test_phase_c.py](../tests/test_phase_c.py); [PHAN_CONG_TUAN_HUNG.md](../PHAN_CONG_TUAN_HUNG.md); [guard_results.json](../artifacts/guard_results.json); [blueprint.md](reports/blueprint.md). |

Người tích hợp/chạy batch/nộp link:

- **Tuấn:** phụ trách batch A/B, kiểm tra bản cuối, chốt commit và nộp một link repo chung. Batch A/B đã có kết quả; kiểm tra bản tích hợp cuối cùng.
- **Hưng:** phụ trách batch C, nhận kết quả A/B, viết blueprint và tích hợp để bàn giao Tuấn. Đã hoàn thành batch C thật ([guard_results.json](../artifacts/guard_results.json)), hoàn thiện [blueprint.md](reports/blueprint.md) và đạt toàn bộ kiểm tra bài nộp.

## Môi trường và chuẩn bị trước lớp

- **OS/Python/compiler:** môi trường cục bộ là Windows, kernel `10.0.26300`; `.venv` dùng CPython **3.11.9**, 64 bit AMD64, thông tin build Python `MSC v.1938`. Chưa xác minh phiên bản C++ Build Tools/compiler dùng để build dependencies; thông tin build Python không chứng minh compiler đã được cài trên máy.
- **Virtualenv/dependencies:** đã kiểm kê phiên bản bằng `importlib.metadata` qua `.\.venv\Scripts\python.exe`. Các package hiện có: `ragas 0.1.22`, `openai 1.109.1`, `qdrant-client 1.9.2`, `nemoguardrails 0.10.0`, `presidio-analyzer 2.2.364`, `presidio-anonymizer 2.2.364`, `spacy 3.8.16`, `en-core-web-lg 3.8.0`, `sentence-transformers 5.7.0`, `pytest 9.1.1`, `jsonschema 4.26.0`. Chưa có `.venv-tests` riêng tại thời điểm kiểm kê. Package đã cài không đồng nghĩa full runtime Presidio/NeMo đã chạy thành công; chưa có kết quả kiểm tra imports/batch C hoặc lỗi runtime C được ghi nhận.
- **Models/Qdrant:** [config.py](../config.py) cấu hình embedding `BAAI/bge-m3`, Qdrant `localhost:6333`, collections `lab24_production`/`lab24_naive`; [m3](../src/m3_rerank.py) dùng mặc định `BAAI/bge-reranker-v2-m3`. [Docker Compose](../infra/docker-compose.yml) pin `qdrant/qdrant:v1.9.7`. Đây là cấu hình; lần cập nhật báo cáo này chưa kiểm tra service đang chạy, indexing hay model cache.
- **50 answers:** [answers_50q.json](../artifacts/answers_50q.json) có đủ **20 factual / 20 multi_hop / 10 adversarial**. Cả 50 bản ghi có `generation_mode=extractive_fallback`, `generation_model=null`; answer, contexts và ground truth được lưu riêng. Theo bàn giao A, giữ bộ answers hiện có để tiết kiệm API và bảo toàn nguồn cho Phase B.
- **Evaluation A đã lưu:** [ragas_50q.json](../artifacts/ragas_50q.json) có metadata `format_version=2`, `run_kind=live`, thời điểm `2026-10-12T04:40:57.912003+00:00` (**11:40:57 ngày 12/10/2026 giờ Việt Nam**). Models theo vai trò: generation `[]`, evaluator `[gpt-4o-mini, text-embedding-3-small]`, judge `[]`, guard `[]`.
- **Evaluation B đã lưu:** [judge_results.json](../artifacts/judge_results.json) có `format_version=2`, `run_kind=live`, thời điểm `2026-10-12T05:10:25.773626+00:00` (**12:10:25 ngày 12/10/2026 giờ Việt Nam**). Models: generation/evaluator/guard `[]`, judge `[gpt-4o-mini]`. Đủ 5 cặp/10 lượt pairwise và 10 binary judgments; **κ=1.0**, position inconsistency **2/5 (40%)**, winner dài hơn **3/3 (100%)** trên decisive cases. Batch dùng đúng **20 requests**, **0 cache hits**, SDK retry tắt, 6.926 prompt tokens và 1.251 completion tokens.
- **Evaluation C đã lưu:** [guard_results.json](../artifacts/guard_results.json) có `format_version=2`, `run_kind=live`, thời điểm `2026-10-12T10:57:53.826320+00:00` (**17:57:53 ngày 12/10/2026 giờ Việt Nam**). Models: guard `[gpt-4o-mini]`. Attacks đạt **20/20 (100%)**, clean controls **8/8 (100%, false-positive rate 0.0)**, output cases **4/4 (100%)**. Latency input layers sequential (20 mẫu timed, 2 warm-up): Presidio P50/P95/P99 là 20.57 / 35.04 / 39.49 ms; NeMo input là 648.23 / 802.57 / 841.43 ms; tổng input guard là 677.68 / 831.73 / 870.50 ms; `latency_budget_ok: false`.
- **Giới hạn kết quả A:** có 50 per-question rows, bốn metrics/câu và 10 bottom rows. `avg_score` toàn bộ là **0.7728**; nhóm yếu nhất là **adversarial (0.7352)**; metric chủ đạo là **answer_relevancy**. Đây là đánh giá answers trích xuất, chưa đánh giá chất lượng generation tổng hợp bằng LLM.

## INDIVIDUAL

### NguyenAnhTuan-2A202602700

- **Phần được giao và phần thực tế đã làm:** phụ trách pipeline RAG, Phase A/B và kiểm tra/nộp bản cuối. Đã đưa m1–m5 vào repo, hoàn thiện Tasks 1–4 và adapter m4, lưu answers/RAGAS và viết báo cáo lỗi. Đã hoàn thiện `pairwise_judge`, `swap_and_average`, `cohen_kappa`, `bias_report` trong [phase_b_judge.py](../src/phase_b_judge.py), chạy batch B, viết báo cáo bias và bàn giao Hưng. Bổ sung client dùng chung, cache responses hợp lệ và giới hạn 20 request cho batch B; sửa lỗi encoding tiếng Việt trong báo cáo A bằng dữ liệu đã lưu.
- **Bằng chứng:** commit A `0ee7c1a74cd449f224f33fe74b6aa8a3398990b4`; [bàn giao A](PHASE_A_HANDOFF.md), [bàn giao B](PHASE_B_HANDOFF.md); [answers](../artifacts/answers_50q.json), [RAGAS](../artifacts/ragas_50q.json), [judge_results.json](../artifacts/judge_results.json); [failure_clusters.md](reports/failure_clusters.md), [bias_report.md](reports/bias_report.md). Commit triển khai B được ghi trong lịch sử Git của repo; SHA dùng để chấm sẽ được chốt khi nộp bản cuối.
- **Cách kiểm tra:** bộ **128 tests offline** A/B/m4/budget/support/contracts đạt, dùng mocks và chặn mạng/API. Lệnh: `python -m pytest tests/test_phase_a.py tests/test_m4_eval.py tests/test_phase_b.py tests/test_judge_budget.py tests/test_support.py tests/test_report_contracts.py -q --tb=short`. Batch B chạy một lần bằng `python scripts/run_experiments.py --phase b --live`: đủ 20 requests, 5 cặp/10 lượt và 10 nhãn binary. Validator schema/nguồn/phép tính/SHA-256 cho A/B đạt. Không chạy lại API A khi sửa văn bản báo cáo.
- **Điều đã học — tổng hợp từ phần triển khai/bàn giao:** bốn metrics RAGAS đo các khía cạnh khác nhau; faithfulness cao chưa đảm bảo answer đúng trọng tâm hoặc retrieval đủ ý. Matrix worst-metric đếm mọi câu nên chọn nhóm yếu bằng mean, không dùng tổng 20/20/10. Phase B phân biệt A/B/tie với nhãn 0/1, quy cả winner và scores lượt swap về A/B gốc, và giữ nhãn người ngoài prompt. κ=1 trên 10 examples chưa chứng minh pairwise đáng tin: IDs 5/21 vẫn có reasoning sai hoặc bỏ sót ý quan trọng.
- **Giới hạn/cách xử lý:** answers A đều là fallback; nếu đổi answers phải cập nhật các báo cáo/hashes liên quan. Hai cặp đổi lựa chọn sau swap; winner dài hơn thắng 3/3 decisive cases nhưng chất lượng và độ dài bị trộn trên bộ mẫu nhỏ. Báo cáo bias phân tích nội dung, đề xuất đối chứng và cách kiểm tra thêm cho lần thực nghiệm được phê duyệt sau. Giữ nguyên prompt/dataset sau batch; không gọi thêm API để nâng điểm. Báo cáo A đã sửa UTF-8, giữ nguyên số đo.
- **Nguồn/AI hỗ trợ:** starter và hướng dẫn trong repo; m1–m5 từ bài RAG trước. Codex hỗ trợ triển khai Tasks 1–8, adapter/runner/cache, viết tests, chạy batch theo yêu cầu và tổng hợp reports/TEAM từ JSON, Git và kết quả kiểm tra. Bằng chứng API là artifacts thật, tests logic dùng mocks riêng; Tuấn rà soát nội dung, hiểu logic và hoàn thiện kê khai nguồn bài RAG trước nếu còn thiếu.

### DangQuangHung-2A20260271

- **Phần được giao và phần thực tế đã làm:** phụ trách Phase C: Tasks 9a–12 gồm phát hiện/ẩn PII tiếng Việt (CCCD 12 số, CMND 9 số, SĐT VN, email) bằng Presidio (`pii_scan`), kiểm tra input rail (`check_input_rail`), adversarial test suite 28 câu (`run_adversarial_suite`), kiểm tra output rail (`check_output_rail`), và đo latency tuần tự P95 với warm-up thật (`measure_p95_latency`) trong [phase_c_guard.py](../src/phase_c_guard.py). Đã chạy batch thật tạo [guard_results.json](../artifacts/guard_results.json), đạt 20/20 attacks và 8/8 clean allowed (0 false positive), 4/4 output cases, hoàn thiện báo cáo [blueprint.md](reports/blueprint.md) và kiểm tra bài nộp.
- **Bằng chứng:** file mã nguồn [src/phase_c_guard.py](../src/phase_c_guard.py); bộ 12 unit tests đạt trong [tests/test_phase_c.py](../tests/test_phase_c.py); kết quả batch thật [artifacts/guard_results.json](../artifacts/guard_results.json); báo cáo kiến trúc và CI gates [doc/reports/blueprint.md](reports/blueprint.md); phân công nhiệm vụ tại [PHAN_CONG_TUAN_HUNG.md](../PHAN_CONG_TUAN_HUNG.md).
- **Cách kiểm tra:** chạy toàn bộ unit tests offline: `.\.venv\Scripts\python.exe -m pytest tests/test_phase_c.py -v` (12/12 passed in 0.10s); chạy toàn bộ test suite offline `pytest tests/` (140/140 passed); chạy batch thực nghiệm live: `.\.venv\Scripts\python.exe scripts/run_experiments.py --phase c --live --latency-samples 20`; kiểm tra bài nộp toàn diện không còn lỗi: `.\.venv\Scripts\python.exe scripts/check_lab.py --with-tests` (0 failed checks).
- **Điều đã học:** hiểu rõ cơ chế bảo vệ nhiều tầng (Defense-in-Depth): Presidio xử lý PII bằng regex/NER cực nhanh ở tầng trước; NeMo Guardrails kiểm soát hội thoại bằng LLM input/output rails; nguyên tắc không suy đoán chặn từ chuỗi trả về mà đọc đúng trạng thái rail stop; phương pháp đo latency tuần tự độc lập có warm-up thật để phản ánh đúng overhead thực tế; nhận diện rõ bottleneck latency nằm ở roundtrip LLM của input rail thay vì regex PII.
- **Giới hạn/cách xử lý:** đo latency hiện tại nằm trong phạm vi `input_layers_sequential`, chưa bao gồm RAG và NeMo output rail. Độ trễ P95 đạt 831.73 ms vượt mục tiêu 500 ms; đã ghi nhận trung thực số đo và đề xuất cơ chế short-circuit khi bắt PII cùng semantic caching cho input rail trong blueprint để tối ưu cho production.
- **Nguồn/AI hỗ trợ nếu có:** tài liệu đề bài và hướng dẫn repo, NeMo Guardrails doc, thư viện Microsoft Presidio; Antigravity hỗ trợ rà soát logic hàm, triển khai code, chạy thực nghiệm batch C và tổng hợp blueprint.

## Trạng thái hoàn thiện bài nộp

Ngày 12/10/2026, toàn bộ ba Phase A, B, C đã có đầy đủ mã nguồn, artifacts kết quả thực nghiệm thật và báo cáo phân tích. Validator xác nhận toàn bộ schema, nguồn dữ liệu, mã băm SHA-256 của 4 artifacts JSON và 3 reports Markdown.

- Phase A: Đầy đủ mã nguồn m1–m5, Tasks 1–4, 50 answers trong `answers_50q.json`, kết quả RAGAS trong `ragas_50q.json` và báo cáo lỗi `failure_clusters.md`.
- Phase B: Hoàn thành Tasks 5–8, kết quả pairwise và binary trong `judge_results.json`, báo cáo bias `bias_report.md` và biên bản bàn giao `PHASE_B_HANDOFF.md`.
- Phase C: Hoàn thành Tasks 9a–12, kết quả thực nghiệm live trong `guard_results.json` (20/20 attacks, 8/8 clean allowed, 4/4 output cases, 20 samples latency), và báo cáo kiến trúc CI/CD `blueprint.md`.
- Kiểm tra toàn diện bằng `.\.venv\Scripts\python.exe scripts/check_lab.py --with-tests` đạt **0 failed checks (100% PASS)** và **140/140 unit tests pass**.
- Tuấn rà soát bản cuối, kiểm tra bảo mật không commit `.env`, chốt commit nộp bài và gửi link repository chung theo thông báo lớp.

## Cập nhật sau khi nộp

Không có cập nhật sau khi nộp.