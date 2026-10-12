# Bàn giao Phase B — Nguyễn Anh Tuấn → Đặng Quang Hưng

Nhóm **Enigma**. Tuấn: **2A202602700**; Hưng: **2A20260271**.

## Kết quả bàn giao

Tasks 5–8 trong [phase_b_judge.py](../src/phase_b_judge.py) đã hoàn thành:

- `pairwise_judge`: accuracy/completeness/conciseness theo reference, JSON winner A/B/tie và scores hữu hạn [0,1].
- `swap_and_average`: hai lượt A/B và B/A, quy winner/scores lượt 2 về A/B gốc; bất đồng trả tie.
- `cohen_kappa`: tính từ nhãn binary, kiểm tra nhãn/độ dài, báo lỗi khi κ không xác định.
- `bias_report`: counts/rates position inconsistency và winner dài hơn trên các cặp decisive, có diễn giải giới hạn.

[judge_results.json](../artifacts/judge_results.json) có 5 cặp IDs 1, 5, 12, 21, 41 với đủ 10 lượt pairwise, cùng 10 binary judgments trên đúng `model_answer` được cấp. [bias_report.md](reports/bias_report.md) ghi đầy đủ candidates, scores/reasoning hai lượt, nhãn và phân tích.

Batch thật dùng `gpt-4o-mini`, **20 requests**, **0 cache hits**, client `max_retries=0`; usage ghi **6.926 prompt tokens** và **1.251 completion tokens**. Thời điểm JSON: `2026-10-12T05:10:25.773626+00:00` (12:10:25 giờ Việt Nam).

## Số liệu để đưa vào blueprint

- **Cohen’s κ = 1.0**, agreement 10/10, chance agreement 0.52.
- **Position inconsistency = 2/5 = 40%**: IDs 5, 21; final winner là tie.
- **Winner dài hơn = 3/3 = 100%** trong các cặp decisive: IDs 1, 12, 41.
- Metadata judge: `["gpt-4o-mini"]`; generation/evaluator/guard của báo cáo B là `[]`.

κ chỉ phản ánh 10 binary examples. Pairwise ở ID 5 đọc sai người phê duyệt, ID 21 bỏ sót phần lương của answer A; reasoning có thể sai dù label đúng. Tỷ lệ winner dài hơn chịu ảnh hưởng chất lượng hai nguồn và bộ mẫu nhỏ. Không diễn giải các số trên thành bảo đảm judge đúng cho toàn hệ thống.

## Cách kiểm tra mà không gọi API

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_phase_a.py tests/test_m4_eval.py tests/test_phase_b.py tests/test_judge_budget.py tests/test_support.py tests/test_report_contracts.py -q --tb=short
```

Bộ kiểm tra A/B/m4/budget/support/contracts có **128 tests**. Đã kiểm tra schema, nguồn, counts/rates, κ và SHA-256 cho kết quả B; bằng chứng A vẫn hợp lệ.

Sau khi ghép code C và mục INDIVIDUAL của Hưng từ commit `638ae0c`, toàn bộ `python -m pytest tests/ -q --tb=short` đạt **140 passed, 3 deselected**. Checker chỉ còn thiếu `guard_results.json` và blueprint. Không chạy API bổ sung khi tích hợp.

Cache B nằm tại `artifacts/.phase_b_cache/`, được gitignore; cache không phải phần bàn giao. Giữ nguyên answers/fixtures, dùng JSON hiện có cho blueprint và không chạy lại batch A/B chỉ để kiểm tra file.

## Hưng tiếp tục

1. Code Phase C Tasks 9a–12 đã được Hưng push trong commit `638ae0c`; dùng bản tích hợp này để chuẩn bị runtime và chạy batch C.
2. Chạy một batch C theo đề: 20 attacks, 8 clean controls, 4 output cases, ít nhất 20 latency samples sau 2 warm-up.
3. Điền blueprint từ kết quả A/B/C; nêu κ/bias cùng các giới hạn trên và metadata model theo vai trò.
4. Tự điền mục INDIVIDUAL của Hưng trong [TEAM.md](TEAM.md), giữ bằng chứng commit và số đo thật.
5. Khi đủ bài, chạy `python scripts/check_lab.py` để kiểm tra repo nộp. Artifact C và blueprint hiện còn thiếu; tests offline chưa thay thế batch thật.

Báo cáo lỗi A đã được sửa tiếng Việt bằng UTF-8 từ JSON có sẵn; không chạy lại RAGAS và không thay số đo.
