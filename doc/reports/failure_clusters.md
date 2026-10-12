# Phân tích lỗi Phase A — Enigma

Người phụ trách: Nguyễn Anh Tuấn — 2A202602700. Thành viên nhóm: Tuấn & Hưng.

Nguồn: [ragas_50q.json](../../artifacts/ragas_50q.json) và [answers_50q.json](../../artifacts/answers_50q.json).

Run timestamp: `2026-10-12T04:40:57.912003+00:00`.

## Phạm vi và điều kiện chạy

Đánh giá đúng 50 answers đã lưu: 20 factual, 20 multi_hop, 10 adversarial; bốn metrics hữu hạn trong [0,1]. Answer, contexts và ground_truth giữ riêng biệt. Cả 50 answers là `extractive_fallback`, `generation_model=null`; metadata generation là `[]`.

Evaluator RAGAS 0.1.22 dùng `gpt-4o-mini` và `text-embedding-3-small`, lấy model IDs thực tế từ m4 và tách khỏi generation/judge/guard. Kết quả này đo answers trích xuất, chưa đo khả năng LLM generation tổng hợp. Bộ answers được giữ để tiết kiệm API và làm nguồn A cố định cho Phase B.

Batch thành công có 200 tác vụ metric (50 × 4), không bật CI reproducibility. Số tác vụ khác số HTTP requests: faithfulness có nhiều bước, context precision đánh giá từng context, answer relevancy dùng embeddings. Client không retry transport; RAGAS giới hạn một lần thử và 2 workers. Cache LLM/embedding được gitignore.

Một lượt trước đó đã dừng sớm do cấu hình JSON object xung đột với parser dạng mảng của RAGAS. Cấu hình được bỏ và parser được kiểm tra offline trước batch thành công. JSON bàn giao là kết quả batch thành công. JSON nguồn được ghi LF để SHA-256 giữ ổn định khi clone Windows/Linux.

Bản cập nhật này sửa văn bản tiếng Việt bị chuyển thành ký tự `?` khi ghi báo cáo qua PowerShell; toàn bộ số liệu và nguồn JSON giữ nguyên, không chạy lại RAGAS.

## Điểm theo distribution

| Metric | factual (20) | multi_hop (20) | adversarial (10) |
|---|---:|---:|---:|
| faithfulness | 0.9500 | 1.0000 | 0.9667 |
| answer_relevancy | 0.3905 | 0.3673 | 0.4077 |
| context_precision | 0.9833 | 0.9708 | 0.9167 |
| context_recall | 0.8500 | 0.7458 | 0.6500 |
| avg_score | 0.7935 | 0.7710 | 0.7352 |

Avg_score toàn bộ: **0.7728**. Faithfulness cao chưa bảo đảm answer đáp ứng đủ câu hỏi hoặc dùng đúng chính sách hiện hành.

## Bottom 10 và chẩn đoán tự động

Danh tính, thứ tự, worst_metric, diagnosis và suggested_fix lấy từ Task 3 trong JSON. Chỉ điểm hiển thị được làm tròn 4 chữ số.

