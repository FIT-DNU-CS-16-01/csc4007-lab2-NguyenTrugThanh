# Lab 2 Analysis Report (IMDB)

## 1. Data audit
- **Số lượng mẫu đã dùng**: 50,000 mẫu (40,000 train, 5,000 val, 5,000 test)
- **Phân bố nhãn positive / negative**: Cân bằng hoàn hảo (25,000 mỗi nhãn, 50% mỗi loại)
- **Độ dài review điển hình (median, p95)**: Median = 970 ký tự / 173 từ; P95 = 3,391 ký tự / 590 từ
- **Có missing / empty text không?**: Không có missing hay empty (0 missing text)
- **Có duplicate không?**: Có 824 reviews trùng lặp (1.648% dữ liệu)
- **3 quan sát đáng chú ý về dữ liệu IMDB**:
  1. Dữ liệu cân bằng tốt (negative = positive), nên accuracy và macro-F1 có thể gần nhau
  2. Độ dài reviews dao động rất lớn (32-13,704 ký tự), một số reviews rất ngắn, một số rất dài
  3. Có lượng nhỏ duplicate (1.65%), có thể làm ảnh hưởng đến tính chính xác của đánh giá

## 2. Preprocessing design

### Chiến lược tiền xử lý được thử nghiệm:

**Chiến lược 1: Raw (không xử lý)**
- Giữ nguyên text gốc, chỉ xử lý missing values
- Mục đích: baseline để so sánh hiệu quả của tiền xử lý

**Chiến lược 2: Gentle cleaning (tiền xử lý nhẹ nhàng)**
- Loại bỏ HTML tags
- Chuyển thành chữ thường
- Làm sạch whitespace và control characters
- **Giữ lại dấu câu, số, URLs, emails** → tránh mất tín hiệu cảm xúc
- Ví dụ: "It's AMAZING!!!" → "it's amazing!!!"

**Chiến lược 3: Basic cleaning (tiền xử lý chuẩn - DEFAULT)**
- Loại bỏ HTML tags
- Thay URL bằng `<URL>` token
- Thay email bằng `<EMAIL>` token
- Giữ hoặc bỏ dấu câu (tuỳ --drop_punct flag)
- Giữ hoặc thay số (tuỳ --replace_number flag)
- Ví dụ: "Check http://example.com and email test@test.com" → "Check <URL> and email <EMAIL>"

**Chiến lược 4: Aggressive cleaning (tiền xử lý tích cực)**
- Loại bỏ HTML tags
- Thay URL bằng `<URL>` token  
- Thay email bằng `<EMAIL>` token
- Thay số bằng `<NUM>` token
- **Loại bỏ tất cả dấu câu**
- Ví dụ: "Love it! 9/10 → http://imdb.com" → "love it <num> <url>"

### Câu hỏi thiết kế:

- **Bạn đã dùng những bước làm sạch nào?**
  - Chủ yếu dùng "basic" cleaning vì đó là cân bằng giữa giữ lại thông tin và loại bỏ noise. Aggressive cleaning mất nhiều dấu hiệu cảm xúc (!!!), gentle giữ quá nhiều noise.

- **Bạn giữ lại dấu câu hay bỏ đi? Vì sao?**
  - Trong basic cleaning, giữ lại dấu câu (mặc định `keep_punct=True`). Dấu câu như "!", "?", "!!!" có chứa tín hiệu cảm xúc mạnh mẽ trên IMDB, đặc biệt để biểu thị độ phấn khích hoặc phản đối.

- **Bạn có thay số bằng `<NUM>` không? Vì sao?**
  - Mặc định không thay (--replace_number không được dùng). Trên IMDB, con số thường thể hiện xếp hạng (9/10, 8/8, v.v.), có ý nghĩa cảm xúc. Tuy nhiên, nếu coi nó chỉ là noise, có thể thay bằng `<NUM>` để giảm độ thưa của features.

- **Có bước nào bạn cố tình **không** làm để tránh mất tín hiệu cảm xúc?**
  - HTML tags: loại bỏ (không chứa tín hiệu cảm xúc chính)
  - Dấu câu: **giữ lại** (biểu thị cảm xúc như excitement, anger, sarcasm)
  - Số: **giữ lại** (rating ngụ ý cảm xúc)
  - Chữ hoa: chuyển thành chữ thường (chuẩn NLP, chữ hoa không chứa nhiều tín hiệu cảm xúc sau khi là chữ đầu câu)

## 3. Experiment comparison

