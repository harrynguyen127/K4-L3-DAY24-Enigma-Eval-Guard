# Đánh giá LLM Judge Phase B — Enigma

Người phụ trách: Nguyễn Anh Tuấn — 2A202602700.

Nguồn: [judge_results.json](../../artifacts/judge_results.json); [module B](../../src/phase_b_judge.py).

Run timestamp: `2026-10-12T05:10:25.773626+00:00`; giờ Việt Nam: 2026-10-12 12:10:25 (UTC+07:00).

## Phạm vi, prompt và số request

Model judge là `gpt-4o-mini`, temperature=0, response_format=json_object. Một client SDK được tái sử dụng, `max_retries=0`, timeout=60s. Prompt pairwise kiểm tra accuracy theo reference, đủ ý thiết yếu, phiên bản/phủ định/điều kiện; xem súc tích sau độ chính xác và đầy đủ. Answer/reference là dữ liệu, không phải chỉ dẫn. Prompt được giữ nguyên sau batch, không điều chỉnh theo nhãn người để tăng κ.

Nguồn A cố định từ `artifacts/answers_50q.json:answer` (extractive fallback, không có generation LLM); B từ `fixtures/human_labels_10q.json:model_answer`; reference từ `fixtures/test_set_50q.json:ground_truth`. Pairwise A/B/tie là lựa chọn tương đối giữa hai candidates; calibration 0/1 đánh giá một answer cụ thể. Hai loại kết quả không chuyển đổi cho nhau.

Batch có **20 API requests**, **0 cache hits**, budget **20**: 5 cặp × 2 lượt = 10 pairwise requests, cộng 10 binary requests. Usage SDK ghi **6926 prompt tokens**, **1251 completion tokens**. Đây là usage đo được, không phải hóa đơn billing.

Responses hợp lệ được cache theo model/prompt/payload trong `artifacts/.phase_b_cache/`, được gitignore. Lượt swap có key khác lượt gốc. Không chạy thêm batch hay live integration để lấy điểm đẹp hơn.

## Năm cặp A/B và hai lượt

IDs: 1, 5, 12, 21, 41. Winner và scores lượt 2 đã quy về A/B gốc. Reasoning lượt 2 giữ nguyên lời model, nên tên Answer A/B bên trong reasoning vẫn nói về thứ tự đã swap.

| ID | Winner 1 | Winner 2 quy đổi | Final | Consistent | Scores 1 A/B | Scores 2 A/B | Độ dài A/B (ký tự) |
|---:|---|---|---|---|---|---|---|
| 1 | A | A | A | True | 1.00/0.50 | 1.00/0.50 | 288/57 |
| 5 | B | A | tie | False | 0.00/1.00 | 1.00/0.00 | 274/33 |
| 12 | A | A | A | True | 1.00/0.50 | 1.00/0.50 | 264/50 |
| 21 | tie | A | tie | False | 1.00/1.00 | 1.00/0.70 | 256/82 |
| 41 | A | A | A | True | 1.00/0.00 | 1.00/0.00 | 274/37 |

### ID 1 — Nhân viên được nghỉ bao nhiêu ngày khi kết hôn?

**Candidate A:**

Trích từ nghi_phep_dac_biet.md.

## Các trường hợp được nghỉ phép đặc biệt Nhân viên được nghỉ có lương trong các trường hợp sau đây mà không trừ vào phép năm: - **Kết hôn**: 3 ngày làm việc - **Tang lễ** (cha mẹ, vợ/chồng, con): 3 ngày làm việc - **Sinh con** (nam giới): 5 ngày làm việc

**Candidate B:**

Nhân viên được nghỉ 3 ngày làm việc có lương khi kết hôn.

**Reasoning lượt 1:** Câu trả lời A cung cấp thông tin đầy đủ hơn, bao gồm cả ngữ cảnh về việc nghỉ phép đặc biệt và các trường hợp khác, trong khi câu B chỉ nêu thông tin về số ngày nghỉ khi kết hôn mà không có ngữ cảnh bổ sung.

**Reasoning lượt 2, thứ tự đã swap:** Answer B cung cấp thông tin đầy đủ hơn về chính sách nghỉ phép đặc biệt, bao gồm cả thông tin về việc không trừ vào phép năm, trong khi Answer A chỉ nêu rõ số ngày nghỉ mà không đề cập đến điều kiện này.

### ID 5 — Muốn mua thiết bị trị giá 55 triệu cần ai phê duyệt?

**Candidate A:**

Trích từ mua_sam.md.