| Rank | ID | Question | Distribution | Avg score | Worst metric | Diagnosis | Suggested fix |
|---:|---:|---|---|---:|---|---|---|
| 1 | 6 | Thông tin lương thuộc cấp độ phân loại dữ liệu nào? | factual | 0.4786 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature |
| 2 | 42 | Thâm niên bao nhiêu năm thì được cộng thêm ngày phép? | adversarial | 0.5502 | answer_relevancy | Answer doesn't match question | Improve prompt template |
| 3 | 5 | Muốn mua thiết bị trị giá 55 triệu cần ai phê duyệt? | factual | 0.5867 | context_recall | Missing relevant chunks | Improve chunking or add BM25 |
| 4 | 39 | So sánh yêu cầu mật khẩu giữa policy v1.0 và v2.0 về độ dài tối thiểu, thời hạn đổi và MFA. | multi_hop | 0.6405 | context_recall | Missing relevant chunks | Improve chunking or add BM25 |
| 5 | 26 | Nhân viên vừa kết hôn và cùng tuần đó có con kết hôn. Tổng số ngày nghỉ đặc biệt có lương là bao nhiêu? | multi_hop | 0.6469 | answer_relevancy | Answer doesn't match question | Improve prompt template |
| 6 | 33 | Nhân viên Manager có thâm niên 12 năm: tổng phụ cấp hàng tháng và số ngày phép năm theo v2024 là bao nhiêu? | multi_hop | 0.6733 | answer_relevancy | Answer doesn't match question | Improve prompt template |
| 7 | 44 | Bao lâu phải đổi mật khẩu một lần? | adversarial | 0.6776 | answer_relevancy | Answer doesn't match question | Improve prompt template |
| 8 | 22 | Nếu cần mua một chiếc laptop 30 triệu cho nhân viên mới, ai phê duyệt và cần gì từ phòng CNTT? | multi_hop | 0.6915 | context_recall | Missing relevant chunks | Improve chunking or add BM25 |
| 9 | 7 | Nghỉ phép không lương 20 ngày cần ai phê duyệt? | factual | 0.6917 | answer_relevancy | Answer doesn't match question | Improve prompt template |
| 10 | 30 | So sánh quyền lợi bảo hiểm giữa nhân viên thử việc và nhân viên chính thức. | multi_hop | 0.6970 | answer_relevancy | Answer doesn't match question | Improve prompt template |

Diagnosis là giả thuyết từ metric thấp nhất, chưa phải kết luận nguyên nhân. Nhãn “LLM hallucinating” ở ID 6 không chứng minh LLM generation gây lỗi vì answers là fallback.

## Đối chiếu answer, contexts và reference

### Bảng bị cắt — IDs 5, 6

ID 5 hỏi ai phê duyệt mua thiết bị 55 triệu. Context 1 từ `mua_sam.md` dừng ở hàng trên 50 triệu và mất ô CEO; contexts 2/3 nói về tạm ứng và expense. Answer chép bảng bị cắt nên thiếu CEO theo reference. Đây là lỗi chunking/retrieval, không thể khắc phục chỉ bằng prompt.

ID 6 hỏi cấp phân loại thông tin lương. Context 2 từ `ky_luong.md` đã nêu thông tin lương là Bí mật, nhưng fallback chỉ chép bảng context 1 bị cắt và không trả lời trực tiếp “Bí mật, cấp 3”. Faithfulness=0 dù answer sao chép context 1 là điểm cần người học rà soát cách evaluator diễn giải bảng; không đủ căn cứ kết luận hallucination.

Đề xuất giữ nguyên hàng bảng khi chunking, thêm header hoặc lấy parent/đoạn kề chứa cả hàng. Kiểm tra coverage IDs 5/6 trước lần evaluation cải tiến có chủ đích.

### Multi-hop thiếu một nhánh hoặc chưa tổng hợp — IDs 21, 22, 26, 30, 33, 39

ID 21 có contexts về phép năm và ví dụ 9 năm được 18 ngày, nhưng thiếu khung lương Senior 20–35 triệu. ID 33 chỉ có các đoạn phép năm, thiếu phụ cấp Manager; answer dừng ở 15 ngày cơ bản thay vì tổng hợp 19 ngày và 1,5 triệu VNĐ/tháng. Cần retrieval cho nhiều chủ đề rồi tổng hợp phép tính.

ID 22 chỉ có yêu cầu phòng CNTT xác nhận cấu hình, thiếu bảng phê duyệt laptop 30 triệu và điều kiện 3 báo giá. Hai contexts khác nói về nghỉ không lương và đào tạo. ID 26 thiếu nghỉ khi con kết hôn nên không tính đủ tổng 4 ngày. ID 30 chỉ có quyền lợi thử việc, thiếu gói PVI 200 triệu/năm của nhân viên chính thức.

ID 39 cần so sánh hai phiên bản mật khẩu trên ba tiêu chí. Contexts có 120 ngày ở v2, 8 ký tự ở v1 và MFA bắt buộc ở v2, nhưng chưa đủ cả sáu ô thông tin; answer chỉ chép đoạn chu kỳ đổi mật khẩu. Có cả retrieval thiếu coverage và giới hạn của fallback không tổng hợp nhiều contexts.

