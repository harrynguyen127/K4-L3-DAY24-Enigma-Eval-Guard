# Blueprint CI/CD cho RAG và guardrails

Nhóm: Enigma

Người phụ trách: Đặng Quang Hưng — 2A20260271

Đây là **đề xuất CI/CD**, không phải workflow đã được triển khai/chạy.
Nguồn kết quả: artifacts/ragas_50q.json, judge_results.json, guard_results.json.
Run timestamp: 2026-10-12T10:57:53.826320+00:00; guard models: ["gpt-4o-mini"].
Models generation/evaluator/judge từ A/B: generation [], evaluator ["gpt-4o-mini", "text-embedding-3-small"] từ ragas_50q.json; judge ["gpt-4o-mini"] từ judge_results.json.

## Kiến trúc và failure action

Input → Presidio → NeMo input → RAG → NeMo output → response.
Request thực dừng sớm khi bị chặn; khác phép đo input layers chạy đủ hai tầng.

Data flow tuần tự qua từng tầng phòng thủ đa lớp (Defense-in-Depth):
1. **Tầng 1 - Presidio PII Detection & Anonymization:** Quét và phát hiện CCCD/CMND (12 số hoặc 9 số), số điện thoại Việt Nam (đầu 03-09), và địa chỉ email. Khi phát hiện PII người dùng nhập vào, hệ thống thực hiện ẩn danh hóa (redact) thay thế bằng token tương ứng (<VN_CCCD>, <VN_PHONE>, <EMAIL_ADDRESS>) hoặc từ chối trực tiếp đối với các query cố ý trích xuất dữ liệu cá nhân.
2. **Tầng 2 - NeMo Input Rails:** Kiểm tra rào chắn đầu vào trước khi câu hỏi tới mô hình/RAG. Áp dụng các flow tự kiểm tra (self-check input) để phát hiện và chặn jailbreak, prompt injection, đóng giả vai trò hoặc hỏi các chủ đề ngoài phạm vi chính sách công ty. Nếu phát hiện vi phạm, kích hoạt `rail.stop = True`, lập tức dừng xử lý (short-circuit), không gọi RAG hay LLM phía sau, và trả về thông báo từ chối an toàn chuẩn mực.
3. **Tầng 3 - RAG Pipeline (m1–m5):** Thực hiện tìm kiếm ngữ nghĩa và reranking tài liệu chính sách. Nếu tài liệu tìm được không đủ độ tin cậy hoặc gặp lỗi truy vấn, hệ thống fallback về câu trả lời an toàn hoặc thông báo từ chối lịch sự, tránh ảo giác.
4. **Tầng 4 - NeMo Output Rails:** Kiểm tra đầu ra từ LLM trước khi gửi đến người dùng. Tầng này xác minh câu trả lời không làm rò rỉ bí mật nội bộ, thông tin cá nhân cụ thể, mật khẩu quản trị, hoặc thông tin nhạy cảm nhân sự. Nếu vi phạm, câu trả lời bị hủy và thay thế bằng canned refusal response.
5. **Quản lý Secrets & Logging:** Mọi API keys và credentials được lưu trong biến môi trường (.env), tuyệt đối không ghi vào log hay commit vào repository. Toàn bộ nội dung log giám sát đều phải qua xử lý ẩn danh PII. Khi có sự cố mạng hoặc lỗi runtime, hệ thống kích hoạt deterministic fallback handler để đảm bảo tính an toàn liên tục.

## Phạm vi và số đo latency

Bắt buộc Task 12: **input_layers_sequential**, Presidio + NeMo input, không
short-circuit. Engines tạo trước đo; có hai warm-up thật không tính vào mẫu.
Percentile nội suy tuyến tính từ raw samples; tổng từ tổng từng sample.

Số mẫu timed: 20; warm-up: 2;
phương pháp: linear.

| Layer / scope | P50 ms | P95 ms | P99 ms | Tình trạng |
|---|---|---|---|---|
| Presidio | 20.57 ms | 35.04 ms | 39.49 ms | Hoàn thành đo Task 12 |
| NeMo input | 648.23 ms | 802.57 ms | 841.43 ms | Hoàn thành đo Task 12 |
| Input guard sequential | 677.68 ms | 831.73 ms | 870.50 ms | Hoàn thành đo Task 12 |
| RAG | chưa đo | chưa đo | chưa đo | Ngoài phạm vi bắt buộc |
| NeMo output | chưa đo | chưa đo | chưa đo | Ngoài phạm vi bắt buộc |
| Full guard / short-circuit request | chưa đo | chưa đo | chưa đo | Không suy từ input_guard_ms |

