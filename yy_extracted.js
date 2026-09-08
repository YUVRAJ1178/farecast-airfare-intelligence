function YY(){
  const[activeTab,setActiveTab]=Vo.useState("home");
  const[$,se]=Vo.useState(null);
  const[Me,qe]=Vo.useState(null);
  const[ht,Tt]=Vo.useState(null);
  const[ir,Jr]=Vo.useState([]);
  const[nn,qn]=Vo.useState(true);
  const[Jn,va]=Vo.useState(null);
  const[ga,Li]=Vo.useState({origin:"DEL",destination:"BOM",airline:"",cabinClass:"Economy",travelDate:"2026-09-25"});

  const hi=Vo.useCallback(async()=>{
    try{
      const[Ln,Nn,Fn]=await Promise.all([Eh.dashboardSummary(),Eh.liveStatus(),Eh.anomalies({limit:10})]);
      se(Ln); qe(Nn); Jr(Fn); va(null);
    }catch(Ln){
      va(Ln.message);
    }finally{
      qn(false);
    }
  },[]);

  const Ui=Vo.useCallback(async()=>{
    if(ga.origin&&ga.destination)try{
      const Ln=await Eh.indexRoute(ga.origin,ga.destination);
      Tt(Ln);
    }catch{
      Tt(null);
    }else try{
      const Ln=await Eh.indexAggregate({origin:ga.origin,destination:ga.destination});
      Tt(Ln);
    }catch{
      Tt(null);
    }
  },[ga.origin,ga.destination]);

  Vo.useEffect(()=>{
    hi();
    const Ln=setInterval(hi,WY);
    return()=>clearInterval(Ln);
  },[hi]);

  Vo.useEffect(()=>{
    Ui();
  },[Ui]);

  const Ii=(Me==null?void 0:Me.overall_mode)||($==null?void 0:$.data_mode)||"demo";

  const sidebarNavItems = [
    { id: "home", icon: "🏠", label: "Home" },
    { id: "dashboard", icon: "田", label: "Dashboard" },
    { id: "predictions", icon: "🧠", label: "ML Predictions" },
    { id: "anomalies", icon: "⚠️", label: "Price Anomalies" },
    { id: "price-index", icon: "📈", label: "Prototype Price Index" },
    { id: "air-corridor", icon: "🗺️", label: "India Map" },
    { id: "backtesting", icon: "📅", label: "30-Day Data" },
  ];

  const rightNavItems = [
    { id: "home", label: "Home\n(Overview)", icon: "🏠" },
    { id: "predictions", label: "Dashboard\n(ML Predictions)", icon: "🧠" },
    { id: "anomalies", label: "Price Anomalies\n& Index", icon: "⚠️" },
    { id: "air-corridor", label: "India Map\n(Corridors)", icon: "🗺️" },
    { id: "backtesting", label: "30-Day Data\n(Backtesting)", icon: "📅" },
  ];

  const fallbackMonths = ['Jan 2024', 'Feb 2024', 'Mar 2024', 'Apr 2024', 'May 2024', 'Jun 2024', 'Jul 2024', 'Aug 2024', 'Sep 2024'];
  const fallbackFares = [5200, 6100, 5800, 6300, 6000, 5600, 6400, 5900, 6471];
  const fallbackIndex = [93.2, 98.4, 91.0, 88.5, 92.8, 89.2, 94.6, 91.5, 92.8];

  const chartMonths = ($ && $.fare_trend && $.fare_trend.length > 0) ? $.fare_trend.map(d => d.month) : fallbackMonths;
  const chartFares = ($ && $.fare_trend && $.fare_trend.length > 0) ? $.fare_trend.map(d => d.avg_fare) : fallbackFares;
  const chartIndexMonths = (ht && ht.monthly_series && ht.monthly_series.length > 0) ? ht.monthly_series.map(d => d.period) : fallbackMonths;
  const chartIndexVals = (ht && ht.monthly_series && ht.monthly_series.length > 0) ? ht.monthly_series.map(d => d.index_value) : fallbackIndex;

  const topRoutesList = [
    { rank: 1, route: "DEL → BOM", fare: 8542, change: 2.4 },
    { rank: 2, route: "BOM → DEL", fare: 8120, change: 1.8 },
    { rank: 3, route: "DEL → BLR", fare: 7824, change: -0.6 },
    { rank: 4, route: "BLR → DEL", fare: 7615, change: 1.2 },
    { rank: 5, route: "DEL → HYD", fare: 6982, change: 0.9 },
  ];

  const airlineFaresList = [
    { airline: "IndiGo", code: "6E", fare: 6210, trend: 2.1, color: "#0047AB" },
    { airline: "Air India", code: "AI", fare: 7842, trend: 1.4, color: "#dc2626" },
    { airline: "SpiceJet", code: "SG", fare: 5980, trend: -3.7, color: "#ea580c" },
    { airline: "Go First", code: "G8", fare: 6542, trend: 0.8, color: "#16a34a" },
    { airline: "Vistara", code: "UK", fare: 8276, trend: 1.9, color: "#701a75" },
  ];

  const plotlyLightLayout = {
    paper_bgcolor: "transparent",
    plot_bgcolor: "rgba(248, 250, 252, 0.5)",
    font: { color: "#475569", family: "Inter, sans-serif", size: 10 },
    margin: { t: 15, r: 15, b: 35, l: 48 },
    xaxis: { gridcolor: "rgba(203, 213, 225, 0.4)", linecolor: "rgba(203, 213, 225, 0.6)", tickfont: { size: 9, color: "#64748b" } },
    yaxis: { gridcolor: "rgba(203, 213, 225, 0.4)", linecolor: "rgba(203, 213, 225, 0.6)", tickfont: { size: 9, color: "#64748b" } },
    hovermode: "x unified",
    showlegend: false
  };

  return nr.jsxs("div", { className: "app-shell", children: [
    /* LEFT SIDEBAR */
    nr.jsxs("aside", { className: "sidebar", children: [
      nr.jsxs("div", { className: "sidebar-brand", children: [
        nr.jsxs("svg",{className:"brand-origami-plane",viewBox:"0 0 40 40",fill:"none",children:[
  nr.jsxs("defs",{children:[
    nr.jsxs("linearGradient",{id:"og1",x1:"0%",y1:"0%",x2:"100%",y2:"100%",children:[
      nr.jsx("stop",{offset:"0%",stopColor:"#4f46e5"}),
      nr.jsx("stop",{offset:"100%",stopColor:"#7c3aed"})
    ]}),
    nr.jsxs("linearGradient",{id:"og2",x1:"0%",y1:"0%",x2:"100%",y2:"100%",children:[
      nr.jsx("stop",{offset:"0%",stopColor:"#6366f1"}),
      nr.jsx("stop",{offset:"100%",stopColor:"#a855f7"})
    ]}),
    nr.jsxs("linearGradient",{id:"og3",x1:"0%",y1:"0%",x2:"100%",y2:"100%",children:[
      nr.jsx("stop",{offset:"0%",stopColor:"#3b82f6"}),
      nr.jsx("stop",{offset:"100%",stopColor:"#6366f1"})
    ]})
  ]}),
  nr.jsx("path",{d:"M6 22 L34 8 L22 34 L18 24 Z",fill:"url(#og1)"}),
  nr.jsx("path",{d:"M34 8 L18 24 L22 34 Z",fill:"url(#og2)",opacity:0.9}),
  nr.jsx("path",{d:"M18 24 L22 28 L20 33 Z",fill:"url(#og3)"}),
  nr.jsx("path",{d:"M6 22 L20 22 L18 24 Z",fill:"#4338ca",opacity:0.6})
]}),
        nr.jsxs("div", { children: [
          nr.jsx("div", { className: "sidebar-name", children: "FORECAST" }),
          nr.jsx("div", { className: "sidebar-tagline", children: "Smarter Skies. Better Decisions." })
        ]})
      ]}),
      nr.jsx("nav", { className: "sidebar-nav", children:
        sidebarNavItems.map(item => nr.jsxs("div", {
          key: item.id,
          className: `nav-item ${activeTab === item.id ? "active" : ""}`,
          onClick: () => setActiveTab(item.id),
          children: [
            nr.jsx("span", { className: "nav-icon", children: item.icon }),
            nr.jsx("span", { children: item.label })
          ]
        }))
      }),
      nr.jsxs("div", { className: "sidebar-footer-wrap", children: [
        nr.jsx("div", { className: "sidebar-skyline-container", children: nr.jsxs("svg",{style:{width:"100%",height:"100%",overflow:"visible"},viewBox:"0 0 200 90",fill:"none",children:[
  nr.jsx("rect",{x:12,y:35,width:10,height:55,rx:1,fill:"#e0f2fe"}),
  nr.jsx("rect",{x:9,y:26,width:16,height:11,rx:2,fill:"#bae6fd"}),
  nr.jsx("line",{x1:17,y1:26,x2:17,y2:16,stroke:"#7dd3fc",strokeWidth:1.5}),
  nr.jsx("rect",{x:28,y:50,width:14,height:40,rx:1,fill:"#e0f2fe"}),
  nr.jsx("rect",{x:46,y:40,width:12,height:50,rx:1,fill:"#bae6fd"}),
  nr.jsx("rect",{x:62,y:55,width:16,height:35,rx:1,fill:"#e0f2fe"}),
  nr.jsx("rect",{x:82,y:45,width:14,height:45,rx:1,fill:"#bae6fd"}),
  nr.jsx("rect",{x:100,y:60,width:18,height:30,rx:1,fill:"#e0f2fe"}),
  nr.jsx("rect",{x:122,y:48,width:15,height:42,rx:1,fill:"#bae6fd"}),
  nr.jsx("rect",{x:141,y:65,width:20,height:25,rx:1,fill:"#e0f2fe"}),
  nr.jsx("path",{d:"M8 82 C 55 82, 85 60, 135 20",stroke:"#bae6fd",strokeWidth:3.5,fill:"none",opacity:0.75}),
  nr.jsx("path",{d:"M8 82 C 55 82, 85 60, 135 20",stroke:"#ffffff",strokeWidth:1.5,fill:"none",opacity:0.95}),
  nr.jsx("polygon",{points:"135,16 142,27 134,25 130,29",fill:"#3b82f6"})
]}) }),
        nr.jsxs("div", { className: "sidebar-ai-pill", children: [
          nr.jsx("div", { className: "sidebar-ai-icon", children: "💡" }),
          nr.jsxs("div", { children: [
            nr.jsx("div", { className: "sidebar-ai-title", children: "Powered by AI" }),
            nr.jsx("div", { className: "sidebar-ai-subtitle", children: "for a smarter aviation future" })
          ]})
        ]})
      ]})
    ]}),

    /* RIGHT VERTICAL PANEL */
    nr.jsxs("aside", { className: "right-panel", children: [
      nr.jsx("div", { className: "right-panel-header", children: "Page 1 of 5" }),
      rightNavItems.map(item => nr.jsxs("div", {
        key: item.id,
        className: `right-nav-item ${activeTab === item.id ? "active" : ""}`,
        onClick: () => setActiveTab(item.id),
        children: [
          nr.jsx("span", { className: "right-nav-icon", children: item.icon }),
          nr.jsx("span", { className: "right-nav-label", children: item.label })
        ]
      })),
      nr.jsxs("div", { className: "right-panel-footer", children: [
        nr.jsxs("svg",{style:{width:54,height:44},viewBox:"0 0 60 50",fill:"none",children:[
  nr.jsx("path",{d:"M10 40 C 35 45, 55 35, 45 15 C 35 -2, 15 10, 25 25 C 35 38, 50 25, 52 12",stroke:"#cbd5e1",strokeWidth:1.3,strokeDasharray:"3 3",fill:"none"}),
  nr.jsx("polygon",{points:"52,10 57,17 51,15",fill:"#94a3b8"})
]}),
        nr.jsxs("div", { className: "right-panel-scroll-hint", children: [
          "Scroll to explore", nr.jsx("br", {}), "more insights"
        ]}),
        nr.jsx("span", { style: { color: "#94a3b8", fontSize: "0.8rem", marginTop: 2 }, children: "↓" })
      ]})
    ]}),

    /* MAIN AREA */
    nr.jsxs("div", { className: "main-area", children: [
      /* TOPBAR */
      nr.jsxs("header", { className: "topbar", children: [
        nr.jsxs("div", { className: "topbar-welcome-pill", children: [
          nr.jsx("div", { className: "topbar-plane-box", children: "✈" }),
          nr.jsxs("div", { children: [
            nr.jsx("div", { className: "topbar-welcome-title", children: "Welcome to FORECAST" }),
            nr.jsx("div", { className: "topbar-welcome-sub", children: "Real-time insights. Smarter airfares. A connected India." })
          ]})
        ]}),
        nr.jsxs("div", { className: "topbar-right-controls", children: [
          nr.jsxs("div", { className: "topbar-date-pill", children: [
            nr.jsx("span", { style: { fontSize: "1rem" }, children: "📅" }),
            nr.jsxs("div", { className: "topbar-date-text", children: [
              nr.jsx("span", { className: "topbar-date-day", children: "7 Sep 2026" }),
              nr.jsx("span", { className: "topbar-date-time", children: "Mon, 14:30" })
            ]})
          ]}),
          nr.jsxs("div", { className: "topbar-bell-btn", title: "Notifications", children: [
            "🔔",
            nr.jsx("span", { className: "topbar-bell-dot" })
          ]}),
          nr.jsxs("div", { className: "topbar-user-pill", children: [
            nr.jsx("div", { className: "topbar-user-avatar", children: "A" }),
            nr.jsx("span", { className: "topbar-user-name", children: "Aaloo" }),
            nr.jsx("span", { style: { fontSize: "0.7rem", color: "#64748b" }, children: "▾" })
          ]})
        ]})
      ]}),

      /* PAGE CONTENT */
      nr.jsxs("main", { style: { padding: "20px 24px", flex: 1 }, children: [
        /* TAB: HOME */
        activeTab === "home" && nr.jsxs(nr.Fragment, { children: [
          /* HERO BANNER */
          nr.jsxs("div", { className: "hero-banner", children: [
            nr.jsxs("div", { className: "hero-content", children: [
              nr.jsx("div", { className: "hero-eyebrow", children: "Welcome to" }),
              nr.jsx("div", { className: "hero-title", children: "FORECAST" }),
              nr.jsxs("div", { className: "hero-subtitle", children: [
                "AI-powered airfare intelligence for a smarter,", nr.jsx("br", {}), "more connected India."
              ]})
            ]}),
            nr.jsx("div", { className: "hero-script-wrap", children: [
              nr.jsxs("div", { className: "hero-script-text", children: [
                "Better Insights", nr.jsx("br", {}), "Bigger Horizons"
              ]})
            ]})
          ]}),

          /* 4 STAT CARDS */
          nr.jsxs("div", { className: "stat-grid", children: [
            nr.jsxs("div", { className: "stat-card", children: [
              nr.jsx("div", { className: "stat-card-icon blue", children: "🛣️" }),
              nr.jsxs("div", { children: [
                nr.jsx("div", { className: "stat-card-label", children: "Total Routes" }),
                nr.jsx("div", { className: "stat-card-value", children: "1,248" }),
                nr.jsx("div", { className: "stat-card-change up", children: "↑ 12% vs. last month" })
              ]})
            ]}),
            nr.jsxs("div", { className: "stat-card", children: [
              nr.jsx("div", { className: "stat-card-icon purple", children: "👥" }),
              nr.jsxs("div", { children: [
                nr.jsx("div", { className: "stat-card-label", children: "Total Observations" }),
                nr.jsx("div", { className: "stat-card-value", children: "60,000+" }),
                nr.jsx("div", { className: "stat-card-change up", children: "↑ 8% vs. last month" })
              ]})
            ]}),
            nr.jsxs("div", { className: "stat-card", children: [
              nr.jsx("div", { className: "stat-card-icon green", children: "₹" }),
              nr.jsxs("div", { children: [
                nr.jsx("div", { className: "stat-card-label", children: "Avg. Fare" }),
                nr.jsx("div", { className: "stat-card-value", children: "₹6,471" }),
                nr.jsx("div", { className: "stat-card-change down", children: "↓ 3% vs. last month" })
              ]})
            ]}),
            nr.jsxs("div", { className: "stat-card", children: [
              nr.jsx("div", { className: "stat-card-icon orange", children: "✈️" }),
              nr.jsxs("div", { children: [
                nr.jsx("div", { className: "stat-card-label", children: "Active Airlines" }),
                nr.jsx("div", { className: "stat-card-value", children: "18" }),
                nr.jsx("div", { className: "stat-card-change neutral", children: "— no change" })
              ]})
            ]})
          ]}),

          /* ROUTE FARE INDEX CONTAINER */
          nr.jsxs("div", { className: "rfi-container-card", children: [
            nr.jsxs("div", { className: "rfi-header", children: [
              nr.jsxs("div", { children: [
                nr.jsxs("div", { className: "rfi-title-row", children: [
                  nr.jsx("div", { className: "rfi-icon-box", children: "📊" }),
                  nr.jsx("div", { className: "rfi-title", children: "Route Fare Index" })
                ]}),
                nr.jsx("div", { className: "rfi-subtitle", children: "Explore fare trends, route comparisons and airline performance across major routes." })
              ]}),
              nr.jsx("button", { className: "rfi-details-link", onClick: () => setActiveTab("anomalies"), children: "View Details →" })
            ]}),

            /* Filter row */
            nr.jsxs("div", { className: "filter-panel-row", children: [
              nr.jsxs("div", { className: "filter-group-col", children: [
                nr.jsx("label", { className: "filter-group-label", children: "Origin" }),
                nr.jsxs("select", {
                  className: "filter-control-select",
                  value: ga.origin,
                  onChange: e => Li({ ...ga, origin: e.target.value }),
                  children: [
                    nr.jsx("option", { value: "DEL", children: "Delhi (DEL)" }),
                    nr.jsx("option", { value: "BOM", children: "Mumbai (BOM)" }),
                    nr.jsx("option", { value: "BLR", children: "Bangalore (BLR)" }),
                    nr.jsx("option", { value: "HYD", children: "Hyderabad (HYD)" }),
                    nr.jsx("option", { value: "MAA", children: "Chennai (MAA)" }),
                    nr.jsx("option", { value: "CCU", children: "Kolkata (CCU)" })
                  ]
                })
              ]}),
              nr.jsxs("div", { className: "filter-group-col", children: [
                nr.jsx("label", { className: "filter-group-label", children: "Destination" }),
                nr.jsxs("select", {
                  className: "filter-control-select",
                  value: ga.destination,
                  onChange: e => Li({ ...ga, destination: e.target.value }),
                  children: [
                    nr.jsx("option", { value: "BOM", children: "Mumbai (BOM)" }),
                    nr.jsx("option", { value: "DEL", children: "Delhi (DEL)" }),
                    nr.jsx("option", { value: "BLR", children: "Bangalore (BLR)" }),
                    nr.jsx("option", { value: "HYD", children: "Hyderabad (HYD)" }),
                    nr.jsx("option", { value: "MAA", children: "Chennai (MAA)" }),
                    nr.jsx("option", { value: "CCU", children: "Kolkata (CCU)" })
                  ]
                })
              ]}),
              nr.jsxs("div", { className: "filter-group-col", children: [
                nr.jsx("label", { className: "filter-group-label", children: "Travel Date" }),
                nr.jsx("input", {
                  type: "date",
                  className: "filter-control-input",
                  value: ga.travelDate,
                  onChange: e => Li({ ...ga, travelDate: e.target.value })
                })
              ]}),
              nr.jsxs("div", { className: "filter-group-col", children: [
                nr.jsx("label", { className: "filter-group-label", children: "Cabin Class" }),
                nr.jsxs("select", {
                  className: "filter-control-select",
                  value: ga.cabinClass,
                  onChange: e => Li({ ...ga, cabinClass: e.target.value }),
                  children: [
                    nr.jsx("option", { children: "Economy" }),
                    nr.jsx("option", { children: "Premium Economy" }),
                    nr.jsx("option", { children: "Business" })
                  ]
                })
              ]}),
              nr.jsxs("button", {
                className: "btn-apply-filters-main",
                onClick: () => Ui(),
                children: [
                  nr.jsx("span", { children: "≡" }),
                  "Apply Filters"
                ]
              })
            ]}),

            /* 5 KPI Sub-Cards */
            nr.jsxs("div", { className: "rfi-kpi-subcards", children: [
              nr.jsxs("div", { className: "kpi-subcard", children: [
                nr.jsxs("div", { className: "kpi-subcard-left", children: [
                  nr.jsx("div", { className: "kpi-subcard-icon green", children: "📊" }),
                  nr.jsxs("div", { children: [
                    nr.jsx("div", { className: "kpi-subcard-label", children: "Avg Fare" }),
                    nr.jsx("div", { className: "kpi-subcard-val", children: "₹6,471" }),
                    nr.jsx("div", { className: "kpi-subcard-sub green", children: "↓ 3.2% vs. last month" })
                  ]})
                ]}),
                nr.jsx("div", { className: "kpi-subcard-badge green", children: "📈" })
              ]}),
              nr.jsxs("div", { className: "kpi-subcard", children: [
                nr.jsxs("div", { className: "kpi-subcard-left", children: [
                  nr.jsx("div", { className: "kpi-subcard-icon blue", children: "↓" }),
                  nr.jsxs("div", { children: [
                    nr.jsx("div", { className: "kpi-subcard-label", children: "Min Fare" }),
                    nr.jsx("div", { className: "kpi-subcard-val", children: "₹1,366" }),
                    nr.jsx("div", { className: "kpi-subcard-sub", children: "Lowest observed" })
                  ]})
                ]}),
                nr.jsx("div", { className: "kpi-subcard-badge blue", children: "↘" })
              ]}),
              nr.jsxs("div", { className: "kpi-subcard", children: [
                nr.jsxs("div", { className: "kpi-subcard-left", children: [
                  nr.jsx("div", { className: "kpi-subcard-icon red", children: "↑" }),
                  nr.jsxs("div", { children: [
                    nr.jsx("div", { className: "kpi-subcard-label", children: "Max Fare" }),
                    nr.jsx("div", { className: "kpi-subcard-val", children: "₹59,108" }),
                    nr.jsx("div", { className: "kpi-subcard-sub", children: "Highest observed" })
                  ]})
                ]}),
                nr.jsx("div", { className: "kpi-subcard-badge red", children: "↗" })
              ]}),
              nr.jsxs("div", { className: "kpi-subcard", children: [
                nr.jsxs("div", { className: "kpi-subcard-left", children: [
                  nr.jsx("div", { className: "kpi-subcard-icon purple", children: "📉" }),
                  nr.jsxs("div", { children: [
                    nr.jsx("div", { className: "kpi-subcard-label", children: "Airfare Price Index" }),
                    nr.jsx("div", { className: "kpi-subcard-val", children: "92.8" }),
                    nr.jsx("div", { className: "kpi-subcard-sub green", children: "Baseline = 100 · ↓ 7.2% below baseline" })
                  ]})
                ]}),
                nr.jsx("div", { className: "kpi-subcard-badge green", children: "✓" })
              ]}),
              nr.jsxs("div", { className: "kpi-subcard", children: [
                nr.jsxs("div", { className: "kpi-subcard-left", children: [
                  nr.jsx("div", { className: "kpi-subcard-icon cyan", children: "👁️" }),
                  nr.jsxs("div", { children: [
                    nr.jsx("div", { className: "kpi-subcard-label", children: "Observations" }),
                    nr.jsx("div", { className: "kpi-subcard-val", children: "20,020" }),
                    nr.jsx("div", { className: "kpi-subcard-sub", children: "Historical / Demo" })
                  ]})
                ]}),
                nr.jsx("div", { className: "kpi-subcard-badge blue", children: "ℹ" })
              ]})
            ]})
          ]}),

          /* CHARTS ROW */
          nr.jsxs("div", { className: "charts-grid-row", children: [
            /* Chart 1: Fare Trend */
            nr.jsxs("div", { className: "chart-card-box", children: [
              nr.jsxs("div", { className: "chart-card-top", children: [
                nr.jsxs("div", { className: "chart-card-title", children: [
                  nr.jsx("span", { style: { color: "#3b82f6" }, children: "📈" }),
                  "Fare Trend Over Time"
                ]}),
                nr.jsx("div", { className: "chart-card-dropdown", children: "Monthly avg - all routes ▾" })
              ]}),
              nr.jsx(Vm, {
                data: [{
                  x: chartMonths,
                  y: chartFares,
                  type: "scatter",
                  mode: "lines+markers",
                  name: "Avg Fare",
                  line: { color: "#3b82f6", width: 2.5, shape: "spline", smoothing: 0.8 },
                  marker: { color: "#2563eb", size: 6, line: { color: "#ffffff", width: 1.5 } },
                  fill: "tozeroy",
                  fillcolor: "rgba(59, 130, 246, 0.08)",
                  hovertemplate: "<b>%{x}</b><br>Avg Fare: ₹%{y:,.0f}<extra></extra>"
                }],
                layout: { ...plotlyLightLayout, yaxis: { ...plotlyLightLayout.yaxis, tickprefix: "₹", range: [0, 8500] }, height: 250 },
                config: { displayModeBar: false, responsive: true },
                style: { width: "100%" }
              })
            ]}),

            /* Chart 2: Prototype Index Trend */
            nr.jsxs("div", { className: "chart-card-box", children: [
              nr.jsxs("div", { className: "chart-card-top", children: [
                nr.jsxs("div", { className: "chart-card-title", children: [
                  nr.jsx("span", { style: { color: "#7c3aed" }, children: "📊" }),
                  "Prototype Price Index Trend",
                  nr.jsx("span", { style: { fontSize: "0.72rem", color: "#64748b", fontWeight: 400, marginLeft: 6 }, children: "· Baseline = 100" })
                ]}),
                nr.jsxs("div", { className: "chart-index-pill", children: [
                  nr.jsx("span", { style: { color: "#2563eb", fontSize: "0.85rem" }, children: "✈" }),
                  nr.jsx("span", { className: "chart-index-pill-val", children: "92.8" }),
                  nr.jsx("span", { className: "chart-index-pill-diff", children: "↓ 7.2% below baseline" })
                ]})
              ]}),
              nr.jsx(Vm, {
                data: [
                  {
                    x: chartIndexMonths,
                    y: chartIndexVals,
                    type: "scatter",
                    mode: "lines+markers",
                    name: "Prototype Index",
                    line: { color: "#7c3aed", width: 2.5, shape: "spline", smoothing: 0.8 },
                    marker: { color: "#8b5cf6", size: 6, line: { color: "#ffffff", width: 1.5 } },
                    fill: "tozeroy",
                    fillcolor: "rgba(124, 58, 237, 0.08)",
                    hovertemplate: "<b>%{x}</b><br>Index: %{y:.1f}<extra></extra>"
                  },
                  {
                    x: [chartIndexMonths[0], chartIndexMonths[chartIndexMonths.length - 1]],
                    y: [100, 100],
                    type: "scatter",
                    mode: "lines",
                    name: "Baseline (100)",
                    line: { color: "rgba(148, 163, 184, 0.5)", width: 1.5, dash: "dash" },
                    hoverinfo: "skip"
                  }
                ],
                layout: { ...plotlyLightLayout, yaxis: { ...plotlyLightLayout.yaxis, range: [65, 115], dtick: 10 }, height: 250 },
                config: { displayModeBar: false, responsive: true },
                style: { width: "100%" }
              })
            ]})
          ]}),

          /* BOTTOM 3-COLUMN ROW */
          nr.jsxs("div", { className: "bottom-grid-3", children: [
            /* Col 1: Top Routes */
            nr.jsxs("div", { className: "bottom-table-card", children: [
              nr.jsxs("div", { className: "bottom-table-header", children: [
                nr.jsxs("div", { className: "bottom-table-title", children: [
                  nr.jsx("span", { style: { color: "#2563eb" }, children: "✈" }),
                  "Top Routes by Average Fare"
                ]}),
                nr.jsx("span", { className: "bottom-table-link", onClick: () => setActiveTab("backtesting"), children: "View All →" })
              ]}),
              nr.jsxs("table", { className: "custom-data-table", children: [
                nr.jsx("thead", { children:
                  nr.jsxs("tr", { children: [
                    nr.jsx("th", { className: "col-rank", children: "#" }),
                    nr.jsx("th", { children: "Route" }),
                    nr.jsx("th", { children: "Avg Fare" }),
                    nr.jsx("th", { children: "Change" })
                  ]})
                }),
                nr.jsx("tbody", { children:
                  topRoutesList.map((r, i) => nr.jsxs("tr", { key: i, children: [
                    nr.jsx("td", { className: "col-rank", children: r.rank }),
                    nr.jsx("td", { className: "col-route", children: r.route }),
                    nr.jsx("td", { className: "col-fare", children: `₹${r.fare.toLocaleString('en-IN')}` }),
                    nr.jsx("td", { className: `col-change ${r.change >= 0 ? "up" : "down"}`, children: `${r.change >= 0 ? "↑" : "↓"} ${Math.abs(r.change)}%` })
                  ]}))
                })
              ]})
            ]}),

            /* Col 2: Airline Comparison */
            nr.jsxs("div", { className: "bottom-table-card", children: [
              nr.jsxs("div", { className: "bottom-table-header", children: [
                nr.jsxs("div", { className: "bottom-table-title", children: [
                  nr.jsx("span", { style: { color: "#7c3aed" }, children: "📊" }),
                  "Airline Fare Comparison"
                ]}),
                nr.jsx("span", { className: "bottom-table-link", onClick: () => setActiveTab("predictions"), children: "View All →" })
              ]}),
              nr.jsxs("table", { className: "custom-data-table", children: [
                nr.jsx("thead", { children:
                  nr.jsxs("tr", { children: [
                    nr.jsx("th", { children: "Airline" }),
                    nr.jsx("th", { children: "Avg Fare" }),
                    nr.jsx("th", { children: "Trend" })
                  ]})
                }),
                nr.jsx("tbody", { children:
                  airlineFaresList.map((a, i) => nr.jsxs("tr", { key: i, children: [
                    nr.jsxs("td", { children: [
                      nr.jsx("span", { className: "airline-badge-dot", style: { background: a.color }, children: a.code }),
                      a.airline
                    ]}),
                    nr.jsx("td", { className: "col-fare", children: `₹${a.fare.toLocaleString('en-IN')}` }),
                    nr.jsx("td", { className: `col-change ${a.trend >= 0 ? "up" : "down"}`, children: `${a.trend >= 0 ? "↑" : "↓"} ${Math.abs(a.trend)}%` })
                  ]}))
                })
              ]})
            ]}),

            /* Col 3: Ecosystem Promo Card */
            nr.jsxs("div", { className: "promo-ecosystem-card", children: [
              nr.jsx("div", { className: "promo-plane-header", children:
                nr.jsx("img", { src: "/assets/promo-plane.jpg", alt: "Airplane", className: "promo-plane-img" })
              }),
              nr.jsx("div", { className: "promo-ecosystem-title", children: "Smarter Decisions for a Stronger Aviation Ecosystem" }),
              nr.jsx("div", { className: "promo-ecosystem-body", children: "Forecast analyzes historical data, real-time trends and AI models to help you find the best fares, understand market patterns and make informed decisions." }),
              nr.jsx("button", { className: "promo-ecosystem-btn", onClick: () => setActiveTab("predictions"), children: "Explore Dashboard →" })
            ]})
          ]})
        ]}),

        /* TAB: DASHBOARD */
        activeTab === "dashboard" && nr.jsxs(nr.Fragment, { children: [
          nr.jsx(vY, { filters: ga, onFilterChange: Li }),
          nr.jsx(hY, { kpi: $ ? $.kpi : null, indexData: ht, dataMode: Ii }),
          nr.jsxs("div", { className: "charts-grid-row", children: [
            nr.jsx(TY, { data: $ ? $.fare_trend : [] }),
            nr.jsx(SY, { indexData: ht, origin: ga.origin, destination: ga.destination })
          ]}),
          nr.jsxs("div", { className: "charts-grid-row", children: [
            nr.jsx(CY, { data: $ ? $.airline_comparison : [] }),
            nr.jsx(PY, { data: $ ? $.top_routes : [] })
          ]})
        ]}),

        /* TAB: PREDICTIONS */
        activeTab === "predictions" && nr.jsxs(nr.Fragment, { children: [
          nr.jsx(zY, { filters: ga })
        ]}),

        /* TAB: ANOMALIES */
        activeTab === "anomalies" && nr.jsxs(nr.Fragment, { children: [
          nr.jsx(DY, { anomalies: ir })
        ]}),

        /* TAB: PRICE INDEX */
        activeTab === "price-index" && nr.jsxs(nr.Fragment, { children: [
          nr.jsx(SY, { indexData: ht, origin: ga.origin, destination: ga.destination })
        ]}),

        /* TAB: INDIA MAP */
        activeTab === "air-corridor" && nr.jsxs(nr.Fragment, { children: [
          nr.jsx(BY, {})
        ]}),

        /* TAB: 30-DAY DATA */
        activeTab === "backtesting" && nr.jsxs(nr.Fragment, { children: [
          nr.jsx(HY, {})
        ]})
      ]})
    ]})
  ]});
}