## Thẩm quyền phê duyệt | Giá trị đơn hàng | Người phê duyệt | |-------------------|-----------------| | Dưới **5.000.000 VNĐ** | Trưởng phòng (Manager) | | Từ **5.000.000 - 50.000.000 VNĐ** | Giám đốc phòng ban (Director) | | Trên **50.000.000 VNĐ** |

**Candidate B:**

Cần Giám đốc phòng ban phê duyệt.

**Reasoning lượt 1:** Answer B cung cấp thông tin chính xác về người phê duyệt cho đơn hàng trị giá 55 triệu, trong khi Answer A không nêu rõ người phê duyệt cho mức giá này và có thông tin không chính xác.

**Reasoning lượt 2, thứ tự đã swap:** Answer B cung cấp thông tin chính xác về mức phê duyệt cần thiết cho đơn hàng trị giá 55 triệu, trong khi Answer A không đúng vì không đề cập đến Tổng Giám đốc mà chỉ nói về Giám đốc phòng ban.

### ID 12 — Thưởng Tết tối thiểu cho nhân viên chính thức có từ 6 tháng trở lên là bao nhiêu?

**Candidate A:**

Trích từ thuong_tet.md.

# Chính sách thưởng Tết
> Phiên bản: 2.0 | Ngày hiệu lực: 01/11/2024 | Phòng ban: Nhân sự & Tài chính ## Mức thưởng tối thiểu
Tất cả nhân viên chính thức có thời gian làm việc từ 6 tháng trở lên được thưởng Tết tối thiểu **1 tháng lương**.

**Candidate B:**

Nhân viên được thưởng Tết tối thiểu 1 tháng lương.

**Reasoning lượt 1:** Answer A cung cấp thông tin đầy đủ và chính xác về mức thưởng Tết tối thiểu cho nhân viên chính thức có từ 6 tháng trở lên, bao gồm cả nguồn gốc và phiên bản chính sách. Answer B tuy đúng nhưng thiếu thông tin về nguồn gốc và không nêu rõ phiên bản.

**Reasoning lượt 2, thứ tự đã swap:** Answer B cung cấp thông tin đầy đủ và chính xác về chính sách thưởng Tết, bao gồm cả phiên bản và ngày hiệu lực, trong khi Answer A chỉ nêu thông tin mà không có ngữ cảnh rõ ràng.

### ID 21 — Một nhân viên Senior có 9 năm thâm niên được nghỉ bao nhiêu ngày phép năm và lương trong khoảng nào?

**Candidate A:**

Trích từ nghi_phep_nam_v2024.md.

Ví dụ: nhân viên 9 năm thâm niên được 18 ngày phép (15 + 3). ## Quy định sử dụng
Phép năm phải được đăng ký trước ít nhất 2 ngày làm việc qua hệ thống HR Portal. Nghỉ phép từ 5 ngày trở lên cần được trưởng phòng phê duyệt.

**Candidate B:**

Được nghỉ 18 ngày phép (15 cơ bản + 3 thâm niên). Lương Senior từ 20 đến 35 triệu.

**Reasoning lượt 1:** Cả hai câu trả lời đều cung cấp thông tin chính xác về số ngày phép và khoảng lương cho nhân viên Senior. Tuy nhiên, answer_a có thêm thông tin về quy định sử dụng phép năm, trong khi answer_b ngắn gọn hơn. Do đó, không có câu trả lời nào rõ ràng tốt hơn câu còn lại.

**Reasoning lượt 2, thứ tự đã swap:** Answer B cung cấp thông tin đầy đủ hơn về quy định sử dụng ngày phép, bao gồm cả yêu cầu đăng ký và phê duyệt, trong khi Answer A chỉ nêu thông tin về số ngày phép và lương mà không có thêm chi tiết nào khác.

### ID 41 — Nhân viên được nghỉ bao nhiêu ngày phép năm?

**Candidate A:**

Trích từ nghi_phep_nam_v2024.md.

# Chính sách nghỉ phép năm (Phiên bản 2024)
> Phiên bản: 2.0 | Ngày hiệu lực: 01/01/2024 | Phòng ban: Nhân sự ## Số ngày phép năm
Mỗi nhân viên chính thức được hưởng **15 ngày phép năm** có lương, tăng từ 12 ngày so với chính sách năm 2023.

**Candidate B:**

Nhân viên được nghỉ 12 ngày phép năm.

**Reasoning lượt 1:** Answer A cung cấp thông tin chính xác về số ngày phép năm theo chính sách v2024, trong khi Answer B đưa ra thông tin không còn hiệu lực. Answer A cũng nêu rõ sự thay đổi từ chính sách năm 2023, làm cho câu trả lời đầy đủ hơn.

