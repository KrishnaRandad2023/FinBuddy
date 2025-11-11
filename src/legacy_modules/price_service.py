"""
Price Service - Fetch live prices from multiple sources
Supports stocks (Yahoo Finance) and crypto (CoinGecko)
"""
import logging
from typing import Optional, Dict, Any
import yfinance as yf
from pycoingecko import CoinGeckoAPI

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize CoinGecko client
cg = CoinGeckoAPI()

# Crypto symbol mapping (common symbols to CoinGecko IDs)
CRYPTO_MAPPING = {
    'BTC': 'bitcoin',
    'ETH': 'ethereum',
    'USDT': 'tether',
    'BNB': 'binancecoin',
    'SOL': 'solana',
    'XRP': 'ripple',
    'ADA': 'cardano',
    'AVAX': 'avalanche-2',
    'DOGE': 'dogecoin',
    'DOT': 'polkadot',
    'MATIC': 'matic-network',
    'LINK': 'chainlink',
    'UNI': 'uniswap',
    'ATOM': 'cosmos',
    'LTC': 'litecoin',
    'BCH': 'bitcoin-cash',
    'XLM': 'stellar',
    'ALGO': 'algorand',
    'VET': 'vechain',
    'ICP': 'internet-computer',
}


def get_crypto_price(symbol: str) -> Optional[Dict[str, Any]]:
    """
    Fetch cryptocurrency price from CoinGecko
    
    Args:
        symbol: Crypto symbol (e.g., BTC, ETH)
    
    Returns:
        Dict with price info or None if failed
    """
    try:
        symbol = symbol.upper()
        
        # Get CoinGecko ID from mapping
        coin_id = CRYPTO_MAPPING.get(symbol)
        
        if not coin_id:
            # Try to search for the coin
            logger.warning(f"⚠️ {symbol} not in mapping, searching CoinGecko...")
            search_results = cg.search(query=symbol)
            
            if search_results and 'coins' in search_results and len(search_results['coins']) > 0:
                coin_id = search_results['coins'][0]['id']
                logger.info(f"✅ Found coin ID: {coin_id}")
            else:
                logger.error(f"❌ Could not find {symbol} on CoinGecko")
                return None
        
        # Fetch price data
        logger.info(f"📊 Fetching price for {symbol} (ID: {coin_id})...")
        price_data = cg.get_price(
            ids=coin_id,
            vs_currencies='usd',
            include_24hr_change=True,
            include_market_cap=True
        )
        
        if coin_id in price_data:
            data = price_data[coin_id]
            result = {
                'symbol': symbol,
                'name': coin_id.replace('-', ' ').title(),
                'price': data.get('usd', 0),
                'change_24h': data.get('usd_24h_change', 0),
                'market_cap': data.get('usd_market_cap', 0),
                'source': 'CoinGecko',
                'asset_type': 'crypto'
            }
            
            logger.info(f"✅ Got {symbol} price: ${result['price']:.2f}")
            return result
        else:
            logger.error(f"❌ No price data returned for {symbol}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Error fetching crypto price for {symbol}: {str(e)}")
        return None


def get_stock_price(symbol: str) -> Optional[Dict[str, Any]]:
    """
    Fetch stock price from Yahoo Finance
    
    Args:
        symbol: Stock symbol (e.g., AAPL, GOOGL)
    
    Returns:
        Dict with price info or None if failed
    """
    try:
        symbol = symbol.upper()
        logger.info(f"📈 Fetching stock price for {symbol}...")
        
        # Create ticker object
        ticker = yf.Ticker(symbol)
        
        # Get current price info
        info = ticker.info
        
        if not info or 'currentPrice' not in info:
            # Try fast_info as fallback
            try:
                fast_info = ticker.fast_info
                current_price = fast_info.last_price
                
                result = {
                    'symbol': symbol,
                    'name': symbol,
                    'price': current_price,
                    'change_24h': 0,  # Not available in fast_info
                    'market_cap': 0,
                    'source': 'Yahoo Finance',
                    'asset_type': 'stock'
                }
                
                logger.info(f"✅ Got {symbol} price (fast): ${result['price']:.2f}")
                return result
            except:
                logger.error(f"❌ Could not fetch price for {symbol}")
                return None
        
        # Extract relevant info
        current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
        previous_close = info.get('previousClose', current_price)
        
        # Calculate 24h change
        change_24h = ((current_price - previous_close) / previous_close * 100) if previous_close > 0 else 0
        
        result = {
            'symbol': symbol,
            'name': info.get('longName', symbol),
            'price': current_price,
            'change_24h': change_24h,
            'market_cap': info.get('marketCap', 0),
            'source': 'Yahoo Finance',
            'asset_type': 'stock'
        }
        
        logger.info(f"✅ Got {symbol} price: ${result['price']:.2f}")
        return result
        
    except Exception as e:
        logger.error(f"❌ Error fetching stock price for {symbol}: {str(e)}")
        return None


def get_live_price(symbol: str, asset_type: str = "stock") -> Optional[Dict[str, Any]]:
    """
    Fetch live price based on asset type
    
    Args:
        symbol: Symbol to fetch (e.g., AAPL, BTC)
        asset_type: Type of asset ('stock', 'crypto', 'etf', etc.)
    
    Returns:
        Dict with price info or None if failed
    """
    try:
        logger.info(f"🔍 Fetching live price for {symbol} (type: {asset_type})...")
        
        # Route to appropriate service
        if asset_type.lower() in ['crypto', 'cryptocurrency']:
            return get_crypto_price(symbol)
        else:
            # Try stock first
            result = get_stock_price(symbol)
            
            # If stock fails and symbol looks like crypto, try crypto
            if not result and len(symbol) <= 5:
                logger.info(f"🔄 Stock lookup failed, trying crypto...")
                result = get_crypto_price(symbol)
            
            return result
            
    except Exception as e:
        logger.error(f"❌ Error in get_live_price: {str(e)}")
        return None


# Test function
if __name__ == "__main__":
    print("🧪 Testing Price Service...\n")
    
    # Test stocks
    print("📈 Testing Stocks:")
    for symbol in ['AAPL', 'GOOGL', 'MSFT']:
        result = get_stock_price(symbol)
        if result:
            print(f"  {symbol}: ${result['price']:.2f} ({result['change_24h']:+.2f}%)")
        else:
            print(f"  {symbol}: ❌ Failed")
    
    print("\n📊 Testing Crypto:")
    # Test crypto
    for symbol in ['BTC', 'ETH', 'SOL']:
        result = get_crypto_price(symbol)
        if result:
            print(f"  {symbol}: ${result['price']:.2f} ({result['change_24h']:+.2f}%)")
        else:
            print(f"  {symbol}: ❌ Failed")
    
    print("\n✅ Testing complete!")