Đề xuất tách câu hỏi thành các nhánh, kiểm tra đủ nguồn cho từng nhánh, rồi trả bảng so sánh/phép tính có căn cứ. Các cải tiến này chưa áp dụng vào baseline đang chấm.

### Xung đột phiên bản đã có trong contexts — IDs 42, 44, 49

ID 42 lấy mốc 5 năm của v2023 dù context 2 đã có mốc 3 năm ở v2024 và ghi thay thế bản cũ. ID 44 lấy chu kỳ 90 ngày của v1 dù context 2 có 120 ngày ở v2 và context 3 ghi thay thế v1. Đây là lỗi ưu tiên phiên bản/ranking và chọn answer đầu tiên; không thể chỉ gọi là thiếu recall.

ID 44 có faithfulness=1 vì 90 ngày được context cũ hỗ trợ nhưng vẫn sai theo reference hiện hành. ID 49 hỏi cả bản cũ và hiện hành; contexts có cả hai nhưng answer chỉ nêu 12 ngày của bản cũ. Cần phân biệt câu hỏi hiện hành với câu hỏi lịch sử.

Đề xuất dùng metadata phiên bản/ngày hiệu lực để ưu tiên đúng bản theo câu hỏi và ghi rõ phiên bản từng con số. Giữ bản cũ trong corpus cho câu hỏi lịch sử.

### Relevancy thấp không tự đồng nghĩa trả lời sai — ID 7

ID 7 trả đúng CEO cho nghỉ không lương 20 ngày, phù hợp context 1 và phần chính của reference. Answer còn liệt kê các khoảng ngày khác; reference thêm điều kiện đóng bảo hiểm chưa có trong contexts. Answer relevancy≈0.2667, context recall=0.5. Không coi mọi row bottom 10 là câu sai hoàn toàn; cần phân biệt dư nội dung với thiếu điều kiện thiết yếu.

## Matrix và nhóm yếu nhất

| Worst metric | factual | multi_hop | adversarial | Tổng |
|---|---:|---:|---:|---:|
| faithfulness | 1 | 0 | 0 | 1 |
| answer_relevancy | 18 | 18 | 10 | 46 |
| context_precision | 0 | 0 | 0 | 0 |
| context_recall | 1 | 2 | 0 | 3 |
| Tổng số câu | 20 | 20 | 10 | 50 |

Nhóm yếu theo mean thấp nhất: **adversarial (0.7352)**. Worst metric chủ đạo là **answer_relevancy, 46/50 câu**. Matrix đếm mọi câu theo metric thấp nhất, không phải số failures; tổng 20/20/10 là kích thước nhóm.

Adversarial mean thấp hơn factual **0.0582**. Kèm phân tích IDs 42/44, so sánh này đáp ứng điều kiện định lượng bonus A, không chứng minh pipeline nhận ra bẫy.

## Bẫy adversarial, giới hạn và kiểm chứng

IDs 46/48 giữ ý phủ định trong đoạn thử việc; ID 47 giữ lệnh không tự xử lý malware nhưng thiếu bước báo cáo trong 1 giờ theo reference. Kiểm tra cả điều kiện và hành động cần thiết, không chỉ sự xuất hiện của từ phủ định.

Giới hạn: 50 câu cố định, 10 adversarial, toàn bộ generation là fallback. Prompts RAGAS mặc định và embedding evaluator được dùng trên tiếng Việt nên có thể ảnh hưởng relevancy. Phase A chưa hiệu chỉnh bằng nhãn người hoặc đo drift; Phase B được đánh giá riêng, không thay cho kiểm chứng toàn bộ pipeline.

Bàn giao A ghi 97 tests offline A/m4/support/contracts đạt, runner thật đủ 50 rows/4 metrics/10 bottom rows. Schema, phép tính và source SHA-256 đã được kiểm tra offline. Các cải tiến retrieval/generation trên là đề xuất, chưa thay đổi answers đã chấm.

Hướng dẫn: [PHASE_A_HANDOFF.md](../PHASE_A_HANDOFF.md). Bản sửa encoding dùng lại JSON hiện có và không gọi API.
