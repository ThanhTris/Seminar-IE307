# Biên dịch báo cáo Seminar IE307

`main.tex` là bản review SEM-50 gồm ba chương, phụ lục phân công và tài liệu tham khảo. Bản này dùng lớp LaTeX `report` vì repo đang chờ template của môn. Lấy `assignments.tex` và `research/references.bib` từ cùng checkout khi biên dịch.

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