| Run | Text version | Vectorizer | Model | Ngram | Macro-F1 | Accuracy | Ghi chú |
|---|---|---|---|---|---:|---:|---|
| 1 | raw | TF-IDF | LogReg | 1 | 0.8986 | 0.8986 | Baseline: text gốc, không xử lý |
| 2 | basic | TF-IDF | LogReg | 1 | 0.8996 | 0.8996 | Basic cleaning, unigram |
| 3 | basic | BoW | LogReg | 1 | 0.8806 | 0.8806 | BoW kém hơn TF-IDF vì không tính TF scaling |
| 4 | basic | TF-IDF | LinearSVM | 1 | 0.9012 | 0.9012 | LinearSVM tốt hơn LogReg một chút |
| 5 | basic | TF-IDF | LogReg | 2 | 0.9068 | 0.9068 | **BEST: Bigrams cải thiện đáng kể** |
| 6 | gentle | TF-IDF | LogReg | 1 | 0.8998 | 0.8998 | Gentle cleaning ≈ basic (same result) |
| 7 | aggressive | TF-IDF | LogReg | 1 | 0.8998 | 0.8998 | Aggressive cleaning ≈ gentle (removing punct không tốn) |

### Phân tích so sánh:

**Raw vs Cleaned text (so sánh run 1 vs 2):**
- Raw: 0.8986 F1
- Basic cleaned: 0.8996 F1
- Cải thiện: +0.10% (~1.01x)
- **Kết luận**: Tiền xử lý cơ bản giúp một chút, nhưng không quá nhiều. Raw text vẫn có hiệu quả tương tự.

**BoW vs TF-IDF (so sánh run 2 vs 3):**
- TF-IDF: 0.8996 F1
- BoW: 0.8806 F1
- Khác biệt: -2.10% (~1.02x kém)
- **Kết luận**: TF-IDF tốt hơn BoW vì tính toán trọng số của từ theo tần suất trong văn bản (TF) và tất cả văn bản (IDF), làm giảm ảnh hưởng của từ phổ biến.

**Logistic Regression vs Linear SVM (so sánh run 2 vs 4):**
- LogReg: 0.8996 F1
- LinearSVM: 0.9012 F1
- Khác biệt: +0.16% (~1.00x tốt hơn)
- **Kết luận**: SVM tốt hơn một chút, có thể vì SVM tìm margin lớn nhất giữa hai lớp.

**Unigram vs Unigram+Bigram (so sánh run 2 vs 5):**
- Unigram (1-gram): 0.8996 F1
- Unigram+Bigram (1-2 gram): 0.9068 F1
- Khác biệt: +0.72% (~1.008x)
- **Kết luận**: Bigrams giúp rất nhiều! Vì chúng bắt được cụm từ có ý nghĩa (e.g., "not good", "very bad", "must watch") mà unigram không thể.

**Gentle vs Aggressive cleaning (run 6 vs 7):**
- Cả hai đều cho F1 = 0.8998
- **Kết luận**: Hai chiến lược cleaning trên IMDB có hiệu quả tương đương, không có sự khác biệt đáng kể. Điều này gợi ý rằng phần quan trọng nhất là tính năng (features), không phải cách làm sạch.

## 4. Error analysis (16 lỗi được phân tích)

### Thống kê lỗi:
- **Tổng số lỗi trên test set**: 501/5000 (10.02% error rate)
- **False Positives** (nhãn thực: negative, dự đoán: positive): 283 (56.5% lỗi)
- **False Negatives** (nhãn thực: positive, dự đoán: negative): 218 (43.5% lỗi)
- **Độ tin cậy trung bình trên lỗi**: 0.6552 (cao, model tự tin nhưng sai)

### Nhóm lỗi chính (14 lỗi được chọn):

#### **Nhóm 1: Mixed Sentiment - Review có cảm xúc trộn lẫn (4 lỗi)**
Những reviews chứa cả phần tích cực và tiêu cực, nhưng không rõ ý chính.

| ID | True | Pred | Độ tin cậy | Giải thích |
|---|---|---|---|---|
| 14750 | positive | negative | 0.9695 | Review bắt đầu "I was prepared for the worst" và "confusing, muddled" nhưng sau đó nói "points for trying". Model nhìn thấy từ tiêu cực ở đầu. |
| 4648 | negative | positive | 0.9576 | Review nói "never really thought it was funny" nhưng "good for a few laughs". Có cả lời khen và chê. |
| 6519 | negative | positive | 0.9267 | Phê bình animation nhưng nói "surprisingly well rated". Mixed signals. |
| 15598 | positive | negative | 0.9351 | Có lời khen actors nhưng overall impression không rõ ràng. |

**Nguyên nhân khả dĩ**: Reviewers thường nêu những điểm tiêu cực trước, rồi mới nêu điểm tích cực (hoặc ngược lại). Model sử dụng Bag-of-Words không hiểu được thứ tự từ, nên bị nhầm lẫn.

