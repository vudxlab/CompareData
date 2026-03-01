# CLAUDE.md — Project Rules

## Auto-commit sau khi test pass

**Khi nào commit:**
- Sau mỗi lần chạy pipeline thành công (test/run pass, không có exception)
- Khi có bất kỳ thay đổi nào trong working tree

**Những gì phải được stage và commit:**

1. Toàn bộ file thay đổi trong source code (`src/`, `scripts/`, `configs/`)
2. Tất cả `*.md` trong `docs/`
3. Tất cả `*.md` và `*.pdf` trong `results/reports/`
4. Các output kết quả: `results/tables/*.csv`, `results/figures/**/*.png`

**Quy trình commit bắt buộc:**

```bash
# Stage tất cả thay đổi liên quan
git add src/ scripts/ configs/
git add docs/*.md
git add results/reports/*.md results/reports/*.pdf
git add results/tables/ results/figures/

# Commit với message rõ ràng
git commit -m "<type>: <mô tả ngắn gọn>

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

**Commit message format:**

| type | khi nào dùng |
|------|--------------|
| `feat` | thêm tính năng mới |
| `fix` | sửa bug |
| `refactor` | cải tổ code, không đổi behavior |
| `results` | cập nhật kết quả phân tích / report |
| `docs` | chỉ cập nhật tài liệu |
| `config` | thay đổi config |

**Ví dụ commit message hợp lệ:**
```
results: update comparison_pair report and metrics after 100s window run
fix: correct unit normalization for sensor_B accZ column
docs: update runbook with new troubleshooting steps
```

## Nguyên tắc khác

- Không commit file data thô (`data/raw/`, `data/processed/`) — đã có trong `.gitignore`
- Không skip hooks (`--no-verify`) trừ khi user yêu cầu rõ ràng
- Luôn chạy `git status` sau commit để xác nhận thành công
