# Metrics Summary
- dataset: imdb
- vectorizer: tfidf
- model: logreg
- val_accuracy: 0.9014
- val_macro_f1: 0.9014
- test_accuracy: 0.8998
- test_macro_f1: 0.8998

## How to read the result on IMDB
- IMDB khá cân bằng nên accuracy và macro-F1 có thể gần nhau.
- Dù vậy vẫn cần báo cáo macro-F1 để giữ thói quen đánh giá đúng khi sang dữ liệu lệch lớp.

## Test per-class report
- class `negative`: precision=0.9105, recall=0.8868, f1=0.8985, support=2500.0
- class `positive`: precision=0.8897, recall=0.9128, f1=0.9011, support=2500.0
- class `macro avg`: precision=0.9001, recall=0.8998, f1=0.8998, support=5000.0
- class `weighted avg`: precision=0.9001, recall=0.8998, f1=0.8998, support=5000.0
