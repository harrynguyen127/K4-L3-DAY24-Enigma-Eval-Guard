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
| 1 | Nguyễn Anh Tuấn | 2A202602700 | Phụ trách pipeline RAG m1–m5, Phase A/B, báo cáo lỗi và bias; kiểm tra bản tích hợp và nộp link. Đã bàn giao Phase A Tasks 1–4 và 50 answers; Phase B Tasks 5–8 còn TODO. | Commit `0ee7c1a74cd449f224f33fe74b6aa8a3398990b4`; [bàn giao A](PHASE_A_HANDOFF.md); [answers](../artifacts/answers_50q.json), [RAGAS](../artifacts/ragas_50q.json), [báo cáo lỗi](reports/failure_clusters.md). |
| 2 | Đặng Quang Hưng | 2A20260271 | Phụ trách Phase C Tasks 9a–12, cấu hình Presidio/NeMo, adversarial suite, output guard và latency input layers; tổng hợp blueprint. Đã hoàn thành code Phase C và đạt 12/12 unit tests offline. | [phase_c_guard.py](../src/phase_c_guard.py); [test_phase_c.py](../tests/test_phase_c.py); [PHAN_CONG_TUAN_HUNG.md](../PHAN_CONG_TUAN_HUNG.md). |

Người tích hợp/chạy batch/nộp link:

- **Tuấn:** phụ trách batch A/B, kiểm tra bản cuối, chốt commit và nộp một link repo chung. Batch A đã có kết quả; batch B và việc nộp link chưa có bằng chứng.
- **Hưng:** phụ trách batch C, nhận kết quả A/B, viết blueprint và tích hợp để bàn giao Tuấn. Đã có tài liệu bàn giao A để sử dụng; chưa có kết quả batch C hoặc commit tích hợp cuối.

## Môi trường và chuẩn bị trước lớp

- **OS/Python/compiler:** môi trường cục bộ là Windows, kernel `10.0.26300`; `.venv` dùng CPython **3.11.9**, 64 bit AMD64, thông tin build Python `MSC v.1938`. Chưa xác minh phiên bản C++ Build Tools/compiler dùng để build dependencies; thông tin build Python không chứng minh compiler đã được cài trên máy.
- **Virtualenv/dependencies:** đã kiểm kê phiên bản bằng `importlib.metadata` qua `.\.venv\Scripts\python.exe`. Các package hiện có: `ragas 0.1.22`, `openai 1.109.1`, `qdrant-client 1.9.2`, `nemoguardrails 0.10.0`, `presidio-analyzer 2.2.364`, `presidio-anonymizer 2.2.364`, `spacy 3.8.16`, `en-core-web-lg 3.8.0`, `sentence-transformers 5.7.0`, `pytest 9.1.1`, `jsonschema 4.26.0`. Chưa có `.venv-tests` riêng tại thời điểm kiểm kê. Package đã cài không đồng nghĩa full runtime Presidio/NeMo đã chạy thành công; chưa có kết quả kiểm tra imports/batch C hoặc lỗi runtime C được ghi nhận.
- **Models/Qdrant:** [config.py](../config.py) cấu hình embedding `BAAI/bge-m3`, Qdrant `localhost:6333`, collections `lab24_production`/`lab24_naive`; [m3](../src/m3_rerank.py) dùng mặc định `BAAI/bge-reranker-v2-m3`. [Docker Compose](../infra/docker-compose.yml) pin `qdrant/qdrant:v1.9.7`. Đây là cấu hình; lần cập nhật báo cáo này chưa kiểm tra service đang chạy, indexing hay model cache.
- **50 answers:** [answers_50q.json](../artifacts/answers_50q.json) có đủ **20 factual / 20 multi_hop / 10 adversarial**. Cả 50 bản ghi có `generation_mode=extractive_fallback`, `generation_model=null`; answer, contexts và ground truth được lưu riêng. Theo bàn giao A, giữ bộ answers hiện có để tiết kiệm API và bảo toàn nguồn cho Phase B.
- **Evaluation đã lưu:** [ragas_50q.json](../artifacts/ragas_50q.json) có metadata `format_version=2`, `run_kind=live`, thời điểm `2026-10-12T04:40:57.912003+00:00` (**11:40:57 ngày 12/10/2026 giờ Việt Nam**). Models theo vai trò: generation `[]`, evaluator `[gpt-4o-mini, text-embedding-3-small]`, judge `[]`, guard `[]`. `gpt-4o-mini` trong cấu hình judge/guard chưa phải bằng chứng hai phase này đã chạy.
- **Giới hạn kết quả A:** có 50 per-question rows, bốn metrics/câu và 10 bottom rows. `avg_score` toàn bộ là **0.7728**; nhóm yếu nhất là **adversarial (0.7352)**; metric chủ đạo là **answer_relevancy**. Đây là đánh giá answers trích xuất, chưa đánh giá chất lượng generation tổng hợp bằng LLM.

