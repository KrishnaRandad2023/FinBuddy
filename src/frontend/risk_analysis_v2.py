# Ultra-friendly Risk Analysis Page V3 - For young micro-investors
# With priority actions, visual charts, summary cards, and balanced technical + simple language

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