**Đề xuất cải thiện**: Dùng RNN/LSTM để hiểu thứ tự từ, hoặc dùng attention mechanism để nhấn mạnh phần quan trọng của review.

---

#### **Nhóm 2: Sarcasm & Irony - Mỉa mai và châm biếm không được phát hiện (2 lỗi)**
Những reviews dùng sarcasm để nói ngược ý.

| ID | True | Pred | Độ tin cậy | Giải thích |
|---|---|---|---|---|
| 37061 | negative | positive | 0.9893 | "pure genius", "brilliant", "9.5/10" nhưng nhãn là negative. Điều này có thể là lỗi gán nhãn hoặc pure sarcasm. |
| 36707 | negative | positive | 0.8908 | Review nói phim là "masterpiece" với "best special effects", nhưng nó là phim B-grade. Pure sarcasm. |

**Nguyên nhân khả dĩ**: Sarcasm có nhiều từ tích cực nhưng ý chính tiêu cực. BoW chỉ đếm từ, không hiểu context.

**Đề xuất cải thiện**: Fine-tune model với tập dữ liệu sarcasm, hoặc dùng language model lớn hơn (BERT, etc.).

---

#### **Nhóm 3: Negative with Positive Elements - Review tiêu cực nhưng có nhiều từ khen (5 lỗi)**
Những reviews tiêu cực nhưng bao gồm lời khen ngôi diễn viên, kĩ xảo điện ảnh, v.v.

| ID | True | Pred | Độ tin cậy | Giải thích |
|---|---|---|---|---|
| 31245 | negative | positive | 0.9837 | Bài review dài (2279 ký tự) khen nhiều diễn viên ("memorable", "powerful") nhưng kết luận tổng quát tiêu cực. |
| 17596 | positive | negative | 0.9850 | Bắt đầu "hardly a masterpiece", "not so well written" nhưng có lời khen. (Chú: nhãn là positive nhưng review brash) |
| 8347 | negative | positive | 0.9196 | "despite excellent cast, unremarkable" - khen cast nhưng chê phim. |
| 36218 | negative | positive | 0.9423 | Phê bình nội dung nhưng khen acting. Điều này khó vì phê bình ý tưởng/kịch bản nhưng khen kĩ năng. |
| 4431 | negative | positive | 0.8890 | Nói "beautiful" và "great voice" nhưng review là negative. |

**Nguyên nhân khả dĩ**: Model cân bằng tất cả từ tích cực/tiêu cực, không hiểu được ý chính. Thường khi review tiêu cực về bộ phim nhưng khen diễn viên, reviewers muốn nói "phim xấu dù diễn viên tốt".

**Đề xuất cải thiện**: Aspect-based sentiment analysis (phân tích cảm xúc theo khía cạnh: diễn viên, kịch bản, etc.).

---

#### **Nhóm 4: Kompleks / Dài - Review rất dài và phức tạp (2 lỗi)**
Những reviews rất dài (>2000 ký tự) với nhiều chi tiết, nhiều luận điểm.

| ID | True | Pred | Độ tin cậy | Giải thích |
|---|---|---|---|---|
| 33759 | negative | positive | 0.9375 | Review dài (2036 ký tự), người viết nói "I loved when I was 12" nhưng "terrible as adult". Kết luận tiêu cực nhưng context dài. |
| 29148 | negative | positive | 0.8200 | Review nói phim "terrifying" và "haunts my dreams". Những từ này thường là tích cực (truyền cảm xúc mạnh) nhưng trong context là tiêu cực. |

**Nguyên nhân khả dĩ**: BoW không theo dõi được arc của review. Người viết có thể bắt đầu tích cực (nhớ tuổi thơ, khen khía cạnh nào đó) nhưng kết luận tiêu cực. Hoặc, dùng từ như "terrifying", "creepy" có thể là khen hoặc chê tuỳ context.

**Đề xuất cải thiện**: Dùng phân đoạn (segmentation) để hiểu cấu trúc review: intro, body paragraphs, conclusion.

---

### Bảng ghi lỗi chi tiết

