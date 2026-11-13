# PDF 免費翻譯

網站前端：<https://yueguov1989.github.io/pdf-translator/>

## 翻譯引擎

後端使用 Helsinki-NLP 的 OPUS-MT English-to-Chinese 專用模型，透過 CTranslate2 int8 在 CPU 上執行，並使用 OpenCC 將簡體字轉為繁體字。OPUS-MT 模型採 Apache-2.0 授權。這是一個專用英中翻譯模型，不是通用聊天模型。

模型輸入長度有限，API 會先按模型 token 分段再翻譯，避免長段落被直接截斷。分段可能影響跨段落的上下文連貫性；請對重要內容校對。

## 網站功能

- 在瀏覽器選擇 PDF，使用 PDF.js 本機提取文字。
- 英文原文與中文譯文逐段並排。
- 選擇繁體中文或簡體中文。
- 可以手動修改每段譯文。
- 匯出中英對照 TXT。
- 原始 PDF 不會上傳；只有抽取出的文字會送到你指定的翻譯 API。

## 尚未完成／目前限制

- 翻譯 API 必須成功部署後才能真正翻譯。
- 掃描圖片版 PDF 尚未支援 OCR。
- 尚未提供 Word 或重新排版 PDF 匯出。
- Render Free 的記憶體只有 512 MB；即使使用 int8 模型，也必須實際部署測試。若模型載入失敗，免費方案可能無法承載，需要改用更精簡模型或其他免費運算環境。

## 部署

1. 登入 <https://render.com/>。
2. 選 **New → Blueprint**，連接 GitHub 儲存庫 `yueguov1989/yueguov1989.github.io`。
3. Render 讀取根目錄的 `render.yaml`，服務名稱為 `pdf-free-translator`，方案為 Free，地區為 Singapore。
4. 建立服務並等待 Docker 建置完成。首次建置需要下載並轉換 OPUS-MT 模型。
5. 部署後打開 Render 服務頁，複製 HTTPS 網址。
6. 在 PDF 翻譯網頁的「翻譯後端網址」欄貼上該網址，測試連線。
7. 必須確認 `/health` 回傳 `model_ready: true` 才能開始翻譯。

## API

健康檢查：`GET /health`

翻譯：`POST /api/translate`

請求 JSON：

```json
{
  "text": "The text to translate.",
  "target_language": "zh-TW"
}
```

`target_language` 支援 `zh-TW`（繁體中文）和 `zh-CN`（簡體中文）。

## 安全與隱私

- 不要把含有密碼、身分證號、銀行資料或其他機密內容的文件交給不受信任的公開後端。
- 前端只傳送抽取出的文字，並非原始 PDF；文字仍可能包含敏感資料。
- 公開服務尚未加入使用者登入、配額、速率限制和濫用防護，不適合直接面向大量陌生使用者。
- 自行部署可避免依賴第三方翻譯 API 的內容處理政策，但不能保證模型永不拒答，也不代表可以忽略適用法律。
