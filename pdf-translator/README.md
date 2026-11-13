# PDF 英漢翻譯器

網站前端：<https://yueguov1989.github.io/pdf-translator/>

## 網站目前提供的功能

- 在瀏覽器選擇 PDF，使用 PDF.js 本機提取文字。
- 英文原文與中文譯文逐段並排。
- 選擇繁體中文或簡體中文。
- 可以手動修改每段譯文。
- 匯出中英對照 TXT。
- 原始 PDF 不會上傳；只有抽取出的文字會送到你指定的翻譯 API。

## 尚未完成／目前限制

- 翻譯 API 需要先部署，網站才可真正翻譯。
- 掃描圖片版 PDF 尚未支援 OCR。
- 尚未提供 Word 或重新排版 PDF 匯出。
- 第一版使用 Argos Translate 英譯中模型，並以 OpenCC 將簡體轉為繁體。它是可自行託管的開源翻譯引擎，不等同於大型語言模型的翻譯品質。
- Render 免費服務只有 512 MB RAM、閒置後會休眠；Argos 模型能否在此規格穩定載入必須以部署測試確認，不能保證成功或持續可用。

## 架構

- 前端：GitHub Pages + HTML/CSS/JavaScript + PDF.js。
- 後端：FastAPI + Argos Translate + OpenCC。
- Render Blueprint 設定：儲存庫根目錄的 `render.yaml`。
- Dockerfile 與後端程式：`pdf-translator/`。

## 部署免費後端

1. 登入 <https://render.com/>。
2. 選 **New → Blueprint**。
3. 連接 GitHub，選擇 `yueguov1989/yueguov1989.github.io`。
4. Render 會讀取根目錄的 `render.yaml`。確認服務名稱 `pdf-translator-api`，方案為 Free，然後建立。
5. 等待建置和部署。第一次建置需要下載 Argos 英譯中模型，可能需要一些時間。
6. 部署後打開 Render 服務頁，複製它提供的 HTTPS 網址。
7. 打開 <https://yueguov1989.github.io/pdf-translator/>，把網址貼到「翻譯後端網址」，按「測試後端連線」。
8. 只有當網站顯示後端與翻譯模型均已就緒，才開始翻譯。

如果部署顯示記憶體不足、模型載入失敗，或服務啟動後 `/health` 顯示 `model_ready: false`，表示免費主機無法承載目前模型；不要把這種狀態當作已部署成功。

## API

健康檢查：

`GET /health`

翻譯：

`POST /api/translate`

請求 JSON：

```json
{
  "text": "The text to translate.",
  "target_language": "zh-TW"
}
```

`target_language` 支援 `zh-TW`（繁體中文）和 `zh-CN`（簡體中文）。

## 本機啟動（Windows 11）

你的電腦是 Windows 11、4GB RAM，不建議在這台電腦上同時執行大型翻譯模型與 PDF 工作流程。若只想測試 API，可在有足夠記憶體的環境執行：

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn app:app --host 127.0.0.1 --port 8000
```

## 安全與隱私

- 不要把含有密碼、身分證號、銀行資料或其他機密內容的文件交給不受信任的公開後端。
- 前端只傳送抽取出的文字，並非原始 PDF；但文字內容仍可能包含敏感資料。
- 公開服務目前尚未加入使用者登入、配額、速率限制和濫用防護，不適合直接面向大量陌生使用者。
- 自行託管可避免依賴第三方翻譯 API 的內容處理政策，但不能保證模型本身永不拒答，也不代表可以忽略適用法律。
