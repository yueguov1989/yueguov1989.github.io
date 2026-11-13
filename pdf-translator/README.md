# PDF 英漢翻譯器（早期版本）

網站前端：<https://yueguov1989.github.io/pdf-translator/>

## 目前已完成

- GitHub Pages 網頁介面。
- 使用 PDF.js 在瀏覽器本機讀取可選取文字的 PDF。
- 英文原文／中文譯文逐段對照。
- 可手動修改譯文，並匯出雙語 TXT。
- 前端只把抽取出的文字傳給翻譯 API，不會把原始 PDF 檔案上傳到後端。

## 技術底座

- 前端：純 HTML/CSS/JavaScript + PDF.js。
- API：Python + FastAPI。
- 第一版翻譯引擎：Argos Translate（開源、可自架），再用 OpenCC 將簡體轉為繁體。
- API 目前未部署。沒有填入後端網址時，網站不會假裝翻譯成功。

## 本機啟動 API（Windows 11）

建議先在另一台有足夠記憶體的伺服器測試。你的電腦只有 4GB RAM，不建議在本機啟動翻譯服務。

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn app:app --host 127.0.0.1 --port 8000
```

健康檢查：<http://127.0.0.1:8000/health>

## API

`GET /health`

`POST /api/translate`

```json
{
  "text": "The text to translate.",
  "target_language": "zh-TW"
}
```

target_language 支援 `zh-TW`（繁體）和 `zh-CN`（簡體）。

## 部署注意事項

GitHub Pages 只能託管靜態網站，不能執行 FastAPI。要讓任何地方都能使用，必須把 API 部署到可從公網連線的伺服器，然後將該 HTTPS API 網址填入網站的「翻譯後端網址」。

部署時設定環境變數：

- `ALLOWED_ORIGINS=https://yueguov1989.github.io`

不要把 Ollama 或 Python API 的管理端口直接暴露到公網。正式公開前還需要加入使用者限流、請求大小限制、逾時控制、錯誤記錄及濫用防護。

## 已知限制

- 掃描版 PDF 尚未支援 OCR。
- 第一版匯出格式是 TXT，尚未做 Word／PDF 排版匯出。
- Argos Translate 是輕量、可自架的基礎翻譯引擎，不等同於大型語言模型的翻譯品質。
- 繁體中文目前以 OpenCC 進行簡繁轉換，並非獨立的繁體翻譯模型。
- 免費主機可能休眠、限流或停止服務；目前沒有已部署的永久免費後端。
- 不應把含有機密或個人敏感資訊的文件交給未經信任的公開服務。

## Render 免費後端部署（尚待帳戶授權）

倉庫根目錄已加入 `render.yaml`。部署時：

1. 登入 Render，選擇 **New → Blueprint**。
2. 連接 GitHub，授權存取 `yueguov1989/yueguov1989.github.io`。
3. 選取此 repository，Render 會讀取根目錄的 `render.yaml`。
4. 確認服務名稱為 `pdf-translator-api`、方案為 Free，再建立服務。
5. 部署成功後複製 Render 提供的 HTTPS 網址。
6. 打開 PDF 翻譯器，在「翻譯後端網址」欄貼上該網址，按「測試後端連線」。

注意：Render 免費 Web Service 會在閒置一段時間後休眠，重新喚醒需要等待；免費資源只有 512 MB RAM 和有限 CPU，Argos 模型是否能穩定載入仍需實際測試。若部署日誌顯示記憶體不足，不能靠修改前端解決，必須換更大規格的運算主機。

## 部署設定補充

- Dockerfile 與 Docker build context 使用相對於 GitHub 儲存庫根目錄的明確路徑。
- Argos 英譯中模型在 Docker image 建置階段下載並安裝，避免每次免費服務喚醒時重新下載模型。
- Render 免費實例只有 512 MB RAM，模型是否能在此限制下正常載入仍需以實際部署結果驗證；若記憶體不足，免費規格可能無法承載此翻譯後端。
