import os
import re

# 1. Update frontend/dist/index.html
index_html = '''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%231d4ed8'%3E%3Cpath d='M21 16v-2l-8-5V3.5c0-.83-.67-1.5-1.5-1.5S10 2.67 10 3.5V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z'/%3E%3C/svg%3E" />
    <title>FARECAST — Smarter Skies. Better Decisions.</title>
    <meta name="description" content="FARECAST — AI-powered aviation and airfare intelligence platform for India. Real-time airfare monitoring, ML fare prediction, price anomalies, and Prototype Airfare Price Index." />
    <meta name="keywords" content="airfare, CPI, consumer price index, India, flight prices, fare prediction, FARECAST" />
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet" />
    <script type="module" crossorigin src="/assets/index-DJ3zwA0y.js"></script>
    <link rel="stylesheet" crossorigin href="/assets/index-CVHLz7nN.css">
  </head>
  <body>
    <div id="root"></div>
  </body>
</html>'''

with open('frontend/dist/index.html', 'w', encoding='utf-8') as f:
    f.write(index_html)
print('Updated frontend/dist/index.html')

# 2. Update frontend/dist/assets/index-CVHLz7nN.css
with open('frontend/src/index.css', 'r', encoding='utf-8') as f:
    css = f.read()
with open('frontend/dist/assets/index-CVHLz7nN.css', 'w', encoding='utf-8') as f:
    f.write(css)
print('Updated frontend/dist/assets/index-CVHLz7nN.css')

# 3. Read bundle
bundle_path = 'frontend/dist/assets/index-DJ3zwA0y.js'
with open(bundle_path, 'r', encoding='utf-8') as f:
    bundle = f.read()

# Locate vY (FilterPanel)
vY_start = bundle.find('function vY({filters:$,onFilterChange:se})')
if vY_start == -1:
    raise Exception("Could not find function vY in bundle")

# Find end of vY: it ends with 'children:"Reset Filters"})]})}'
vY_marker = 'children:"Reset Filters"})]})}'
vY_end = bundle.find(vY_marker, vY_start) + len(vY_marker)
old_vY = bundle[vY_start:vY_end]
print("Found vY, len:", len(old_vY))