| ID | True | Pred | Nhóm lỗi | Tự tin | Giải thích ngắn |
|---|---|---|---|---|---|
| 37061 | neg | pos | Sarcasm | 0.99 | "pure genius", "brilliant" - pure sarcasm hay mislabel |
| 17596 | pos | neg | Mixed | 0.98 | "hardly masterpiece" nhưng khen diễn viên |
| 31245 | neg | pos | Neg+Pos | 0.98 | Khen actors nhưng phim tiêu cực overall |
| 14750 | pos | neg | Mixed | 0.97 | "prepared for worst" rồi "points for trying" |
| 4648 | neg | pos | Mixed | 0.96 | "never funny" nhưng "good for laughs" - contradict |
| 22479 | pos | neg | Mixed | 0.94 | Mix of praise and criticism |
| 36218 | neg | pos | Neg+Pos | 0.94 | Khen acting nhưng chê nội dung |
| 33759 | neg | pos | Complex | 0.94 | Dài, "loved at 12" nhưng "terrible now" |
| 15598 | pos | neg | Mixed | 0.94 | Talent actors nhưng unclear main sentiment |
| 25609 | neg | pos | Neg+Pos | 0.93 | Khen series nhưng review là negative |
| 6519 | neg | pos | Mixed | 0.93 | Chê animation nhưng "surprisingly rated" |
| 34543 | neg | pos | Neg+Pos | 0.92 | Khen creativity nhưng chê luận đề |
| 8347 | neg | pos | Neg+Pos | 0.92 | "excellent cast" nhưng "unremarkable film" |
| 21465 | pos | neg | Mixed | 0.92 | "edge of seat", "laughing" - sarcasm? |
| 155 | neg | pos | Mixed | 0.90 | Thought/expectation mismatch + mixed sentiment |
| 36707 | neg | pos | Sarcasm | 0.89 | Sarcasm: "masterpiece" + "best effects" |

## 5. Reflection

### Q: Pipeline nào tốt nhất trên IMDB? Vì sao?

**Đáp**: **Run 5: basic preprocessing + TF-IDF + LogReg + bigram** (F1=0.9068, Acc=0.9068)

**Vì sao?**
1. **TF-IDF > BoW**: TF-IDF tính trọng số từ, làm giảm ảnh hưởng của từ phổ biến (e.g., "the", "is").
2. **Bigram rất quan trọng**: Bắt được cụm từ có ý nghĩa như "not good", "very bad", "must watch" → tăng 0.72% F1.
3. **Basic preprocessing**: Cân bằng giữa giữ thông tin và loại bỏ noise. Removal quá tích cực (aggressive) mất dấu hiệu cảm xúc.
4. **LogReg vs LinearSVM**: LinearSVM tốt hơn 0.16% nhưng LogReg dễ train hơn, nên LogReg là lựa chọn hợp lý.

### Q: Trên IMDB, accuracy và macro-F1 có chênh nhau nhiều không?

**Đáp**: **Không, rất gần**. Ví dụ Run 5: Accuracy=0.9068, Macro-F1=0.9068 (sai lệch <0.01%)

**Lý do**: IMDB dữ liệu cân bằng tốt (50% neg, 50% pos), nên accuracy = macro-F1 ≈ weighted-F1. Trên dữ liệu cân bằng, accuracy là một metric tốt.

### Q: Nếu chuyển sang dữ liệu lệch lớp hơn, bạn kỳ vọng metric nào sẽ phản ánh tốt hơn?

**Đáp**: **Macro-F1**

**Lý do**:
- Accuracy bị lệch về class chiếm đa số. Nếu 95% negative, 5% positive, model predict all negative → 95% accuracy nhưng F1 = 0% (vì không detect positive).
- Macro-F1 trung bình F1 của mỗi class, nên phản ánh hiệu quả trên cả two classes.
- Weighted-F1 cũng tốt nhưng ưu tiên class lớn hơn.

**Recommendation**: Dùng macro-F1 + confusion matrix để có hình ảnh rõ hơn.

### Q: Một cải tiến bạn muốn thử ở Lab 3 là gì?

**Đáp**: **Sequence models (RNN/LSTM/Transformers) để hiểu ngữ cảnh và thứ tự từ**

**Chi tiết**:
1. **Hiện tại (Lab 2)**: BoW + TF-IDF không hiểu thứ tự từ. "Not good" và "Good not bad" sẽ có vector giống nhau.
2. **Lab 3 (mong muốn)**:
   - Dùng LSTM/GRU để hiểu thứ tự từ → phát hiện negation ("not good" ≠ "good").
   - Hoặc fine-tune BERT/DistilBERT (pre-trained transformer) → hiểu context, sarcasm tốt hơn.
   - Dùng attention mechanism → xem model chú trọng vào phần nào của review.
   - Aspect-based sentiment analysis → phân tích riêng "sentiment về diễn viên" vs "sentiment về kịch bản".

3. **Expected improvement**: Có thể giảm từ 501 errors xuống ~200-300 errors (40-60% giảm) bằng cách phát hiện sarcasm, negation, mixed sentiment tốt hơn.

