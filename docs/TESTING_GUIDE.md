# 🧪 Testing Guide - Streamlit & Microservices

## ✅ Pre-Test Checklist

### **1. Environment Setup**

- [x] All services implemented
- [x] API Gateway configured
- [x] .env file organized
- [x] Streamlit updated to use Gateway
- [x] Dashboard endpoint added to Portfolio Service

### **2. Files Modified**

| File                                | Change                                | Status |
| ----------------------------------- | ------------------------------------- | ------ |
| `app.py`                            | Removed direct `price_service` import | ✅     |
| `app.py`                            | All price calls through Gateway       | ✅     |
| `app.py`                            | Dashboard call updated                | ✅     |
| `services/portfolio_service/app.py` | Added `/dashboard/{user_id}` endpoint | ✅     |

---

## 🚀 Quick Start Testing

### **Step 1: Start All Services**

```powershell
# In project root directory
.\start_all_services.ps1
```

**Expected Output:**

```
Starting FinBuddy Microservices...
✓ API Gateway (Port 8000)
✓ User Service (Port 8001)
✓ Portfolio Service (Port 8002)
✓ News Service (Port 8003)
✓ AI Service (Port 8004)
✓ Risk Service (Port 8005)
✓ Learning Service (Port 8006)

All services started! 🚀
```

### **Step 2: Verify Services Health**

```powershell
# Check if all services are running
curl http://localhost:8000/health
```

**Expected Response:**

```json
{
  "gateway": "healthy",
  "services": {
    "users": "healthy",
    "portfolio": "healthy",
    "news": "healthy",
    "ai": "healthy",
    "risk": "healthy",
    "learning": "healthy"
  }
}
```

### **Step 3: Start Streamlit**

```powershell
streamlit run app.py
```

**Expected:** Browser opens at `http://localhost:8501`

---

## 🧪 Test Cases

### **Test 1: User Registration & Login** ✅

**Steps:**

1. Go to **🏠 Home** page
2. Switch to "Register" tab
3. Enter: Username, Email, Password
4. Click "Register"
5. Switch to "Login" tab
6. Enter: User ID (from registration), Password
7. Click "Login"

**Expected:**

- ✅ Registration success message
- ✅ User ID displayed
- ✅ Login redirects to Dashboard
- ✅ Username shown in sidebar

**API Calls:**

```
POST /api/users/register
GET /api/users/{id}
```

---

### **Test 2: Dashboard View** ✅

**Prerequisites:** Logged in user

**Steps:**

1. Navigate to **📊 Dashboard**
2. Verify metrics display

**Expected:**

- ✅ Portfolio Value displayed
- ✅ Total Invested shown
- ✅ Number of Investments count
- ✅ Top Performers list (if investments exist)
- ✅ Recent Investments table

**API Calls:**

```
GET /api/portfolio/dashboard/{user_id}
```

**API Gateway Logs:**

```
INFO: GET /api/portfolio/dashboard/1 → http://localhost:8002/dashboard/1
```

**Portfolio Service Logs:**

```
📊 Fetching dashboard for user 1
```

---

### **Test 3: Live Price Fetching** 🎯 **CRITICAL**

**Prerequisites:** Logged in user

**Steps:**

1. Go to **➕ Add Investment**
2. Enter Symbol: `AAPL`
3. Select Asset Type: `stock`
4. Click **🔄 Live Price** button
5. Verify price display

**Expected:**

- ✅ Loading spinner appears
- ✅ Current price displayed (e.g., $234.56)
- ✅ 24h change shown with color
- ✅ Data source indicated (Yahoo Finance)
- ✅ Asset name shown (Apple Inc.)
- ✅ "Set Live Price" button available

**API Calls:**

```
GET /api/portfolio/price/AAPL?asset_type=stock
```

**API Gateway Logs:**

```
INFO: GET /api/portfolio/price/AAPL?asset_type=stock → http://localhost:8002/price/AAPL
```

**Portfolio Service Logs:**

```
💵 Fetching price for AAPL (stock)
```

**Test Variations:**

- Try Crypto: `BTC`, `ETH` with asset_type=`crypto`
- Try different stocks: `GOOGL`, `MSFT`, `TSLA`
- Try invalid symbol: `INVALID123` (should show error)

---

### **Test 4: Add Investment with Live Price** ✅