## INDIVIDUAL

### NguyenAnhTuan-2A202602700

- **Phần được giao và phần thực tế đã làm:** phụ trách pipeline RAG, Phase A/B và kiểm tra/nộp bản cuối. Theo bàn giao A và commit hiện có, đã đưa m1–m5 vào repo, hoàn thiện `group_by_distribution`, `run_ragas_50q`, `bottom_10`, `cluster_analysis` trong [phase_a_ragas.py](../src/phase_a_ragas.py), adapter [m4_eval.py](../src/m4_eval.py), lưu answers/RAGAS và viết báo cáo lỗi. Mục đích là đánh giá đúng 50 câu, giữ nguồn/model evaluator và xác định nhóm cần cải thiện. Phase B Tasks 5–8, batch B và báo cáo bias chưa hoàn thành trong repo.
- **Bằng chứng:** commit `0ee7c1a74cd449f224f33fe74b6aa8a3398990b4`; [PHASE_A_HANDOFF.md](PHASE_A_HANDOFF.md); [answers_50q.json](../artifacts/answers_50q.json); [ragas_50q.json](../artifacts/ragas_50q.json); [failure_clusters.md](reports/failure_clusters.md). Chưa có `artifacts/judge_results.json`; [bias_report.md](reports/bias_report.md) còn placeholder.
- **Cách kiểm tra:** tài liệu bàn giao ghi bộ **97 tests offline** cho Phase A/m4/support/contracts, dùng mocks và chặn mạng/API, với lệnh `python -m pytest tests/test_phase_a.py tests/test_m4_eval.py tests/test_support.py tests/test_report_contracts.py -q --tb=short`. Báo cáo lỗi ghi bộ này đã đạt; lần cập nhật TEAM không chạy lại pytest. Batch A đã được lưu với lệnh được bàn giao `python scripts/run_experiments.py --phase a --live`; đối chiếu schema, nguồn và SHA-256 bằng checker offline, không cần chạy lại API.
- **Điều đã học — tổng hợp từ phần triển khai/bàn giao:** bốn metrics RAGAS đo các khía cạnh khác nhau; faithfulness cao chưa đảm bảo answer đúng trọng tâm hoặc retrieval đủ ý. Matrix worst-metric đếm mọi câu, nên chọn nhóm yếu bằng mean `avg_score`, không dùng tổng số câu 20/20/10. Model evaluator phải lấy từ m4, tách khỏi generation/judge/guard. Với Phase B sắp làm, cần phân biệt winner A/B/tie và nhãn chất lượng 0/1, quy kết quả lượt swap về A/B gốc và không đưa nhãn người vào prompt.
- **Giới hạn/cách xử lý:** bộ answers đang dùng fallback; cần đọc question/answer/contexts/reference trước khi kết luận nguyên nhân và thử cải tiến prompt, chunking/retrieval hoặc lọc phiên bản policy. Nếu đổi answers phải cập nhật lại các báo cáo và hashes liên quan. Hoàn thiện Phase B với cặp IDs 1, 5, 12, 21, 41, 10 nhãn judge trên đúng `model_answer` nguồn, κ và phân tích bias trước khi bàn giao Hưng. Báo cáo lỗi hiện có nhiều ký tự tiếng Việt bị thay bằng `?`; cần sửa văn bản trước bản nộp cuối.
- **Nguồn/AI hỗ trợ:** starter và hướng dẫn trong repo; m1–m5 được bàn giao từ bài RAG trước, cần bổ sung nguồn tác giả/đồng tác giả nếu có. Codex hỗ trợ tổng hợp TEAM trong lần cập nhật này từ phân công, Git và artifacts, đối chiếu số liệu bằng đọc JSON và kiểm tra offline. Chưa có kê khai chi tiết AI hỗ trợ phần code/thực nghiệm trước đó; Tuấn bổ sung nếu đã sử dụng.

### DangQuangHung-2A20260271

