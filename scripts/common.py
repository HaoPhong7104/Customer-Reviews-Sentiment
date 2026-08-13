"""
common.py
-----------
Module dùng chung cho toàn bộ pipeline - tránh lặp code giữa các bước
(1 nguồn định nghĩa duy nhất cho aspect keywords + lexicon cảm xúc).

Gồm:
  - clean_text()            : chuẩn hoá whitespace cho review
  - ASPECT_KEYWORDS          : từ điển 7 khía cạnh sản phẩm skincare
  - detect_aspects()         : phát hiện khía cạnh được nhắc trong 1 đoạn text
  - split_clauses()          : tách review thành từng mệnh đề (cho ABSA)
  - clause_polarity()        : tính cực tính (positive/negative/neutral) của
                                1 mệnh đề, có xử lý phủ định đơn giản
"""
import re

# ---------------- Aspect keywords (7 khía cạnh phổ biến trong review skincare) ----------------
ASPECT_KEYWORDS = {
    "Hiệu quả": ["hiệu quả", "cải thiện", "giảm", "mờ vết", "sáng da", "hết mụn",
                 "trị", "kết quả", "tác dụng", "cấp ẩm", "dưỡng ẩm", "mịn màng",
                 "thô ráp", "ngứa", "kích ứng"],
    "Giá cả": ["giá", "sale", "khuyến mãi", "flash sale", "voucher"],
    "Chất lượng/Đóng gói": ["đóng gói", "chất lượng", "nguyên vẹn", "móp", "vỡ",
                             "rách", "seal", "bọc hàng", "hộp"],
    "Giao hàng": ["giao hàng", "ship", "shipper", "đúng hẹn"],
    "Mùi hương/Kết cấu": ["mùi", "thơm", "nhờn", "nhẹ mặt", "kết cấu", "thấm nhanh", "dịu nhẹ"],
    "Thành phần": ["thành phần", "an toàn", "tự nhiên", "hữu cơ", "organic"],
    "Dịch vụ/Uy tín": ["uy tín", "tư vấn", "nhiệt tình", "shop", "chăm sóc khách hàng"],
}

# ---------------- Lexicon cảm xúc ----------------
# Lưu ý: đã bỏ các từ đơn lẻ mang cực tính mập mờ theo ngữ cảnh (vd "đắt",
# "nhờn" đứng riêng) vì kiểm tra dữ liệu cho thấy chúng gây false positive
# nặng (VD "nhờn" xuất hiện 446 lần, phần lớn ở dạng phủ định "không nhờn"
# = đang KHEN). Thay bằng cụm từ có ngữ cảnh rõ ràng hơn.
NEGATIVE_WORDS = [
    "tệ", "kém", "thất vọng", "lừa đảo", "hàng giả", "hàng nhái", "cũ",
    "hỏng", "vỡ", "móp", "rách", "bẩn", "dơ", "không như mô tả", "hết date",
    "không giống hình", "chậm trễ", "giao chậm", "không hài lòng",
    "kích ứng", "dị ứng", "nổi mụn", "ngứa", "rát", "khô căng",
    "không hiệu quả", "không có tác dụng", "phí tiền", "không đáng",
    "trả hàng", "hoàn tiền", "dính bẩn", "thô ráp",
    "mốc", "hết hạn", "cận date", "giả mạo", "không nên mua", "đừng mua",
    "tránh xa", "quá tệ", "rất tệ", "chán", "buồn", "bực", "nhái",
    "giá đắt", "quá đắt", "hơi đắt", "khá đắt", "mắc quá",
    "để lại nhờn", "bết dính", "nhờn rít",
]
POSITIVE_WORDS = [
    "tốt", "tuyệt vời", "hài lòng", "ổn", "mịn màng", "mượt", "sáng da",
    "cải thiện", "hiệu quả", "thích", "yêu thích", "đáng mua", "đáng tiền",
    "giao nhanh", "chất lượng", "uy tín", "sẽ mua lại", "ủng hộ", "hoàn hảo",
    "an tâm", "chính hãng", "đóng gói cẩn thận", "nhẹ nhàng", "dễ chịu",
    "tuyệt", "xuất sắc", "ưng ý", "thoải mái", "đáng đồng tiền", "đúng hẹn",
    "nhiệt tình", "dịu", "thơm",
    "giá hời", "giá tốt", "giá rẻ", "xắt ra miếng", "không nhờn", "không bết dính",
]
NEGATION_WORDS = ["không", "chẳng", "chả", "đâu có", "chưa"]

_NEG_PATTERNS = sorted(NEGATIVE_WORDS, key=len, reverse=True)
_POS_PATTERNS = sorted(POSITIVE_WORDS, key=len, reverse=True)

_CLAUSE_SPLIT = re.compile(
    r"[.,;!?\n]|(?:\bnhưng\b)|(?:\btuy nhiên\b)|(?:\bsong\b)|(?:\bmà\b)|(?:\bcòn\b)",
    re.UNICODE
)


def clean_text(t):
    if not isinstance(t, str):
        return ""
    t = t.strip()
    t = re.sub(r"\s+", " ", t)
    return t.strip()


def detect_aspects(text):
    """Trả về list các khía cạnh được nhắc trong 1 đoạn text (review hoặc clause)."""
    t = text.lower()
    return [a for a, kws in ASPECT_KEYWORDS.items() if any(kw in t for kw in kws)]


def split_clauses(text):
    """Tách review thành các mệnh đề theo dấu câu & liên từ tương phản -
    bước bắt buộc để làm ABSA (mỗi mệnh đề có thể mang sentiment khác nhau)."""
    parts = [p.strip() for p in _CLAUSE_SPLIT.split(text) if p and p.strip()]
    return parts if parts else [text]


def clause_polarity(clause):
    """Tính cực tính của 1 mệnh đề, có xử lý phủ định đơn giản (cửa sổ 3 từ
    trước 1 từ cảm xúc). Trả về (sentiment, neg_hits, pos_hits)."""
    t = clause.lower()
    tokens = t.split()
    pos, neg = 0, 0

    def has_negation_before(word_idx):
        window = tokens[max(0, word_idx - 3):word_idx]
        return any(neg_w in " ".join(window) for neg_w in NEGATION_WORDS)

    for w in _NEG_PATTERNS:
        for m in re.finditer(r"\b" + re.escape(w) + r"\b", t):
            word_idx = len(t[:m.start()].split())
            if has_negation_before(word_idx):
                pos += 1  # "không tệ" -> đảo thành tích cực
            else:
                neg += 1
    for w in _POS_PATTERNS:
        for m in re.finditer(r"\b" + re.escape(w) + r"\b", t):
            word_idx = len(t[:m.start()].split())
            if has_negation_before(word_idx):
                neg += 1  # "không tốt" -> đảo thành tiêu cực
            else:
                pos += 1

    if pos == 0 and neg == 0:
        return "neutral", neg, pos
    return ("positive" if pos > neg else "negative" if neg > pos else "neutral"), neg, pos
