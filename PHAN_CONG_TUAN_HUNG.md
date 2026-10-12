# Phân công bài lab Eval + Guardrail — Tuấn & Hưng

Tuấn phụ trách Phase A/B và pipeline RAG. Hưng phụ trách Phase C, tích hợp kết quả và tổng hợp blueprint. Hai người dùng một repo chung, mỗi người có commit và bằng chứng đóng góp riêng.

Tài liệu này giao việc cần làm. Kết quả thực hiện, MSSV và bằng chứng commit được cập nhật vào [TEAM.md](TEAM.md) khi hoàn thành.

## 1. Phạm vi của Tuấn

- Kiểm tra giao diện năm module RAG `src/m1_chunking.py` đến `src/m5_enrichment.py` theo [PIPELINE_INTERFACE.md](PIPELINE_INTERFACE.md).
- Chuẩn bị Qdrant, embedding/reranker và sinh `artifacts/answers_50q.json` trước buổi học.
- Hoàn thiện Tasks 1–4 trong `src/phase_a_ragas.py`: nhóm câu hỏi, chạy RAGAS, lấy bottom 10 và phân tích nhóm lỗi.
- Hoàn thiện Tasks 5–8 trong `src/phase_b_judge.py`: pairwise judge, swap-and-average, Cohen’s κ và bias report.
- Chạy tests offline và batch thật A/B; viết `doc/reports/failure_clusters.md` và `doc/reports/bias_report.md`.
- Bàn giao kết quả A/B và nhận xét cho Hưng để đưa vào blueprint.
- Kiểm tra bản tích hợp, chốt commit và gửi link repo chung theo thông báo lớp.

Đầu ra Tuấn bàn giao:

- `artifacts/answers_50q.json`.
- `artifacts/ragas_50q.json`.
- `artifacts/judge_results.json`.
- `doc/reports/failure_clusters.md`.
- `doc/reports/bias_report.md`.
- Mục `INDIVIDUAL` của Tuấn trong `doc/TEAM.md`.

## 2. Job của Hưng — Phase C

File chính: [src/phase_c_guard.py](../src/phase_c_guard.py). Cấu hình liên quan nằm trong `guardrails/config.yml` và `guardrails/rails.co`.

Đọc [ASSIGNMENT.md](ASSIGNMENT.md), [ENVIRONMENT.md](ENVIRONMENT.md) và [REPORT_SCHEMAS.md](REPORT_SCHEMAS.md) trước khi triển khai. Giữ giao diện hàm và định dạng đầu ra mà runner/tests đang dùng.

### C0. Chuẩn bị môi trường Guardrails trước lớp

- [x] Chuẩn bị Python 3.11 và dependencies theo constraints của repo.
- [x] Kiểm tra Presidio, spaCy/model và NeMo Guardrails trên môi trường sẽ chạy batch thật.
- [x] Kiểm tra cấu hình guard và API key trong môi trường cục bộ.
- [x] Ghi phiên bản, kết quả kiểm tra và lỗi cài đặt thực tế vào TEAM.

Môi trường unit test có thể dùng `.venv-tests`; môi trường chạy thật dùng `.venv` theo hướng dẫn repo. Tests mock pass chưa đủ để xác nhận full runtime đã chạy được.

### C1. Task 9a — Phát hiện và ẩn PII

Hàm: `pii_scan(text, analyzer=None, anonymizer=None)`.

- [x] Sử dụng Presidio analyzer/anonymizer; tái sử dụng engines được truyền vào.
- [x] Phát hiện CCCD/CMND, số điện thoại Việt Nam và email.
- [x] Trả đủ `has_pii`, `entities`, `anonymized`.
- [x] Mỗi entity có `type`, `text`, `score`, `start`, `end` đúng vị trí trong input.
- [x] Ẩn PII trong `anonymized`; giữ nguyên văn bản nếu không có PII.

### C2. Task 9b — Kiểm tra input bằng NeMo

Hàm async: `check_input_rail(text, rails=None)`.

- [x] Chạy input rail và bật logging các rail được kích hoạt.
- [x] Trả đủ `allowed`, `blocked_reason`, `response`.
- [x] Xác định chặn từ quyết định rail; không suy ra từ các từ “xin lỗi”, “không thể” trong response.
- [x] Cho phép các câu hỏi chính sách hợp lệ trong bộ clean controls.

### C3. Task 10 — Chạy attacks và clean controls

Hàm: `run_adversarial_suite(adversarial_set, rails=None, analyzer=None, anonymizer=None)`.

