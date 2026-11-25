# Biên dịch báo cáo Seminar IE307

`main.tex` dùng bố cục LaTeX chuyển từ mẫu Word. `front-matter.tex` gồm trang bìa, mục lục, danh sách hình và bảng, cùng phần tóm tắt. Nội dung theo bố cục ba chương của seminar, có phụ lục phân công và tài liệu tham khảo. Biên dịch từ cùng checkout để Tectonic đọc các tệp nguồn trong `report/latex/` và `research/references.bib`.

## Build trên Windows

Cài Tectonic và font Times New Roman, gồm regular, bold, italic và bold italic. Lần đầu Tectonic cần mạng để tải gói LaTeX vào cache. Từ thư mục gốc của repo, chạy PowerShell:

```powershell
New-Item -ItemType Directory -Force .local/sem50-build | Out-Null
$output = (Resolve-Path .local/sem50-build).Path
Push-Location report/latex
$env:SOURCE_DATE_EPOCH = '1795564800'
tectonic --keep-logs --outdir $output main.tex
$buildExit = $LASTEXITCODE
Pop-Location
if ($buildExit -ne 0) { throw 'LaTeX build failed' }
Copy-Item (Join-Path $output 'main.pdf') report/seminar-ie307.pdf
```

Tectonic tự chạy BibTeX và các lượt biên dịch để cập nhật mục lục. Mở PDF và kiểm tiếng Việt, mục lục, citation DOI và link evidence sau mỗi lần đổi template, hình hoặc video. Kiểm chứng và phần đang chờ bàn giao có trong [CHECKS SEM-50](../../docs/evidence/SEM-50/CHECKS.md).
