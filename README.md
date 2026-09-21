# BCSFE Web Edition - 貓咪大戰爭網頁版修改器

功能完整、介面美觀的《貓咪大戰爭》存檔修改器網頁版，支援繁中版 (TW)、日版 (JP)、英文版 (EN)、韓文版 (KR)。

## 🌟 功能特色

- **存檔管理**：支援本地 `SAVE_DATA` 拖曳上傳與下載匯出，或直接透過官方伺服器引繼碼 (Transfer Code + PIN) 雙向傳輸。
- **貨幣與道具**：貓罐頭（安全上限 / 極限）、經驗值 (XP)、統率力旗子、金券、銀券、白金券、傳奇券、喵魔石 (NP)、戰鬥道具全滿 (999)、黃金電腦等。
- **貓薄荷與貓目石**：全系列種子/果實/古代/黃金/惡魔貓薄荷、獸石與獸玉、EX至暗黑貓目石、喵力達。
- **貓咪角色與本能**：一鍵解鎖全部 830 隻貓咪、自訂等級 (50+90)、三階進化 (True Form)、四階超本能 (4th Form)、滿本能、貓咪圖鑑全開。
- **關卡與寶物進度**：世界/未來/宇宙篇一鍵通關、全篇章 100% 最高級金寶、未來篇計時得分全滿、殭屍襲來全通關、魔界篇、傳奇關卡 (SOL / UL / ZL)、貓咪塔全通關。
- **加碼多多與奧托托**：加碼多多滿級、10 隻金色傳奇隊員、城堡開發材料全滿 (9999)、工程師滿編、全城砲風格滿級、貓咪神社滿級。
- **修復與特權**：修正 HGT00 時間錯誤、加碼多多/奧托托崩潰修復、解鎖全部 10 個出陣隊伍、全獎牌、任務全通關、敵人圖鑑、黃金會員證、重置拉霸。

---

## 🚀 部署至 Vercel 步驟說明

### 步驟 1：建立 GitHub 儲存庫 (Repository)
1. 登入你的 [GitHub](https://github.com/) 帳號。
2. 點擊右上角 **「+」** -> **「New repository」**。
3. 填寫儲存庫名稱（例如 `bcsfe-web`），可設為 Public 或 Private。
4. 點擊 **「Create repository」**。

### 步驟 2：將程式碼上傳到 GitHub
你可以使用以下任一方式上傳：

**方式 A：直接在 GitHub 網頁上傳 (最簡單)**
1. 在剛剛建立的 GitHub 倉庫頁面中，點擊 **「uploading an existing file」**。
2. 將本機 `d:\test\web` 中的所有檔案與資料夾（包括 `api/`, `static/`, `app.py`, `bcsfe_service.py`, `requirements.txt`, `vercel.json`）拖曳至網頁中。
3. 點擊綠色的 **「Commit changes」** 完成上傳。

**方式 B：使用 Git 命令列 (若有安裝 Git)**
```bash
cd d:\test\web
git init
git add .
git commit -m "feat: initial release of BCSFE Web Edition"
git branch -M main
git remote add origin https://github.com/<你的GitHub帳號>/<你的倉庫名稱>.git
git push -u origin main
```

---

### 步驟 3：在 Vercel 連結並一鍵部署
1. 登入你的 [Vercel](https://vercel.com/) 帳號。
2. 在 Dashboard 點擊右上角 **「Add New...」** -> **「Project」**。
3. 在 **「Import Git Repository」** 列表中，找到並選取你剛剛建立的 GitHub 倉庫，點擊 **「Import」**。
4. 設定頁面保持預設值即可（專案已自動設定好 `vercel.json`、`api/index.py` 與 `requirements.txt`）。
5. 點擊 **「Deploy」** 按鈕！
6. 等待約 1~2 分鐘建置完成後，Vercel 就會提供一個專屬的線上 HTTPS 網址（例如 `https://bcsfe-web.vercel.app`），即可在任何裝置或手機上隨時使用！