- [x] Nhận danh sách inputs bất kỳ; runner sẽ truyền chung 20 attacks và 8 clean controls.
- [x] Giữ nguyên `id`, `category`, `input`, `expected` của mỗi bản ghi.
- [x] Chạy các lớp guard để xác định `actual` và `blocked_by`.
- [x] Chỉ dùng `expected` để đối chiếu `passed`, không dùng nó để quyết định chặn.
- [x] Trả đủ các rows, gồm `actual`, `blocked_by`, `passed`.
- [x] Đạt tối thiểu 15/20 attacks và 8/8 clean được allowed; tính rõ false-positive rate.

Bonus Phase C: đạt ít nhất 18/20 attacks và vẫn giữ 8/8 clean được allowed. Không sửa fixtures để đạt ngưỡng.

### C4. Task 11 — Kiểm tra output

Hàm async: `check_output_rail(question, answer, rails=None)`.

- [x] Kiểm tra answer đã có bằng output rail, với context question/answer.
- [x] Trả đủ `safe`, `final_answer`, `flagged_reason`.
- [x] Giữ nguyên answer sạch; thay bằng phản hồi an toàn hoặc redact answer nhạy cảm.
- [x] Kiểm tra đủ 4 cases trong `fixtures/output_set_4.json`: 2 sạch và 2 nhạy cảm.

### C5. Task 12 — Đo latency

Hàm: `measure_p95_latency(test_inputs, n_runs=20, rails=None, analyzer=None, anonymizer=None)`.

- [x] Khởi tạo engines trước khi đo và tái sử dụng trong các lượt chạy.
- [x] Thực hiện 2 lượt warm-up thật cho cả Presidio và NeMo input; loại chúng khỏi samples.
- [x] Thu ít nhất 20 timed samples bằng `time.perf_counter()`.
- [x] Mỗi mẫu luôn chạy Presidio rồi NeMo input, kể cả khi Presidio phát hiện PII.
- [x] Lưu `presidio_ms`, `nemo_input_ms`, `input_guard_ms` của từng mẫu; tổng bằng tổng hai lớp trong mẫu đó.
- [x] Dùng helper `summarize_latency()` được cung cấp để tính percentile nội suy tuyến tính.
- [x] Ghi scope `input_layers_sequential`; báo cáo số thực tế kể cả khi vượt mục tiêu 500 ms.

Phép đo này chỉ bao gồm hai lớp input. RAG, output rail và full guard chưa đo thì ghi rõ “chưa đo” trong blueprint.

## 3. Hưng chạy kiểm tra và tạo bằng chứng

Chạy các lệnh từ gốc repo, bằng Python của virtualenv tương ứng. Các lệnh dưới đây là hướng dẫn thực hiện, chưa phải bằng chứng đã chạy.

Kiểm tra logic Phase C bằng tests offline:

```powershell
.\.venv-tests\Scripts\python.exe -m pytest tests/test_phase_c.py -q
```

Sau khi tests đạt và full runtime sẵn sàng, chạy một batch thật để tạo `artifacts/guard_results.json`. Lệnh `--live` dùng API/mạng và có chi phí:

```powershell
.\.venv\Scripts\python.exe scripts/run_experiments.py --phase c --live --latency-samples 20
```

Đọc JSON sau khi chạy và kiểm tra đủ 20 attacks, 8 clean controls, 4 output cases, 2 warm-up, ít nhất 20 latency samples và metadata model thực tế. Không chạy lại live integration nếu batch đã tạo đủ bằng chứng; chỉ chạy lại khi có thay đổi hoặc lỗi cần kiểm chứng.

## 4. Hưng tổng hợp blueprint và tích hợp

File báo cáo: [doc/reports/blueprint.md](reports/blueprint.md).

- [ ] Viết kiến trúc `Input → Presidio → NeMo input → RAG → NeMo output → response` và cách xử lý khi từng lớp chặn/lỗi.
- [ ] Điền số đo latency và phân tích bottleneck từ `guard_results.json`.
- [ ] Nhận số liệu RAGAS, nhóm lỗi, κ/bias và model IDs theo vai trò từ Tuấn.
- [ ] Đề xuất CI gates, monitoring và cải tiến dựa trên bằng chứng A/B/C.
- [ ] Phân biệt ngưỡng lab 15/20 với ngưỡng bonus/CI đề xuất 18/20; cả hai cần clean 8/8.
- [ ] Ghi rõ CI/CD là đề xuất nếu chưa triển khai workflow thực tế.
- [ ] Hoàn thiện mục `INDIVIDUAL` của Hưng trong TEAM; Tuấn tự điền phần của Tuấn.
- [ ] Kiểm tra đủ bốn JSON và ba báo cáo Markdown, rồi chạy checker cuối bài.

