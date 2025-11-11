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

# Initialize session state
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Helper Functions
def check_server_status():
    """Check if backend server is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=3)
        return response.status_code == 200
    except:
        return False

def make_api_request(method, endpoint, data=None):
    """Make API request with error handling"""
    url = f"{API_BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        
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
         "💬 AI Chat", "🧠 Market Insights", "📚 Learn Finance", "🔍 Fraud Detection", "📊 Risk Analysis", "📰 Market News"],
        index=["🏠 Home", "👤 User Profile", "💼 Portfolio", "➕ Add Investment", 
               "💬 AI Chat", "🧠 Market Insights", "📚 Learn Finance", "🔍 Fraud Detection", "📊 Risk Analysis", "📰 Market News"].index(st.session_state.nav_selection) if st.session_state.nav_selection in ["🏠 Home", "👤 User Profile", "💼 Portfolio", "➕ Add Investment", "💬 AI Chat", "🧠 Market Insights", "📚 Learn Finance", "🔍 Fraud Detection", "📊 Risk Analysis", "📰 Market News"] else 0
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
    with st.spinner("🧠 Analyzing market news with AI..."):
        success, insights = make_api_request("GET", "/api/ai/market-insights")
    
    if success:
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
    st.markdown("## 🧠 AI Portfolio Risk Intelligence")
    st.markdown("*Your portfolio analyzed by AI in simple terms*")
    
    if not st.session_state.user_id:
        st.warning("⚠️ Please login to view your portfolio risk analysis")
    else:
        # Refresh button at top
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            if st.button("🔄 Refresh Analysis", key="refresh_risk_btn", use_container_width=True):
                st.rerun()
        
        st.markdown("---")
        
        with st.spinner("🧠 AI is analyzing your portfolio..."):
            success, risk_report = make_api_request("GET", f"/api/risk/portfolio-ai-report?user_id={st.session_state.user_id}")
            
            if success:
                # ================================================================
                # TOP SECTION: OVERALL RISK SCORE (BIG & BOLD)
                # ================================================================
                st.markdown("### 🎯 Overall Risk Assessment")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    risk_emoji = "�" if risk_report['overall_risk'] == "High" else "🟡" if risk_report['overall_risk'] == "Medium" else "�"
                    st.metric(
                        "Risk Level",
                        f"{risk_emoji} {risk_report['overall_risk']}",
                        delta=None
                    )
                
                with col2:
                    score_color = "🔴" if risk_report['score'] >= 70 else "🟡" if risk_report['score'] >= 40 else "🟢"
                    st.metric(
                        "Risk Score",
                        f"{risk_report['score']:.0f}/100 {score_color}",
                        delta=None
                    )
                
                with col3:
                    gain_loss = risk_report['portfolio_summary']['total_gain_loss']
                    gain_emoji = "📈" if gain_loss > 0 else "📉"
                    st.metric(
                        "Total Gain/Loss",
                        f"${gain_loss:,.2f} {gain_emoji}",
                        delta=f"{risk_report['portfolio_summary']['total_gain_loss_pct']:.2f}%"
                    )
                
                with col4:
                    st.metric(
                        "Portfolio Value",
                        f"${risk_report['portfolio_summary']['total_value']:,.2f}",
                        delta=None
                    )
                
                # ================================================================
                # AI SUMMARY (Gemini-generated advice)
                # ================================================================
                st.markdown("### 🤖 AI Risk Summary")
                st.info(risk_report['ai_summary'])
                
                st.markdown("---")
                
                # ================================================================
                # RISK COMPONENTS BREAKDOWN (4 Gauges)
                # ================================================================
                st.markdown("### 📊 Risk Components Breakdown")
                st.caption("*How your risk score is calculated - transparency matters!*")
                
                components = risk_report['risk_components']
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    conc_score = components['concentration']
                    conc_color = "🔴" if conc_score >= 70 else "🟡" if conc_score >= 40 else "🟢"
                    st.metric("Concentration", f"{conc_score:.0f}/100 {conc_color}")
                    with st.expander("ℹ️ What is this?"):
                        st.markdown("""
                        **Concentration Risk** measures if your portfolio is too heavily invested in one asset.
                        
                        **Calculation:**
                        - If top holding > 40% → High Risk (80 points)
                        - If top holding > 25% → Medium Risk (50 points)
                        - Otherwise → Low Risk (20 points)
                        
                        **Why it matters:** Putting all eggs in one basket is risky! Diversification protects you.
                        """)
                
                with col2:
                    vol_score = components['volatility']
                    vol_color = "🔴" if vol_score >= 70 else "🟡" if vol_score >= 40 else "🟢"
                    st.metric("Volatility", f"{vol_score:.0f}/100 {vol_color}")
                    with st.expander("ℹ️ What is this?"):
                        st.markdown("""
                        **Volatility Risk** measures how much your portfolio's value fluctuates.
                        
                        **Calculation:**
                        - Standard deviation of gain/loss % across holdings
                        - High volatility (>20%) → High Risk (75 points)
                        - Medium volatility (>10%) → Medium Risk (45 points)
                        - Low volatility → Low Risk (20 points)
                        
                        **Why it matters:** High volatility = unpredictable swings in value.
                        """)
                
                with col3:
                    sent_score = components['sentiment']
                    sent_color = "🔴" if sent_score >= 70 else "🟡" if sent_score >= 40 else "🟢"
                    st.metric("News Sentiment", f"{sent_score:.0f}/100 {sent_color}")
                    with st.expander("ℹ️ What is this?"):
                        st.markdown("""
                        **Sentiment Risk** analyzes news articles about your holdings.
                        
                        **Calculation:**
                        - AI matches news to your stocks
                        - Negative news sentiment < -0.3 → High Risk (70 points)
                        - Slightly negative → Medium Risk (45 points)
                        - Positive/neutral → Low Risk (25 points)
                        
                        **Why it matters:** Negative news often predicts price drops.
                        """)
                
                with col4:
                    exp_score = components['exposure']
                    exp_color = "🔴" if exp_score >= 70 else "🟡" if exp_score >= 40 else "🟢"
                    st.metric("Sector Exposure", f"{exp_score:.0f}/100 {exp_color}")
                    with st.expander("ℹ️ What is this?"):
                        st.markdown("""
                        **Exposure Risk** measures sector concentration.
                        
                        **Calculation:**
                        - If one sector > 50% → High Risk (70 points)
                        - If one sector > 35% → Medium Risk (45 points)
                        - Diversified → Low Risk (20 points)
                        
                        **Why it matters:** If one sector crashes, diversified portfolios survive better.
                        """)
                
                # Visual: Risk Components Radar Chart
                st.markdown("#### 📈 Visual Risk Profile")
                
                risk_labels = ['Concentration', 'Volatility', 'News Sentiment', 'Sector Exposure']
                risk_values = [
                    components['concentration'],
                    components['volatility'],
                    components['sentiment'],
                    components['exposure']
                ]
                
                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(
                    r=risk_values,
                    theta=risk_labels,
                    fill='toself',
                    name='Risk Levels',
                    line_color='red'
                ))
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(visible=True, range=[0, 100])
                    ),
                    showlegend=False,
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("---")
                
                # ================================================================
                # ALERTS & RED FLAGS
                # ================================================================
                if risk_report['alerts']:
                    st.markdown("### ⚠️ Risk Alerts & Red Flags")
                    st.caption(f"Found {len(risk_report['alerts'])} concerns that need your attention")
                    
                    for idx, alert in enumerate(risk_report['alerts'], 1):
                        if "🔴" in alert or "High" in alert:
                            st.error(f"{idx}. {alert}")
                        elif "🟡" in alert or "Medium" in alert or "Moderate" in alert:
                            st.warning(f"{idx}. {alert}")
                        else:
                            st.info(f"{idx}. {alert}")
                
                st.markdown("---")
                
                # ================================================================
                # OPPORTUNITIES & THREATS (Side by side)
                # ================================================================
                col_opp, col_threat = st.columns(2)
                
                with col_opp:
                    st.markdown("### 📈 Opportunities (Positive News)")
                    if risk_report['opportunities']:
                        for idx, opp in enumerate(risk_report['opportunities'], 1):
                            with st.expander(f"#{idx} - {opp['symbol']}: {opp['title'][:60]}...", expanded=idx==1):
                                st.markdown(f"**Symbol:** {opp['symbol']}")
                                st.markdown(f"**Headline:** {opp['title']}")
                                st.caption(f"Source: {opp['source']}")
                                st.markdown(f"**Summary:** {opp['summary']}")
                                st.markdown(f"**Sentiment Score:** {opp['sentiment_score']:.2f} 🟢")
                                if opp.get('url'):
                                    st.markdown(f"[📖 Read Full Article]({opp['url']})")
                    else:
                        st.info("No positive news found for your holdings")
                
                with col_threat:
                    st.markdown("### 📉 Threats (Negative News)")
                    if risk_report['threats']:
                        for idx, threat in enumerate(risk_report['threats'], 1):
                            with st.expander(f"#{idx} - {threat['symbol']}: {threat['title'][:60]}...", expanded=idx==1):
                                st.markdown(f"**Symbol:** {threat['symbol']}")
                                st.markdown(f"**Headline:** {threat['title']}")
                                st.caption(f"Source: {threat['source']}")
                                st.markdown(f"**Summary:** {threat['summary']}")
                                st.markdown(f"**Sentiment Score:** {threat['sentiment_score']:.2f} 🔴")
                                if threat.get('url'):
                                    st.markdown(f"[📖 Read Full Article]({threat['url']})")
                    else:
                        st.success("No negative news found for your holdings")
                
                st.markdown("---")
                
                # ================================================================
                # DETAILED ANALYSIS SECTIONS
                # ================================================================
                with st.expander("🔍 Detailed Concentration Analysis", expanded=False):
                    conc = risk_report['concentration_analysis']
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Top Holding", conc['top_holding'])
                        st.metric("Concentration %", f"{conc['top_holding_pct']:.1f}%")
                    with col2:
                        st.metric("Concentration Risk Score", f"{conc['score']}/100")
                    
                    st.markdown("#### Holdings Distribution")
                    if conc.get('holdings_distribution'):
                        df_conc = pd.DataFrame(conc['holdings_distribution'])
                        fig = px.bar(
                            df_conc,
                            x='symbol',
                            y='pct',
                            title='Portfolio Weight by Symbol',
                            labels={'pct': 'Percentage (%)', 'symbol': 'Symbol'},
                            color='pct',
                            color_continuous_scale='Reds'
                        )
                        st.plotly_chart(fig, use_container_width=True)
                
                with st.expander("📊 Detailed Volatility Analysis", expanded=False):
                    vol = risk_report['volatility_analysis']
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Standard Deviation", f"{vol['std_deviation']:.2f}%")
                        st.metric("Variance Level", vol['variance_level'])
                    with col2:
                        st.metric("Volatility Risk Score", f"{vol['score']}/100")
                    
                    st.markdown("""
                    **How to interpret:**
                    - Low variance (<10%): Stable portfolio
                    - Medium variance (10-20%): Moderate fluctuations
                    - High variance (>20%): Highly volatile
                    """)
                
                with st.expander("📰 Detailed News Sentiment Analysis", expanded=False):
                    sent = risk_report['sentiment_analysis']
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("News Matches Found", sent['total_matches'])
                        st.metric("Sentiment Risk Score", f"{sent['score']}/100")
                    
                    st.markdown("#### Recent News Matches")
                    if sent.get('matches'):
                        for match in sent['matches'][:10]:
                            sentiment_emoji = "🟢" if match['sentiment_score'] > 0.3 else "🔴" if match['sentiment_score'] < -0.3 else "🟡"
                            st.caption(f"{sentiment_emoji} **{match['symbol']}**: {match['article_title'][:100]}... (Score: {match['sentiment_score']:.2f})")
                
                with st.expander("🎯 Detailed Sector Exposure Analysis", expanded=False):
                    exp = risk_report['exposure_analysis']
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Dominant Sector", exp['dominant_sector'])
                        st.metric("Dominant Sector %", f"{exp['dominant_sector_pct']:.1f}%")
                    with col2:
                        st.metric("Exposure Risk Score", f"{exp['score']}/100")
                    
                    st.markdown("#### Sector Distribution")
                    if exp.get('sector_distribution'):
                        sector_df = pd.DataFrame([
                            {"Sector": k, "Percentage": v}
                            for k, v in exp['sector_distribution'].items()
                        ])
                        fig = px.pie(
                            sector_df,
                            values='Percentage',
                            names='Sector',
                            title='Portfolio Distribution by Sector'
                        )
                        st.plotly_chart(fig, use_container_width=True)
                
                # ================================================================
                # PER-ASSET RISK TABLE
                # ================================================================
                st.markdown("### � Per-Asset Risk Breakdown")
                
                asset_df = pd.DataFrame(risk_report['per_asset_risk'])
                asset_df['risk_emoji'] = asset_df['risk_level'].apply(
                    lambda x: "🔴" if x == "High" else "🟡" if x == "Medium" else "🟢"
                )
                
                st.dataframe(
                    asset_df[['symbol', 'risk_level', 'risk_emoji', 'value_pct']].rename(columns={
                        'symbol': 'Symbol',
                        'risk_level': 'Risk Level',
                        'risk_emoji': 'Status',
                        'value_pct': 'Portfolio Weight (%)'
                    }),
                    use_container_width=True
                )
                
                # ================================================================
                # HOW THE FINAL SCORE IS CALCULATED
                # ================================================================
                with st.expander("🧮 How is the Final Risk Score Calculated?", expanded=False):
                    st.markdown("""
                    ### Risk Score Formula
                    
                    Your final risk score is a **weighted average** of 4 components:
                    
                    ```
                    Final Score = (Concentration × 30%) + 
                                  (Volatility × 25%) + 
                                  (Sentiment × 25%) + 
                                  (Exposure × 20%)
                    ```
                    
                    **Example Calculation:**
                    - Concentration: {:.1f}/100 × 0.30 = {:.1f}
                    - Volatility: {:.1f}/100 × 0.25 = {:.1f}
                    - Sentiment: {:.1f}/100 × 0.25 = {:.1f}
                    - Exposure: {:.1f}/100 × 0.20 = {:.1f}
                    
                    **Total: {:.1f}/100**
                    
                    **Risk Levels:**
                    - 🟢 Low Risk: 0-39
                    - 🟡 Medium Risk: 40-69
                    - 🔴 High Risk: 70-100
                    """.format(
                        components['concentration'], components['concentration'] * 0.30,
                        components['volatility'], components['volatility'] * 0.25,
                        components['sentiment'], components['sentiment'] * 0.25,
                        components['exposure'], components['exposure'] * 0.20,
                        risk_report['score']
                    ))
                
                st.caption(f"Report generated at: {risk_report['timestamp']}")
                
            else:
                st.error(f"❌ Error generating risk report: {risk_report}")

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