# New vY with:
# 1. Dynamic Origin / Destination logic (ensures Origin != Destination, resets destination on origin change)
# 2. Date picker functionality for travel date
new_vY = '''function vY({filters:$,onFilterChange:se}){
  const[Me,qe]=Vo.useState([]),[ht,Tt]=Vo.useState([]);
  Vo.useEffect(()=>{Eh.routes().then(qe).catch(()=>{}),Eh.airlines().then(Tt).catch(()=>{})},[]);
  const ir=[...new Set(Me.map(Jn=>Jn.origin))].sort();
  const Jr=Me.filter(Jn=>!$.origin||Jn.origin===$.origin).map(Jn=>Jn.destination).filter((Jn,va,ga)=>ga.indexOf(Jn)===va&&Jn!==$.origin).sort();
  
  const handleOriginChange = (e) => {
    const val = e.target.value;
    const newDest = ($.destination === val) ? "" : $.destination;
    se({ ...$, origin: val, destination: newDest });
  };
  
  const handleDestChange = (e) => {
    const val = e.target.value;
    const newOrig = ($.origin === val) ? "" : $.origin;
    se({ ...$, destination: val, origin: newOrig });
  };
  
  const nn=Jn=>va=>se({...$,[Jn]:va.target.value});
  const qn=()=>se({origin:"",destination:"",airline:"",cabinClass:"Economy",travelDate:""});
  
  const todayStr = new Date().toISOString().split("T")[0];

  return nr.jsxs("div",{className:"filter-panel",children:[
    nr.jsxs("div",{className:"filter-group",children:[
      nr.jsx("label",{className:"filter-label",htmlFor:"filter-origin",children:"Origin"}),
      nr.jsxs("select",{id:"filter-origin",className:"filter-select",value:$.origin,onChange:handleOriginChange,children:[
        nr.jsx("option",{value:"",children:"All Origins"}),
        ir.map(Jn=>nr.jsx("option",{value:Jn,children:C7[Jn]||Jn},Jn))
      ]})
    ]}),
    nr.jsxs("div",{className:"filter-group",children:[
      nr.jsx("label",{className:"filter-label",htmlFor:"filter-destination",children:"Destination"}),
      nr.jsxs("select",{id:"filter-destination",className:"filter-select",value:$.destination,onChange:handleDestChange,children:[
        nr.jsx("option",{value:"",children:"All Destinations"}),
        Jr.map(Jn=>nr.jsx("option",{value:Jn,children:C7[Jn]||Jn},Jn))
      ]})
    ]}),
    nr.jsxs("div",{className:"filter-group",children:[
      nr.jsx("label",{className:"filter-label",htmlFor:"filter-airline",children:"Airline"}),
      nr.jsxs("select",{id:"filter-airline",className:"filter-select",value:$.airline,onChange:nn("airline"),children:[
        nr.jsx("option",{value:"",children:"All Airlines"}),
        ht.map(Jn=>nr.jsx("option",{value:Jn.name||Jn,children:Jn.name||Jn},Jn.name||Jn))
      ]})
    ]}),
    nr.jsxs("div",{className:"filter-group",children:[
      nr.jsx("label",{className:"filter-label",htmlFor:"filter-cabin",children:"Cabin Class"}),
      nr.jsx("select",{id:"filter-cabin",className:"filter-select",value:$.cabinClass,onChange:nn("cabinClass"),children:
        dY.map(Jn=>nr.jsx("option",{value:Jn,children:Jn||"All Classes"},Jn))
      })
    ]}),
    nr.jsxs("div",{className:"filter-group",children:[
      nr.jsx("label",{className:"filter-label",htmlFor:"filter-date",children:"Travel Date"}),
      nr.jsx("input",{
        id:"filter-date",
        type:"date",
        min:todayStr,
        className:"filter-input",
        value:$.travelDate||"",
        onChange:nn("travelDate")
      })
    ]}),
    nr.jsx("button",{className:"btn-secondary",onClick:qn,id:"filter-reset",children:"Reset Filters"})
  ]});
}'''

bundle = bundle[:vY_start] + new_vY + bundle[vY_end:]
print("Replaced vY successfully")

# Locate zY (PredictionPanel)
zY_start = bundle.find('function zY({filters:$})')
if zY_start == -1:
    raise Exception("Could not find function zY in bundle")

zY_marker = 'historical medians."})]})]})}'
zY_end = bundle.find(zY_marker, zY_start) + len(zY_marker)
old_zY = bundle[zY_start:zY_end]
print("Found zY, len:", len(old_zY))