Checker mặc định chỉ đọc files, không gọi API và không chạy lại pytest:

```powershell
.\.venv-tests\Scripts\python.exe scripts/check_lab.py
```

Nếu muốn gộp kiểm tra bài nộp và toàn bộ unit tests vào một lần, dùng `--with-tests`. Không cần chạy lại toàn bộ tests nếu đã kiểm tra đủ và không có thay đổi mới.

## 5. Mốc phối hợp đề xuất

Chuẩn bị môi trường, model, indexing và 50 answers trước buổi học. Dùng 15 phút đầu buổi để xác nhận sẵn sàng và thống nhất phân công.

1. **0–30 phút thực hành:** Tuấn hoàn thiện/chạy A; Hưng triển khai các hàm guard. Cuối mốc này Tuấn bàn giao kết quả A và phân tích lỗi.
2. **30–60 phút:** Tuấn hoàn thiện/chạy B; Hưng hoàn thiện Phase C và tests offline. Cuối mốc này Tuấn bàn giao kết quả B và thông tin cần cho blueprint.
3. **60–90 phút:** Hưng chạy batch C, tổng hợp blueprint và tích hợp; Tuấn hỗ trợ xử lý lỗi, kiểm tra báo cáo và rà soát bài nộp.

Khi nhận yêu cầu checkpoint trực tiếp từ giảng viên, hai người phối hợp để đạt checkpoint của phase tương ứng.

## 6. Quy ước làm chung

- Branch gợi ý: Tuấn dùng `tuan/eval-ab`, Hưng dùng `hung/guard-c`.
- Tuấn sở hữu `phase_a_ragas.py`, `phase_b_judge.py`, m1–m5 và hai báo cáo A/B. Hưng sở hữu `phase_c_guard.py`, cấu hình guard và blueprint.
- Các file chung như `config.py`, dependencies, scripts, schemas và TEAM: báo cho nhau trước khi cùng sửa; giữ giao diện starter.
- Hưng chủ động phát triển/tests offline Phase C trong khi Tuấn làm A/B. Kết quả A/B được dùng khi viết blueprint tổng hợp.
- Mỗi người commit code, kết quả chạy thật và báo cáo thuộc phần mình sau khi kiểm tra secrets. Không commit API key, `.env`, virtualenv hoặc cache model.
- Tuấn kiểm tra bản cuối và nộp link repo chung. Hạn nộp theo thông báo lớp; mặc định đề bài là 23:59 ngày lab, giờ Việt Nam.
- Theo hướng dẫn workspace: không chạy tests trên database `pitaya_panel`, `pitaya_app`; không gửi request generate Wapro faktura đến IP thật.

## 7. Checklist Hưng bàn giao cho Tuấn

- [x] Tasks 9a, 9b, 10, 11, 12 đã implement; không còn TODO trong `src/phase_c_guard.py`.
- [x] Tests offline Phase C đạt; có lệnh/kết quả kiểm tra để đối chiếu (`pytest tests/test_phase_c.py -v` đạt 12/12 passed).
- [x] `artifacts/guard_results.json` là kết quả batch thật, đúng schema và nguồn dữ liệu (đã chạy batch live hoàn tất).
- [x] Hưng đạt 20/20 trong [batch riêng](artifacts/guard_results_hung.json); bản tích hợp với input prompt hiện tại đạt 19/20, clean allowed 8/8, FPR=0, đủ mốc bắt buộc/bonus. Còn attack #16 được kê khai trong blueprint.
- [x] Đủ 4 output cases và 20 latency samples sau 2 warm-up thật.
- [x] `doc/reports/blueprint.md` được điền từ kết quả thật, có giới hạn và cải tiến cụ thể từ A/B/C.
- [x] TEAM có thông tin và mục INDIVIDUAL của Hưng cùng bằng chứng commit.
- [x] Checker bài nộp đạt sau khi ghép kết quả A/B/C; bản bàn giao Hưng đạt 140 tests, bản tích hợp Tuấn bổ sung regressions đạt 145 tests offline và 0 failed checks.

Đối chiếu cuối cùng với [RUBRIC.md](RUBRIC.md), [CHECKPOINTS.md](CHECKPOINTS.md) và [SUBMISSION.md](SUBMISSION.md).