**Reasoning lượt 2, thứ tự đã swap:** Answer B cung cấp thông tin chính xác về số ngày phép năm theo chính sách v2024, là 15 ngày, và nêu rõ sự thay đổi từ 12 ngày của năm 2023. Trong khi đó, Answer A chỉ nêu số ngày phép của năm 2023, không phản ánh chính sách hiện hành.

## Position và verbosity: dấu hiệu cùng giới hạn

Position inconsistency: **2/5 = 40%**. Hai cặp không nhất quán là IDs 5 và 21; consensus trả tie. Thống kê đo đổi lựa chọn sau swap, chưa tự chứng minh nguyên nhân chỉ là vị trí.

ID 5: reference yêu cầu CEO cho đơn hàng trên 50 triệu. B nêu Giám đốc phòng ban, A là bảng bị cắt thiếu ô CEO. Lượt 1 vẫn gọi B chính xác và cho B=1; lượt 2 lại cho A=1 sau quy đổi. Cả hai lý do có khẳng định không được candidate/reference hỗ trợ. Swap phát hiện không ổn định nhưng không sửa được lỗi đọc nội dung.

ID 21: B có đủ 18 ngày phép và lương 20–35 triệu, A chỉ có phép năm và quy định sử dụng, thiếu lương. Lượt 1 nói cả hai đủ thông tin và trả tie; lượt 2 ưu tiên A vì chi tiết quy định sử dụng, dù chúng không bù phần lương đang thiếu. Đây là ví dụ judge nhận xét sai nội dung và có dấu hiệu ưu tiên chi tiết phụ.

Winner dài hơn: **100%** trên **3 cặp decisive**. A dài hơn thắng 3 cặp (IDs 1, 12, 41); không có B dài hơn thắng. Tie bị loại khỏi mẫu số; độ dài tính bằng số ký tự như hợp đồng validator.

ID 41 là trường hợp A đúng v2024 còn B dùng 12 ngày của v2023, nên độ chính xác và độ dài bị trộn với nhau. ID 1 có điều kiện không trừ phép năm hữu ích, nhưng reasoning còn khen thông tin về các trường hợp nghỉ khác. ID 12 khen nguồn/phiên bản/ngày hiệu lực thay vì chỉ xét mức thưởng và điều kiện hỏi. Không thể từ 3/3 kết luận mọi lựa chọn vì verbosity; cần bộ đối chứng giữ chất lượng tương đương và chỉ đổi độ dài.

## Calibration đúng model_answer

Chấm đúng question/model_answer có trong bộ nhãn người, reference ghép theo question_id. Prompt binary chỉ nhận question, answer, reference; không nhận human_label, human_note hoặc phân bố nhãn. Runner tạo đủ 10 judgments trước khi lấy nhãn người để tính agreement. Payload và nguồn đã được tests/validator đối chiếu.

| ID | Model answer gốc | Judge label | Human label | Agree | Reasoning |
|---:|---|---:|---:|---|---|
| 1 | Nhân viên được nghỉ 3 ngày làm việc có lương khi kết hôn. | 1 | 1 | True | Câu trả lời chính xác và đầy đủ theo thông tin trong reference, không thiếu ý thiết yếu. |
| 5 | Cần Giám đốc phòng ban phê duyệt. | 0 | 0 | True | Câu trả lời sai vì cần Tổng Giám đốc phê duyệt chứ không phải Giám đốc phòng ban. |
| 12 | Nhân viên được thưởng Tết tối thiểu 1 tháng lương. | 1 | 1 | True | Câu trả lời chính xác theo thông tin trong reference, nêu rõ điều kiện và mức thưởng cho nhân viên chính thức có từ 6 tháng trở lên. |
| 21 | Được nghỉ 18 ngày phép (15 cơ bản + 3 thâm niên). Lương Senior từ 20 đến 35 triệu. | 1 | 1 | True | Câu trả lời chính xác theo reference, nêu rõ số ngày phép và khoảng lương cho nhân viên Senior với 9 năm thâm niên. |
| 23 | Hoàn trả 25 triệu vì chưa đủ 1 năm cam kết. | 1 | 1 | True | Câu trả lời chính xác theo reference, nêu rõ số tiền phải hoàn trả và lý do nghỉ việc trước hạn cam kết. |
| 29 | Trưởng phòng phê duyệt. Phạt 2% tháng trên 8 triệu. | 0 | 0 | True | Câu trả lời thiếu thông tin về sự cần thiết có sự phê duyệt của Kế toán trưởng bên cạnh Trưởng phòng. Ngoài ra, phí phạt được tính cho quá hạn 15 ngày, không phải là 2% trên tổng số tiền tạm ứng. |
| 33 | Phép: 19 ngày. Phụ cấp: 1.500.000 VNĐ/tháng. | 1 | 1 | True | Câu trả lời cung cấp đúng số ngày phép và tổng phụ cấp hàng tháng theo thông tin trong reference. |
| 41 | Nhân viên được nghỉ 12 ngày phép năm. | 0 | 0 | True | Câu trả lời sai vì nó dựa trên chính sách cũ (v2023) thay vì chính sách hiện hành (v2024) là 15 ngày phép năm. |
| 46 | Nhân viên thử việc không được nghỉ phép năm và phải xin nghỉ không lương nếu cần. | 1 | 1 | True | Câu trả lời chính xác theo reference, nêu rõ rằng nhân viên thử việc không được nghỉ phép năm và phải xin nghỉ không lương nếu cần, đồng thời không bỏ qua điều kiện cần có sự phê duyệt của trưởng phòng. |
| 50 | Được, miễn là đảm bảo kết nối an toàn. | 0 | 0 | True | Câu trả lời sai vì cho phép sử dụng VPN cá nhân, trong khi reference rõ ràng cấm điều này. |