# New zY with:
# 1. Dynamic Origin / Destination logic (prevents same city)
# 2. Date picker functionality with auto-calculated remaining days
new_zY = '''function zY({filters:$}){
  const[se,Me]=Vo.useState(null),
       [qe,ht]=Vo.useState(!1),
       [Tt,ir]=Vo.useState(null);

  const getFutureDateStr = (days) => {
    const d = new Date();
    d.setDate(d.getDate() + days);
    return d.toISOString().split("T")[0];
  };
  const todayStr = new Date().toISOString().split("T")[0];

  const[Jr,nn]=Vo.useState({
    origin:$.origin||"DEL",
    destination:($.destination&&$.destination!==$.origin)?$.destination:"BOM",
    airline:$.airline||"IndiGo",
    cabin_class:$.cabinClass||"Economy",
    stops:0,
    days_left:30,
    duration_minutes:135,
    travel_date:getFutureDateStr(30)
  });

  Vo.useEffect(()=>{
    nn(va=>{
      const newOrig = $.origin || va.origin;
      let newDest = $.destination || va.destination;
      if (newDest === newOrig) {
        newDest = newOrig === "DEL" ? "BOM" : "DEL";
      }
      return {
        ...va,
        origin: newOrig,
        destination: newDest,
        airline: $.airline || va.airline,
        cabin_class: $.cabinClass || va.cabin_class
      };
    });
  },[$]);

  const allAirports = ["DEL","BOM","BLR","HYD","MAA","CCU","GOI","JAI","AMD","COK","ATQ","IXC"];

  const handleOriginSelect = (e) => {
    const newOrig = e.target.value;
    let newDest = Jr.destination;
    if (newDest === newOrig) {
      newDest = newOrig === "DEL" ? "BOM" : "DEL";
    }
    nn({ ...Jr, origin: newOrig, destination: newDest });
  };

  const handleDestSelect = (e) => {
    const newDest = e.target.value;
    let newOrig = Jr.origin;
    if (newOrig === newDest) {
      newOrig = newDest === "DEL" ? "BOM" : "DEL";
    }
    nn({ ...Jr, destination: newDest, origin: newOrig });
  };

  const handleDateChange = (e) => {
    const dateVal = e.target.value;
    if (dateVal) {
      const today = new Date();
      today.setHours(0,0,0,0);
      const target = new Date(dateVal);
      target.setHours(0,0,0,0);
      const diffDays = Math.max(1, Math.round((target - today) / (1000 * 60 * 60 * 24)));
      nn({ ...Jr, travel_date: dateVal, days_left: diffDays });
    }
  };

  const qn = async () => {
    ht(!0); ir(null);
    try {
      const va = await Eh.prediction(Jr);
      Me(va);
    } catch(va) {
      ir(va.message);
    } finally {
      ht(!1);
    }
  };

  const Jn = va => ga => nn({ ...Jr, [va]: ga.target.value });

  return nr.jsxs("div",{className:"prediction-card",id:"prediction-panel",children:[
    nr.jsxs("div",{style:{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:14},children:[
      nr.jsx("div",{className:"card-title",style:{margin:0},children:"🤖 ML Fare Prediction Engine"}),
      nr.jsx("span",{className:"chip blue",children:"CatBoost Model"})
    ]}),
    nr.jsxs("div",{style:{display:"grid",gridTemplateColumns:"1fr 1fr",gap:10,marginBottom:12},children:[
      nr.jsxs("div",{className:"filter-group",children:[
        nr.jsx("label",{className:"filter-label",htmlFor:"pred-origin",children:"Origin"}),
        nr.jsx("select",{
          id:"pred-origin",
          className:"filter-select",
          value:Jr.origin,
          onChange:handleOriginSelect,
          style:{fontSize:"0.82rem",padding:"7px 10px"},
          children:allAirports.map(va=>nr.jsx("option",{value:va,children:L7[va]||va},va))
        })
      ]}),
      nr.jsxs("div",{className:"filter-group",children:[
        nr.jsx("label",{className:"filter-label",htmlFor:"pred-dest",children:"Destination"}),
        nr.jsx("select",{
          id:"pred-dest",
          className:"filter-select",
          value:Jr.destination,
          onChange:handleDestSelect,
          style:{fontSize:"0.82rem",padding:"7px 10px"},
          children:allAirports.filter(va=>va!==Jr.origin).map(va=>nr.jsx("option",{value:va,children:L7[va]||va},va))
        })
      ]}),
      nr.jsxs("div",{className:"filter-group",children:[
        nr.jsxs("label",{className:"filter-label",htmlFor:"pred-date",children:[
          "Travel Date ",
          nr.jsx("span",{style:{color:"var(--accent-primary)",fontWeight:700},children:`(${Jr.days_left}d lead)`})
        ]}),
        nr.jsx("input",{
          id:"pred-date",
          className:"filter-input",
          type:"date",
          min:todayStr,
          value:Jr.travel_date||getFutureDateStr(Jr.days_left),
          onChange:handleDateChange,
          style:{fontSize:"0.82rem",padding:"6px 10px"}
        })
      ]}),
      nr.jsxs("div",{className:"filter-group",children:[
        nr.jsx("label",{className:"filter-label",htmlFor:"pred-cabin",children:"Cabin Class"}),
        nr.jsxs("select",{
          id:"pred-cabin",
          className:"filter-select",
          value:Jr.cabin_class,
          onChange:Jn("cabin_class"),
          style:{fontSize:"0.82rem",padding:"7px 10px"},
          children:[
            nr.jsx("option",{children:"Economy"}),
            nr.jsx("option",{children:"Premium Economy"}),
            nr.jsx("option",{children:"Business"})
          ]
        })
      ]})
    ]}),
    nr.jsx("button",{
      className:"btn-primary",
      onClick:qn,
      disabled:qe,
      id:"predict-btn",
      style:{width:"100%",marginBottom:14,justifyContent:"center"},
      children:qe?"Calculating Fare Intelligence…":"Predict Fare"
    }),
    Tt&&nr.jsx("div",{style:{color:"var(--accent-red)",fontSize:"0.75rem",marginBottom:10,background:"var(--accent-red-pale)",padding:"8px 12px",borderRadius:6},children:
      Tt.includes("not trained")||Tt.includes("503")
        ?"⚠ ML model not trained yet. Run: python ml/train.py"
        :`⚠ ${Tt}`
    }),
    se&&!Tt&&nr.jsxs("div",{style:{borderTop:"1px solid var(--border)",paddingTop:12},children:[
      nr.jsxs("div",{style:{display:"flex",justifyContent:"space-between",alignItems:"baseline"},children:[
        nr.jsxs("div",{className:"prediction-fare",children:[
          "₹",Number(se.predicted_fare).toLocaleString("en-IN",{maximumFractionDigits:0})
        ]}),
        nr.jsx("span",{className:`confidence-badge ${(se.confidence||"low").toLowerCase()}`,children:
          `${(se.confidence||"LOW").toUpperCase()} confidence`
        })
      ]}),
      se.lower_bound!=null&&se.upper_bound!=null&&nr.jsxs("div",{className:"prediction-range",children:[
        "Expected Band: ₹",Number(se.lower_bound).toLocaleString("en-IN",{maximumFractionDigits:0}),
        " – ₹",Number(se.upper_bound).toLocaleString("en-IN",{maximumFractionDigits:0})
      ]}),
      nr.jsxs("div",{style:{display:"flex",gap:8,alignItems:"center",marginTop:8,flexWrap:"wrap"},children:[
        se.lookup_method&&nr.jsx("span",{className:"chip blue",children:se.lookup_method.replace("_"," ").toUpperCase()}),
        se.r2_score!=null&&nr.jsxs("span",{style:{fontSize:"0.7rem",color:"var(--text-secondary)"},children:[
          "R² Score: ",Number(se.r2_score).toFixed(2),
          se.mae!=null&&` · Baseline MAE: ₹${Number(se.mae).toLocaleString("en-IN",{maximumFractionDigits:0})}`
        ]})
      ]}),
      nr.jsxs("div",{style:{fontSize:"0.68rem",color:"var(--text-muted)",marginTop:8,lineHeight:1.4},children:[
        se.model_name," · Real-time booking lead & yield dynamics calibrated against DGCA historical medians."
      ]})
    ]})
  ]});
}'''