**Prerequisites:** Price fetched from Test 3

**Steps:**

1. Click **✅ Set Live Price** button
2. Adjust quantity (e.g., `10`)
3. Click **📊 Add Investment**

**Expected:**

- ✅ Success message with balloons 🎈
- ✅ Risk analysis shown (low/medium/high)
- ✅ Recommendations displayed
- ✅ AI insights provided

**API Calls:**

```
POST /api/investments/{user_id}
  Body: {
    "symbol": "AAPL",
    "asset_type": "stock",
    "quantity": 10,
    "purchase_price": 234.56
  }
```

---

### **Test 5: Portfolio View with Price Refresh** 🎯 **CRITICAL**

**Prerequisites:** At least one investment added

**Steps:**

1. Go to **💼 Portfolio**
2. View existing investments
3. Click **🔄 Refresh All Prices** button
4. Wait for update
5. Click individual **🔄** button on one investment

**Expected:**

- ✅ All prices update simultaneously
- ✅ Success message shows count (e.g., "Updated 3/3 prices")
- ✅ Individual refresh updates single investment
- ✅ Total portfolio value recalculated
- ✅ Gain/loss percentages updated

**API Calls:**

```
# Refresh all (called multiple times)
GET /api/portfolio/price/{symbol}?asset_type={type}

# Individual refresh
GET /api/portfolio/price/{symbol}?asset_type={type}
```

**Logs to Watch:**

- Multiple price fetch calls
- No direct `price_service` imports
- All calls through Gateway on port 8000

---

### **Test 6: Market News Fetching** ✅

**Steps:**

1. Go to **📰 Market News**
2. Select news sources (checkboxes)
3. Click **🔄 Fetch Latest News**
4. View articles

**Expected:**

- ✅ News articles load
- ✅ Sentiment badges shown (Positive 😊, Neutral 😐, Negative 😞)
- ✅ Source displayed
- ✅ Timestamps shown
- ✅ Links work

**API Calls:**

```
GET /api/news/latest?sources=economictimes,newsapi&limit=10
GET /api/news/sources
```

---

### **Test 7: AI Chat** ✅

**Prerequisites:** Logged in, GEMINI_API_KEY set in .env

**Steps:**

1. Go to **🤖 AI Chat**
2. Enter question: "What is dollar-cost averaging?"
3. Click **Send** or press Enter
4. View response

**Expected:**

- ✅ AI responds with financial advice
- ✅ Chat history maintained
- ✅ Streaming response (if enabled)
- ✅ Formatted with markdown

**API Calls:**

```
POST /api/ai/chat
  Body: {
    "user_id": 1,
    "message": "What is dollar-cost averaging?",
    "chat_history": []
  }
```

---

### **Test 8: Fraud Detection** ✅

**Steps:**

1. Go to **🛡️ Fraud Detection**
2. Test Scam Detector:
   - Enter: "URGENT! Your account has been locked. Click here to verify: bit.ly/verify123"
   - Click **🔍 Analyze Message**
3. Test URL Checker:
   - Enter: "https://paypal-secure-login.tk/account"
   - Click **🔗 Check URL**

**Expected:**

- ✅ Scam probability shown (e.g., 85%)
- ✅ Risk level indicated (🔴 High Risk)
- ✅ Red flags listed
- ✅ AI analysis provided
- ✅ URL legitimacy score displayed

**API Calls:**

```
POST /api/fraud/detect-scam
POST /api/fraud/check-url
```

---

### **Test 9: Risk Analysis** ✅

**Prerequisites:** Portfolio with investments

**Steps:**

1. Go to **📈 Risk Analysis**
2. View risk dashboard

**Expected:**

- ✅ Overall risk score (0-100)
- ✅ Risk level badge (Low/Medium/High)
- ✅ Diversification chart
- ✅ Asset allocation breakdown
- ✅ Recommendations list
- ✅ Individual investment risks

**API Calls:**

```
GET /api/risk/analyze-portfolio/{user_id}
```

---

## 🔍 Debugging Tips

### **Check Service Logs**

Each service outputs logs in its terminal window:

**API Gateway (Port 8000):**

```
INFO: 127.0.0.1:12345 - "GET /api/portfolio/price/AAPL HTTP/1.1" 200 OK
INFO: Forwarding to http://localhost:8002/price/AAPL
```

