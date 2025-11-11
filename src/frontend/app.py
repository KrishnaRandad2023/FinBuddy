"""
FinBuddy - Complete Streamlit Frontend
Professional UI for AI-Powered Financial Companion
"""
import streamlit as st
import requests
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime
import json

# Configuration
API_BASE_URL = "http://localhost:8000"
st.set_page_config(
    page_title="FinBuddy - AI Financial Companion",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        margin: 1rem 0;
    }
    .warning-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        margin: 1rem 0;
    }
    .danger-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
        margin: 1rem 0;
    }
    .stButton>button {
        width: 100%;
        border-radius: 0.5rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state with persistence using query params
if 'user_id' not in st.session_state:
    # Try to restore from query params (auto-login)
    query_params = st.query_params
    if 'uid' in query_params:
        try:
            st.session_state.user_id = int(query_params['uid'])
            st.session_state.username = query_params.get('uname', 'User')
        except:
            st.session_state.user_id = None
    else:
        st.session_state.user_id = None

if 'username' not in st.session_state:
    st.session_state.username = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Auto-persist login in URL (so refresh keeps you logged in)
if st.session_state.user_id:
    st.query_params.update({
        'uid': str(st.session_state.user_id),
        'uname': st.session_state.username or 'User'
    })

# Helper Functions
def check_server_status():
    """Check if backend server is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=3)
        return response.status_code == 200
    except:
        return False

def make_api_request(method, endpoint, data=None, json=None, timeout=10):
    """Make API request with error handling"""
    url = f"{API_BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, timeout=timeout)
        elif method == "POST":
            response = requests.post(url, json=json or data, timeout=timeout)
        
        if response.status_code in [200, 201]:
            return True, response.json()
        else:
            error_msg = response.json().get('detail', 'Unknown error')
            return False, error_msg
    except requests.exceptions.ConnectionError:
        return False, "❌ Server not connected! Run: start_server.ps1"
    except requests.exceptions.Timeout:
        return False, "⏱️ Request timed out"
    except Exception as e:
        return False, f"Error: {str(e)}"


def create_portfolio_chart(investments):
    """Create pie chart for portfolio distribution"""
    if not investments:
        return None
    
    df = pd.DataFrame(investments)
    df['total_value'] = df['current_price'] * df['quantity']
    
    fig = px.pie(df, values='total_value', names='symbol', 
                 title='Portfolio Distribution',
                 color_discrete_sequence=px.colors.qualitative.Set3)
    return fig

def create_performance_chart(investments):
    """Create bar chart for investment performance"""
    if not investments:
        return None
    
    df = pd.DataFrame(investments)
    df['gain_loss_pct'] = ((df['current_price'] - df['purchase_price']) / df['purchase_price'] * 100)
    
    fig = go.Figure(data=[
        go.Bar(
            x=df['symbol'],
            y=df['gain_loss_pct'],
            marker_color=['green' if x >= 0 else 'red' for x in df['gain_loss_pct']],
            text=[f"{x:.2f}%" for x in df['gain_loss_pct']],
            textposition='auto',
        )
    ])
    fig.update_layout(title='Investment Performance (%)', xaxis_title='Symbol', yaxis_title='Gain/Loss %')
    return fig

# Sidebar Navigation
with st.sidebar:
    st.markdown("### 🤖 FinBuddy AI")
    st.markdown("*Your Smart Financial Companion*")
    st.markdown("---")
    
    if st.session_state.user_id:
        st.success(f"👤 Logged in as: **{st.session_state.username}**")
        st.markdown("---")
    
    # Initialize nav selection if not exists
    if 'nav_selection' not in st.session_state:
        st.session_state.nav_selection = "🏠 Home"
    
    page = st.radio(
        "Navigation",
        ["🏠 Home", "👤 User Profile", "💼 Portfolio", "➕ Add Investment", 
         "💬 AI Chat", "🧠 Market Insights", "📚 Learn Finance", "🔍 Fraud Detection", "📊 Risk Analysis", "💡 AI Recommendations", "🎮 Portfolio Simulator", "📰 Market News"],
        index=["🏠 Home", "👤 User Profile", "💼 Portfolio", "➕ Add Investment", 
               "💬 AI Chat", "🧠 Market Insights", "📚 Learn Finance", "🔍 Fraud Detection", "📊 Risk Analysis", "💡 AI Recommendations", "🎮 Portfolio Simulator", "📰 Market News"].index(st.session_state.nav_selection) if st.session_state.nav_selection in ["🏠 Home", "👤 User Profile", "💼 Portfolio", "➕ Add Investment", "💬 AI Chat", "🧠 Market Insights", "📚 Learn Finance", "🔍 Fraud Detection", "📊 Risk Analysis", "💡 AI Recommendations", "🎮 Portfolio Simulator", "📰 Market News"] else 0
    )
    
    # Update nav_selection when radio changes
    if page != st.session_state.nav_selection:
        st.session_state.nav_selection = page
    
    st.markdown("---")
    if st.session_state.user_id:
        if st.button("🚪 Logout", key="logout_btn"):
            st.session_state.user_id = None
            st.session_state.username = None
            st.session_state.chat_history = []
            # Clear URL params to prevent auto-login
            st.query_params.clear()
            st.rerun()
    
    st.markdown("---")
    st.markdown("### Server Status")
    if check_server_status():
        st.success("✅ Server Online")
    else:
        st.error("❌ Server Offline")
        st.caption("Run: start_server.ps1")

# Main Content
if page == "🏠 Home":
    st.markdown("<h1 class='main-header'>💰 FinBuddy</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #666;'>Your AI-Powered Financial Companion</h3>", unsafe_allow_html=True)
    
    if not st.session_state.user_id:
        # Registration/Login Section
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("## Get Started")
            
            tab1, tab2 = st.tabs(["📝 Register", "🔐 Login"])
            
            with tab1:
                st.markdown("### Create New Account")
                reg_username = st.text_input("Username", key="reg_username")
                reg_email = st.text_input("Email", key="reg_email")
                reg_password = st.text_input("Password", type="password", key="reg_password")
                risk_tolerance = st.selectbox("Risk Tolerance", ["low", "medium", "high"], key="risk_select")
                
                if st.button("Register", key="register_btn"):
                    if reg_username and reg_email and reg_password:
                        with st.spinner("Creating account..."):
                            success, result = make_api_request("POST", "/api/users/register", {
                                "username": reg_username,
                                "email": reg_email,
                                "password": reg_password,
                                "risk_tolerance": risk_tolerance
                            })
                            
                            if success:
                                st.success(f"✅ {result.get('message', 'Registration successful!')}")
                                st.session_state.user_id = result['id']
                                st.session_state.username = result['username']
                                st.balloons()
                                st.rerun()
                            else:
                                st.error(f"❌ Registration failed: {result}")
                    else:
                        st.warning("⚠️ Please fill all fields")
            
            with tab2:
                st.markdown("### Login to Account")
                st.info("💡 For demo: Use any User ID from the registration")
                login_id = st.number_input("User ID", min_value=1, key="login_id")
                
                if st.button("Login", key="login_btn"):
                    with st.spinner("Logging in..."):
                        success, result = make_api_request("GET", f"/api/users/{login_id}")
                        
                        if success:
                            st.session_state.user_id = result['id']
                            st.session_state.username = result['username']
                            st.success(f"✅ Welcome back, {result['username']}!")
                            st.rerun()
                        else:
                            st.error(f"❌ Login failed: {result}")
    
    else:
        # Dashboard for logged-in users
        st.markdown(f"## Welcome back, {st.session_state.username}! 👋")
        
        # Fetch dashboard data from Portfolio Service
        success, dashboard = make_api_request("GET", f"/api/portfolio/dashboard/{st.session_state.user_id}")
        
        if success:
            # Key Metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "💼 Portfolio Value",
                    f"${dashboard['portfolio_summary']['total_value']:,.2f}",
                    f"{dashboard['portfolio_summary']['gain_loss_percentage']:.2f}%"
                )
            
            with col2:
                st.metric(
                    "📈 Total Invested",
                    f"${dashboard['portfolio_summary']['total_invested']:,.2f}"
                )
            
            with col3:
                st.metric(
                    "💰 Gain/Loss",
                    f"${dashboard['portfolio_summary']['gain_loss']:,.2f}",
                    delta_color="normal"
                )
            
            with col4:
                st.metric(
                    "🔢 Investments",
                    dashboard['portfolio_summary']['total_investments']
                )
            
            # Alerts
            if dashboard['alerts']['risk_alerts'] > 0 or dashboard['alerts']['fraud_alerts'] > 0:
                st.markdown("### ⚠️ Alerts")
                col1, col2 = st.columns(2)
                with col1:
                    if dashboard['alerts']['risk_alerts'] > 0:
                        st.warning(f"🚨 {dashboard['alerts']['risk_alerts']} Risk Alert(s)")
                with col2:
                    if dashboard['alerts']['fraud_alerts'] > 0:
                        st.error(f"🛡️ {dashboard['alerts']['fraud_alerts']} Fraud Alert(s)")
            
            # Quick Actions
            st.markdown("### Quick Actions")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if st.button("➕ Add Investment", key="quick_invest"):
                    st.session_state.nav_selection = "➕ Add Investment"
                    st.rerun()
            with col2:
                if st.button("💬 Chat with AI", key="quick_chat"):
                    st.session_state.nav_selection = "💬 AI Chat"
                    st.rerun()
            with col3:
                if st.button("📚 Learn", key="quick_learn"):
                    st.session_state.nav_selection = "📚 Learn Finance"
                    st.rerun()
            with col4:
                if st.button("🔍 Check Scam", key="quick_scam"):
                    st.session_state.nav_selection = "🔍 Fraud Detection"
                    st.rerun()

elif page == "👤 User Profile":
    st.markdown("## 👤 User Profile")
    
    if not st.session_state.user_id:
        st.warning("⚠️ Please login first")
    else:
        success, user_data = make_api_request("GET", f"/api/users/{st.session_state.user_id}")
        
        if success:
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.markdown("### Profile Information")
                st.info(f"**User ID:** {user_data['id']}")
                st.info(f"**Username:** {user_data['username']}")
                st.info(f"**Email:** {user_data['email']}")
                st.info(f"**Risk Tolerance:** {user_data['risk_tolerance'].upper()}")
                st.info(f"**Member Since:** {user_data['created_at'][:10]}")
            
            with col2:
                st.markdown("### Account Statistics")
                success, portfolio = make_api_request("GET", f"/api/portfolio/{st.session_state.user_id}")
                
                if success:
                    st.metric("Total Investments", portfolio['total_investments'])
                    
                    if portfolio['investments']:
                        df = pd.DataFrame(portfolio['investments'])
                        total_value = (df['current_price'] * df['quantity']).sum()
                        st.metric("Portfolio Value", f"${total_value:,.2f}")
        else:
            st.error(f"❌ Error loading profile: {user_data}")

elif page == "💼 Portfolio":
    st.markdown("## 💼 My Portfolio")
    
    if not st.session_state.user_id:
        st.warning("⚠️ Please login first")
    else:
        success, portfolio = make_api_request("GET", f"/api/portfolio/{st.session_state.user_id}")
        
        if success:
            if portfolio['total_investments'] == 0:
                st.info("📊 No investments yet. Start by adding your first investment!")
                if st.button("➕ Add Investment"):
                    st.session_state.nav_radio = "➕ Add Investment"
                    st.rerun()
            else:
                # Portfolio Overview
                st.markdown(f"### Total Investments: {portfolio['total_investments']}")
                
                # Charts
                col1, col2 = st.columns(2)
                
                with col1:
                    pie_chart = create_portfolio_chart(portfolio['investments'])
                    if pie_chart:
                        st.plotly_chart(pie_chart, width='stretch')
                
                with col2:
                    perf_chart = create_performance_chart(portfolio['investments'])
                    if perf_chart:
                        st.plotly_chart(perf_chart, width='stretch')
                
                # Investment List with Live Price Refresh
                col_header_1, col_header_2 = st.columns([3, 1])
                with col_header_1:
                    st.markdown("### Investment Details")
                with col_header_2:
                    if st.button("🔄 Refresh All Prices", key="refresh_all_prices", help="Update all prices to current market values"):
                        with st.spinner("Fetching live prices..."):
                            updated_count = 0
                            for inv in portfolio['investments']:
                                # Call API Gateway to fetch live price from Portfolio Service
                                success, price_data = make_api_request("GET", f"/api/portfolio/price/{inv['symbol']}?asset_type={inv['asset_type']}")
                                if success and price_data:
                                    updated_count += 1
                                    # Store in session for display
                                    if 'live_prices' not in st.session_state:
                                        st.session_state.live_prices = {}
                                    st.session_state.live_prices[inv['symbol']] = price_data
                            
                            if updated_count > 0:
                                st.success(f"✅ Updated {updated_count}/{len(portfolio['investments'])} prices")
                                st.rerun()
                            else:
                                st.warning("⚠️ Could not update prices")
                
                # Initialize live prices storage
                if 'live_prices' not in st.session_state:
                    st.session_state.live_prices = {}
                
                for inv in portfolio['investments']:
                    # Check if we have live price data
                    live_price_data = st.session_state.live_prices.get(inv['symbol'])
                    current_price = live_price_data['price'] if live_price_data else inv['current_price']
                    
                    with st.expander(f"📈 {inv['symbol']} - {inv['asset_type'].upper()}"):
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Quantity", inv['quantity'])
                            st.metric("Purchase Price", f"${inv['purchase_price']:.2f}")
                        with col2:
                            # Show live price if available
                            if live_price_data:
                                st.metric("Live Price", f"${current_price:.2f}", 
                                         f"{live_price_data.get('change_24h', 0):+.2f}%")
                                st.caption(f"📊 {live_price_data.get('source', 'N/A')}")
                            else:
                                st.metric("Current Price", f"${current_price:.2f}")
                        with col3:
                            gain_loss = (current_price - inv['purchase_price']) * inv['quantity']
                            gain_loss_pct = ((current_price - inv['purchase_price']) / inv['purchase_price'] * 100)
                            st.metric("Gain/Loss", f"${gain_loss:.2f}", f"{gain_loss_pct:.2f}%")
                        with col4:
                            total_value = current_price * inv['quantity']
                            st.metric("Total Value", f"${total_value:.2f}")
                            
                            # Individual refresh button
                            if st.button(f"🔄", key=f"refresh_{inv['id']}", help=f"Refresh {inv['symbol']} price"):
                                # Call API Gateway to fetch live price from Portfolio Service
                                success, price_data = make_api_request("GET", f"/api/portfolio/price/{inv['symbol']}?asset_type={inv['asset_type']}")
                                if success and price_data:
                                    st.session_state.live_prices[inv['symbol']] = price_data
                                    st.success(f"✅ Updated {inv['symbol']}")
                                    st.rerun()
                                else:
                                    st.error(f"❌ Could not fetch price")
        else:
            st.error(f"❌ Error loading portfolio: {portfolio}")

elif page == "➕ Add Investment":
    st.markdown("## ➕ Add New Investment")
    
    if not st.session_state.user_id:
        st.warning("⚠️ Please login first")
    else:
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("### Investment Details")
            
            symbol = st.text_input("Stock Symbol", placeholder="e.g., AAPL, GOOGL, BTC, ETH")
            
            # Initialize session state for price data and last symbol
            if 'fetched_price_data' not in st.session_state:
                st.session_state.fetched_price_data = None
            if 'last_symbol' not in st.session_state:
                st.session_state.last_symbol = ""
            if 'use_live_price' not in st.session_state:
                st.session_state.use_live_price = False
            if 'live_price_value' not in st.session_state:
                st.session_state.live_price_value = 100.0
            
            # Clear price data if symbol changes
            if symbol != st.session_state.last_symbol:
                st.session_state.fetched_price_data = None
                st.session_state.use_live_price = False
                st.session_state.last_symbol = symbol
            
            asset_type = st.selectbox("Asset Type", ["stock", "crypto", "bond", "etf", "mutual_fund"])
            quantity = st.number_input("Quantity", min_value=0.01, value=1.0, step=0.01)
            
            # Price input with live price button
            col_price_1, col_price_2 = st.columns([3, 1])
            with col_price_1:
                # Use live price if set, otherwise default
                if st.session_state.use_live_price and st.session_state.fetched_price_data:
                    default_price = st.session_state.fetched_price_data['price']
                else:
                    default_price = st.session_state.live_price_value
                
                purchase_price = st.number_input(
                    "Purchase Price ($)", 
                    min_value=0.01, 
                    value=default_price, 
                    step=0.01,
                    key="price_input"
                )
                
                # Update live_price_value when user manually changes it
                if not st.session_state.use_live_price:
                    st.session_state.live_price_value = purchase_price
            
            with col_price_2:
                st.markdown("<br>", unsafe_allow_html=True)  # Spacing to align button
                if st.button("🔄 Live Price", key="fetch_price_btn", help="Fetch current market price"):
                    if symbol:
                        with st.spinner(f"Fetching live price for {symbol}..."):
                            # Call API Gateway to fetch live price from Portfolio Service
                            success, price_data = make_api_request("GET", f"/api/portfolio/price/{symbol}?asset_type={asset_type}")
                            
                            if success and price_data:
                                # Store in session state so it persists
                                st.session_state.fetched_price_data = price_data
                                st.rerun()  # Refresh to update the price input
                            else:
                                st.session_state.fetched_price_data = None
                                st.error(f"❌ Could not fetch price for {symbol}")
                                st.info("💡 Tip: Use symbols like AAPL, GOOGL for stocks or BTC, ETH for crypto")
                    else:
                        st.warning("⚠️ Please enter a symbol first")
            
            # Display fetched price info (persists after rerun)
            if st.session_state.fetched_price_data:
                price_data = st.session_state.fetched_price_data
                
                # Create prominent info box with price details
                st.markdown("---")
                st.markdown("### 💰 Live Market Price")
                
                # Price display
                col_price_info1, col_price_info2, col_price_info3 = st.columns(3)
                
                with col_price_info1:
                    st.metric(
                        label="Current Price",
                        value=f"${price_data['price']:,.2f}",
                        delta=None
                    )
                
                with col_price_info2:
                    if price_data.get('change_24h') is not None:
                        change_val = price_data['change_24h']
                        st.metric(
                            label="24h Change",
                            value=f"{change_val:+.2f}%",
                            delta=f"{change_val:+.2f}%",
                            delta_color="normal"
                        )
                    else:
                        st.metric(label="24h Change", value="N/A")
                
                with col_price_info3:
                    st.metric(
                        label="Data Source",
                        value=price_data['source'].split()[0]  # Show "Yahoo" or "CoinGecko"
                    )
                
                # Additional info
                if price_data.get('name'):
                    st.caption(f"📊 **{price_data['name']}** ({price_data['symbol']})")
                
                st.markdown("---")
                
                # Action buttons
                col_btn1, col_btn2 = st.columns(2)
                
                with col_btn1:
                    # Show status if live price is already set
                    if st.session_state.use_live_price:
                        st.success(f"✅ Using live price: ${price_data['price']:,.2f}")
                    else:
                        if st.button("✅ Set Live Price", key="set_price_btn", help="Use this price as purchase price"):
                            # Set the flag to use live price
                            st.session_state.use_live_price = True
                            st.session_state.live_price_value = price_data['price']
                            st.rerun()  # Refresh to update the price input
                
                with col_btn2:
                    if st.button("🗑️ Clear", key="clear_price_btn", help="Clear and enter custom price"):
                        st.session_state.fetched_price_data = None
                        st.session_state.use_live_price = False
                        st.session_state.live_price_value = 100.0
                        st.rerun()
                
                st.markdown("---")
            
            if st.button("📊 Add Investment", key="add_investment_btn"):
                if symbol:
                    with st.spinner("Adding investment and analyzing risk..."):
                        success, result = make_api_request("POST", f"/api/investments/{st.session_state.user_id}", {
                            "symbol": symbol.upper(),
                            "asset_type": asset_type,
                            "quantity": quantity,
                            "purchase_price": purchase_price
                        })
                        
                        if success:
                            st.success(f"✅ {result.get('message', 'Investment added!')}")
                            st.balloons()
                            
                            # Show Risk Analysis
                            if 'risk_analysis' in result:
                                st.markdown("### 🎯 Risk Analysis")
                                risk = result['risk_analysis']
                                
                                # Risk Score
                                risk_color = "🟢" if risk['risk_level'] == 'low' else "🟡" if risk['risk_level'] == 'medium' else "🔴"
                                st.markdown(f"**Risk Level:** {risk_color} {risk['risk_level'].upper()} (Score: {risk['risk_score']:.2f})")
                                
                                # Recommendations
                                st.markdown("**Recommendations:**")
                                for rec in risk.get('recommendations', []):
                                    st.info(rec)
                            
                            # Show AI Insights
                            if 'ai_insights' in result:
                                st.markdown("### 🤖 AI Insights")
                                ai = result['ai_insights']
                                st.markdown(f"**{ai.get('summary', 'Analysis complete')}**")
                                
                                if 'recommendations' in ai:
                                    st.markdown("**AI Recommendations:**")
                                    for rec in ai['recommendations']:
                                        st.success(f"💡 {rec}")
                        else:
                            st.error(f"❌ Failed to add investment: {result}")
                else:
                    st.warning("⚠️ Please enter a stock symbol")

elif page == "💬 AI Chat":
    st.markdown("## 💬 Chat with FinBuddy AI")
    
    if not st.session_state.user_id:
        st.warning("⚠️ Please login first")
    else:
        # Chat History Display
        st.markdown("### Conversation")
        chat_container = st.container()
        
        with chat_container:
            for message in st.session_state.chat_history:
                if message['role'] == 'user':
                    st.markdown(f"**You:** {message['content']}")
                else:
                    st.markdown(f"**🤖 FinBuddy:** {message['content']}")
                st.markdown("---")
        
        # Chat Input
        st.markdown("### Ask FinBuddy")
        user_message = st.text_area("Your Question", placeholder="e.g., What is a good investment strategy for beginners?", height=100)
        
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("📤 Send", key="send_chat"):
                if user_message:
                    with st.spinner("🤖 FinBuddy is thinking..."):
                        success, result = make_api_request("POST", "/api/ai/chat", {
                            "message": user_message,
                            "user_id": st.session_state.user_id
                        })
                        
                        if success:
                            # Add to chat history
                            st.session_state.chat_history.append({
                                'role': 'user',
                                'content': user_message
                            })
                            st.session_state.chat_history.append({
                                'role': 'assistant',
                                'content': result['response']
                            })
                            st.rerun()
                        else:
                            st.error(f"❌ Chat error: {result}")
                else:
                    st.warning("⚠️ Please enter a message")
        
        with col2:
            if st.button("🗑️ Clear Chat", key="clear_chat"):
                st.session_state.chat_history = []
                st.rerun()

elif page == "🧠 Market Insights":
    st.markdown("## 🧠 AI Market Insight Engine")
    st.markdown("*Real-time AI analysis of market news for actionable intelligence*")
    st.markdown("---")
    
    # Fetch button
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("🔄 Refresh Market Insights", key="refresh_insights_btn", use_container_width=True):
            st.rerun()
    
    # Fetch insights
    with st.spinner("🧠 Analyzing market news with AI... (this may take up to 30 seconds)"):
        success, insights = make_api_request("GET", "/api/ai/market-insights", timeout=30)
    
    if success:
        # Check if there's no data
        if insights.get('total_analyzed', 0) == 0:
            st.warning("📭 No news articles found in database.")
            st.info("💡 Tip: Go to '📰 Market News' page and click 'Fetch News' to load articles first!")
            st.stop()
        # Top-level metrics
        st.markdown("### 📊 Market Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            mood_emoji = "📈" if "Bullish" in insights['market_mood'] else "📉" if "Bearish" in insights['market_mood'] else "➡️"
            st.metric(
                "Market Mood",
                insights['market_mood'],
                delta=None
            )
        
        with col2:
            sentiment_color = "🟢" if insights['avg_sentiment'] > 0.3 else "🔴" if insights['avg_sentiment'] < -0.3 else "🟡"
            st.metric(
                "Avg Sentiment",
                f"{insights['avg_sentiment']:.3f} {sentiment_color}",
                delta=None
            )
        
        with col3:
            risk_emoji = "🔴" if insights['global_risk'] == "High" else "🟡" if insights['global_risk'] == "Medium" else "🟢"
            st.metric(
                "Global Risk",
                f"{insights['global_risk']} {risk_emoji}",
                delta=None
            )
        
        with col4:
            st.metric(
                "Confidence",
                f"{int(insights['confidence_score'] * 100)}%",
                delta=None
            )
        
        # AI Summary
        st.markdown("### 💬 AI Market Summary")
        st.info(insights['summary'])
        
        st.markdown("---")
        
        # Two columns for Opportunities and Threats
        col_opp, col_threat = st.columns(2)
        
        with col_opp:
            st.markdown("### 📈 Top 5 Opportunities")
            if insights['opportunities']:
                for idx, opp in enumerate(insights['opportunities'], 1):
                    with st.expander(f"#{idx} - Score: {opp['sentiment']:.2f}", expanded=idx==1):
                        st.markdown(f"**{opp['title']}**")
                        st.caption(f"Source: {opp['source']}")
                        st.markdown(f"**Why Opportunity:** {opp['reason']}")
                        st.markdown(f"**Relevance:** {opp['relevance']} | **Risk:** {opp['risk']}")
                        if opp.get('url'):
                            st.markdown(f"[📖 Read More]({opp['url']})")
            else:
                st.info("No significant opportunities detected")
        
        with col_threat:
            st.markdown("### 📉 Top 5 Threats")
            if insights['threats']:
                for idx, threat in enumerate(insights['threats'], 1):
                    with st.expander(f"#{idx} - Score: {threat['sentiment']:.2f}", expanded=idx==1):
                        st.markdown(f"**{threat['title']}**")
                        st.caption(f"Source: {threat['source']}")
                        st.markdown(f"**Why Threat:** {threat['reason']}")
                        st.markdown(f"**Relevance:** {threat['relevance']} | **Risk:** {threat['risk']}")
                        if threat.get('url'):
                            st.markdown(f"[📖 Read More]({threat['url']})")
            else:
                st.success("No significant threats detected")
        
        st.markdown("---")
        
        # Developer View - Detailed Analysis
        with st.expander("🔧 Developer View - Detailed Sentiment Analysis", expanded=False):
            st.markdown("### All Processed News Articles")
            st.caption(f"Showing {len(insights['processed_news'])} of {insights['total_analyzed']} analyzed articles")
            
            # Create DataFrame for better visualization
            df_data = []
            for article in insights['processed_news']:
                df_data.append({
                    "Title": article['title'][:80] + "..." if len(article['title']) > 80 else article['title'],
                    "Source": article['source'],
                    "Sentiment Score": article['sentiment'],
                    "Sentiment": article['sentiment_label'],
                    "Risk": article['risk'],
                    "Relevance": article['relevance'],
                    "Published": article['published_at'][:10] if article['published_at'] else "N/A"
                })
            
            df = pd.DataFrame(df_data)
            
            # Display metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                positive_count = len([a for a in insights['processed_news'] if a['sentiment'] > 0.3])
                st.metric("Positive News", positive_count)
            with col2:
                neutral_count = len([a for a in insights['processed_news'] if -0.3 <= a['sentiment'] <= 0.3])
                st.metric("Neutral News", neutral_count)
            with col3:
                negative_count = len([a for a in insights['processed_news'] if a['sentiment'] < -0.3])
                st.metric("Negative News", negative_count)
            with col4:
                high_risk_count = len([a for a in insights['processed_news'] if a['risk'] == 'High'])
                st.metric("High Risk Items", high_risk_count)
            
            # Display table
            st.dataframe(df, use_container_width=True, height=400)
            
            # Sentiment distribution chart
            st.markdown("### 📊 Sentiment Distribution")
            sentiment_counts = df['Sentiment'].value_counts()
            fig = px.pie(
                values=sentiment_counts.values,
                names=sentiment_counts.index,
                title="Sentiment Breakdown",
                color_discrete_map={'positive': '#00ff00', 'neutral': '#ffff00', 'negative': '#ff0000'}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Raw JSON
            st.markdown("### 📋 Raw JSON Response")
            st.json(insights)
        
        st.caption(f"Last updated: {insights['timestamp']}")
    
    else:
        st.error(f"❌ Error loading market insights: {insights}")
        
        # Helpful troubleshooting
        if "timed out" in str(insights):
            st.warning("⚠️ **Timeout Troubleshooting:**")
            st.info("""
            The request took too long. This usually happens when:
            1. **No news in database** - Go to '📰 Market News' and fetch news first
            2. **AI taking too long** - The Gemini AI might be slow (fixed with 5s timeout now)
            3. **Server overloaded** - Try again in a few seconds
            
            **Quick Fix:** Refresh this page or fetch news articles first!
            """)
        
        if st.button("🔄 Try Again", key="retry_insights"):
            st.rerun()

elif page == "📚 Learn Finance":
    st.markdown("## 📚 Learn Financial Terms")
    
    st.markdown("### Financial Dictionary")
    st.info("💡 Learn complex financial terms explained in simple language")
    
    # Term Explanation
    term = st.text_input("Enter a financial term", placeholder="e.g., Dividend, ETF, Compound Interest")
    
    if st.button("📖 Explain", key="explain_term"):
        if term:
            with st.spinner("🤖 AI is preparing explanation..."):
                success, result = make_api_request("POST", "/api/ai/explain-term", {
                    "term": term
                })
                
                if success:
                    st.markdown(f"### 📚 {term}")
                    st.success(result['explanation'])
                    
                    # Show related learning resources
                    st.markdown("### 💡 Want to learn more?")
                    st.info("Check out the 'Chat with AI' section for personalized financial advice!")
                else:
                    st.error(f"❌ Error: {result}")
        else:
            st.warning("⚠️ Please enter a term")
    
    # Common Terms Quick Access
    st.markdown("### Popular Terms")
    col1, col2, col3 = st.columns(3)
    
    common_terms = ["Dividend", "ETF", "Portfolio", "Bull Market", "Bear Market", "ROI", "Diversification", "Compound Interest", "Index Fund"]
    
    for i, t in enumerate(common_terms):
        col = [col1, col2, col3][i % 3]
        with col:
            if st.button(t, key=f"term_{i}"):
                with st.spinner(f"Explaining {t}..."):
                    success, result = make_api_request("POST", "/api/ai/explain-term", {"term": t})
                    if success:
                        st.markdown(f"### 📚 {t}")
                        st.success(result['explanation'])

elif page == "🔍 Fraud Detection":
    st.markdown("## 🔍 Fraud Detection Center")
    
    st.info("🛡️ Protect yourself from scams! Use AI to detect suspicious messages and URLs")
    
    tab1, tab2 = st.tabs(["📧 Check Message", "🔗 Check URL"])
    
    with tab1:
        st.markdown("### Check Suspicious Messages")
        message = st.text_area("Enter the message to check", placeholder="Paste suspicious email or text message here...", height=150)
        sender = st.text_input("Sender (optional)", placeholder="e.g., unknown@suspicious.com")
        
        if st.button("🔍 Analyze Message", key="check_message"):
            if message:
                with st.spinner("🤖 AI is analyzing the message..."):
                    success, result = make_api_request("POST", "/api/fraud/detect-scam", {
                        "message": message,
                        "sender": sender or ""
                    })
                    
                    if success:
                        if result['is_suspicious']:
                            st.error(f"⚠️ SUSPICIOUS! Confidence: {result['confidence']*100:.0f}%")
                            
                            st.markdown("### 🚩 Red Flags Detected:")
                            for flag in result.get('red_flags', []):
                                st.warning(f"• {flag}")
                            
                            st.markdown("### 📝 Explanation:")
                            st.error(result.get('explanation', 'This message shows signs of fraud'))
                        else:
                            st.success("✅ This message appears to be safe")
                            st.info(result.get('explanation', 'No major red flags detected'))
                    else:
                        st.error(f"❌ Error: {result}")
            else:
                st.warning("⚠️ Please enter a message to check")
    
    with tab2:
        st.markdown("### Check Suspicious URLs")
        url = st.text_input("Enter the URL to check", placeholder="https://suspicious-site.com")
        
        if st.button("🔍 Analyze URL", key="check_url"):
            if url:
                with st.spinner("Checking URL safety..."):
                    success, result = make_api_request("POST", "/api/fraud/check-url", {
                        "url": url
                    })
                    
                    if success:
                        if result['is_safe']:
                            st.success(f"✅ URL appears safe (Risk Score: {result['risk_score']:.2f})")
                        else:
                            st.error(f"⚠️ RISKY URL! (Risk Score: {result['risk_score']:.2f})")
                            
                            st.markdown("### 🚩 Risk Factors:")
                            for factor in result.get('risk_factors', []):
                                st.warning(f"• {factor}")
                        
                        st.info(result.get('recommendation', 'Always verify links before clicking!'))
                    else:
                        st.error(f"❌ Error: {result}")
            else:
                st.warning("⚠️ Please enter a URL to check")







elif page == "📊 Risk Analysis":
    st.markdown("## 🎯 Your Portfolio Health Check")
    st.markdown("*Simple, visual insights about your investments*")
    
    if not st.session_state.user_id:
        st.warning("👋 Please login first to see your portfolio analysis")
    else:
        # Centered refresh button
        col1, col2, col3 = st.columns([3, 2, 3])
        with col2:
            if st.button("🔄 Refresh Now", key="refresh_risk", use_container_width=True, type="primary"):
                st.rerun()
        
        st.markdown("---")
        
        with st.spinner("🔮 Reading your portfolio..."):
            success, risk_report = make_api_request("GET", f"/api/risk/portfolio-ai-report?user_id={st.session_state.user_id}")
            
            if success:
                
                # ================================================================
                # PRIORITY ACTIONS - Top 3 things to fix FIRST
                # ================================================================
                st.markdown("### 🎯 Top 3 Things to Fix First")
                st.caption("*Start here! These are ranked by importance*")
                
                # Calculate priorities based on risk scores
                priorities = []
                components = risk_report['risk_components']
                
                if components['concentration'] >= 70:
                    top_holding = risk_report['concentration_analysis']['top_holding']
                    top_pct = risk_report['concentration_analysis']['top_holding_pct']
                    priorities.append({
                        'priority': 1,
                        'icon': '🧺',
                        'title': 'Too Much Money in One Stock',
                        'problem': f'{top_holding} makes up {top_pct:.0f}% of your portfolio (should be max 30%)',
                        'action': f'Sell {max(0, top_pct - 30):.0f}% of your {top_holding} shares and buy 2-3 different stocks',
                        'why': 'If this one company fails, you lose most of your money!',
                        'urgency': 'urgent'
                    })
                
                # Count negative news by stock
                news_by_stock = {}
                for alert in risk_report.get('alerts', []):
                    if "Negative news" in alert:
                        for stock in ["AAPL", "GOOGL", "MSFT"]:
                            if stock in alert:
                                news_by_stock[stock] = news_by_stock.get(stock, 0) + 1
                
                if news_by_stock:
                    worst_stock = max(news_by_stock.items(), key=lambda x: x[1])
                    priorities.append({
                        'priority': 2,
                        'icon': '📰',
                        'title': f'Lots of Bad News About {worst_stock[0]}',
                        'problem': f'Found {worst_stock[1]} negative news articles about {worst_stock[0]}',
                        'action': f'Check the News tab below, read the articles, then decide if you should sell some {worst_stock[0]} shares',
                        'why': 'Bad news often leads to stock price drops. Better to know and act early.',
                        'urgency': 'this-week'
                    })
                
                if components['exposure'] >= 60:
                    priorities.append({
                        'priority': 3,
                        'icon': '🎯',
                        'title': 'All Your Stocks Are From Same Industry',
                        'problem': 'You only invested in one sector (like all tech companies)',
                        'action': 'Buy stocks from 2-3 different industries: healthcare, banking, consumer goods, energy',
                        'why': 'If tech industry crashes, all your stocks will drop together!',
                        'urgency': 'this-month'
                    })
                
                if components['volatility'] >= 70 and len(priorities) < 3:
                    priorities.append({
                        'priority': len(priorities) + 1,
                        'icon': '🎢',
                        'title': 'Your Portfolio Value Jumps Too Much',
                        'problem': 'Your portfolio value swings up and down like a rollercoaster',
                        'action': 'Add stable "blue chip" stocks: big banks, Coca-Cola, Procter & Gamble',
                        'why': 'Wild swings = stress + panic selling at the wrong time',
                        'urgency': 'optional'
                    })
                
                # Show priority cards
                for p in sorted(priorities[:3], key=lambda x: x['priority']):
                    urgency_color = {
                        'urgent': '#dc2626',
                        'this-week': '#f59e0b', 
                        'this-month': '#3b82f6',
                        'optional': '#6b7280'
                    }
                    
                    urgency_text = {
                        'urgent': '🔴 DO THIS NOW',
                        'this-week': '🟡 This Week',
                        'this-month': '🔵 This Month',
                        'optional': '⚪ Optional'
                    }
                    
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%); 
                                padding: 25px; border-radius: 15px; margin-bottom: 20px;
                                border-left: 6px solid {urgency_color[p["urgency"]]};'>
                        <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;'>
                            <h3 style='margin: 0; color: #1f2937;'>{p['icon']} Priority #{p['priority']}: {p['title']}</h3>
                            <span style='background: {urgency_color[p["urgency"]]}; color: white; 
                                         padding: 6px 15px; border-radius: 20px; font-size: 13px; font-weight: bold;'>
                                {urgency_text[p['urgency']]}
                            </span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        st.markdown("**❌ The Problem:**")
                        st.error(p['problem'])
                        st.markdown("**💡 Why This Matters:**")
                        st.info(p['why'])
                    
                    with col2:
                        st.markdown("**✅ What to Do:**")
                        st.success(p['action'])
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                
                if len(priorities) == 0:
                    st.success("🎉 Great job! Your portfolio looks healthy. No urgent actions needed!")
                
                st.markdown("---")
                
                # ================================================================
                # PROGRESS TRACKING - Real tracking with checkboxes and auto-detection
                # ================================================================
                st.markdown("### 📈 Your Progress Tracker")
                st.caption("*Mark issues as resolved when you fix them, or we'll auto-detect on next refresh!*")
                
                # Initialize progress tracking in session state
                if 'fixed_issues' not in st.session_state:
                    st.session_state.fixed_issues = set()
                
                # Auto-detect fixed issues based on current risk scores
                auto_fixed = []
                if components['concentration'] < 70:
                    auto_fixed.append('concentration')
                if components['volatility'] < 70:
                    auto_fixed.append('volatility')
                if components['exposure'] < 60:
                    auto_fixed.append('sector')
                
                # Update session state with auto-detected fixes
                for fixed in auto_fixed:
                    st.session_state.fixed_issues.add(fixed)
                
                # Calculate progress
                total_issue_types = 4  # concentration, volatility, news, sector
                fixed_count = len(st.session_state.fixed_issues)
                remaining_count = total_issue_types - fixed_count
                progress_pct = (fixed_count / total_issue_types) * 100
                
                prog_col1, prog_col2 = st.columns([2, 1])
                
                with prog_col1:
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); 
                                padding: 25px; border-radius: 15px; border-left: 6px solid #3b82f6;'>
                        <h4 style='color: #1e40af; margin: 0 0 15px 0;'>🎯 Issue Resolution Progress</h4>
                        <div style='background: #dbeafe; height: 30px; border-radius: 15px; overflow: hidden;'>
                            <div style='background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%); 
                                        height: 30px; width: {progress_pct}%; display: flex; align-items: center; 
                                        justify-content: center; color: white; font-weight: bold; font-size: 14px;'>
                                {progress_pct:.0f}%
                            </div>
                        </div>
                        <p style='color: #1e40af; margin: 10px 0 0 0; font-size: 14px;'>
                            ✅ Fixed: {fixed_count} | ⏳ Remaining: {remaining_count} | 📊 Total: {total_issue_types} risk types
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Show checkboxes for manual tracking
                    st.markdown("#### ☑️ Manual Tracking (Check when fixed)")
                    
                    track_col1, track_col2 = st.columns(2)
                    
                    with track_col1:
                        # Concentration checkbox
                        conc_fixed = 'concentration' in st.session_state.fixed_issues
                        conc_auto = components['concentration'] < 70
                        
                        if st.checkbox(
                            f"{'✅' if conc_fixed else '☐'} Concentration Fixed (Currently: {components['concentration']:.0f}/100)",
                            value=conc_fixed,
                            key="fix_concentration",
                            disabled=conc_auto,
                            help="Auto-detected when concentration drops below 70"
                        ):
                            st.session_state.fixed_issues.add('concentration')
                        elif not conc_auto and not st.session_state.get('fix_concentration', False):
                            st.session_state.fixed_issues.discard('concentration')
                        
                        if conc_auto:
                            st.caption("✨ Auto-detected as fixed!")
                        
                        # Volatility checkbox
                        vol_fixed = 'volatility' in st.session_state.fixed_issues
                        vol_auto = components['volatility'] < 70
                        
                        if st.checkbox(
                            f"{'✅' if vol_fixed else '☐'} Volatility Fixed (Currently: {components['volatility']:.0f}/100)",
                            value=vol_fixed,
                            key="fix_volatility",
                            disabled=vol_auto,
                            help="Auto-detected when volatility drops below 70"
                        ):
                            st.session_state.fixed_issues.add('volatility')
                        elif not vol_auto and not st.session_state.get('fix_volatility', False):
                            st.session_state.fixed_issues.discard('volatility')
                        
                        if vol_auto:
                            st.caption("✨ Auto-detected as fixed!")
                    
                    with track_col2:
                        # News checkbox (manual only)
                        news_fixed = 'news' in st.session_state.fixed_issues
                        news_count = sum(1 for a in risk_report.get('alerts', []) if "negative news" in a.lower())
                        
                        if st.checkbox(
                            f"{'✅' if news_fixed else '☐'} News Issues Addressed ({news_count} articles)",
                            value=news_fixed,
                            key="fix_news",
                            help="Check this when you've read the news and taken action"
                        ):
                            st.session_state.fixed_issues.add('news')
                        elif not st.session_state.get('fix_news', False):
                            st.session_state.fixed_issues.discard('news')
                        
                        # Sector checkbox
                        sector_fixed = 'sector' in st.session_state.fixed_issues
                        sector_auto = components['exposure'] < 60
                        
                        if st.checkbox(
                            f"{'✅' if sector_fixed else '☐'} Sector Diversified (Currently: {components['exposure']:.0f}/100)",
                            value=sector_fixed,
                            key="fix_sector",
                            disabled=sector_auto,
                            help="Auto-detected when sector exposure drops below 60"
                        ):
                            st.session_state.fixed_issues.add('sector')
                        elif not sector_auto and not st.session_state.get('fix_sector', False):
                            st.session_state.fixed_issues.discard('sector')
                        
                        if sector_auto:
                            st.caption("✨ Auto-detected as fixed!")
                    
                    if fixed_count > 0:
                        st.success(f"🎉 Great work! You've resolved {fixed_count} out of {total_issue_types} risk types. Keep it up!")
                    else:
                        st.info("💪 Start fixing the priority items above and check them off here!")
                
                with prog_col2:
                    # Achievement badge based on progress
                    if progress_pct == 100:
                        badge_emoji = "🏆"
                        badge_text = "Perfect!"
                        badge_subtext = "All issues fixed!"
                        badge_bg = "#10b981"
                    elif progress_pct >= 75:
                        badge_emoji = "🌟"
                        badge_text = "Almost There!"
                        badge_subtext = "1 more to go"
                        badge_bg = "#3b82f6"
                    elif progress_pct >= 50:
                        badge_emoji = "💪"
                        badge_text = "Halfway!"
                        badge_subtext = "Keep going"
                        badge_bg = "#f59e0b"
                    elif progress_pct >= 25:
                        badge_emoji = "🚀"
                        badge_text = "Good Start!"
                        badge_subtext = "You're improving"
                        badge_bg = "#6366f1"
                    else:
                        badge_emoji = "📋"
                        badge_text = "Let's Begin!"
                        badge_subtext = "Start fixing"
                        badge_bg = "#6b7280"
                    
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, {badge_bg} 0%, {badge_bg}dd 100%); 
                                padding: 25px; border-radius: 12px; text-align: center; height: 100%;
                                display: flex; flex-direction: column; justify-content: center;'>
                        <h1 style='color: white; margin: 0; font-size: 64px;'>{badge_emoji}</h1>
                        <p style='color: white; margin: 15px 0 5px 0; font-size: 18px; font-weight: bold;'>
                            {badge_text}
                        </p>
                        <p style='color: rgba(255,255,255,0.9); margin: 0; font-size: 13px;'>
                            {badge_subtext}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Reset button
                    if st.button("🔄 Reset Progress", key="reset_progress", help="Clear all tracked progress"):
                        st.session_state.fixed_issues = set()
                        st.rerun()
                
                st.markdown("---")
                
                # ================================================================
                # COMPARISON & HISTORICAL VIEW
                # ================================================================
                st.markdown("### 📊 How You Compare")
                
                comp_col1, comp_col2, comp_col3 = st.columns(3)
                
                risk_score = risk_report['score']
                
                # Calculate comparison percentile (simulated - in real app, compare with database)
                percentile = min(95, max(5, 100 - risk_score))
                
                # Simulate historical data (in real app, store monthly snapshots)
                historical_risk = risk_score + 7  # Pretend it was higher before
                improvement = historical_risk - risk_score
                
                with comp_col1:
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); 
                                padding: 20px; border-radius: 12px; text-align: center;'>
                        <h4 style='color: #78350f; margin: 0 0 10px 0; font-size: 14px;'>vs Other Beginners</h4>
                        <h1 style='color: #92400e; margin: 0; font-size: 42px;'>{percentile:.0f}%</h1>
                        <p style='color: #a16207; margin: 10px 0 0 0; font-size: 13px;'>
                            {'Safer than' if risk_score < 50 else 'Riskier than'} {percentile:.0f}% of micro-investors
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with comp_col2:
                    trend_emoji = "📉" if improvement > 0 else "📈" if improvement < 0 else "➡️"
                    trend_color = "#10b981" if improvement > 0 else "#ef4444" if improvement < 0 else "#6b7280"
                    trend_text = "Improving!" if improvement > 0 else "Getting riskier" if improvement < 0 else "Stable"
                    
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); 
                                padding: 20px; border-radius: 12px; text-align: center;'>
                        <h4 style='color: #1e40af; margin: 0 0 10px 0; font-size: 14px;'>Risk Trend (30 days)</h4>
                        <h1 style='color: {trend_color}; margin: 0; font-size: 42px;'>{trend_emoji}</h1>
                        <p style='color: #1e40af; margin: 10px 0 5px 0; font-size: 13px;'>
                            Was: {historical_risk:.0f} → Now: {risk_score:.0f}
                        </p>
                        <p style='color: {trend_color}; margin: 0; font-size: 13px; font-weight: bold;'>
                            {trend_text}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with comp_col3:
                    ideal_risk = 40  # Ideal risk score for beginners
                    gap = abs(risk_score - ideal_risk)
                    
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%); 
                                padding: 20px; border-radius: 12px; text-align: center;'>
                        <h4 style='color: #15803d; margin: 0 0 10px 0; font-size: 14px;'>Target Risk Score</h4>
                        <h1 style='color: #16a34a; margin: 0; font-size: 42px;'>{ideal_risk}</h1>
                        <p style='color: #22c55e; margin: 10px 0 5px 0; font-size: 13px;'>
                            Ideal for beginners
                        </p>
                        <p style='color: #16a34a; margin: 0; font-size: 13px; font-weight: bold;'>
                            You're {gap:.0f} points {'above' if risk_score > ideal_risk else 'below'}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("---")
                
                # ================================================================
                # BIG PICTURE METRICS - Visual Cards with speedometer
                # ================================================================
                st.markdown("### 💰 Your Money at a Glance")
                
                metric_col1, metric_col2, metric_col3 = st.columns(3)
                
                with metric_col1:
                    st.container()
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 15px; text-align: center;'>
                        <h4 style='color: white; margin: 0;'>Portfolio Value</h4>
                        <h1 style='color: white; margin: 10px 0;'>${risk_report['portfolio_summary']['total_value']:,.0f}</h1>
                        <p style='color: #e0e0e0; margin: 0; font-size: 14px;'>Total worth of all your stocks</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with metric_col2:
                    gain_loss = risk_report['portfolio_summary']['total_gain_loss']
                    gain_pct = risk_report['portfolio_summary']['total_gain_loss_pct']
                    profit_color = "#10b981" if gain_loss > 0 else "#ef4444"
                    profit_emoji = "📈" if gain_loss > 0 else "📉"
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, {profit_color} 0%, {"#059669" if gain_loss > 0 else "#dc2626"} 100%); padding: 20px; border-radius: 15px; text-align: center;'>
                        <h4 style='color: white; margin: 0;'>Your Profit/Loss {profit_emoji}</h4>
                        <h1 style='color: white; margin: 10px 0;'>${gain_loss:,.0f}</h1>
                        <p style='color: #e0e0e0; margin: 0; font-size: 14px;'>{gain_pct:.1f}% {"gain" if gain_loss > 0 else "loss"}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with metric_col3:
                    risk_score = risk_report['score']
                    risk_level = risk_report['overall_risk']
                    
                    # Color coding based on risk level
                    if risk_score < 40:
                        risk_emoji = "🟢"
                        risk_bg = "#10b981"
                        risk_zone = "Safe Zone"
                        zone_emoji = "�"
                    elif risk_score < 70:
                        risk_emoji = "🟡"
                        risk_bg = "#f59e0b"
                        risk_zone = "Moderate Zone"
                        zone_emoji = "😐"
                    else:
                        risk_emoji = "🔴"
                        risk_bg = "#ef4444"
                        risk_zone = "Risky Zone"
                        zone_emoji = "😰"
                    
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, {risk_bg} 0%, {"#dc2626" if risk_score >= 70 else "#d97706" if risk_score >= 40 else "#059669"} 100%); 
                                padding: 20px; border-radius: 15px; text-align: center;'>
                        <h4 style='color: white; margin: 0;'>Risk Health Score {risk_emoji}</h4>
                        <h1 style='color: white; margin: 10px 0; font-size: 48px;'>{risk_score:.0f}</h1>
                        <div style='background: rgba(255,255,255,0.3); height: 10px; border-radius: 5px; margin: 15px 0;'>
                            <div style='background: white; height: 10px; border-radius: 5px; width: {risk_score}%;'></div>
                        </div>
                        <p style='color: #ffffff; margin: 5px 0; font-size: 16px; font-weight: bold;'>{zone_emoji} {risk_zone}</p>
                        <p style='color: #e0e0e0; margin: 0; font-size: 12px;'>Technical: {risk_level} Risk Volatility</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # ================================================================
                # AI ADVICE - Big, friendly box
                # ================================================================
                st.markdown("### 🤖 What Should You Do?")
                st.info(f"💡 **AI's Advice:** {risk_report['ai_summary']}")
                
                st.markdown("---")
                
                # ================================================================
                # MAIN SECTIONS - Use TABS for better organization
                # ================================================================
                tab1, tab2, tab3, tab4 = st.tabs([
                    "⚠️ Alerts (What to Watch)", 
                    "📰 News (Good & Bad)", 
                    "📊 Risk Breakdown",
                    "📚 Learn More"
                ])
                
                # ================================================================
                # TAB 1: ALERTS - Summary cards with organized expandables
                # ================================================================
                with tab1:
                    st.markdown("### ⚠️ Portfolio Alert Summary")
                    st.caption("*Quick overview - click to see details and what to do*")
                    
                    if risk_report['alerts']:
                        # Count different types of alerts
                        concentration_alerts = sum(1 for a in risk_report['alerts'] if "concentration" in a.lower() or "represents" in a.lower())
                        volatility_alerts = sum(1 for a in risk_report['alerts'] if "volatility" in a.lower() or "variance" in a.lower())
                        news_alerts = sum(1 for a in risk_report['alerts'] if "negative news" in a.lower())
                        sector_alerts = sum(1 for a in risk_report['alerts'] if "sector" in a.lower())
                        
                        total_types = sum([1 for x in [concentration_alerts, volatility_alerts, news_alerts, sector_alerts] if x > 0])
                        
                        # Big summary at top
                        st.markdown(f"""
                        <div style='background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); 
                                    padding: 25px; border-radius: 15px; text-align: center; margin-bottom: 25px;'>
                            <h2 style='color: #78350f; margin: 0;'>⚠️ {total_types} Alert Types Found</h2>
                            <p style='color: #92400e; margin: 10px 0 0 0; font-size: 16px;'>
                                Total Issues: {len(risk_report['alerts'])} ({concentration_alerts} concentration, {volatility_alerts} volatility, {news_alerts} news, {sector_alerts} sector)
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Summary cards - show counts
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            if concentration_alerts > 0:
                                st.markdown(f"""
                                <div style='background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%); 
                                            padding: 20px; border-radius: 12px; text-align: center; cursor: pointer;'>
                                    <h1 style='color: #991b1b; margin: 0; font-size: 36px;'>🧺</h1>
                                    <h3 style='color: #7f1d1d; margin: 10px 0 5px 0;'>{concentration_alerts}</h3>
                                    <p style='color: #991b1b; margin: 0; font-size: 13px; font-weight: bold;'>Concentration Risk</p>
                                    <p style='color: #b91c1c; margin: 5px 0 0 0; font-size: 11px;'>Click below to see</p>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        with col2:
                            if volatility_alerts > 0:
                                st.markdown(f"""
                                <div style='background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); 
                                            padding: 20px; border-radius: 12px; text-align: center;'>
                                    <h1 style='color: #92400e; margin: 0; font-size: 36px;'>🎢</h1>
                                    <h3 style='color: #78350f; margin: 10px 0 5px 0;'>{volatility_alerts}</h3>
                                    <p style='color: #92400e; margin: 0; font-size: 13px; font-weight: bold;'>Volatility Alert</p>
                                    <p style='color: #a16207; margin: 5px 0 0 0; font-size: 11px;'>Click below to see</p>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        with col3:
                            if news_alerts > 0:
                                st.markdown(f"""
                                <div style='background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%); 
                                            padding: 20px; border-radius: 12px; text-align: center;'>
                                    <h1 style='color: #991b1b; margin: 0; font-size: 36px;'>📰</h1>
                                    <h3 style='color: #7f1d1d; margin: 10px 0 5px 0;'>{news_alerts}</h3>
                                    <p style='color: #991b1b; margin: 0; font-size: 13px; font-weight: bold;'>News Alerts</p>
                                    <p style='color: #b91c1c; margin: 5px 0 0 0; font-size: 11px;'>Bad news found</p>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        with col4:
                            if sector_alerts > 0:
                                st.markdown(f"""
                                <div style='background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); 
                                            padding: 20px; border-radius: 12px; text-align: center;'>
                                    <h1 style='color: #92400e; margin: 0; font-size: 36px;'>🎯</h1>
                                    <h3 style='color: #78350f; margin: 10px 0 5px 0;'>{sector_alerts}</h3>
                                    <p style='color: #92400e; margin: 0; font-size: 13px; font-weight: bold;'>Sector Risk</p>
                                    <p style='color: #a16207; margin: 5px 0 0 0; font-size: 11px;'>Click below to see</p>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        
                        # Detailed expandable sections with ACTUAL information
                        if concentration_alerts > 0:
                            with st.expander(f"🧺 Click to view Concentration Risk details ({concentration_alerts} alert)", expanded=False):
                                st.markdown("### 🧺 Too Much Money in One Stock")
                                
                                top_holding = risk_report['concentration_analysis']['top_holding']
                                top_pct = risk_report['concentration_analysis']['top_holding_pct']
                                
                                col1, col2 = st.columns([2, 1])
                                with col1:
                                    st.markdown("**❌ The Problem:**")
                                    st.error(f"{top_holding} makes up {top_pct:.1f}% of your portfolio. Experts recommend max 30% per stock!")
                                    
                                    st.markdown("**💡 Why This Matters (Technical):**")
                                    st.info(f"**Portfolio Concentration Ratio:** {top_pct:.1f}% in single asset exceeds recommended diversification threshold. High concentration increases unsystematic risk exposure.")
                                    
                                    st.markdown("**💡 Simple Explanation:**")
                                    st.info("If this one company fails or stock price drops 50%, you lose almost half your money! That's risky.")
                                
                                with col2:
                                    # Visual pie chart simulation
                                    st.markdown(f"""
                                    <div style='background: #f9fafb; padding: 20px; border-radius: 12px; text-align: center;'>
                                        <p style='margin: 0; font-size: 12px; color: #6b7280;'>Your Portfolio</p>
                                        <div style='margin: 15px 0;'>
                                            <div style='background: #ef4444; height: 80px; width: 80px; 
                                                        border-radius: 50%; margin: 0 auto; position: relative;'>
                                                <div style='position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
                                                            color: white; font-weight: bold; font-size: 18px;'>
                                                    {top_pct:.0f}%
                                                </div>
                                            </div>
                                        </div>
                                        <p style='margin: 10px 0 0 0; font-size: 14px; color: #374151; font-weight: bold;'>{top_holding}</p>
                                        <p style='margin: 5px 0 0 0; font-size: 11px; color: #6b7280;'>Rest: {100-top_pct:.0f}%</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                                
                                st.markdown("**✅ What to Do:**")
                                st.success(f"**Action:** Sell {max(0, top_pct - 30):.0f}% of your {top_holding} shares (about ${risk_report['portfolio_summary']['total_value'] * (top_pct - 30) / 100:.0f})\n\n**Then:** Buy 2-3 different stocks from other industries")
                        
                        if volatility_alerts > 0:
                            with st.expander(f"🎢 Click to view Volatility Risk details ({volatility_alerts} alert)", expanded=False):
                                st.markdown("### 🎢 Your Portfolio Value Jumps Around A Lot")
                                
                                vol_variance = risk_report['volatility_analysis'].get('variance', 0)
                                
                                col1, col2 = st.columns([3, 1])
                                with col1:
                                    st.markdown("**❌ The Problem:**")
                                    st.error("Your portfolio value swings up and down like a rollercoaster!")
                                    
                                    st.markdown("**💡 Technical Details:**")
                                    st.info(f"**Volatility Variance:** {vol_variance:.2f}% - Your portfolio shows high standard deviation. Beta coefficient indicates aggressive price movements relative to market index.")
                                    
                                    st.markdown("**💡 Simple Explanation:**")
                                    st.info("Yesterday: $4,000. Today: $4,200. Tomorrow: $3,900. This stress leads to panic selling!")
                                    
                                    st.markdown("**✅ What to Do:**")
                                    st.success("**Action:** Add 'blue chip' stocks - big, stable companies like:\n- Banks: JPMorgan, Bank of America\n- Consumer Goods: Coca-Cola, Procter & Gamble\n- Utilities: electricity/water companies\n\nThese are boring but stable!")
                                
                                with col2:
                                    # Volatility visualization
                                    st.markdown(f"""
                                    <div style='background: #fef3c7; padding: 20px; border-radius: 12px; text-align: center;'>
                                        <p style='margin: 0; font-size: 12px; color: #78350f; font-weight: bold;'>Your Volatility</p>
                                        <h1 style='margin: 15px 0; color: #92400e; font-size: 42px;'>🎢</h1>
                                        <p style='margin: 0; font-size: 24px; color: #78350f; font-weight: bold;'>{risk_report['risk_components']['volatility']:.0f}/100</p>
                                        <p style='margin: 10px 0 0 0; font-size: 11px; color: #92400e;'>High swings</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                        
                        if news_alerts > 0:
                            with st.expander(f"📰 Click to view {news_alerts} Bad News Articles", expanded=False):
                                st.markdown(f"### 📰 Found {news_alerts} Negative News Articles")
                                st.caption("*These news stories could affect your stock prices*")
                                
                                # Group news by stock and show ACTUAL headlines from threats
                                news_by_stock = {}
                                for threat in risk_report.get('threats', []):
                                    stock = threat.get('symbol', 'Unknown')
                                    news_by_stock.setdefault(stock, []).append(threat)
                                
                                for stock, articles in news_by_stock.items():
                                    st.markdown(f"#### 📊 {stock} - {len(articles)} negative articles")
                                    
                                    for idx, article in enumerate(articles[:3], 1):  # Show top 3 per stock
                                        st.markdown(f"""
                                        <div style='background: #fef2f2; padding: 15px; border-radius: 10px; 
                                                    border-left: 4px solid #ef4444; margin-bottom: 15px;'>
                                            <p style='margin: 0; font-size: 14px; font-weight: bold; color: #7f1d1d;'>
                                                {idx}. {article.get('title', 'News article')}
                                            </p>
                                            <p style='margin: 8px 0; font-size: 12px; color: #991b1b;'>
                                                {article.get('summary', 'No summary available')[:150]}...
                                            </p>
                                            <p style='margin: 5px 0 0 0; font-size: 11px; color: #b91c1c;'>
                                                Sentiment: {article.get('sentiment_score', 0):.2f} | Source: {article.get('source', 'Unknown')}
                                            </p>
                                        </div>
                                        """, unsafe_allow_html=True)
                                    
                                    if len(articles) > 3:
                                        st.caption(f"+ {len(articles) - 3} more articles about {stock}")
                                    
                                    st.markdown("---")
                                
                                st.info("💡 **Tip:** Go to the 'News' tab above to see full details, why it matters, and what action to take for each article!")
                        
                        if sector_alerts > 0:
                            with st.expander(f"🎯 Click to view Sector Concentration details ({sector_alerts} alert)", expanded=False):
                                st.markdown("### 🎯 All Your Stocks Are From Same Industry")
                                
                                top_sector = risk_report['exposure_analysis'].get('top_sector', 'Technology')
                                top_sector_pct = risk_report['exposure_analysis'].get('top_sector_pct', 0)
                                
                                col1, col2 = st.columns([3, 1])
                                with col1:
                                    st.markdown("**❌ The Problem:**")
                                    st.error(f"{top_sector_pct:.0f}% of your money is in {top_sector} sector")
                                    
                                    st.markdown("**💡 Technical Explanation:**")
                                    st.info(f"**Sector Concentration:** {top_sector_pct:.0f}% exposure to {top_sector} sector exceeds optimal 40% threshold. High sector correlation increases systematic risk during industry-specific downturns.")
                                    
                                    st.markdown("**💡 Simple Explanation:**")
                                    st.info(f"All your stocks are {top_sector} companies. If {top_sector} industry crashes (like tech in 2000), ALL your stocks drop together!")
                                    
                                    st.markdown("**✅ What to Do:**")
                                    st.success("**Action:** Diversify across sectors! Try:\n- **Healthcare:** Johnson & Johnson, Pfizer\n- **Finance:** Banks, insurance companies\n- **Consumer:** Walmart, McDonald's\n- **Energy:** Oil, renewable energy companies")
                                
                                with col2:
                                    st.markdown(f"""
                                    <div style='background: #fef3c7; padding: 20px; border-radius: 12px; text-align: center;'>
                                        <p style='margin: 0; font-size: 12px; color: #78350f;'>Sector Mix</p>
                                        <div style='margin: 15px 0;'>
                                            <div style='background: #f59e0b; height: 60px; width: 60px; 
                                                        border-radius: 50%; margin: 0 auto;'>
                                            </div>
                                            <p style='margin: 10px 0 0 0; font-size: 18px; color: #92400e; font-weight: bold;'>
                                                {top_sector_pct:.0f}%
                                            </p>
                                        </div>
                                        <p style='margin: 0; font-size: 11px; color: #78350f;'>{top_sector}</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                    
                    else:
                        st.success("🎉 Excellent! No major alerts found. Your portfolio looks healthy!")
                
                # ================================================================
                # TAB 2: NEWS - Good vs Bad in scrollable containers
                # ================================================================
                with tab2:
                    st.markdown("### 📰 News That Affects Your Investments")
                    st.caption("*We analyzed recent news and found articles about your stocks*")
                    
                    # Summary Cards - Just show counts
                    summary_col1, summary_col2 = st.columns(2)
                    
                    with summary_col1:
                        good_count = len(risk_report.get('opportunities', []))
                        st.markdown(f"""
                        <div style='background: linear-gradient(135deg, #10b981 0%, #059669 100%); 
                                    padding: 30px; border-radius: 15px; text-align: center;'>
                            <h1 style='color: white; margin: 0; font-size: 48px;'>{good_count}</h1>
                            <h3 style='color: #d1fae5; margin: 10px 0 0 0;'>🌟 Good News Articles</h3>
                            <p style='color: #a7f3d0; margin: 5px 0 0 0; font-size: 14px;'>Positive news about your stocks</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with summary_col2:
                        bad_count = len(risk_report.get('threats', []))
                        st.markdown(f"""
                        <div style='background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); 
                                    padding: 30px; border-radius: 15px; text-align: center;'>
                            <h1 style='color: white; margin: 0; font-size: 48px;'>{bad_count}</h1>
                            <h3 style='color: #fecaca; margin: 10px 0 0 0;'>⚠️ Warning Articles</h3>
                            <p style='color: #fca5a5; margin: 5px 0 0 0; font-size: 14px;'>Negative news about your stocks</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # Detailed News in Dropdowns
                    if good_count > 0:
                        with st.expander(f"📈 Click to see {good_count} positive news articles", expanded=False):
                            st.markdown("### 🌟 Good News - Why Your Stocks Might Go Up")
                            
                            for idx, opp in enumerate(risk_report['opportunities'], 1):
                                # Rich card for each news
                                st.markdown(f"""
                                <div style='background: #f0fdf4; padding: 20px; border-radius: 12px; 
                                            border-left: 5px solid #10b981; margin-bottom: 20px;'>
                                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                                        <span style='background: #10b981; color: white; padding: 5px 12px; 
                                                     border-radius: 20px; font-size: 13px; font-weight: bold;'>
                                            {opp['symbol']}
                                        </span>
                                        <span style='color: #059669; font-size: 12px;'>
                                            {opp['source']}
                                        </span>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                st.markdown(f"#### 📰 {idx}. {opp['title']}")
                                
                                col1, col2 = st.columns([3, 1])
                                with col1:
                                    st.markdown("**� Why this is good news:**")
                                    st.success(opp['summary'])
                                    
                                    st.markdown("**✅ What this means for you:**")
                                    if opp['sentiment_score'] > 0.5:
                                        st.info("🚀 Very positive! This stock might perform well. Consider holding or buying more.")
                                    elif opp['sentiment_score'] > 0.2:
                                        st.info("👍 Moderately positive. Things are looking good for this company.")
                                    else:
                                        st.info("🙂 Slightly positive. Good sign but monitor other news too.")
                                
                                with col2:
                                    # Sentiment badge
                                    sentiment_color = "#10b981" if opp['sentiment_score'] > 0.5 else "#34d399"
                                    st.markdown(f"""
                                    <div style='background: {sentiment_color}; padding: 15px; 
                                                border-radius: 10px; text-align: center;'>
                                        <p style='color: white; margin: 0; font-size: 12px;'>Positivity</p>
                                        <p style='color: white; margin: 5px 0 0 0; font-size: 24px; font-weight: bold;'>
                                            {opp['sentiment_score']:.2f}
                                        </p>
                                        <p style='color: white; margin: 5px 0 0 0; font-size: 20px;'>😊</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                                
                                if opp.get('url'):
                                    st.markdown(f"[� Read the full article here →]({opp['url']})")
                                
                                st.markdown("---")
                    
                    if bad_count > 0:
                        with st.expander(f"� Click to see {bad_count} warning news articles", expanded=False):
                            st.markdown("### ⚠️ Warning News - What You Need to Know")
                            
                            for idx, threat in enumerate(risk_report['threats'], 1):
                                # Rich card for each news
                                st.markdown(f"""
                                <div style='background: #fef2f2; padding: 20px; border-radius: 12px; 
                                            border-left: 5px solid #ef4444; margin-bottom: 20px;'>
                                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                                        <span style='background: #ef4444; color: white; padding: 5px 12px; 
                                                     border-radius: 20px; font-size: 13px; font-weight: bold;'>
                                            {threat['symbol']}
                                        </span>
                                        <span style='color: #dc2626; font-size: 12px;'>
                                            {threat['source']}
                                        </span>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                st.markdown(f"#### 📰 {idx}. {threat['title']}")
                                
                                col1, col2 = st.columns([3, 1])
                                with col1:
                                    st.markdown("**⚠️ Why this is concerning:**")
                                    st.error(threat['summary'])
                                    
                                    st.markdown("**🎯 What you should do:**")
                                    if threat['sentiment_score'] < -0.5:
                                        st.warning("🔴 **Very negative!** This is serious. Consider:\n- Selling some shares to reduce risk\n- Moving money to safer stocks\n- Don't panic, but act soon")
                                    elif threat['sentiment_score'] < -0.2:
                                        st.warning("🟡 **Moderately negative.** Keep a close eye:\n- Watch the stock price daily\n- Read more news about this company\n- Be ready to sell if more bad news comes")
                                    else:
                                        st.info("🟢 **Slightly negative.** Not too worried:\n- Just monitor the situation\n- No immediate action needed\n- Check back in a few days")
                                
                                with col2:
                                    # Sentiment badge
                                    sentiment_color = "#dc2626" if threat['sentiment_score'] < -0.5 else "#ef4444"
                                    emoji = "😰" if threat['sentiment_score'] < -0.5 else "😟"
                                    st.markdown(f"""
                                    <div style='background: {sentiment_color}; padding: 15px; 
                                                border-radius: 10px; text-align: center;'>
                                        <p style='color: white; margin: 0; font-size: 12px;'>Negativity</p>
                                        <p style='color: white; margin: 5px 0 0 0; font-size: 24px; font-weight: bold;'>
                                            {threat['sentiment_score']:.2f}
                                        </p>
                                        <p style='color: white; margin: 5px 0 0 0; font-size: 20px;'>{emoji}</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                                
                                if threat.get('url'):
                                    st.markdown(f"[� Read the full article here →]({threat['url']})")
                                
                                st.markdown("---")
                    
                    if good_count == 0 and bad_count == 0:
                        st.info("📭 No significant news found about your stocks right now. Check back later!")
                
                # ================================================================
                # TAB 3: RISK BREAKDOWN - Visual with progress bars
                # ================================================================
                with tab3:
                    st.markdown("### 📊 Your Risk Score Explained")
                    st.caption("*We check 4 things to calculate your risk*")
                    
                    components = risk_report['risk_components']
                    
                    # Visual risk meter
                    st.markdown("#### Your Overall Risk Score")
                    risk_score = risk_report['score']
                    
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        st.progress(int(risk_score) / 100)
                        st.markdown(f"<h2 style='text-align: center;'>{risk_score:.0f}/100</h2>", unsafe_allow_html=True)
                        
                        if risk_score < 40:
                            st.success("🟢 **Low Risk** - You're playing it safe! Good for beginners.")
                        elif risk_score < 70:
                            st.warning("🟡 **Medium Risk** - Balanced. Not too risky, not too safe.")
                        else:
                            st.error("🔴 **High Risk** - Aggressive! Only for experienced investors.")
                    
                    st.markdown("---")
                    
                    # ================================================================
                    # PIE CHART - Visual Portfolio Breakdown
                    # ================================================================
                    st.markdown("#### 📊 Your Portfolio Mix (Visual)")
                    
                    # Get portfolio holdings data
                    top_holding = risk_report['concentration_analysis']['top_holding']
                    top_pct = risk_report['concentration_analysis']['top_holding_pct']
                    others_pct = 100 - top_pct
                    
                    chart_col1, chart_col2 = st.columns([1, 1])
                    
                    with chart_col1:
                        # Create pie chart using plotly
                        try:
                            import plotly.graph_objects as go
                            
                            fig = go.Figure(data=[go.Pie(
                                labels=[top_holding, 'Other Holdings'],
                                values=[top_pct, others_pct],
                                hole=0.4,
                                marker=dict(colors=['#ef4444', '#3b82f6']),
                                textinfo='label+percent',
                                textfont=dict(size=16, color='white', family='Arial')
                            )])
                            
                            fig.update_layout(
                                title=dict(
                                    text="Portfolio Concentration",
                                    font=dict(size=18, color='#1f2937')
                                ),
                                showlegend=True,
                                height=300,
                                margin=dict(t=50, b=20, l=20, r=20)
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                        except:
                            # Fallback if plotly not available - HTML pie chart
                            st.markdown(f"""
                            <div style='text-align: center; padding: 20px;'>
                                <svg width='200' height='200' viewBox='0 0 200 200'>
                                    <circle cx='100' cy='100' r='80' fill='#ef4444' />
                                    <path d='M 100 100 L 100 20 A 80 80 0 {1 if top_pct > 50 else 0} 1 {100 + 80 * np.sin(2 * np.pi * top_pct / 100)} {100 - 80 * np.cos(2 * np.pi * top_pct / 100)} Z' fill='#3b82f6' />
                                    <circle cx='100' cy='100' r='50' fill='white' />
                                    <text x='100' y='105' text-anchor='middle' font-size='24' font-weight='bold' fill='#1f2937'>{top_pct:.0f}%</text>
                                </svg>
                                <p style='margin: 15px 0 5px 0; font-size: 14px; color: #ef4444; font-weight: bold;'>🔴 {top_holding}: {top_pct:.0f}%</p>
                                <p style='margin: 0; font-size: 14px; color: #3b82f6; font-weight: bold;'>🔵 Others: {others_pct:.0f}%</p>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    with chart_col2:
                        st.markdown(f"""
                        <div style='background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%); 
                                    padding: 25px; border-radius: 15px; height: 280px; display: flex; 
                                    flex-direction: column; justify-content: center;'>
                            <h3 style='color: #991b1b; margin: 0 0 15px 0;'>⚠️ Concentration Alert</h3>
                            <p style='color: #7f1d1d; margin: 0 0 10px 0; font-size: 14px;'>
                                <strong>Problem:</strong> {top_pct:.0f}% in one stock is risky!
                            </p>
                            <p style='color: #991b1b; margin: 0 0 10px 0; font-size: 14px;'>
                                <strong>Recommended:</strong> Max 30% per stock
                            </p>
                            <p style='color: #7f1d1d; margin: 0; font-size: 14px;'>
                                <strong>Action:</strong> Sell ${risk_report['portfolio_summary']['total_value'] * (top_pct - 30) / 100:.0f} 
                                of {top_holding} and diversify
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("---")
                    
                    # The 4 checks - Simple cards
                    st.markdown("#### The 4 Things We Check:")
                    
                    check_col1, check_col2 = st.columns(2)
                    
                    with check_col1:
                        # Check 1: Concentration
                        with st.container():
                            conc_score = components['concentration']
                            st.markdown("**1️⃣ Are you putting all eggs in one basket?**")
                            st.progress(int(conc_score) / 100)
                            st.caption(f"Score: {conc_score:.0f}/100")
                            
                            top_holding = risk_report['concentration_analysis']['top_holding']
                            top_pct = risk_report['concentration_analysis']['top_holding_pct']
                            
                            if conc_score >= 70:
                                st.error(f"❌ Yes! {top_holding} is {top_pct:.0f}% of your money")
                            elif conc_score >= 40:
                                st.warning(f"⚠️ Kind of. {top_holding} is {top_pct:.0f}%")
                            else:
                                st.success(f"✅ No! Well spread out")
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        
                        # Check 2: Volatility
                        with st.container():
                            vol_score = components['volatility']
                            st.markdown("**2️⃣ Does your money jump up and down a lot?**")
                            st.progress(int(vol_score) / 100)
                            st.caption(f"Score: {vol_score:.0f}/100")
                            
                            if vol_score >= 70:
                                st.error("❌ Yes! It's like a rollercoaster 🎢")
                            elif vol_score >= 40:
                                st.warning("⚠️ Sometimes. Moderate ups and downs")
                            else:
                                st.success("✅ No! Pretty stable 😌")
                    
                    with check_col2:
                        # Check 3: News Sentiment
                        with st.container():
                            sent_score = components['sentiment']
                            st.markdown("**3️⃣ Is the news talking bad about your stocks?**")
                            st.progress(int(sent_score) / 100)
                            st.caption(f"Score: {sent_score:.0f}/100")
                            
                            news_count = risk_report['sentiment_analysis']['total_matches']
                            
                            if sent_score >= 70:
                                st.error(f"❌ Yes! Found {news_count} negative articles")
                            elif sent_score >= 40:
                                st.warning(f"⚠️ Mixed. {news_count} articles, some bad")
                            else:
                                st.success(f"✅ No! News is positive/neutral")
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        
                        # Check 4: Sector Exposure
                        with st.container():
                            exp_score = components['exposure']
                            st.markdown("**4️⃣ Are all your stocks from the same industry?**")
                            st.progress(int(exp_score) / 100)
                            st.caption(f"Score: {exp_score:.0f}/100")
                            
                            dom_sector = risk_report['exposure_analysis']['dominant_sector']
                            dom_pct = risk_report['exposure_analysis']['dominant_sector_pct']
                            
                            if exp_score >= 70:
                                st.error(f"❌ Yes! {dom_sector} is {dom_pct:.0f}% of portfolio")
                            elif exp_score >= 40:
                                st.warning(f"⚠️ Mostly. {dom_sector}: {dom_pct:.0f}%")
                            else:
                                st.success(f"✅ No! Well diversified across industries")
                
                # ================================================================
                # TAB 4: LEARN MORE - Educational content
                # ================================================================
                with tab4:
                    st.markdown("### 📚 Want to Learn More?")
                    st.caption("*Understanding investing - made simple!*")
                    
                    with st.expander("🤔 What is 'Concentration Risk'?"):
                        st.markdown("""
                        **Simple answer:** Putting too much money in one company.
                        
                        **Example:** If you have ₹10,000 and put ₹8,000 in Apple stock:
                        - If Apple crashes, you lose ₹8,000 😢
                        - If you spread it across 4 companies (₹2,500 each), one crash only loses ₹2,500
                        
                        **Rule for beginners:** No single stock should be more than 25% of your money.
                        """)
                    
                    with st.expander("🎢 What is 'Volatility'?"):
                        st.markdown("""
                        **Simple answer:** How much your money's value jumps around.
                        
                        **Example:**
                        - **High volatility:** Your ₹1000 becomes ₹1200 today, ₹900 tomorrow, ₹1100 next day 📈📉
                        - **Low volatility:** Your ₹1000 stays around ₹1000-₹1050 slowly 📊
                        
                        **For beginners:** High volatility = more stress! Start with stable stocks.
                        """)
                    
                    with st.expander("📰 Why does news matter?"):
                        st.markdown("""
                        **Simple answer:** News affects stock prices.
                        
                        **Example:**
                        - **Good news:** "Apple sold record iPhones" → Price goes up 📈
                        - **Bad news:** "Facebook data leak scandal" → Price goes down 📉
                        
                        **For beginners:** Follow news about companies you invest in!
                        """)
                    
                    with st.expander("🎯 What is 'Sector Exposure'?"):
                        st.markdown("""
                        **Simple answer:** Which industries you're investing in.
                        
                        **Sectors:** Technology, Banking, Healthcare, Energy, etc.
                        
                        **Example:**
                        - ❌ **Bad:** All money in tech stocks (Apple, Google, Microsoft)
                        - ✅ **Good:** Spread across tech, banking, healthcare, energy
                        
                        **Why?** If one industry crashes (like tech in 2022), you don't lose everything!
                        """)
                    
                    with st.expander("🧮 How is the final score calculated?"):
                        st.markdown(f"""
                        **Simple formula:**
                        
                        Your risk score = Mix of the 4 checks above
                        
                        **Your numbers:**
                        - Concentration check: {components['concentration']:.0f} points (30% weight)
                        - Volatility check: {components['volatility']:.0f} points (25% weight)
                        - News check: {components['sentiment']:.0f} points (25% weight)
                        - Sector check: {components['exposure']:.0f} points (20% weight)
                        
                        **Final score:** {risk_report['score']:.0f}/100
                        
                        **What it means:**
                        - 0-39 = Low risk (safe)
                        - 40-69 = Medium risk (balanced)
                        - 70-100 = High risk (aggressive)
                        """)
                    
                    # Your stocks table
                    st.markdown("---")
                    st.markdown("### 📋 Your Stocks - Simple View")
                    
                    assets_data = []
                    for asset in risk_report['per_asset_risk']:
                        risk_emoji = "🔴" if asset['risk_level'] == "High" else "🟡" if asset['risk_level'] == "Medium" else "🟢"
                        assets_data.append({
                            "Stock": f"{risk_emoji} {asset['symbol']}",
                            "Risk": asset['risk_level'],
                            "% of Portfolio": f"{asset['value_pct']:.1f}%"
                        })
                    
                    st.table(pd.DataFrame(assets_data))
                
                # ================================================================
                # ACTION BUTTONS - Interactive portfolio management
                # ================================================================
                st.markdown("---")
                st.markdown("### 🎬 Take Action Now")
                st.caption("*Click buttons to get personalized guidance*")
                
                action_col1, action_col2, action_col3 = st.columns(3)
                
                with action_col1:
                    if st.button("📊 Rebalance My Portfolio", use_container_width=True, type="primary"):
                        st.session_state.show_rebalance = True
                
                with action_col2:
                    if st.button("📰 Read Latest News", use_container_width=True):
                        st.session_state.active_tab = "News"
                        st.info("💡 Switch to the 'News' tab above to see all articles!")
                
                with action_col3:
                    if st.button("🎓 Learn About Risk", use_container_width=True):
                        st.session_state.show_learn = True
                
                # Show rebalance guide
                if st.session_state.get('show_rebalance', False):
                    st.markdown("---")
                    st.markdown("### 📊 Your Personalized Rebalancing Plan")
                    
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); 
                                padding: 25px; border-radius: 15px; border-left: 6px solid #3b82f6;'>
                        <h4 style='color: #1e40af; margin: 0 0 15px 0;'>🎯 Step-by-Step Rebalancing Guide</h4>
                        <p style='color: #1e3a8a; margin: 0; font-size: 14px;'>
                            Based on your portfolio analysis, here's what to do:
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # Generate specific recommendations
                    rebal_col1, rebal_col2 = st.columns([1, 1])
                    
                    with rebal_col1:
                        st.markdown("#### 🔴 SELL (Reduce Concentration)")
                        
                        top_holding = risk_report['concentration_analysis']['top_holding']
                        top_pct = risk_report['concentration_analysis']['top_holding_pct']
                        
                        if top_pct > 30:
                            sell_pct = top_pct - 30
                            sell_amount = risk_report['portfolio_summary']['total_value'] * sell_pct / 100
                            
                            st.error(f"""
                            **Stock:** {top_holding}
                            
                            **Current:** {top_pct:.1f}% of portfolio
                            
                            **Target:** 30% (safer level)
                            
                            **Action:** Sell {sell_pct:.1f}% (~${sell_amount:.0f})
                            
                            **Why:** Reduce risk if {top_holding} drops
                            """)
                        else:
                            st.success("✅ Your concentration looks good! No immediate selling needed.")
                    
                    with rebal_col2:
                        st.markdown("#### 🟢 BUY (Diversify)")
                        
                        top_sector = risk_report['exposure_analysis'].get('top_sector', 'Technology')
                        
                        st.success(f"""
                        **Current Sector:** {top_sector} (overweight)
                        
                        **Recommended New Sectors:**
                        
                        1. **Healthcare:** JNJ, PFE, UNH
                           - Defensive, stable growth
                        
                        2. **Finance:** JPM, BAC, V
                           - Dividend income, stable
                        
                        3. **Consumer Goods:** PG, KO, WMT
                           - Recession-resistant
                        
                        **Amount to Invest:** ~${risk_report['portfolio_summary']['total_value'] * 0.2:.0f}
                        (20% of portfolio)
                        """)
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    st.info("""
                    💡 **How to Execute:**
                    1. Log in to your brokerage app
                    2. Place SELL order for recommended stock
                    3. Wait for order to fill (1-2 minutes)
                    4. Use proceeds to BUY new stocks
                    5. Come back here and refresh to see new risk score!
                    """)
                    
                    if st.button("✅ Got it! Close this guide", key="close_rebalance"):
                        st.session_state.show_rebalance = False
                        st.rerun()
                
                # Show learning content
                if st.session_state.get('show_learn', False):
                    st.markdown("---")
                    st.markdown("### 🎓 Risk Management 101")
                    
                    learn_tab1, learn_tab2, learn_tab3 = st.tabs(["📚 Basics", "📊 Advanced", "💡 Tips"])
                    
                    with learn_tab1:
                        st.markdown("""
                        #### What is Portfolio Risk?
                        
                        **Simple:** How likely you are to lose money
                        
                        **Technical:** Statistical measure of portfolio volatility and downside exposure
                        
                        #### Why Does It Matter?
                        
                        - **High risk** = Big gains OR big losses (gambling)
                        - **Low risk** = Small steady gains (safe)
                        - **Medium risk** = Balanced (best for beginners)
                        
                        #### The Golden Rule
                        
                        > "Don't put all eggs in one basket" - Warren Buffett
                        
                        Spread your money across 5-10 different stocks from different industries!
                        """)
                    
                    with learn_tab2:
                        st.markdown("""
                        #### Advanced Concepts
                        
                        **1. Beta Coefficient**
                        - Simple: How much your stock moves vs the market
                        - Technical: β = Covariance(Asset, Market) / Variance(Market)
                        - β > 1 = More volatile than market
                        - β < 1 = Less volatile (safer)
                        
                        **2. Sharpe Ratio**
                        - Simple: Reward per unit of risk
                        - Technical: (Return - Risk-free rate) / Standard Deviation
                        - Higher = Better risk-adjusted returns
                        
                        **3. Value at Risk (VaR)**
                        - Simple: Worst case loss in normal conditions
                        - Technical: Maximum expected loss at 95% confidence level
                        - Example: VaR = $500 means 95% sure you won't lose more than $500
                        """)
                    
                    with learn_tab3:
                        st.markdown("""
                        #### 💡 Pro Tips for Micro-Investors
                        
                        1. **Start Small**
                           - Invest only money you can afford to lose
                           - Start with $100-500, learn, then invest more
                        
                        2. **Diversify Smart**
                           - 3-5 stocks minimum
                           - Different sectors (tech, healthcare, finance)
                           - Mix of growth + stable stocks
                        
                        3. **Don't Panic Sell**
                           - Market drops are normal
                           - Hold for 1-5 years minimum
                           - Only sell based on research, not fear
                        
                        4. **Read News Daily**
                           - 15 minutes every morning
                           - Focus on YOUR stocks
                           - Use our News tab!
                        
                        5. **Rebalance Quarterly**
                           - Check portfolio every 3 months
                           - Adjust if concentration > 30%
                           - Take profits, cut losses
                        """)
                    
                    if st.button("✅ Close Learning Guide", key="close_learn"):
                        st.session_state.show_learn = False
                        st.rerun()
                
                st.markdown("---")
                st.caption(f"*Report created: {risk_report['timestamp']}*")
                
            else:
                st.error(f"❌ Oops! Couldn't load your report: {risk_report}")


elif page == "💡 AI Recommendations":
    st.markdown("## 💡 AI-Powered Investment Recommendations")
    st.caption("Personalized suggestions based on your portfolio, risk analysis, and market news")
    
    if not st.session_state.user_id:
        st.warning("👋 Please login first to see your personalized recommendations")
    else:
        # Centered refresh button
        col1, col2, col3 = st.columns([3, 2, 3])
        with col2:
            if st.button("🔄 Regenerate Recommendations", key="refresh_recommendations", use_container_width=True, type="primary"):
                st.rerun()
        
        st.markdown("---")
        
        with st.spinner("🤖 AI is analyzing your portfolio and generating personalized recommendations..."):
            success, recommendations = make_api_request("GET", f"/api/ai/recommendations?user_id={st.session_state.user_id}")
            
            if success:
                # ================================================================
                # OVERALL SUMMARY
                # ================================================================
                st.markdown("### 📋 Overall Assessment")
                st.info(f"💡 {recommendations.get('overall_summary', 'No summary available')}")
                
                st.markdown("---")
                
                # ================================================================
                # RECOMMENDED BUYS
                # ================================================================
                st.markdown("### ✅ Recommended Stocks to Buy")
                st.caption("*AI suggests these stocks to improve your portfolio diversification and growth potential*")
                
                buys = recommendations.get('recommended_buys', [])
                if buys:
                    for idx, buy in enumerate(buys, 1):
                        st.markdown(f"""
                        <div style='background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%); 
                                    padding: 20px; border-radius: 12px; margin-bottom: 15px;
                                    border-left: 5px solid #28a745;'>
                            <div style='display: flex; justify-content: space-between; align-items: center;'>
                                <div>
                                    <h3 style='margin: 0; color: #155724;'>#{idx}. {buy.get('symbol', 'N/A')}</h3>
                                    <p style='margin: 10px 0 0 0; color: #155724; font-size: 14px;'>
                                        💡 {buy.get('reason', 'No reason provided')}
                                    </p>
                                </div>
                                <div style='text-align: right;'>
                                    <p style='margin: 0; font-size: 24px; font-weight: bold; color: #28a745;'>
                                        {buy.get('allocation_percent', 0)}%
                                    </p>
                                    <p style='margin: 5px 0 0 0; font-size: 12px; color: #155724;'>
                                        Suggested allocation
                                    </p>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.success("🎉 Your current portfolio looks well-balanced! No urgent buy recommendations at this time.")
                
                st.markdown("---")
                
                # ================================================================
                # RECOMMENDED SELLS/HOLDS
                # ================================================================
                st.markdown("### 📉 Recommended Sells / Holds")
                st.caption("*Consider rebalancing these positions to reduce risk*")
                
                sells = recommendations.get('recommended_sells', [])
                if sells:
                    for idx, sell in enumerate(sells, 1):
                        st.markdown(f"""
                        <div style='background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%); 
                                    padding: 20px; border-radius: 12px; margin-bottom: 15px;
                                    border-left: 5px solid #ffc107;'>
                            <div>
                                <h3 style='margin: 0; color: #856404;'>⚠️ {sell.get('symbol', 'N/A')}</h3>
                                <p style='margin: 10px 0 0 0; color: #856404; font-size: 14px;'>
                                    💡 {sell.get('reason', 'No reason provided')}
                                </p>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("👍 No immediate sell recommendations. Your current holdings are stable.")
                
                st.markdown("---")
                
                # ================================================================
                # DIVERSIFICATION PLAN
                # ================================================================
                st.markdown("### 📦 Sector Diversification Plan")
                st.caption("*Target sector allocation for a balanced portfolio*")
                
                diversification = recommendations.get('diversification_plan', [])
                if diversification:
                    # Create 3 columns for diversification cards
                    div_cols = st.columns(min(3, len(diversification)))
                    
                    for idx, (col, div) in enumerate(zip(div_cols, diversification)):
                        with col:
                            st.markdown(f"""
                            <div style='background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%); 
                                        padding: 20px; border-radius: 12px; text-align: center; height: 100%;
                                        border-top: 4px solid #17a2b8;'>
                                <h3 style='margin: 0 0 10px 0; color: #0c5460;'>{div.get('sector', 'N/A')}</h3>
                                <p style='margin: 0; font-size: 32px; font-weight: bold; color: #17a2b8;'>
                                    {div.get('target_percent', 0)}%
                                </p>
                                <p style='margin: 10px 0 0 0; font-size: 12px; color: #0c5460;'>
                                    Target allocation
                                </p>
                                <hr style='margin: 15px 0; border: 0; border-top: 1px solid #17a2b8;'>
                                <p style='margin: 0; font-size: 13px; color: #0c5460; text-align: left;'>
                                    💡 {div.get('why', 'No explanation provided')}
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    # If more than 3 sectors, show remaining in rows
                    if len(diversification) > 3:
                        for div in diversification[3:]:
                            st.markdown(f"""
                            <div style='background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%); 
                                        padding: 15px; border-radius: 12px; margin-top: 15px;
                                        border-left: 4px solid #17a2b8;'>
                                <div style='display: flex; justify-content: space-between; align-items: center;'>
                                    <div>
                                        <h4 style='margin: 0; color: #0c5460;'>{div.get('sector', 'N/A')}</h4>
                                        <p style='margin: 5px 0 0 0; font-size: 12px; color: #0c5460;'>
                                            💡 {div.get('why', 'No explanation provided')}
                                        </p>
                                    </div>
                                    <div style='text-align: right;'>
                                        <p style='margin: 0; font-size: 24px; font-weight: bold; color: #17a2b8;'>
                                            {div.get('target_percent', 0)}%
                                        </p>
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.info("📊 Your portfolio is well-diversified across sectors!")
                
                st.markdown("---")
                
                # ================================================================
                # ALLOCATION PIE CHART (Optional)
                # ================================================================
                if buys and len(buys) > 0:
                    st.markdown("### 📊 Recommended Allocation Breakdown")
                    
                    try:
                        # Create pie chart data
                        symbols = [b.get('symbol', 'Unknown') for b in buys]
                        allocations = [b.get('allocation_percent', 0) for b in buys]
                        
                        # Create Plotly pie chart
                        fig = go.Figure(data=[go.Pie(
                            labels=symbols,
                            values=allocations,
                            hole=0.4,
                            marker=dict(colors=['#28a745', '#17a2b8', '#ffc107', '#dc3545', '#6f42c1']),
                            textposition='inside',
                            textinfo='label+percent'
                        )])
                        
                        fig.update_layout(
                            title={
                                'text': 'Suggested New Investment Allocation',
                                'x': 0.5,
                                'xanchor': 'center'
                            },
                            showlegend=True,
                            height=400
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    except Exception as e:
                        st.caption(f"Chart unavailable: {str(e)}")
                
                st.markdown("---")
                
                # ================================================================
                # ACTION STEPS
                # ================================================================
                st.markdown("### 🎯 Next Steps")
                
                with st.expander("📝 How to Use These Recommendations", expanded=False):
                    st.markdown("""
                    **Step 1: Review Your Current Portfolio**
                    - Go to the "💼 Portfolio" page
                    - Check your current holdings and their values
                    
                    **Step 2: Research Recommended Stocks**
                    - Use the "🧠 Market Insights" page to learn about suggested stocks
                    - Check recent news on the "📰 Market News" page
                    
                    **Step 3: Make Informed Decisions**
                    - Don't blindly follow AI recommendations
                    - Consider your financial goals and risk tolerance
                    - Start with small allocations and diversify gradually
                    
                    **Step 4: Execute Trades**
                    - Use your preferred trading platform (Zerodha, Groww, etc.)
                    - Follow the suggested allocation percentages
                    - Keep emergency funds separate
                    
                    **Step 5: Monitor & Rebalance**
                    - Check your "📊 Risk Analysis" regularly
                    - Regenerate recommendations monthly
                    - Adjust based on market conditions
                    
                    ⚠️ **Disclaimer**: These are AI-generated suggestions based on your current portfolio.
                    Always do your own research and consult a financial advisor for major decisions.
                    """)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Fun stats
                total_buys = len(buys)
                total_sells = len(sells)
                total_sectors = len(diversification)
                
                stat_col1, stat_col2, stat_col3 = st.columns(3)
                with stat_col1:
                    st.metric("Buy Recommendations", total_buys, delta="opportunities" if total_buys > 0 else None)
                with stat_col2:
                    st.metric("Rebalance Suggestions", total_sells, delta="adjustments" if total_sells > 0 else None)
                with stat_col3:
                    st.metric("Sector Targets", total_sectors, delta="sectors" if total_sectors > 0 else None)
            
            else:
                st.error(f"❌ Failed to generate recommendations: {recommendations}")


elif page == "🎮 Portfolio Simulator":
    st.markdown("## 🎮 AI Portfolio Simulator")
    st.caption("Test portfolio changes before you make them - see what happens to your risk and returns!")
    
    # Show AI Recommendation Success Statistics
    with st.spinner("📊 Loading success statistics..."):
        success, stats = make_api_request("GET", "/api/recommendations/success-stats?recommendation_type=portfolio_simulation")
    
    if success and stats.get('total_followed', 0) > 0:
        # Create attractive stats banner
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
            <h3 style='color: white; margin: 0; text-align: center;'>
                📊 AI Recommendation Success Rate
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)
        
        with stats_col1:
            st.metric(
                "✅ Success Rate",
                f"{stats['success_rate']}%",
                delta=f"{stats['positive_count']} users benefited",
                delta_color="normal"
            )
        
        with stats_col2:
            st.metric(
                "👥 Total Users",
                stats['total_followed'],
                delta=f"{stats['evaluation_complete']} evaluated"
            )
        
        with stats_col3:
            avg_gain = stats.get('average_gain', 0)
            st.metric(
                "📈 Average Gain",
                f"{avg_gain:+.2f}%",
                delta="portfolio value change" if avg_gain != 0 else None,
                delta_color="normal" if avg_gain >= 0 else "inverse"
            )
        
        with stats_col4:
            success_emoji = "🎯" if stats['success_rate'] >= 70 else "📊" if stats['success_rate'] >= 50 else "⚠️"
            st.metric(
                "Confidence Level",
                f"{success_emoji} {stats['success_rate']:.0f}%",
                delta="High" if stats['success_rate'] >= 70 else "Medium" if stats['success_rate'] >= 50 else "Low"
            )
        
        # Show breakdown
        with st.expander("📋 See detailed breakdown"):
            breakdown_col1, breakdown_col2, breakdown_col3 = st.columns(3)
            
            with breakdown_col1:
                st.success(f"✅ Positive: {stats['positive_count']}")
            
            with breakdown_col2:
                st.warning(f"⚖️ Neutral: {stats['neutral_count']}")
            
            with breakdown_col3:
                st.error(f"❌ Negative: {stats['negative_count']}")
            
            if stats.get('pending_count', 0) > 0:
                st.info(f"⏳ Pending evaluation: {stats['pending_count']}")
        
        st.markdown("<hr>", unsafe_allow_html=True)
    
    elif success and stats.get('total_followed', 0) == 0:
        st.info("📊 **Be the first!** No users have followed AI recommendations yet. Your experience will help others make better decisions!")
    
    if not st.session_state.user_id:
        st.warning("👋 Please login first to use the simulator")
    else:
        # Fetch current portfolio
        with st.spinner("📊 Loading your portfolio..."):
            success, portfolio_data = make_api_request("GET", f"/api/portfolio/{st.session_state.user_id}")
        
        if not success or not portfolio_data.get('investments'):
            st.info("💼 You need to add investments first before using the simulator. Go to '➕ Add Investment' page!")
        else:
            current_investments = portfolio_data['investments']
            
            # Initialize session state for modified portfolio
            if 'sim_modified_portfolio' not in st.session_state:
                st.session_state.sim_modified_portfolio = []
            
            if 'sim_current_portfolio' not in st.session_state:
                st.session_state.sim_current_portfolio = []
            
            # User profile inputs
            st.markdown("### 👤 Your Investment Profile")
            
            profile_col1, profile_col2, profile_col3 = st.columns(3)
            
            with profile_col1:
                risk_appetite = st.selectbox(
                    "Risk Appetite",
                    ["low", "medium", "high"],
                    index=1,
                    help="How much risk are you willing to take?"
                )
            
            with profile_col2:
                investment_goal = st.selectbox(
                    "Investment Goal",
                    ["long-term", "short-term", "retirement", "wealth-building", "income"],
                    index=0,
                    help="What's your main investment objective?"
                )
            
            with profile_col3:
                horizon_years = st.number_input(
                    "Time Horizon (years)",
                    min_value=1,
                    max_value=50,
                    value=5,
                    help="How long do you plan to hold these investments?"
                )
            
            st.markdown("---")
            
            # Two columns: Current vs Modified
            col_current, col_modified = st.columns(2)
            
            with col_current:
                st.markdown("### 💼 Current Portfolio")
                st.caption("*Your actual holdings*")
                
                current_portfolio = []
                for inv in current_investments:
                    # Simple sector mapping
                    sector = "Technology" if inv['symbol'] in ["AAPL", "GOOGL", "MSFT", "META", "AMZN", "TSLA"] else \
                             "Finance" if inv['symbol'] in ["JPM", "BAC", "GS", "V", "MA"] else \
                             "Healthcare" if inv['symbol'] in ["JNJ", "PFE", "UNH", "ABBV"] else \
                             "Consumer" if inv['symbol'] in ["KO", "PG", "WMT", "NKE"] else \
                             "Other"
                    
                    current_portfolio.append({
                        "symbol": inv['symbol'],
                        "quantity": float(inv['quantity']),
                        "avg_buy_price": float(inv['purchase_price']),
                        "sector": sector
                    })
                    
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); 
                                padding: 15px; border-radius: 10px; margin-bottom: 10px;'>
                        <h4 style='margin: 0; color: #1565c0;'>{inv['symbol']}</h4>
                        <p style='margin: 5px 0 0 0; color: #1976d2; font-size: 13px;'>
                            Qty: {inv['quantity']} @ ${inv['purchase_price']:.2f} | Sector: {sector}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.session_state.sim_current_portfolio = current_portfolio
            
            with col_modified:
                st.markdown("### 🎯 Modified Portfolio")
                st.caption("*What you're planning to change*")
                
                # Add holdings to modified portfolio
                st.markdown("#### ➕ Add New Holdings")
                
                add_col1, add_col2, add_col3, add_col4 = st.columns([2, 1, 1, 1])
                
                with add_col1:
                    new_symbol = st.text_input("Symbol", key="sim_new_symbol", placeholder="e.g., TCS")
                with add_col2:
                    new_qty = st.number_input("Qty", min_value=0.01, value=1.0, key="sim_new_qty", step=0.01)
                with add_col3:
                    new_price = st.number_input("Price", min_value=0.01, value=100.0, key="sim_new_price", step=0.01)
                with add_col4:
                    new_sector = st.selectbox("Sector", ["Technology", "Finance", "Healthcare", "Consumer", "Energy", "Other"], key="sim_new_sector")
                
                if st.button("➕ Add to Modified Portfolio", use_container_width=True):
                    if new_symbol:
                        st.session_state.sim_modified_portfolio.append({
                            "symbol": new_symbol.upper(),
                            "quantity": float(new_qty),
                            "avg_buy_price": float(new_price),
                            "sector": new_sector
                        })
                        st.success(f"✅ Added {new_symbol.upper()} to modified portfolio!")
                        st.rerun()
                
                st.markdown("---")
                
                # Show modified portfolio holdings
                if st.session_state.sim_modified_portfolio:
                    st.markdown("#### 📋 Modified Holdings")
                    
                    for idx, item in enumerate(st.session_state.sim_modified_portfolio):
                        col_info, col_del = st.columns([4, 1])
                        
                        with col_info:
                            st.markdown(f"""
                            <div style='background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); 
                                        padding: 15px; border-radius: 10px; margin-bottom: 10px;'>
                                <h4 style='margin: 0; color: #2e7d32;'>{item['symbol']}</h4>
                                <p style='margin: 5px 0 0 0; color: #388e3c; font-size: 13px;'>
                                    Qty: {item['quantity']} @ ${item['avg_buy_price']:.2f} | Sector: {item['sector']}
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col_del:
                            if st.button("🗑️", key=f"del_{idx}", help="Remove"):
                                st.session_state.sim_modified_portfolio.pop(idx)
                                st.rerun()
                else:
                    st.info("💡 Add stocks to create your modified portfolio, or copy from current portfolio below")
                
                st.markdown("---")
                
                # Copy current portfolio button
                if st.button("📋 Copy Current Portfolio", use_container_width=True, help="Start with your current holdings"):
                    st.session_state.sim_modified_portfolio = current_portfolio.copy()
                    st.success("✅ Copied current portfolio! Now modify it above.")
                    st.rerun()
                
                # Clear modified portfolio
                if st.session_state.sim_modified_portfolio and st.button("🗑️ Clear All", use_container_width=True, type="secondary"):
                    st.session_state.sim_modified_portfolio = []
                    st.rerun()
            
            st.markdown("---")
            
            # Simulate button
            if st.session_state.sim_modified_portfolio:
                col_sim1, col_sim2, col_sim3 = st.columns([2, 3, 2])
                
                with col_sim2:
                    if st.button("🎮 RUN SIMULATION", use_container_width=True, type="primary"):
                        # Call API
                        with st.spinner("🤖 AI is analyzing your portfolio changes..."):
                            payload = {
                                "user_id": st.session_state.user_id,
                                "current_portfolio": st.session_state.sim_current_portfolio,
                                "modified_portfolio": st.session_state.sim_modified_portfolio,
                                "risk_appetite": risk_appetite,
                                "investment_goal": investment_goal,
                                "horizon_years": horizon_years
                            }
                            
                            success, simulation_result = make_api_request("POST", "/api/portfolio/simulate", json=payload, timeout=30)
                            
                            if success:
                                st.session_state.simulation_result = simulation_result
                                st.rerun()
                            else:
                                st.error(f"❌ Simulation failed: {simulation_result}")
            else:
                st.warning("⚠️ Add stocks to modified portfolio first, then click 'Run Simulation'")
            
            # Show results if available
            if 'simulation_result' in st.session_state:
                result = st.session_state.simulation_result
                
                st.markdown("---")
                st.markdown("## 📊 Simulation Results")
                
                # AI Recommendation
                ai_summary = result['ai_summary']
                
                if ai_summary['should_proceed']:
                    st.success(f"✅ **AI Recommends: PROCEED** (Confidence: {ai_summary['confidence']*100:.0f}%)")
                else:
                    st.error(f"⚠️ **AI Recommends: RECONSIDER** (Confidence: {ai_summary['confidence']*100:.0f}%)")
                
                st.info(f"💡 **Reasoning:** {ai_summary['reasoning']}")
                
                # Warnings
                if ai_summary['warnings']:
                    with st.expander("⚠️ Warnings & Considerations", expanded=True):
                        for warning in ai_summary['warnings']:
                            st.warning(f"• {warning}")
                
                st.markdown("---")
                
                # Metrics Comparison
                st.markdown("### 📈 Before vs After Comparison")
                
                metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
                
                with metric_col1:
                    st.metric(
                        "Portfolio Value",
                        f"${result['modified_portfolio']['total_value']:,.0f}",
                        delta=f"${result['changes']['value_delta']:+,.0f}"
                    )
                
                with metric_col2:
                    st.metric(
                        "Risk Score",
                        f"{result['modified_portfolio']['risk_score']:.0f}",
                        delta=f"{result['changes']['risk_delta']:+.1f}",
                        delta_color="inverse"
                    )
                
                with metric_col3:
                    st.metric(
                        "Diversification",
                        f"{result['modified_portfolio']['diversification_score']:.0f}",
                        delta=f"{result['changes']['diversification_delta']:+.1f}"
                    )
                
                with metric_col4:
                    st.metric(
                        "Top Holding %",
                        f"{result['modified_portfolio']['top_holding_pct']:.0f}%",
                        delta=f"{result['changes']['top_holding_delta']:+.1f}%",
                        delta_color="inverse"
                    )
                
                st.markdown("---")
                
                # Detailed comparison charts
                st.markdown("### 📊 Detailed Analysis")
                
                chart_tab1, chart_tab2, chart_tab3 = st.tabs(["Risk & Diversification", "Sector Distribution", "All Metrics"])
                
                with chart_tab1:
                    # Risk comparison
                    risk_df = pd.DataFrame({
                        'Portfolio': ['Current', 'Modified'],
                        'Risk Score': [result['initial_portfolio']['risk_score'], result['modified_portfolio']['risk_score']],
                        'Diversification': [result['initial_portfolio']['diversification_score'], result['modified_portfolio']['diversification_score']]
                    })
                    
                    fig_risk = go.Figure()
                    fig_risk.add_trace(go.Bar(name='Risk Score', x=risk_df['Portfolio'], y=risk_df['Risk Score'], marker_color='#ef4444'))
                    fig_risk.add_trace(go.Bar(name='Diversification', x=risk_df['Portfolio'], y=risk_df['Diversification'], marker_color='#3b82f6'))
                    fig_risk.update_layout(barmode='group', title='Risk & Diversification Comparison', yaxis_title='Score (0-100)')
                    st.plotly_chart(fig_risk, use_container_width=True)
                
                with chart_tab2:
                    # Sector distribution comparison
                    col_sector1, col_sector2 = st.columns(2)
                    
                    with col_sector1:
                        st.markdown("**Current Sectors**")
                        current_sectors = result['initial_portfolio']['sector_distribution']
                        if current_sectors:
                            fig_current = go.Figure(data=[go.Pie(labels=list(current_sectors.keys()), values=list(current_sectors.values()))])
                            fig_current.update_layout(title='Current', height=300)
                            st.plotly_chart(fig_current, use_container_width=True)
                    
                    with col_sector2:
                        st.markdown("**Modified Sectors**")
                        modified_sectors = result['modified_portfolio']['sector_distribution']
                        if modified_sectors:
                            fig_modified = go.Figure(data=[go.Pie(labels=list(modified_sectors.keys()), values=list(modified_sectors.values()))])
                            fig_modified.update_layout(title='Modified', height=300)
                            st.plotly_chart(fig_modified, use_container_width=True)
                
                with chart_tab3:
                    # All metrics table
                    metrics_comparison = pd.DataFrame({
                        'Metric': ['Total Value', 'Risk Score', 'Diversification', 'Sentiment', 'Opportunity', 'Threat', 'Top Holding %', 'Holdings Count'],
                        'Current': [
                            f"${result['initial_portfolio']['total_value']:,.0f}",
                            f"{result['initial_portfolio']['risk_score']:.1f}",
                            f"{result['initial_portfolio']['diversification_score']:.1f}",
                            f"{result['initial_portfolio']['sentiment_score']:.1f}",
                            f"{result['initial_portfolio']['opportunity_exposure']:.1f}",
                            f"{result['initial_portfolio']['threat_exposure']:.1f}",
                            f"{result['initial_portfolio']['top_holding_pct']:.1f}%",
                            f"{result['initial_portfolio']['holdings_count']}"
                        ],
                        'Modified': [
                            f"${result['modified_portfolio']['total_value']:,.0f}",
                            f"{result['modified_portfolio']['risk_score']:.1f}",
                            f"{result['modified_portfolio']['diversification_score']:.1f}",
                            f"{result['modified_portfolio']['sentiment_score']:.1f}",
                            f"{result['modified_portfolio']['opportunity_exposure']:.1f}",
                            f"{result['modified_portfolio']['threat_exposure']:.1f}",
                            f"{result['modified_portfolio']['top_holding_pct']:.1f}%",
                            f"{result['modified_portfolio']['holdings_count']}"
                        ],
                        'Change': [
                            f"${result['changes']['value_delta']:+,.0f}",
                            f"{result['changes']['risk_delta']:+.1f}",
                            f"{result['changes']['diversification_delta']:+.1f}",
                            f"{result['changes']['sentiment_delta']:+.1f}",
                            f"{result['changes']['opportunity_delta']:+.1f}",
                            f"{result['changes']['threat_delta']:+.1f}",
                            f"{result['changes']['top_holding_delta']:+.1f}%",
                            f"{result['modified_portfolio']['holdings_count'] - result['initial_portfolio']['holdings_count']:+d}"
                        ]
                    })
                    
                    st.dataframe(metrics_comparison, use_container_width=True, hide_index=True)
                
                st.markdown("---")
                
                # Action buttons
                action_col1, action_col2 = st.columns(2)
                
                with action_col1:
                    if st.button("🔄 Run New Simulation", use_container_width=True):
                        del st.session_state.simulation_result
                        st.rerun()
                
                with action_col2:
                    if st.button("✅ Looks Good! (Close)", use_container_width=True, type="primary"):
                        del st.session_state.simulation_result
                        st.rerun()
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Recommendation Follow-up Section
                st.markdown("---")
                st.markdown("### 🎯 Did you follow this recommendation?")
                st.caption("Help other investors by sharing your experience!")
                
                follow_col1, follow_col2 = st.columns([2, 1])
                
                with follow_col1:
                    st.info("📊 **Track Your Results**: If you implement these changes, we'll track the outcome to help improve our AI recommendations for everyone!")
                
                with follow_col2:
                    # Track recommendation button
                    if st.button("📝 I Implemented This!", use_container_width=True, type="secondary"):
                        # Record that user is following this recommendation
                        track_payload = {
                            "user_id": st.session_state.user_id,
                            "recommendation_type": "portfolio_simulation",
                            "initial_portfolio_value": result['initial_portfolio']['total_value'],
                            "recommendation_summary": ai_summary['reasoning'][:500]  # Limit length
                        }
                        
                        track_success, track_result = make_api_request(
                            "POST", 
                            "/api/recommendations/track-follow",
                            json=track_payload
                        )
                        
                        if track_success:
                            st.session_state.tracked_outcome_id = track_result['outcome_id']
                            st.success("✅ Great! We'll track this recommendation.")
                            st.balloons()
                        else:
                            st.error("❌ Failed to track recommendation")
                
                # If user already tracked this recommendation, show outcome update form
                if 'tracked_outcome_id' in st.session_state:
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown("#### 📈 How did it go?")
                    st.caption("After some time, come back and let us know the results!")
                    
                    outcome_form_col1, outcome_form_col2, outcome_form_col3 = st.columns(3)
                    
                    with outcome_form_col1:
                        final_portfolio_value = st.number_input(
                            "Current Portfolio Value ($)",
                            min_value=0.0,
                            value=result['modified_portfolio']['total_value'],
                            step=100.0,
                            help="What's your portfolio worth now?"
                        )
                    
                    with outcome_form_col2:
                        outcome_type = st.selectbox(
                            "Overall Outcome",
                            ["positive", "neutral", "negative"],
                            help="Did following the AI recommendation help you?"
                        )
                    
                    with outcome_form_col3:
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button("💾 Submit Results", use_container_width=True, type="primary"):
                            # Update the outcome
                            update_payload = {
                                "outcome_id": st.session_state.tracked_outcome_id,
                                "final_portfolio_value": final_portfolio_value,
                                "outcome": outcome_type
                            }
                            
                            update_success, update_result = make_api_request(
                                "POST",
                                "/api/recommendations/update-outcome",
                                json=update_payload
                            )
                            
                            if update_success:
                                change_pct = update_result.get('percentage_change', 0)
                                st.success(f"✅ Thank you! Your portfolio changed by {change_pct:+.2f}%")
                                del st.session_state.tracked_outcome_id
                                st.balloons()
                                st.rerun()
                            else:
                                st.error("❌ Failed to update outcome")


elif page == "📰 Market News":
    st.markdown("## 📰 Market News & Insights")
    
    st.markdown("""
    Stay updated with the latest financial news from multiple trusted sources including:
    - **Economic Times** - India's leading business newspaper
    - **Zerodha Pulse** - Curated financial news and insights
    - **NewsAPI** - Global news aggregator (API key required)
    - **Alpha Vantage** - Financial market news (API key required)
    - **Finnhub** - Real-time financial news (API key required)
    - **Marketaux** - Market news (Free, no key needed)
    - **GNews** - Global news (Free tier available)
    """)
    
    # Source selection and fetch controls
    st.markdown("### 🎯 Select News Sources")
    
    col_sources = st.columns(4)
    selected_sources = []
    
    with col_sources[0]:
        if st.checkbox("📰 Economic Times", value=True, key="src_et"):
            selected_sources.append("economic_times")
        if st.checkbox("🐂 Zerodha Pulse", value=True, key="src_zp"):
            selected_sources.append("zerodha")
    
    with col_sources[1]:
        if st.checkbox("🌐 NewsAPI", value=False, key="src_na"):
            selected_sources.append("newsapi")
        if st.checkbox("📊 Alpha Vantage", value=False, key="src_av"):
            selected_sources.append("alpha_vantage")
    
    with col_sources[2]:
        if st.checkbox("📈 Finnhub", value=False, key="src_fh"):
            selected_sources.append("finnhub")
        if st.checkbox("💹 Marketaux", value=True, key="src_mx"):
            selected_sources.append("marketaux")
    
    with col_sources[3]:
        if st.checkbox("🌍 GNews", value=False, key="src_gn"):
            selected_sources.append("gnews")
    
    st.markdown("---")
    
    # Fetch News button with selected sources
    col1, col2, col3, col4 = st.columns([1.5, 1, 1, 1])
    with col1:
        fetch_btn_text = f"🔄 Refresh from {len(selected_sources)} Source(s)" if selected_sources else "⚠️ Select at least one source"
        if st.button(fetch_btn_text, key="refresh_news_btn", disabled=len(selected_sources)==0, 
                     help=f"Fetch latest news from: {', '.join(selected_sources)}"):
            with st.spinner(f"Fetching latest news from {len(selected_sources)} sources..."):
                # Send selected sources to API
                import requests
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/api/news/fetch",
                        json=selected_sources if selected_sources else None,
                        timeout=60
                    )
                    if response.status_code == 200:
                        result = response.json()
                        new_count = result.get('new_articles_saved', 0)
                        total_count = result.get('articles_fetched', 0)
                        dup_count = result.get('duplicates_skipped', 0)
                        
                        if new_count > 0:
                            st.success(f"✅ Added {new_count} new articles!")
                        else:
                            st.info(f"ℹ️ All {total_count} articles already in database (no new articles)")
                        
                        st.info(f"📊 Fetched: {total_count} | New: {new_count} | Duplicates: {dup_count}")
                        st.rerun()
                    else:
                        st.error(f"❌ Error: {response.text}")
                except Exception as e:
                    st.error(f"❌ Error fetching news: {str(e)}")
    
    with col2:
        if st.button("📊 View Stats", key="stats_btn"):
            stats_success, stats_data = make_api_request("GET", "/api/news/sources")
            if stats_success:
                st.info(f"Total Sources: {len(stats_data.get('sources', []))}")
    
    with col3:
        # Filter by source
        sources_success, sources_data = make_api_request("GET", "/api/news/sources")
        if sources_success and sources_data.get('sources'):
            source_filter = st.selectbox(
                "Filter by Source",
                ["All"] + [src['name'] for src in sources_data['sources']],
                key="source_filter"
            )
        else:
            source_filter = "All"
    
    with col4:
        # Filter by sentiment
        sentiment_filter = st.selectbox(
            "Filter by Sentiment",
            ["All", "positive", "neutral", "negative"],
            key="sentiment_filter"
        )
    
    st.markdown("---")
    
    # Fetch and display news
    params = "?limit=100"
    if source_filter != "All":
        params += f"&source={source_filter}"
    if sentiment_filter != "All":
        params += f"&sentiment={sentiment_filter}"
    
    success, news_data = make_api_request("GET", f"/api/news/latest{params}")
    
    if success:
        articles = news_data.get('articles', [])
        
        if not articles:
            st.info("📭 No news articles yet. Click 'Refresh News' to fetch latest articles!")
        else:
            st.markdown(f"### Latest {len(articles)} Articles")
            
            # Display articles
            for article in articles:
                sentiment_emoji = "😊" if article['sentiment'] == 'positive' else "😐" if article['sentiment'] == 'neutral' else "😞"
                
                with st.expander(f"{sentiment_emoji} {article['title']}", expanded=False):
                    col_art1, col_art2 = st.columns([3, 1])
                    
                    with col_art1:
                        st.markdown(f"**Source:** {article['source']}")
                        if article['summary']:
                            st.markdown(f"**Summary:** {article['summary'][:300]}...")
                        st.markdown(f"**Published:** {article['published_at'][:10] if article['published_at'] else 'N/A'}")
                    
                    with col_art2:
                        # Sentiment indicator
                        sentiment_color = "🟢" if article['sentiment'] == 'positive' else "🟡" if article['sentiment'] == 'neutral' else "🔴"
                        st.metric(
                            "Sentiment",
                            article['sentiment'].capitalize(),
                            delta=None
                        )
                    
                    # Read more button
                    if article['url']:
                        st.markdown(f"[📖 Read Full Article]({article['url']})")
    else:
        st.error(f"❌ Error loading news: {news_data}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p><strong>FinBuddy v1.0.0</strong> - AI-Powered Financial Companion</p>
    <p>🤖 Powered by Google Gemini AI | 💻 Built with Streamlit</p>
    <p>⚠️ For Educational Purposes Only</p>
</div>
""", unsafe_allow_html=True)
