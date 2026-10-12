# Bàn giao Phase A — Tuấn → Hưng

## Phần đã triển khai

Tuấn phụ trách Tasks 1–4 trong `src/phase_a_ragas.py`:

- `group_by_distribution`: nhóm factual/multi_hop/adversarial, giữ nguyên dữ liệu từng câu.
- `run_ragas_50q`: gọi m4 trên 50 answers đúng phân bố 20/20/10; giữ nguồn answer/contexts/reference và model IDs evaluator. Báo lỗi khi thiếu câu, trùng ID, sai thứ tự nguồn hoặc điểm không hữu hạn/ngoài [0,1].
- `bottom_10`: xếp tăng dần avg_score, trả tối đa 10 câu cùng rank, worst_metric, diagnosis và suggested_fix.
- `cluster_analysis`: matrix worst_metric × distribution trên mọi câu; nhóm yếu được chọn theo mean thấp nhất, bỏ nhóm rỗng.

Các module m1–m5 được đưa vào repo để Hưng có đủ nguồn pipeline. `src/m4_eval.py` dùng riêng evaluator `gpt-4o-mini` và `text-embedding-3-small`, không lấy model judge để điền metadata.

## Dữ liệu và báo cáo

- [answers_50q.json](../artifacts/answers_50q.json): 50 answers đã lưu, phân bố 20 factual / 20 multi_hop / 10 adversarial. Toàn bộ ở chế độ `extractive_fallback`, `generation_model=null`; không sinh lại để tiết kiệm API theo yêu cầu của Tuấn.
- [ragas_50q.json](../artifacts/ragas_50q.json): kết quả đánh giá bốn metrics, bottom 10, matrix/means và metadata nguồn/model.
- [failure_clusters.md](reports/failure_clusters.md): số liệu, phân tích answer/contexts/reference, giới hạn của fallback và các cải tiến đề xuất.

Giữ bộ answers này khi làm Phase B để các cặp A/B dùng đúng nguồn và báo cáo A không bị stale. Nếu chủ động thay answers, phải đánh giá lại và cập nhật tất cả bằng chứng có liên quan.

## Kiểm tra offline

Chạy từ gốc repo bằng Python trong môi trường của mình:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_phase_a.py tests/test_m4_eval.py tests/test_support.py tests/test_report_contracts.py -q --tb=short
```

Bộ kiểm tra này có 97 tests, dùng mocks và chặn mạng/API. Tests Phase B/C thuộc phần chưa triển khai nên không dùng kết quả bộ này để kết luận toàn bài đã hoàn thành.

JSON được ghi LF và `.gitattributes` giữ LF khi clone để source SHA-256 không bị stale do chuyển CRLF/LF. Chuẩn hóa xuống dòng không thay đổi nội dung answers, fixtures hoặc số đo.

## Quy ước hạn chế API

- Dùng các artifacts đã bàn giao; Hưng không cần chạy lại setup hoặc batch A để bắt đầu Phase C.
- Evaluator giới hạn 2 workers, SDK `max_retries=0`, RAGAS `max_retries=1` (một lần thử), không bật CI reproducibility.
- Answer relevancy giữ chuẩn mặc định 3 câu hỏi sinh trong một completion request; số tác vụ metric không đồng nghĩa số HTTP requests.
- Không ép `response_format=json_object`: RAGAS 0.1.22 có những parser yêu cầu JSON dạng mảng.
- Responses LLM và embeddings được cache tại `artifacts/.phase_a_cache/`, được gitignore. Cache chứa responses thật và khóa theo prompt/model hoặc nội dung/model của embedding; không phải kết quả mock.
- Không commit API key, `.env`, virtualenv hoặc cache. Hưng tự cấu hình key cục bộ khi chạy phần của mình.
- Khi artifacts hiện có hợp lệ, không chạy `--phase all --live` hoặc live integration chỉ để kiểm tra lại file.

Nếu cần chạy A vì dữ liệu hoặc implementation thay đổi, lệnh của đề bài là:

```powershell
.\.venv\Scripts\python.exe scripts/run_experiments.py --phase a --live
```

Lệnh này dùng API trả phí. Kiểm tra JSON/báo cáo đã có bằng validator/checker offline trước khi quyết định chạy lại.

## Hưng tiếp tục phần nào

1. Hoàn thiện Tasks 9a–12 trong `src/phase_c_guard.py` và cấu hình guard theo phân công.
2. Chạy tests offline Phase C, rồi một batch C khi runtime sẵn sàng: 20 attacks, 8 clean controls, 4 output cases và ít nhất 20 latency samples sau 2 warm-up.
3. Dùng số liệu Phase A đã bàn giao để viết phần RAGAS/nhóm lỗi trong `doc/reports/blueprint.md`; bổ sung kết quả B khi Tuấn bàn giao.
4. Hai người điền MSSV, công việc thực tế, commit và INDIVIDUAL trong `doc/TEAM.md`.
5. Chạy `python scripts/check_lab.py` khi toàn bộ A/B/C và reports đã đủ. Checker toàn bài có thể fail vì B/C hoặc TEAM còn thiếu dù Phase A đã đạt.

Theo hướng dẫn workspace: không chạy tests trên database `pitaya_panel`, `pitaya_app`; không gửi request generate Wapro faktura đến IP thật.