**Portfolio Service (Port 8002):**

```
💵 Fetching price for AAPL (stock)
```

### **Common Issues**

**Issue:** "Connection refused" error

- **Solution:** Ensure all services are running with `.\start_all_services.ps1`

**Issue:** "Price not found" error

- **Solution:** Check internet connection, verify symbol is valid

**Issue:** Empty dashboard

- **Solution:** Add at least one investment first

**Issue:** "Unauthorized" error

- **Solution:** Login again, check session state

**Issue:** AI not responding

- **Solution:** Verify `GEMINI_API_KEY` in `.env` file

---

## 📊 Performance Benchmarks

### **Expected Response Times**

| Endpoint             | Expected Time   | Status              |
| -------------------- | --------------- | ------------------- |
| User Registration    | < 500ms         | ⚡ Fast             |
| User Login           | < 300ms         | ⚡ Fast             |
| Fetch Portfolio      | < 200ms         | ⚡ Fast             |
| **Live Price Fetch** | **1-3 seconds** | 🐢 External API     |
| Add Investment       | < 500ms         | ⚡ Fast             |
| Dashboard Load       | < 400ms         | ⚡ Fast             |
| News Fetch           | 2-5 seconds     | 🐢 Multiple sources |
| AI Chat              | 2-10 seconds    | 🐢 LLM generation   |
| Risk Analysis        | 1-3 seconds     | 🚀 With AI          |
| Fraud Detection      | 1-2 seconds     | 🚀 With AI          |

---

## ✅ Success Criteria

### **All Tests Pass When:**

- [x] No direct service imports in `app.py`
- [x] All API calls go through Gateway (port 8000)
- [x] Live pricing works through `/api/portfolio/price/{symbol}`
- [x] Dashboard loads from `/api/portfolio/dashboard/{user_id}`
- [x] All 9 Streamlit pages functional
- [x] No 404 or 500 errors in normal operation
- [x] Gateway properly routes to all 6 services
- [x] Logs show proper service-to-service calls

---

## 🎯 Critical Path Test (3 Minutes)

**Fastest way to verify everything works:**

1. **Start services** (30 sec)

   ```powershell
   .\start_all_services.ps1
   streamlit run app.py
   ```

2. **Register & Login** (30 sec)

   - Register new user
   - Login with credentials

3. **Test Live Pricing** (60 sec) 🎯

   - Go to Add Investment
   - Enter `AAPL`
   - Click **🔄 Live Price**
   - Verify price displays
   - Add to portfolio

4. **View Dashboard** (30 sec)

   - Go to Dashboard
   - Verify metrics show

5. **Refresh Prices** (30 sec) 🎯
   - Go to Portfolio
   - Click **🔄 Refresh All Prices**
   - Verify prices update

**If all 5 steps pass → ✅ COMPLETE SUCCESS!**

---

## 📝 Test Results Template

```
=== FinBuddy Microservices Test Results ===

Date: [DATE]
Tester: [NAME]

Services Status:
[ ] API Gateway (8000)
[ ] User Service (8001)
[ ] Portfolio Service (8002)
[ ] News Service (8003)
[ ] AI Service (8004)
[ ] Risk Service (8005)
[ ] Learning Service (8006)

Test Cases:
[ ] User Registration
[ ] User Login
[ ] Dashboard Load
[ ] Live Price Fetch  🎯 CRITICAL
[ ] Add Investment
[ ] Portfolio View
[ ] Price Refresh  🎯 CRITICAL
[ ] Market News
[ ] AI Chat
[ ] Fraud Detection
[ ] Risk Analysis

Architecture Verification:
[ ] No direct service imports
[ ] All calls through Gateway
[ ] Proper routing logs
[ ] No errors in operation

Overall Result: [ PASS / FAIL ]

Notes:
_________________________________
_________________________________
```

---

## 🚀 Next Steps After Testing

**If All Tests Pass:**

1. ✅ Mark migration as complete
2. 📝 Update FINAL_SUCCESS.md
3. 🎉 Celebrate! 🎊
4. 📚 Review optional enhancements

**If Tests Fail:**

1. 📋 Check service logs
2. 🐛 Debug specific endpoint
3. 🔧 Fix issue
4. 🔄 Retest

---

_Testing Guide v2.0_
_Microservices Migration - Final Phase_