Input-layer budget target: 500ms; kết quả thực tế/budget_ok: P95 = 831.73 ms / budget_ok: False.
Bottleneck xác định: Độ trễ chủ yếu đến từ NeMo input rail khi phải thực hiện network roundtrip gọi LLM kiểm tra an toàn (P95 là 802.57 ms, chiếm hơn 96% tổng thời gian input guard). Ngược lại, tầng Presidio PII chạy regex và NER cục bộ rất nhanh với P95 chỉ đạt 35.04 ms. Các phạm vi ngoài luồng như RAG, NeMo output rail và full-guard short-circuit hiện được giữ ở trạng thái "chưa đo"; nhóm dự kiến lấy mẫu bổ sung với 2 warm-up và 20 mẫu timed riêng biệt khi đưa vào tích hợp hệ thống hoàn chỉnh.

## CI gates đề xuất

- RAGAS faithfulness ≥0.75, avg_score ≥0.65 trên 50 câu.
- Attacks ≥18/20 cho CI đề xuất; clean 8/8 allowed; output cases đúng.
- Full guard P95 <500ms chỉ áp dụng sau khi thực sự đo full guard.

Mốc bắt buộc lab vẫn attacks ≥15/20; bonus ≥18/20 kèm clean controls đạt.
Đề xuất lệnh kiểm tra tự động trong quy trình CI/CD:
`python scripts/check_lab.py --with-tests`
Script kiểm tra thực hiện rà soát nghiêm ngặt toàn bộ schema, tính hợp lệ của nguồn dữ liệu, mã băm SHA-256 và các điều kiện chất lượng bắt buộc. Khi bất kỳ tiêu chí nào không đạt (ví dụ false positive trên clean set > 0, hoặc tỷ lệ chặn attack < 15/20), script trả về exit code khác 0 để tự động hủy bỏ build và chặn merge code vào nhánh production. Quy trình này là kiến trúc đề xuất; nhóm chưa cấu hình GitHub Actions workflow runner tự động trong repository này.

## Monitoring và cải tiến

Hệ thống giám sát vận hành liên tục (Production Monitoring):
- **Chỉ số theo dõi chính:** Tỷ lệ vi phạm chính sách bảo mật (Attack Catch Rate), tỷ lệ chặn nhầm (False Positive Rate) trên các câu hỏi hợp lệ của nhân viên, và thời gian đáp ứng P95 của các lớp kiểm duyệt.
- **Ngưỡng cảnh báo tự động:** Phát cảnh báo mức độ cao (Alert) khi False Positive Rate vượt quá 0.0% trên các câu hỏi chính sách chuẩn, hoặc khi P95 của input guard vượt quá 1000 ms liên tục trong 15 phút.
- **Thu thập mẫu & Quyền riêng tư:** Tự động lấy mẫu ngẫu nhiên 5% yêu cầu hằng ngày sau khi đã qua xử lý che giấu PII (redacted data) để chuyên viên nhân sự và kỹ sư an toàn thông tin thẩm định định kỳ.
- **Phân định trách nhiệm:** Đội ngũ Security Operations tiếp nhận và xử lý cảnh báo khi phát hiện tấn công dồn dập (drift hoặc attack campaign); đội ngũ HR Admin cập nhật các tài liệu chính sách mới vào knowledge base.

RAGAS mean/worst distribution: avg_score toàn bộ 0.7728; nhóm yếu nhất là adversarial với avg_score 0.7352 theo ragas_50q.json.
Cohen’s κ: 1.0 (hoàn toàn đồng thuận 10/10 nhãn giữa judge và human theo judge_results.json).
Attacks passed: 20/20; clean false_positive_rate: 0.0 theo guard_results.json.

Kế hoạch cải tiến có thể kiểm chứng:
1. Triển khai cơ chế short-circuit thực tế ở tầng đầu vào: Khi Presidio phát hiện PII độc hại, ngắt yêu cầu ngay lập tức để tiết kiệm chi phí và giảm thời gian xử lý xuống dưới 40 ms.
2. Áp dụng Semantic Caching đối với NeMo input rails cho các mẫu câu hỏi thường gặp nhằm giảm độ trễ P95 từ 831.73 ms xuống dưới ngân sách 500 ms đề ra.
3. Mở rộng tập luật nhận diện Tiếng Việt trong Presidio để hỗ trợ thêm các định dạng mã số thuế cá nhân và số tài khoản ngân hàng.
4. Gia tăng số lượng câu kiểm thử adversarial từ 20 câu lên 100 câu, bao gồm các kịch bản tấn công gián tiếp (indirect prompt injection) và jailbreak đa lượt hội thoại.
