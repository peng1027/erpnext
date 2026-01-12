# VMS 管理員操作手冊 (Pansen 租戶站)

**站點**: pansen.vmsys.co
**版本**: v1.1
**日期**: 2026-01-12

---

## 目錄

1. [系統登入](#1-系統登入)
2. [控制台總覽](#2-控制台總覽)
3. [通行證管理 (Site Pass)](#3-通行證管理-site-pass)
4. [訪客註冊 (Self Registration)](#4-訪客註冊-self-registration)
5. [安全掃描 (Security Scanner)](#5-安全掃描-security-scanner)
6. [團隊管理 (Team Management)](#6-團隊管理-team-management)
7. [不合格報告 (NCR)](#7-不合格報告-ncr)
8. [改正措施 (CAPA)](#8-改正措施-capa)
9. [報表與統計](#9-報表與統計)
10. [系統設定](#10-系統設定)
11. [Email 地址修改](#11-email-地址修改)

---

## 1. 系統登入

### 1.1 登入步驟

1. 開啟瀏覽器，訪問 **https://pansen.vmsys.co**
2. 輸入管理員帳號和密碼
3. 點擊「Login」按鈕

### 1.2 登入畫面

![VMS 登入畫面](vms_sop_images/vms_sop_01_login.png)

**畫面說明：**
- 輸入 Email 和 Password
- 點擊「Login」按鈕登入
- 可選擇「Login with Email Link」免密碼登入
- 新訪客可點擊「Register here」自助註冊

### 1.3 忘記密碼

1. 點擊「Forgot Password?」連結
2. 輸入註冊的 Email
3. 檢查郵箱收取重設密碼連結

---

## 2. 控制台總覽

登入後會進入 VMS Control Center，主要功能分為以下區塊：

![VMS 控制台](vms_sop_images/vms_sop_02_dashboard.png)

### 2.1 快捷功能

| 圖示 | 功能 | 說明 |
|------|------|------|
| 👥 | Team Management | 管理員工和用戶 |
| 📋 | Site Pass | 通行證管理 |
| 🔍 | Security Scanner | 入口掃描 QR Code |
| 📝 | Self Registration | 訪客自助註冊 |
| ⚠️ | NCR | 不合格報告 |
| ✅ | CAPA | 改正措施追蹤 |

### 2.2 待處理項目

- **Pending Approval**: 待核准的通行證
- **Active On-Site**: 目前在場人員

---

## 3. 通行證管理 (Site Pass)

### 3.1 通行證類型

| 類型 | 說明 | 有效期 |
|------|------|--------|
| **Visitor** | 訪客通行證 | 單日有效 |
| **Worker** | 工人通行證 | 多日有效，可重複進出 |
| **Vendor** | 供應商通行證 | 依合約設定 |

### 3.2 建立新通行證

**步驟：**

1. 進入「Site Pass」模組
2. 點擊「+ Add Site Pass」
3. 填寫基本資料：
   - **Pass Type**: 選擇通行證類型
   - **Person Name**: 姓名
   - **Mobile**: 手機號碼
   - **Email**: 電子郵件（可選）
   - **Company**: 公司名稱
   - **Purpose**: 訪問目的
   - **Valid From**: 有效開始日期
   - **Valid Until**: 有效結束日期
4. 點擊「Save」儲存

### 3.3 核准通行證

**步驟：**

1. 進入「Pending Approval」
2. 選擇待核准的通行證
3. 審核資料無誤後，將狀態改為「Issued」
4. 點擊「Save」
5. 系統自動發送核准郵件（含 QR Code）

### 3.4 通行證狀態流程

```
Draft → Pending Approval → Issued → Checked In → Checked Out
                              ↓
                          Rejected
```

| 狀態 | 說明 |
|------|------|
| Draft | 草稿 |
| Pending Approval | 待核准 |
| Issued | 已核發 |
| Checked In | 已入場 |
| Checked Out | 已離場 |
| Expired | 已過期 |
| Rejected | 已拒絕 |
| Cancelled | 已取消 |

---

## 4. 訪客註冊 (Self Registration)

### 4.1 訪客自助註冊流程

訪客可透過以下網址自行註冊：
**https://pansen.vmsys.co/register**

**註冊步驟：**

1. 選擇通行證類型
2. 輸入個人資料
3. 輸入手機號碼
4. 點擊「Send OTP」接收驗證碼
5. 輸入 6 位數 OTP 驗證碼
6. 提交申請

### 4.2 OTP 驗證說明

- 系統使用 MSG91 發送 SMS 驗證碼
- 驗證碼為 6 位數字
- 有效期限 10 分鐘
- 如未收到，可點擊「Resend OTP」重新發送

---

## 5. 安全掃描 (Security Scanner)

### 5.1 功能說明

Security Scanner 供保全人員在入口處掃描訪客 QR Code，執行 Check-in/Check-out。

**網址**: https://pansen.vmsys.co/security-scanner

### 5.2 掃描入場 (Check-in)

**步驟：**

1. 開啟 Security Scanner 頁面
2. 點擊「Scan」或使用手機相機掃描
3. 掃描訪客的 QR Code
4. 系統顯示訪客資料
5. 確認資料正確後點擊「Check In」

### 5.3 掃描離場 (Check-out)

**步驟：**

1. 掃描訪客 QR Code
2. 系統識別已入場狀態
3. 點擊「Check Out」完成離場登記

### 5.4 掃描結果說明

| 狀態 | 顯示 | 動作 |
|------|------|------|
| Valid Pass | 綠色 ✓ | 可進行 Check-in/out |
| Expired | 紅色 ✗ | 通行證已過期 |
| Already Checked In | 黃色 ⚠ | 已入場，可 Check-out |
| Invalid | 紅色 ✗ | 無效 QR Code |

---

## 6. 團隊管理 (Team Management)

### 6.1 新增用戶

**步驟：**

1. 進入「Team Management」
2. 點擊「+ Add User」
3. 填寫用戶資料：
   - Email
   - Full Name
   - Role (角色)
4. 點擊「Save」
5. 系統發送邀請郵件給新用戶

### 6.2 用戶角色

| 角色 | 權限 |
|------|------|
| **VMS Admin** | 完整管理權限 |
| **VMS Manager** | 管理通行證、報表 |
| **VMS Security** | 使用 Scanner、查看 Dashboard |
| **VMS HR Admin** | 管理通行證、審計日誌 |

### 6.3 編輯/停用用戶

1. 在用戶列表中選擇目標用戶
2. 編輯資料或變更角色
3. 如需停用，將「Enabled」取消勾選
4. 點擊「Save」

---

## 7. 不合格報告 (NCR)

### 7.1 建立 NCR

**步驟：**

1. 進入「NCR」模組
2. 點擊「+ Add NCR」
3. 填寫報告內容：
   - **Title**: 標題
   - **Category**: 類別
   - **Description**: 詳細描述
   - **Severity**: 嚴重程度 (Low/Medium/High/Critical)
   - **Photos**: 上傳現場照片
4. 點擊「Save」提交

### 7.2 NCR 狀態

| 狀態 | 說明 |
|------|------|
| Open | 新建立，待處理 |
| In Progress | 處理中 |
| Resolved | 已解決 |
| Closed | 已關閉 |

---

## 8. 改正措施 (CAPA)

### 8.1 建立 CAPA

CAPA (Corrective and Preventive Action) 用於追蹤改正措施。

**步驟：**

1. 進入「CAPA」模組
2. 點擊「+ Add CAPA」
3. 填寫：
   - **Related NCR**: 關聯的 NCR
   - **Action Type**: Corrective / Preventive
   - **Description**: 措施說明
   - **Assigned To**: 負責人
   - **Due Date**: 期限
4. 點擊「Save」

### 8.2 追蹤進度

1. 在 CAPA 列表查看所有改正措施
2. 點擊進入查看詳情
3. 更新進度狀態
4. 完成後標記為「Completed」

---

## 9. 報表與統計

### 9.1 可用報表

| 報表名稱 | 說明 |
|----------|------|
| **Visitor Statistics** | 訪客統計分析 |
| **NCR Summary** | NCR 匯總報表 |
| **Site Pass Report** | 通行證報表 |

### 9.2 查看報表

**步驟：**

1. 進入對應的報表模組
2. 設定篩選條件（日期範圍、類型等）
3. 點擊「Refresh」或「Run」
4. 可匯出為 Excel 或 PDF

### 9.3 常用篩選條件

- **Date Range**: 日期範圍
- **Pass Type**: 通行證類型
- **Status**: 狀態
- **Project Site**: 站點

---

## 10. 系統設定

### 10.1 Project Site 管理

**路徑**: VMS Control Center → Project Site

**新增站點：**

1. 點擊「+ Add Project Site」
2. 填寫站點資料：
   - Site Name
   - Address
   - Contact Person
3. 點擊「Save」

### 10.2 Checklist Template

**路徑**: VMS Control Center → Checklist Template

用於建立標準檢查表模板，可套用於巡檢。

### 10.3 DPDP Settings (資料保護)

**路徑**: VMS Control Center → DPDP Settings

設定資料保護相關參數，符合 DPDP 法規要求。

---

## 11. Email 地址修改

### 11.1 Email 類型說明

VMS 系統中有以下幾種 Email 地址：

| Email 類型 | 位置 | 可修改 | 說明 |
|------------|------|--------|------|
| **訪客 Email** | Site Pass | ✅ 可以 | 通行證上的訪客聯絡 Email |
| **Host Email** | Site Pass | ⚠️ 間接 | 從 Host User 帶入，需改用戶 |
| **團隊成員 Email** | Team Management | ❌ 不可 | 是系統登入帳號，無法直接修改 |

### 11.2 修改 Site Pass 訪客 Email

**步驟：**

1. 進入「Site Pass」模組
2. 找到並開啟目標通行證
3. 編輯「Email」欄位
4. 點擊「Save」儲存
5. 如需重新發送核准郵件，使用「Send Email」功能

**注意事項：**
- 修改 Email 後，舊地址將不再收到通知
- 建議修改後重新發送核准郵件確保訪客收到 QR Code

### 11.3 變更團隊成員 Email

**重要說明：**
團隊成員的 Email 是系統登入帳號（Login ID），無法直接修改。

**替代方案 - 停用舊帳號並邀請新帳號：**

1. 進入「Team Management」
2. 找到需要變更 Email 的成員
3. 點擊「Edit」開啟編輯視窗
4. 將「Status」設為「Inactive」
5. 點擊「Save」儲存
6. 點擊「+ Invite Member」按鈕
7. 輸入新的 Email 地址
8. 輸入相同的姓名
9. 選擇相同的角色
10. 點擊「Confirm」送出邀請
11. 新用戶會收到邀請郵件，可使用新 Email 登入

### 11.4 Email 修改限制說明

| 操作 | 允許 | 原因 |
|------|------|------|
| 修改 Site Pass 訪客 Email | ✅ | 只是聯絡資訊欄位 |
| 修改團隊成員姓名 | ✅ | 可在 Team Management 編輯 |
| 修改團隊成員角色 | ✅ | 可在 Team Management 編輯 |
| 修改團隊成員 Email | ❌ | Email 是登入帳號，系統限制 |
| 停用團隊成員帳號 | ✅ | 可在 Team Management 設為 Inactive |

---

## 附錄 A: 常見問題 (FAQ)

### Q1: 訪客沒有收到 OTP 簡訊？

**解決方案：**
1. 確認手機號碼格式正確（含國碼，如 91xxxxxxxxxx）
2. 等待 1-2 分鐘，簡訊可能延遲
3. 點擊「Resend OTP」重新發送
4. 如持續未收到，聯繫系統管理員

### Q2: QR Code 掃描失敗？

**解決方案：**
1. 確保 QR Code 清晰可見
2. 檢查通行證是否已過期
3. 確認通行證狀態為「Issued」
4. 重新整理 Scanner 頁面

### Q3: 如何查看審計日誌？

**步驟：**
1. 進入「VMS Audit Log」
2. 設定日期範圍
3. 可按用戶、動作類型篩選

### Q4: 忘記管理員密碼？

**解決方案：**
1. 在登入頁面點擊「Forgot Password?」
2. 輸入管理員 Email
3. 檢查郵箱收取重設連結
4. 如無法重設，聯繫系統管理員

### Q5: 如何修改團隊成員的 Email 地址？

**說明：**
團隊成員的 Email 是系統登入帳號，無法直接修改。

**解決方案：**
1. 在 Team Management 中將舊帳號設為 Inactive
2. 使用新 Email 邀請新成員
3. 選擇相同的角色和權限
4. 新用戶會收到邀請郵件

詳細步驟請參考 [11.3 變更團隊成員 Email](#113-變更團隊成員-email)

### Q6: 如何修改 Site Pass 上的訪客 Email？

**解決方案：**
1. 進入 Site Pass 模組
2. 開啟目標通行證
3. 直接編輯 Email 欄位
4. 點擊 Save 儲存
5. 可選擇重新發送核准郵件

---

## 附錄 B: 聯絡支援

| 項目 | 資訊 |
|------|------|
| **系統管理員** | admin@pansen.vmsys.co |
| **技術支援** | support@vmsys.co |
| **緊急聯繫** | +91-XXXXXXXXXX |

---

## 附錄 C: 系統網址一覽

| 功能 | 網址 |
|------|------|
| 管理後台 | https://pansen.vmsys.co |
| 訪客註冊 | https://pansen.vmsys.co/register |
| Security Scanner | https://pansen.vmsys.co/security-scanner |
| Auditor Scanner | https://pansen.vmsys.co/auditor-scanner |
| QR Poster | https://pansen.vmsys.co/qr-poster |

---

**文檔結束**

*本手冊適用於 VMS 系統 Pansen 租戶站點管理員。如有更新，請參考最新版本。*