- **Phần được giao và phần thực tế đã làm:** phụ trách Phase C: Tasks 9a–12 gồm phát hiện/ẩn PII tiếng Việt (CCCD 12 số, CMND 9 số, SĐT VN, email) bằng Presidio (`pii_scan`), kiểm tra input rail (`check_input_rail`), adversarial test suite 28 câu (`run_adversarial_suite`), kiểm tra output rail (`check_output_rail`), và đo latency tuần tự P95 với warm-up thật (`measure_p95_latency`) trong [phase_c_guard.py](../src/phase_c_guard.py). Đã triển khai hoàn chỉnh toàn bộ hàm học viên, loại bỏ hết TODO và tuân thủ đúng hợp đồng interface.
- **Bằng chứng:** file mã nguồn [src/phase_c_guard.py](../src/phase_c_guard.py); bộ 12 unit tests đạt trong [tests/test_phase_c.py](../tests/test_phase_c.py); phân công nhiệm vụ tại [PHAN_CONG_TUAN_HUNG.md](../PHAN_CONG_TUAN_HUNG.md).
- **Cách kiểm tra:** chạy toàn bộ unit tests offline: `.\.venv\Scripts\python.exe -m pytest tests/test_phase_c.py -v` (kết quả: 12 passed in 0.13s). Kiểm tra hoàn thiện code không còn TODO: `.\.venv\Scripts\python.exe scripts/check_lab.py` (PASS phase_c_guard.py và PASS doc/TEAM.md).
- **Điều đã học:** hiểu rõ cơ chế bảo vệ nhiều tầng (Defense-in-Depth): Presidio xử lý PII bằng regex/NER cực nhanh ở tầng trước; NeMo Guardrails kiểm soát hội thoại bằng LLM input/output rails; nguyên tắc không suy đoán chặn từ chuỗi trả về mà đọc đúng trạng thái rail stop; phương pháp đo latency tuần tự độc lập có warm-up thật để phản ánh đúng overhead thực tế.
- **Giới hạn/cách xử lý:** đo latency hiện tại nằm trong phạm vi `input_layers_sequential`, chưa bao gồm RAG và NeMo output rail. Khi chạy batch live cần có OPENAI_API_KEY hợp lệ để sinh `guard_results.json` và tổng hợp blueprint.
- **Nguồn/AI hỗ trợ nếu có:** tài liệu đề bài và hướng dẫn repo, NeMo Guardrails doc, thư viện Microsoft Presidio; Antigravity hỗ trợ rà soát logic hàm, triển khai code và kiểm thử unit tests.

## Trạng thái hoàn thiện bài nộp

Kết quả kiểm tra offline ngày 12/10/2026, **trước khi để trống mục INDIVIDUAL của Hưng**: chạy `.\.venv\Scripts\python.exe scripts/check_lab.py` không kèm `--with-tests`. **PASS** cho TEAM, answers và Phase A artifact (gồm schema, phép tính, nguồn và SHA-256). Lần kiểm tra đó có **6 checks chưa đạt**: `bias_report.md` và `blueprint.md` còn placeholder; `phase_b_judge.py` và `phase_c_guard.py` còn TODO; thiếu `judge_results.json` và `guard_results.json`. Checker trả mã thoát 1; đây không phải điểm rubric. Lần kiểm tra này không chạy pytest hoặc batch live. Mục INDIVIDUAL của Hưng hiện chờ Hưng tự điền trước khi nộp.

- Phase A đã có code và hai JSON bằng chứng; báo cáo lỗi cần sửa ký tự tiếng Việt bị hỏng trước khi nộp.
- Tuấn hoàn thiện Phase B, tạo `judge_results.json`, điền `bias_report.md` và bàn giao κ/bias cùng model IDs cho Hưng.
- Hưng hoàn thiện Phase C, tạo `guard_results.json`, điền blueprint từ A/B/C và bổ sung bằng chứng cá nhân.
- Khi đủ bốn JSON và ba báo cáo, kiểm tra bằng `.\.venv\Scripts\python.exe scripts/check_lab.py`; checker mặc định chỉ đọc files, không gọi API hoặc chạy pytest. Kết quả toàn bài chỉ được ghi đạt sau khi các checks thực sự pass.
- Tuấn kiểm tra secrets, chốt commit nộp và gửi một link repo chung theo thông báo lớp. Không commit `.env`, API keys, virtualenv hoặc model cache.

## Cập nhật sau khi nộp

Chưa có bằng chứng nộp link hoặc phiên bản nộp cuối trong repo; chưa ghi nhận cập nhật sau khi nộp. Khi nộp, Tuấn lưu commit SHA và thời điểm gửi. Nếu sửa sau deadline, ghi commit, thời điểm, lý do và quyết định của coach về việc áp dụng bản cập nhật theo [RULES.md](RULES.md).
