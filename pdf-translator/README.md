# PDF 免費翻譯

網站：<https://yueguov1989.github.io/pdf-translator/>

## 翻譯引擎

目前採用 **Google Cloud Translation Basic (NMT) + Qwen3-1.7B** 的混合流程：Qwen3 先在瀏覽器本機分析文章背景、人物／機構指涉與術語表；Google 翻譯 API 逐段產生初稿；最後由本機 Qwen3 參考全篇背景及相鄰段落校正初稿。

- 模型：`huggingworld/Qwen3-1.7B`
- 執行方式：Transformers.js + WebGPU + `q4f16`
- 授權：Qwen3 系列採 Apache-2.0；請同時查閱衍生模型倉庫的模型卡與授權資訊。
- PDF 原始檔在瀏覽器本機解析，不會上傳原始 PDF；但抽取出的英文段落會傳送到 Google Cloud Translation API 進行翻譯。
- Google API 金鑰只存在當前頁面記憶體，不寫入 localStorage 或網站原始碼。建議在 Google Cloud Console 將 API 金鑰限制為網站 HTTP referrer，並限制只能呼叫 Cloud Translation API。
- 首次使用需下載模型檔案，之後是否快取取決於瀏覽器儲存空間與設定。

## 主要功能

- 在瀏覽器本機讀取可選取文字的 PDF。
- 先整理文章主題、背景和術語，再翻譯各段落。
- 參考前後段落，盡量維持同一術語及語境一致。
- 繁體中文／簡體中文切換。
- 手動修改譯文。
- 匯出中英對照 TXT。

## Google 翻譯 API 設定\n\n1. 在 Google Cloud Console 建立或選擇專案。\n2. 啟用 Cloud Translation API（Basic / v2）。\n3. 建立 API 金鑰，並設定 HTTP referrer 限制為 `https://yueguov1989.github.io/*`，API 限制只允許 Cloud Translation API。\n4. 在翻譯器頁面貼上金鑰。金鑰只在當前頁面記憶體中使用，重新整理頁面後需要重新輸入。\n\nGoogle Cloud Translation NMT 目前每月前 500,000 個字元有免費額度；使用前仍可能需要啟用帳單帳戶。超出免費額度可能產生費用，請在 Google Cloud 設定預算與配額警示。免費額度及價格以 Google 官方定價頁為準：<https://cloud.google.com/translate/pricing>。\n\n## 硬體與瀏覽器要求

- 必須使用支援 WebGPU 的新版瀏覽器，建議新版 Chrome 或 Edge。
- 模型量化後仍需要較多記憶體和 GPU 資源。低記憶體設備可能無法載入或速度很慢。
- 你的 Windows 電腦只有 4GB RAM，未必能穩定運行 1.7B 模型；建議先在有較充足記憶體且支援 WebGPU 的設備測試。
- Android／iOS 裝置的 WebGPU 支援因瀏覽器、系統版本和 GPU 而異，不能保證所有手機都能運行。
- 如果瀏覽器不支援 WebGPU，頁面會提示無法載入模型。

## 上下文能力與限制

Qwen3 是語言模型，不是專用翻譯引擎。這個網頁會先把長文分批分析，建立全篇背景筆記，再把背景、前後段落和當前段落一起交給模型翻譯。這比只把每段獨立交給傳統機器翻譯模型更能利用上下文。

但受模型大小及上下文長度限制，不能保證完整理解每一篇長文的所有細節。對法律、醫療、合約、學術或其他重要文件，仍需人工核對。若 PDF 超長，前置背景整理也可能遺漏細節。

## 尚未支援

- 掃描圖片版 PDF 的 OCR。
- 匯出 Word 或重新排版 PDF（目前只有雙語 TXT）。
- 跨裝置同步模型或翻譯內容。

## 隱私

Qwen3 推理在瀏覽器本機進行；Google 翻譯初稿服務會收到 PDF 抽取出的文字段落。載入模型時，瀏覽器會從模型託管平台下載模型檔案。請勿在不受信任的裝置上處理敏感文件。