bundle = bundle[:zY_start] + new_zY + bundle[zY_end:]
print("Replaced zY successfully")

# Locate YY (App component)
YY_start = bundle.find('function YY()')
if YY_start == -1:
    raise Exception("Could not find function YY in bundle")

root_marker = 'G3.createRoot(document.getElementById("root"))'
root_idx = bundle.find(root_marker, YY_start)
if root_idx == -1:
    raise Exception("Could not find root_marker in bundle")

old_YY = bundle[YY_start:root_idx]
print("Found YY, len:", len(old_YY))

# Multi-section redesign for FARECAST:
# 5 sections:
# 1. "fare-index": Route Fare Index (Dashboard/Default)
# 2. "predictions": ML Predictions
# 3. "anomalies": Price Anomalies & Prototype Price Index
# 4. "air-corridor": India Air Corridor Map
# 5. "backtesting": 30-Day Data & DGCA Validation

new_YY = '''function YY(){
  const[activeTab,setActiveTab]=Vo.useState("fare-index");
  const[sidebarCollapsed,setSidebarCollapsed]=Vo.useState(false);
  const[$,se]=Vo.useState(null);
  const[Me,qe]=Vo.useState(null);
  const[ht,Tt]=Vo.useState(null);
  const[ir,Jr]=Vo.useState([]);
  const[nn,qn]=Vo.useState(true);
  const[Jn,va]=Vo.useState(null);
  const[ga,Li]=Vo.useState({origin:"",destination:"",airline:"",cabinClass:"Economy",travelDate:""});

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

  const navItems = [
    { id: "fare-index", icon: "📊", label: "Route Fare Index", subtitle: "Overview, Trends & Core Indices" },
    { id: "predictions", icon: "🤖", label: "ML Predictions", subtitle: "Dynamic Fare Forecasting & Yield Modeling" },
    { id: "anomalies", icon: "⚠️", label: "Price Anomalies & Index", subtitle: "Detection Engine & Prototype Price Index" },
    { id: "air-corridor", icon: "🗺️", label: "India Air Corridor Map", subtitle: "Route Traffic Density & Geo Connectivity" },
    { id: "backtesting", icon: "📋", label: "30-Day Data & DGCA", subtitle: "Empirical Backtesting & Route Weights" },
  ];

  const currentNav = navItems.find(n => n.id === activeTab) || navItems[0];

  return nr.jsxs("div",{className:"app-shell",children:[
    // Sidebar
    nr.jsxs("aside",{className:`sidebar ${sidebarCollapsed?"collapsed":""}`,children:[
      nr.jsxs("div",{className:"sidebar-brand",children:[
        nr.jsx("div",{className:"sidebar-logo",children:"✈"}),
        nr.jsxs("div",{className:"sidebar-brand-text",children:[
          nr.jsx("div",{className:"sidebar-name",children:"FARECAST"}),
          nr.jsx("div",{className:"sidebar-tagline",children:"Smarter Skies. Better Decisions."})
        ]}),
        nr.jsx("button",{
          className:"sidebar-toggle",
          title: sidebarCollapsed ? "Expand Sidebar" : "Collapse Sidebar",
          onClick: () => setSidebarCollapsed(!sidebarCollapsed),
          children: sidebarCollapsed ? "→" : "←"
        })
      ]}),
      nr.jsxs("nav",{className:"sidebar-nav",children:[
        nr.jsx("div",{className:"sidebar-section-label",children:"Intelligence Modules"}),
        navItems.map(item => nr.jsxs("div",{
          key: item.id,
          className: `nav-item ${activeTab === item.id ? "active" : ""}`,
          "data-tooltip": item.label,
          onClick: () => setActiveTab(item.id),
          children:[
            nr.jsx("span",{className:"nav-icon",children:item.icon}),
            nr.jsx("span",{className:"nav-label",children:item.label})
          ]
        }))
      ]}),
      nr.jsx("div",{className:"sidebar-footer",children:[
        nr.jsxs("div",{className:"sidebar-footer-info",children:[
          nr.jsx("span",{className:"live-dot",style:{backgroundColor: Ii==="live"?"#10b981":"#f59e0b"}}),
          nr.jsxs("div",{className:"sidebar-footer-text",children:[
            nr.jsx("div",{className:"sidebar-footer-label",children:"System Status"}),
            nr.jsx("div",{className:"sidebar-footer-val",children:Ii.toUpperCase()})
          ]})
        ]})
      ]})
    ]}),

    // Main Area
    nr.jsxs("div",{className:`main-area ${sidebarCollapsed?"sidebar-collapsed":""}`,children:[
      // Topbar
      nr.jsxs("header",{className:"topbar",children:[
        nr.jsxs("div",{className:"topbar-left",children:[
          nr.jsx("button",{
            className:"btn-secondary",
            style:{padding:"6px 10px",fontSize:"1rem",border:"none",background:"transparent",cursor:"pointer"},
            onClick: () => setSidebarCollapsed(!sidebarCollapsed),
            title: "Toggle Sidebar",
            children: "☰"
          }),
          nr.jsxs("div",{children:[
            nr.jsx("div",{className:"topbar-page-title",children:currentNav.label}),
            nr.jsx("div",{className:"topbar-page-subtitle",children:currentNav.subtitle})
          ]})
        ]}),
        nr.jsxs("div",{className:"topbar-right",children:[
          nr.jsxs("span",{className:`topbar-badge ${Ii}`,children:[
            nr.jsx("span",{className:"live-dot",style:{backgroundColor: Ii==="live"?"#10b981":"#f59e0b"}}),
            Ii === "live" ? "Live Amadeus Feed" : Ii === "historical" ? "Historical Data" : "Demo Simulation"
          ]}),
          nr.jsx("span",{className:"topbar-date",children:new Date().toLocaleDateString("en-IN",{weekday:"short",month:"short",day:"numeric",year:"numeric"})})
        ]})
      ]}),

      // Status Banner
      nr.jsx(FY,{mode:Ii,status:Me}),

      // Page Content
      nr.jsxs("main",{className:"page-content",children:[
        nn&&nr.jsxs("div",{className:"loading",children:[
          nr.jsx("div",{className:"spinner"}),
          "Loading airfare intelligence datasets…"
        ]}),
        Jn&&nr.jsxs("div",{className:"error-state",children:[
          "⚠ Could not connect to FARECAST backend: ",Jn,
          nr.jsx("br",{}),
          nr.jsx("small",{children:"Ensure the FastAPI service is running: uvicorn backend.app.main:app --port 8000"})
        ]}),
        !nn&&!Jn&&$&&nr.jsxs("div",{className:"page-enter",key:activeTab,children:[
          // 1. ROUTE FARE INDEX (Dashboard / Default)
          activeTab === "fare-index" && nr.jsxs(nr.Fragment,{children:[
            nr.jsx(vY,{filters:ga,onFilterChange:Li}),
            nr.jsx(hY,{kpi:$.kpi,indexData:ht,dataMode:Ii}),
            nr.jsxs("div",{className:"charts-grid",children:[
              nr.jsx(TY,{data:$.fare_trend}),
              nr.jsx(SY,{indexData:ht,origin:ga.origin,destination:ga.destination})
            ]}),
            nr.jsxs("div",{className:"charts-grid",children:[
              nr.jsx(CY,{data:$.airline_comparison}),
              nr.jsx(PY,{data:$.top_routes})
            ]}),
            // Quick prototype price index snapshot
            nr.jsxs("div",{className:"card",style:{marginTop:20},children:[
              nr.jsx("div",{className:"card-title",children:"Prototype Airfare Price Index Snapshot"}),
              ht?nr.jsxs("div",{style:{display:"flex",justifyContent:"space-between",alignItems:"center",flexWrap:"wrap",gap:16,padding:"8px 4px"},children:[
                nr.jsxs("div",{children:[
                  nr.jsxs("div",{style:{fontSize:"2.2rem",fontWeight:800,color:"var(--accent-primary)"},children:[
                    (ht.index_value||ht.aggregate_index||100).toFixed(1)
                  ]}),
                  nr.jsx("div",{style:{fontSize:"0.72rem",color:"var(--text-muted)",textTransform:"uppercase",letterSpacing:"0.08em"},children:"Index Score (Base = 100)"})
                ]}),
                nr.jsxs("div",{style:{fontSize:"0.85rem",color:"var(--text-secondary)"},children:[
                  nr.jsx("strong",{children:ga.origin&&ga.destination ? `${ga.origin} → ${ga.destination}` : "All Major Indian Domestic Routes"}),
                  nr.jsx("br",{}),
                  "Baseline Period: ",ht.baseline_period||"2025-Q1",
                  " · Baseline Fare: ₹",(ht.baseline_avg_fare||ht.baseline_fare||0).toLocaleString("en-IN")
                ]}),
                nr.jsx("button",{
                  className:"btn-primary",
                  onClick:()=>setActiveTab("anomalies"),
                  children:"Deep-Dive in Price Anomalies →"
                })
              ]}):nr.jsx("div",{className:"empty-state",children:"Select a route above to see index snapshot"})
            ]})
          ]}),

          // 2. ML PREDICTIONS
          activeTab === "predictions" && nr.jsxs(nr.Fragment,{children:[
            nr.jsxs("div",{className:"section-header",children:[
              nr.jsxs("div",{className:"section-header-left",children:[
                nr.jsx("span",{className:"section-eyebrow",children:"Machine Learning Yield Engine"}),
                nr.jsx("h2",{className:"section-title",children:"Dynamic ML Fare Prediction & Lead-Time Analytics"}),
                nr.jsx("p",{className:"section-subtitle",children:"Calibrated CatBoost regression models with DGCA yield curves and advance booking lead-time dynamics."})
              ]})
            ]}),
            nr.jsxs("div",{className:"charts-grid",children:[
              nr.jsx(zY,{filters:ga}),
              nr.jsxs("div",{className:"card",children:[
                nr.jsx("div",{className:"card-title",children:"Historical Fare Trend for Context"}),
                nr.jsx(TY,{data:$.fare_trend}),
                nr.jsxs("div",{style:{marginTop:14,padding:12,background:"var(--bg-app)",borderRadius:"var(--radius-sm)",border:"1px solid var(--border)"},children:[
                  nr.jsx("div",{style:{fontWeight:700,fontSize:"0.78rem",marginBottom:4,color:"var(--text-primary)"},children:"💡 How FARECAST Predicts Fares"}),
                  nr.jsx("p",{style:{fontSize:"0.72rem",color:"var(--text-secondary)",lineHeight:1.5},children:"Our CatBoost engine factors in route distance, airline operational tier, cabin class, days remaining before departure, day of week, and seasonal peak factors calibrated from over 89,400 observations across Indian corridors."})
                ]})
              ]})
            ]})
          ]}),

          // 3. PRICE ANOMALIES & PROTOTYPE PRICE INDEX
          activeTab === "anomalies" && nr.jsxs(nr.Fragment,{children:[
            nr.jsxs("div",{className:"section-header",children:[
              nr.jsxs("div",{className:"section-header-left",children:[
                nr.jsx("span",{className:"section-eyebrow",children:"Surge & Anomaly Detection"}),
                nr.jsx("h2",{className:"section-title",children:"Price Anomalies & Prototype Price Index"}),
                nr.jsx("p",{className:"section-subtitle",children:"Algorithmic surge detection and DGCA passenger-weighted consumer price index tracking."})
              ]})
            ]}),
            nr.jsxs("div",{className:"charts-grid",children:[
              nr.jsx(DY,{anomalies:ir}),
              nr.jsxs("div",{className:"card",children:[
                nr.jsx("div",{className:"card-title",children:"Prototype Airfare Price Index"}),
                ht?nr.jsxs("div",{className:"index-display",children:[
                  nr.jsx("div",{className:"index-number",children:(ht.index_value||ht.aggregate_index||100).toFixed(1)}),
                  nr.jsx("div",{className:"index-label",children:"Index Value (Baseline = 100)"}),
                  nr.jsxs("div",{className:`index-change ${(ht.index_value||ht.aggregate_index||100)>100?"up":"down"}`,children:[
                    (ht.index_value||ht.aggregate_index||100)>100?"↑":"↓"," ",
                    Math.abs((ht.index_value||ht.aggregate_index||100)-100).toFixed(1),"% ",
                    (ht.index_value||ht.aggregate_index||100)>100?"above":"below"," baseline"
                  ]}),
                  nr.jsxs("div",{className:"index-note",children:[
                    ht.note||"Prototype Airfare Price Index — academic and regulatory intelligence prototype.",
                    nr.jsx("br",{}),
                    "Baseline Period: ",ht.baseline_period||"2025-Q1"," (₹",(ht.baseline_avg_fare||ht.baseline_fare||0).toLocaleString("en-IN"),")"
                  ]})
                ]}):nr.jsx("div",{className:"empty-state",children:"No route index data available"}),
                nr.jsx("div",{style:{marginTop:16},children:nr.jsx(SY,{indexData:ht,origin:ga.origin,destination:ga.destination})})
              ]})
            ]})
          ]}),

          // 4. INDIA AIR CORRIDOR MAP
          activeTab === "air-corridor" && nr.jsxs(nr.Fragment,{children:[
            nr.jsxs("div",{className:"section-header",children:[
              nr.jsxs("div",{className:"section-header-left",children:[
                nr.jsx("span",{className:"section-eyebrow",children:"Geographic Connectivity"}),
                nr.jsx("h2",{className:"section-title",children:"India Air Corridor & Traffic Density Map"}),
                nr.jsx("p",{className:"section-subtitle",children:"Interactive route network visualizing flight volume, passenger density, and median fare corridors."})
              ]})
            ]}),
            nr.jsx(HY,{})
          ]}),

          // 5. 30-DAY DATA & DGCA VALIDATION
          activeTab === "backtesting" && nr.jsxs(nr.Fragment,{children:[
            nr.jsxs("div",{className:"section-header",children:[
              nr.jsxs("div",{className:"section-header-left",children:[
                nr.jsx("span",{className:"section-eyebrow",children:"Statistical Benchmarking"}),
                nr.jsx("h2",{className:"section-title",children:"30-Day Data & DGCA Benchmark Validation"}),
                nr.jsx("p",{className:"section-subtitle",children:"Empirical backtesting suite comparing platform scraped prices against official DGCA market benchmarks and city-pair weights."})
              ]})
            ]}),
            nr.jsx(BY,{})
          ]})
        ]})
      ]}),

      // Footer
      nr.jsxs("footer",{className:"dashboard-footer",children:[
        nr.jsxs("div",{style:{display:"flex",justifyContent:"space-between",alignItems:"center",width:"100%",flexWrap:"wrap",gap:12},children:[
          nr.jsxs("div",{className:"footer-badge",children:[
            nr.jsx("span",{children:"✈"}),
            " FARECAST · SIH 2026 Problem Statement 26056"
          ]}),
          nr.jsxs("div",{className:"footer-links",children:[
            nr.jsx("span",{children:"Ministry of Civil Aviation / MoSPI Context"}),
            nr.jsx("span",{children:"·"}),
            nr.jsx("span",{children:"CatBoost ML Engine"}),
            nr.jsx("span",{children:"·"}),
            nr.jsx("span",{children:"FastAPI + React"})
          ]})
        ]}),
        nr.jsx("div",{className:"footer-disclaimer",children:
          "FARECAST is an academic and aviation intelligence research prototype for airfare price index calculation, anomaly detection, and empirical DGCA benchmarking. Not affiliated with the official Government of India Consumer Price Index."
        })
      ]})
    ]})
  ]});
}'''

bundle = bundle[:YY_start] + new_YY + bundle[root_idx:]
print("Replaced YY successfully")

with open(bundle_path, 'w', encoding='utf-8') as f:
    f.write(bundle)

print("Finished writing patched bundle, final size:", len(bundle))