Observed agreement p_o = **1.00** (10/10). Cả judge và human có 6 nhãn 1, 4 nhãn 0; phân bố này chỉ dùng khi đối chiếu sau judge. Chance agreement p_e = 0.6×0.6 + 0.4×0.4 = **0.52**.

Cohen’s κ = (p_o − p_e)/(1 − p_e) = (1 − 0.52)/(1 − 0.52) = **1.00**. Không có case lệch nhãn trong 10 calibration examples; ngưỡng bonus κ>0.6 được đáp ứng trên đúng answers nguồn.

## Độ tin cậy và cải tiến đề xuất

κ=1 trên 10 examples không chứng minh judge chính xác cho mọi câu hoặc cho pairwise. ID 5 được binary chấm đúng là 0 nhưng pairwise từng cho B=1; ID 21 binary nhận ra answer B đủ ý nhưng pairwise nói answer A cũng có lương. Giữ riêng hai quy trình và đọc reasoning thay vì chỉ nhìn κ.

Reasoning binary ở IDs 12/46 có diễn đạt rằng answer đã nêu điều kiện mà thực tế chỉ question/reference chứa. ID 29 label=0 đúng nhưng câu giải thích phí phạt chưa thật rõ. Nhãn đúng không bảo đảm mọi câu trong reasoning đúng; người học cần kiểm tra cả hai.

Bộ mẫu chỉ có 5 cặp và 10 nhãn; A đều là fallback, chất lượng và độ dài hai nguồn không được cân bằng. Chưa đo tính ổn định qua seed/lượt khác hoặc khái quát sang corpus khác. Temperature=0 không phải chứng minh tính quyết định tuyệt đối.

Cải tiến cho lần thử nghiệm được phê duyệt sau: yêu cầu judge liệt kê các ý thiết yếu và trích đoạn candidate hỗ trợ trước khi cho điểm; kiểm tra thiếu nhánh multi-hop và dùng sai người phê duyệt; tạo đối chứng chất lượng tương đương nhưng khác độ dài/thứ tự. Chưa áp dụng các đề xuất này và chưa gọi thêm API sau batch 20 request.

## Kiểm chứng và bàn giao

128 tests offline A/B/m4/budget/support/contracts đạt; kiểm tra scores/JSON, swap và reference hai lượt, κ undefined/nhãn sai, tỷ lệ verbosity, cache và request cap. Unit tests chặn mạng/API.

Batch B thật hoàn thành đủ 5 cặp/10 lượt và 10 binary judgments. JSON Schema, nguồn A/B/reference, thứ tự nhãn, κ, counts/rates và SHA-256 nguồn được validator kiểm tra đạt. Giữ nguyên answers/fixtures và kết quả A; Hưng dùng κ/bias/metadata judge này cho blueprint.

Lệnh tests: `python -m pytest tests/test_phase_a.py tests/test_m4_eval.py tests/test_phase_b.py tests/test_judge_budget.py tests/test_support.py tests/test_report_contracts.py -q --tb=short`.

Lệnh thực nghiệm đã chạy một lần: `python scripts/run_experiments.py --phase b --live`.

Sau khi tích hợp commit Phase C của Hưng `638ae0c`, toàn bộ tests offline đạt **140 passed, 3 deselected** với `python -m pytest tests/ -q --tb=short`. Các integration tests live không chạy, và không có request API bổ sung khi tích hợp. Checker còn thiếu artifact C và blueprint.
