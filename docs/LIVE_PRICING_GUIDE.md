# 🔄 Live Price Integration - Feature Documentation

## 📋 Overview

FinBuddy now supports **real-time price fetching** for stocks and cryptocurrencies using:

- **Yahoo Finance API** - For stocks, ETFs, and other securities
- **CoinGecko API** - For cryptocurrencies

## ✨ Features Added

### 1. 🆕 Price Service (`price_service.py`)

A dedicated service that fetches live market prices from multiple sources.

**Supported Assets:**

- ✅ **Stocks** - AAPL, GOOGL, MSFT, TSLA, etc.
- ✅ **Cryptocurrencies** - BTC, ETH, SOL, BNB, etc.
- ✅ **ETFs** - Automatically detected
- ✅ Smart fallback - Tries crypto if stock lookup fails

**Key Functions:**

```python
get_stock_price(symbol)      # Yahoo Finance
get_crypto_price(symbol)     # CoinGecko
get_live_price(symbol, type) # Smart router
```

### 2. 📊 Add Investment Page Enhancement

**Location:** Add Investment Page

**New Feature:** "🔄 Live Price" button next to price input field

**How It Works:**

1. User enters stock/crypto symbol (e.g., AAPL, BTC)
2. Clicks "🔄 Live Price" button
3. System fetches current market price
4. Price input auto-updates
5. Shows 24h change and data source

**User Experience:**

- ✅ Instant price lookup
- ✅ Shows 24h price change with emoji (📈/📉)
- ✅ Displays data source (Yahoo Finance/CoinGecko)
- ✅ Error handling with helpful tips
- ✅ Auto-refreshes the input field

### 3. 💼 Portfolio Page Enhancement

**Location:** Portfolio Page

**New Features:**

1. **"🔄 Refresh All Prices"** - Updates all investments at once
2. **Individual refresh buttons** - Update single investment
3. **Live price display** - Shows current market price vs purchase price
4. **24h change indicator** - Percentage change in last 24 hours
5. **Data source badge** - Shows where price came from

**Portfolio Display:**

- Live Price (with 24h change)
- Real-time Gain/Loss calculation
- Updated Total Value
- Source indicator

## 🎯 Supported Symbols

### 📈 Stocks (Yahoo Finance)

```
Tech: AAPL, GOOGL, MSFT, TSLA, NVDA, META, AMZN
Finance: JPM, BAC, GS, MS, C
Retail: WMT, TGT, COST
Healthcare: JNJ, PFE, UNH
Energy: XOM, CVX, BP
... and thousands more!
```

### 💰 Cryptocurrencies (CoinGecko)

```
Major: BTC, ETH, BNB, SOL, XRP, ADA
DeFi: UNI, LINK, AAVE, SUSHI, COMP
Stablecoins: USDT, USDC, DAI, BUSD
Alt-coins: DOGE, MATIC, AVAX, DOT, ATOM
... and 14,000+ more!
```

## 🚀 How to Use

### Adding Investment with Live Price:

1. **Navigate** to "➕ Add Investment"
2. **Enter** stock symbol (e.g., "AAPL" or "BTC")
3. **Select** asset type (stock/crypto)
4. **Click** "🔄 Live Price" button
5. **Wait** for price to load (1-2 seconds)
6. **Review** the fetched price and 24h change
7. **Adjust** quantity as needed
8. **Click** "📊 Add Investment"

### Refreshing Portfolio Prices:

#### Option 1: Refresh All

1. **Go to** "💼 Portfolio"
2. **Click** "🔄 Refresh All Prices" (top right)
3. **Wait** for all prices to update
4. **View** updated portfolio values

#### Option 2: Individual Refresh

1. **Expand** any investment card
2. **Click** small "🔄" button in that card
3. **See** instant price update for that symbol

## 💡 Examples

### Example 1: Adding Apple Stock

```
Symbol: AAPL
Asset Type: stock
Click "🔄 Live Price"
→ Shows: $270.37 📉 24h: -0.38%
→ Source: Yahoo Finance
```

### Example 2: Adding Bitcoin

```
Symbol: BTC
Asset Type: crypto
Click "🔄 Live Price"
→ Shows: $110,196.00 📈 24h: +0.04%
→ Source: CoinGecko
```

### Example 3: Portfolio Refresh

```
Portfolio has: AAPL, GOOGL, BTC, ETH
Click "🔄 Refresh All Prices"
→ Updates: 4/4 investments
→ Shows: New total portfolio value
→ Displays: Updated gain/loss for each
```

## 🔧 Technical Details

### API Limits

- **Yahoo Finance:** Unlimited (free, no key needed)
- **CoinGecko:**
  - Free tier: 10-50 calls/minute
  - No API key required
  - Rate limiting handled automatically

### Data Accuracy

- ✅ Real-time or near real-time (< 15 min delay)
- ✅ 24h price change included
- ✅ Market cap data available
- ✅ Multiple fallback mechanisms

### Error Handling

- ❌ Invalid symbol → User-friendly error message
- ❌ API down → Shows helpful tips
- ❌ Rate limit → Graceful degradation
- ❌ Network error → Retry mechanism

### Performance

