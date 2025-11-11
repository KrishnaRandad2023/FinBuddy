# Clean Risk Analysis Page - To be integrated into app.py

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
                # SECTION 1: YOUR PORTFOLIO AT A GLANCE
                # ================================================================
                st.markdown("### 💼 Your Portfolio Snapshot")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "💰 Total Value",
                        f"${risk_report['portfolio_summary']['total_value']:,.2f}"
                    )
                
                with col2:
                    gain_loss = risk_report['portfolio_summary']['total_gain_loss']
                    gain_pct = risk_report['portfolio_summary']['total_gain_loss_pct']
                    st.metric(
                        "📊 Profit/Loss",
                        f"${gain_loss:,.2f}",
                        delta=f"{gain_pct:.2f}%"
                    )
                
                with col3:
                    risk_emoji = "🔴" if risk_report['overall_risk'] == "High" else "🟡" if risk_report['overall_risk'] == "Medium" else "🟢"
                    st.metric(
                        "🎯 Risk Level",
                        f"{risk_report['overall_risk']}"
                    )
                    st.markdown(f"<p style='text-align: center; font-size: 40px;'>{risk_emoji}</p>", unsafe_allow_html=True)
                
                with col4:
                    score_color = "🔴" if risk_report['score'] >= 70 else "🟡" if risk_report['score'] >= 40 else "🟢"
                    st.metric(
                        "📈 Risk Score",
                        f"{risk_report['score']:.0f}/100"
                    )
                    st.progress(int(risk_report['score']))
                
                st.markdown("---")
                
                # ================================================================
                # SECTION 2: WHAT AI THINKS (Most Important)
                # ================================================================
                st.markdown("### 🤖 What Our AI Recommends")
                st.info(f"💡 {risk_report['ai_summary']}")
                
                st.markdown("---")
                
                # ================================================================
                # SECTION 3: YOUR MAIN RISKS (Simplified)
                # ================================================================
                st.markdown("### ⚠️ Things You Should Know")
                st.caption("*These are the most important alerts about your portfolio*")
                
                if risk_report['alerts']:
                    for idx, alert in enumerate(risk_report['alerts'], 1):
                        # Clean up the alert text
                        clean_alert = alert.replace("⚠️", "").replace("🔴", "").replace("🟡", "").strip()
                        
                        if "High concentration" in alert:
                            st.error(f"**{idx}. Too Many Eggs in One Basket** 🧺")
                            st.caption(f"   {clean_alert}")
                            st.caption("   💡 *What this means:* You have too much money in one stock. If it drops, you lose a lot!")
                        elif "High volatility" in alert:
                            st.warning(f"**{idx}. Your Portfolio is on a Rollercoaster** 🎢")
                            st.caption(f"   {clean_alert}")
                            st.caption("   💡 *What this means:* Your portfolio value swings a lot. This can be stressful!")
                        elif "Negative news" in alert:
                            st.error(f"**{idx}. Bad News Alert** 📰")
                            st.caption(f"   {clean_alert}")
                            st.caption("   💡 *What this means:* Recent news about your stocks isn't good. Keep an eye on this!")
                        elif "sector concentration" in alert:
                            st.warning(f"**{idx}. All Your Stocks Are Similar** 🎯")
                            st.caption(f"   {clean_alert}")
                            st.caption("   💡 *What this means:* You're only invested in one type of industry. Spread it out!")
                        else:
                            st.info(f"**{idx}.** {clean_alert}")
                else:
                    st.success("✅ No major risks detected! Your portfolio looks good!")
                
                st.markdown("---")
                
                # ================================================================
                # SECTION 4: NEWS THAT MATTERS TO YOU
                # ================================================================
                st.markdown("### 📰 News About Your Stocks")
                st.caption("*We found news articles that might affect your investments*")
                
                # Create tabs for better organization
                tab1, tab2 = st.tabs(["📈 Good News (Opportunities)", "📉 Bad News (Threats)"])
                
                with tab1:
                    st.markdown("#### 🌟 Positive News For Your Holdings")
                    if risk_report['opportunities']:
                        st.success(f"Found {len(risk_report['opportunities'])} positive news articles!")
                        
                        for idx, opp in enumerate(risk_report['opportunities'], 1):
                            with st.container():
                                st.markdown(f"**#{idx} - {opp['symbol']}** 🟢")
                                st.markdown(f"📰 *{opp['title']}*")
                                st.caption(f"**Why this is good:** {opp['summary'][:200]}...")
                                st.caption(f"Sentiment: **{opp['sentiment_score']:.2f}** (Higher is better) | Source: {opp['source']}")
                                if opp.get('url'):
                                    st.markdown(f"[🔗 Read more]({opp['url']})")
                                st.markdown("---")
                    else:
                        st.info("No significant positive news found at the moment.")
                
                with tab2:
                    st.markdown("#### ⚠️ Negative News For Your Holdings")
                    if risk_report['threats']:
                        st.warning(f"Found {len(risk_report['threats'])} concerning news articles!")
                        
                        for idx, threat in enumerate(risk_report['threats'], 1):
                            with st.container():
                                st.markdown(f"**#{idx} - {threat['symbol']}** 🔴")
                                st.markdown(f"📰 *{threat['title']}*")
                                st.caption(f"**Why this matters:** {threat['summary'][:200]}...")
                                st.caption(f"Sentiment: **{threat['sentiment_score']:.2f}** (Negative) | Source: {threat['source']}")
                                if threat.get('url'):
                                    st.markdown(f"[🔗 Read more]({threat['url']})")
                                st.markdown("---")
                    else:
                        st.success("No negative news found! That's great!")
                
                st.markdown("---")
                
                # ================================================================
                # SECTION 5: UNDERSTANDING YOUR NUMBERS (Expandable)
                # ================================================================
                with st.expander("📚 Want to Learn More? Understanding Your Risk Score", expanded=False):
                    st.markdown("### How We Calculate Your Risk Score")
                    st.caption("*We use 4 different checks to understand your portfolio risk*")
                    
                    components = risk_report['risk_components']
                    
                    # Show each component with simple explanation
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("#### 1️⃣ Concentration Check")
                        conc_score = components['concentration']
                        st.progress(int(conc_score))
                        st.caption(f"Score: {conc_score:.0f}/100")
                        st.info(f"""
                        **What it is:** Are you putting too much money in one stock?
                        
                        **Your situation:** Your biggest holding is {risk_report['concentration_analysis']['top_holding']} at {risk_report['concentration_analysis']['top_holding_pct']:.1f}% of your portfolio.
                        
                        **Rule of thumb:** Ideally, no single stock should be more than 25% of your portfolio.
                        """)
                        
                        st.markdown("#### 2️⃣ Volatility Check")
                        vol_score = components['volatility']
                        st.progress(int(vol_score))
                        st.caption(f"Score: {vol_score:.0f}/100")
                        st.info(f"""
                        **What it is:** How much does your portfolio value jump around?
                        
                        **Your situation:** Variance level is {risk_report['volatility_analysis']['variance_level']}.
                        
                        **Rule of thumb:** Lower volatility = more stable and less stressful!
                        """)
                    
                    with col2:
                        st.markdown("#### 3️⃣ News Sentiment Check")
                        sent_score = components['sentiment']
                        st.progress(int(sent_score))
                        st.caption(f"Score: {sent_score:.0f}/100")
                        st.info(f"""
                        **What it is:** What's the news saying about your stocks?
                        
                        **Your situation:** We found {risk_report['sentiment_analysis']['total_matches']} news articles about your holdings.
                        
                        **Rule of thumb:** Negative news = higher risk of price drops.
                        """)
                        
                        st.markdown("#### 4️⃣ Sector Diversity Check")
                        exp_score = components['exposure']
                        st.progress(int(exp_score))
                        st.caption(f"Score: {exp_score:.0f}/100")
                        st.info(f"""
                        **What it is:** Are all your stocks from the same industry?
                        
                        **Your situation:** {risk_report['exposure_analysis']['dominant_sector']} makes up {risk_report['exposure_analysis']['dominant_sector_pct']:.1f}% of your portfolio.
                        
                        **Rule of thumb:** Spread across different sectors (tech, healthcare, finance, etc.)
                        """)
                    
                    st.markdown("---")
                    st.markdown("### 🧮 The Final Calculation")
                    st.code(f"""
Final Risk Score = 
    (Concentration: {components['concentration']:.0f} × 30%) + 
    (Volatility: {components['volatility']:.0f} × 25%) + 
    (News Sentiment: {components['sentiment']:.0f} × 25%) + 
    (Sector Exposure: {components['exposure']:.0f} × 20%)
    
    = {risk_report['score']:.0f}/100
                    """)
                    
                    st.markdown("**What Your Score Means:**")
                    st.markdown("- 🟢 0-39: **Low Risk** - You're playing it safe!")
                    st.markdown("- 🟡 40-69: **Medium Risk** - Balanced approach")
                    st.markdown("- 🔴 70-100: **High Risk** - Aggressive strategy, be careful!")
                
                # ================================================================
                # SECTION 6: YOUR INDIVIDUAL STOCKS
                # ================================================================
                with st.expander("📋 See Risk for Each Stock", expanded=False):
                    st.markdown("### Your Holdings Breakdown")
                    
                    for asset in risk_report['per_asset_risk']:
                        risk_emoji = "🔴" if asset['risk_level'] == "High" else "🟡" if asset['risk_level'] == "Medium" else "🟢"
                        
                        col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
                        with col1:
                            st.markdown(f"**{asset['symbol']}**")
                        with col2:
                            st.caption(f"{asset['value_pct']:.1f}% of portfolio")
                        with col3:
                            st.caption(f"Risk: {asset['risk_level']}")
                        with col4:
                            st.markdown(risk_emoji)
                        
                        st.markdown("---")
                
                st.caption(f"*Report generated: {risk_report['timestamp']}*")
                
            else:
                st.error(f"❌ Couldn't load risk report: {risk_report}")