- ⚡ Stock lookup: 1-2 seconds
- ⚡ Crypto lookup: 1-3 seconds
- ⚡ Cached results (session-based)
- ⚡ Async-ready architecture

## 📊 Price Data Returned

### Stock Price Response:

```json
{
  "symbol": "AAPL",
  "name": "Apple Inc.",
  "price": 270.37,
  "change_24h": -0.38,
  "market_cap": 3900000000000,
  "source": "Yahoo Finance",
  "asset_type": "stock"
}
```

### Crypto Price Response:

```json
{
  "symbol": "BTC",
  "name": "Bitcoin",
  "price": 110196.0,
  "change_24h": 0.04,
  "market_cap": 2100000000000,
  "source": "CoinGecko",
  "asset_type": "crypto"
}
```

## 🎨 UI/UX Enhancements

### Visual Indicators:

- 📈 Green arrow for price increase
- 📉 Red arrow for price decrease
- 🔄 Spinning icon during fetch
- ✅ Success checkmark
- ❌ Error X mark
- 📊 Source badge

### User Feedback:

- Spinner while loading
- Success message with price
- Error message with tips
- Info box with 24h change
- Auto-refresh on update

## 🛡️ Security & Privacy

### Data Safety:

- ✅ No API keys stored in frontend
- ✅ Read-only API access
- ✅ No personal data sent to price APIs
- ✅ HTTPS connections only
- ✅ No data logged externally

### Rate Limiting:

- Implemented on CoinGecko side
- Graceful handling of limits
- User-friendly error messages

## 🐛 Troubleshooting

### Issue: "Could not fetch price"

**Solutions:**

1. Check symbol spelling (AAPL not APPLE)
2. Verify internet connection
3. Try different symbol
4. Check if market is open (stocks)
5. Use crypto symbols for crypto assets

### Issue: "Price not updating"

**Solutions:**

1. Click refresh button again
2. Check browser console for errors
3. Verify backend is running
4. Clear browser cache
5. Restart Streamlit app

### Issue: "Wrong price displayed"

**Solutions:**

1. Markets may be closed (stocks show last close)
2. Crypto prices are 24/7 real-time
3. Click refresh for latest
4. Check source badge

## 📈 Future Enhancements

### Planned Features:

1. ⏰ **Auto-refresh** - Update prices every 5 minutes
2. 🔔 **Price alerts** - Notify when target price reached
3. 📊 **Price history** - Show historical charts
4. 💹 **More sources** - Add Alpha Vantage, Finnhub
5. 🌍 **Multi-currency** - Support EUR, GBP, INR
6. 📉 **Technical indicators** - RSI, MACD, Bollinger Bands
7. 🎯 **Price predictions** - AI-powered forecasts
8. 📱 **Push notifications** - Mobile alerts

## 🎓 Learn More

### APIs Used:

- **Yahoo Finance (yfinance)**: https://pypi.org/project/yfinance/
- **CoinGecko**: https://www.coingecko.com/en/api/documentation

### Related Files:

- `price_service.py` - Core price fetching logic
- `app.py` - Frontend integration (lines 395-460, 365-410)
- `requirements.txt` - Dependencies

### Testing:

```bash
# Test price service
python price_service.py

# Test in app
streamlit run app.py
# Navigate to Add Investment
# Click "Get Live Price"
```

## 📝 Code Examples

### Fetch Stock Price:

```python
from price_service import get_stock_price

price_data = get_stock_price("AAPL")
print(f"Price: ${price_data['price']:.2f}")
```

### Fetch Crypto Price:

```python
from price_service import get_crypto_price

price_data = get_crypto_price("BTC")
print(f"Price: ${price_data['price']:.2f}")
```

### Smart Fetch:

```python
from price_service import get_live_price

# Auto-detects type
price_data = get_live_price("AAPL", "stock")
price_data = get_live_price("BTC", "crypto")
```

## ✅ Testing Results

### Test Run Output:

```
🧪 Testing Price Service...

📈 Testing Stocks:
  AAPL: $270.37 (-0.38%)    ✅
  GOOGL: $281.19 (-0.10%)   ✅
  MSFT: $517.81 (-1.52%)    ✅

📊 Testing Crypto:
  BTC: $110,196.00 (-0.04%) ✅
  ETH: $3,859.64 (-0.30%)   ✅
  SOL: $184.29 (-0.45%)     ✅

✅ All tests passed!
```

## 🎉 Summary

### What's New:

✅ Real-time stock prices (Yahoo Finance)
✅ Real-time crypto prices (CoinGecko)
✅ Live price button on Add Investment page
✅ Refresh all/individual prices on Portfolio
✅ 24h price change indicators
✅ Data source badges
✅ Smart symbol detection
✅ Comprehensive error handling

### Benefits:

💰 Accurate portfolio valuation
📊 Real-time market data
🚀 Better investment decisions
⚡ Fast and reliable
🎯 User-friendly interface

### Status:

🟢 **Fully Functional**
🟢 **Production Ready**
🟢 **Tested & Working**

---

**Version:** 2.0.0 (Live Pricing)
**Last Updated:** November 2, 2025
**Status:** ✅ Active
**Dependencies:** yfinance==0.2.66, pycoingecko==3.2.0
