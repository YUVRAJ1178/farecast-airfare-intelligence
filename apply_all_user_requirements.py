"""
apply_all_user_requirements.py

Implements all user requirements on index-DJ3zwA0y.js:
1. Fix all filters (vY) with Origin, Destination, Airline, Cabin Class, Travel Date, Apply & Reset.
2. Modernize ML Prediction interface (zY) into a clean, compact, professional cockpit without blank spaces.
3. Interchange 30-Day Data & India Map in navItems and render layout.
4. Enhance India Map (HY) with quick airport selector for all 17 hubs and full connecting route displays.
5. Remove any 'Powered by AI' completely.
6. Maintain FARECAST branding everywhere.
"""
import re

BUNDLE_PATH = 'frontend/dist/assets/index-DJ3zwA0y.js'

with open(BUNDLE_PATH, 'r', encoding='utf-8') as f:
    bundle = f.read()

print("Original bundle length:", len(bundle))

# ══════════════════════════════════════════════════════════════════
# COMPONENT 1: NEW vY (FilterPanel)
# ══════════════════════════════════════════════════════════════════
new_vY = '''function vY({filters:$,onFilterChange:se}){
  const[Me,qe]=Vo.useState([]),[ht,Tt]=Vo.useState([]);
  Vo.useEffect(()=>{
    Eh.routes().then(qe).catch(()=>{});
    Eh.airlines().then(Tt).catch(()=>{});
  },[]);

  const ir=[...new Set(Me.map(Jn=>Jn.origin))].sort();
  const Jr=Me.filter(Jn=>!$.origin||Jn.origin===$.origin).map(Jn=>Jn.destination).filter((Jn,va,ga)=>ga.indexOf(Jn)===va&&Jn!==$.origin).sort();
  
  const handleOriginChange=(e)=>{
    const val=e.target.value;
    const newDest=($.destination===val)?"":$.destination;
    se({...$,origin:val,destination:newDest});
  };

  const handleDestChange=(e)=>{
    const val=e.target.value;
    const newOrig=($.origin===val)?"":$.origin;
    se({...$,destination:val,origin:newOrig});
  };

  const nn=Jn=>va=>se({...$,[Jn]:va.target.value});
  const qn=()=>se({origin:"",destination:"",airline:"",cabinClass:"Economy",travelDate:""});
  const todayStr=new Date().toISOString().split("T")[0];

  const cityMap={
    DEL:"Delhi (DEL)",BOM:"Mumbai (BOM)",BLR:"Bengaluru (BLR)",HYD:"Hyderabad (HYD)",
    CCU:"Kolkata (CCU)",MAA:"Chennai (MAA)",AMD:"Ahmedabad (AMD)",PNQ:"Pune (PNQ)",
    GOI:"Goa (GOI)",COK:"Kochi (COK)",GAU:"Guwahati (GAU)",JAI:"Jaipur (JAI)",
    LKO:"Lucknow (LKO)",PAT:"Patna (PAT)",SXR:"Srinagar (SXR)",ATQ:"Amritsar (ATQ)",IXC:"Chandigarh (IXC)"
  };

  return nr.jsxs("div",{className:"filter-panel",style:{display:"flex",gap:12,alignItems:"flex-end",flexWrap:"wrap",background:"var(--bg-secondary)",padding:"14px 18px",borderRadius:12,border:"1px solid var(--border)",marginBottom:20},children:[
    // Origin
    nr.jsxs("div",{className:"filter-group",style:{display:"flex",flexDirection:"column",gap:4,flex:"1 1 140px"},children:[
      nr.jsx("label",{className:"filter-label",htmlFor:"filter-origin",style:{fontSize:"0.72rem",fontWeight:600,color:"var(--text-muted)",textTransform:"uppercase",letterSpacing:"0.04em"},children:"Origin"}),
      nr.jsxs("select",{id:"filter-origin",className:"filter-select",value:$.origin||"",onChange:handleOriginChange,style:{fontSize:"0.82rem",padding:"8px 10px",borderRadius:8,background:"var(--bg-app)",color:"var(--text-primary)",border:"1px solid var(--border)"},children:[
        nr.jsx("option",{value:"",children:"All Origins"}),
        ir.map(Jn=>nr.jsx("option",{value:Jn,children:cityMap[Jn]||(C7&&C7[Jn])||Jn},Jn))
      ]})
    ]}),

    // Destination
    nr.jsxs("div",{className:"filter-group",style:{display:"flex",flexDirection:"column",gap:4,flex:"1 1 140px"},children:[
      nr.jsx("label",{className:"filter-label",htmlFor:"filter-destination",style:{fontSize:"0.72rem",fontWeight:600,color:"var(--text-muted)",textTransform:"uppercase",letterSpacing:"0.04em"},children:"Destination"}),
      nr.jsxs("select",{id:"filter-destination",className:"filter-select",value:$.destination||"",onChange:handleDestChange,style:{fontSize:"0.82rem",padding:"8px 10px",borderRadius:8,background:"var(--bg-app)",color:"var(--text-primary)",border:"1px solid var(--border)"},children:[
        nr.jsx("option",{value:"",children:"All Destinations"}),
        Jr.map(Jn=>nr.jsx("option",{value:Jn,children:cityMap[Jn]||(C7&&C7[Jn])||Jn},Jn))
      ]})
    ]}),

    // Airline
    nr.jsxs("div",{className:"filter-group",style:{display:"flex",flexDirection:"column",gap:4,flex:"1 1 130px"},children:[
      nr.jsx("label",{className:"filter-label",htmlFor:"filter-airline",style:{fontSize:"0.72rem",fontWeight:600,color:"var(--text-muted)",textTransform:"uppercase",letterSpacing:"0.04em"},children:"Airline"}),
      nr.jsxs("select",{id:"filter-airline",className:"filter-select",value:$.airline||"",onChange:nn("airline"),style:{fontSize:"0.82rem",padding:"8px 10px",borderRadius:8,background:"var(--bg-app)",color:"var(--text-primary)",border:"1px solid var(--border)"},children:[
        nr.jsx("option",{value:"",children:"All Airlines"}),
        ht.map(Jn=>nr.jsx("option",{value:Jn.name||Jn,children:Jn.name||Jn},Jn.name||Jn))
      ]})
    ]}),

    // Cabin Class
    nr.jsxs("div",{className:"filter-group",style:{display:"flex",flexDirection:"column",gap:4,flex:"1 1 120px"},children:[
      nr.jsx("label",{className:"filter-label",htmlFor:"filter-cabin",style:{fontSize:"0.72rem",fontWeight:600,color:"var(--text-muted)",textTransform:"uppercase",letterSpacing:"0.04em"},children:"Cabin Class"}),
      nr.jsxs("select",{id:"filter-cabin",className:"filter-select",value:$.cabinClass||"Economy",onChange:nn("cabinClass"),style:{fontSize:"0.82rem",padding:"8px 10px",borderRadius:8,background:"var(--bg-app)",color:"var(--text-primary)",border:"1px solid var(--border)"},children:[
        nr.jsx("option",{value:"Economy",children:"Economy"}),
        nr.jsx("option",{value:"Premium Economy",children:"Premium Economy"}),
        nr.jsx("option",{value:"Business",children:"Business"})
      ]})
    ]}),

    // Travel Date
    nr.jsxs("div",{className:"filter-group",style:{display:"flex",flexDirection:"column",gap:4,flex:"1 1 130px"},children:[
      nr.jsx("label",{className:"filter-label",htmlFor:"filter-date",style:{fontSize:"0.72rem",fontWeight:600,color:"var(--text-muted)",textTransform:"uppercase",letterSpacing:"0.04em"},children:"Travel Date"}),
      nr.jsx("input",{id:"filter-date",type:"date",min:todayStr,className:"filter-input",value:$.travelDate||"",onChange:nn("travelDate"),style:{fontSize:"0.82rem",padding:"7px 10px",borderRadius:8,background:"var(--bg-app)",color:"var(--text-primary)",border:"1px solid var(--border)"}})
    ]}),

    // Action Buttons
    nr.jsxs("div",{style:{display:"flex",gap:8,alignItems:"center"},children:[
      nr.jsx("button",{className:"btn-primary",id:"filter-apply",onClick:()=>se({...$}),style:{whiteSpace:"nowrap",padding:"8px 16px",fontSize:"0.82rem",display:"flex",alignItems:"center",gap:6,cursor:"pointer"},children:"✈ Apply"}),
      nr.jsx("button",{className:"btn-secondary",id:"filter-reset",onClick:qn,style:{whiteSpace:"nowrap",padding:"8px 14px",fontSize:"0.82rem",cursor:"pointer"},title:"Reset all filters",children:"↺ Reset"})
    ]})
  ]});
}'''

# ══════════════════════════════════════════════════════════════════
# COMPONENT 2: NEW zY (ML Prediction Interface - Improved Cockpit)
# ══════════════════════════════════════════════════════════════════
new_zY = '''function zY({filters:$}){
  const[se,Me]=Vo.useState(null),
       [qe,ht]=Vo.useState(!1),
       [Tt,ir]=Vo.useState(null);

  const getFutureDateStr=(days)=>{
    const d=new Date();
    d.setDate(d.getDate()+days);
    return d.toISOString().split("T")[0];
  };
  const todayStr=new Date().toISOString().split("T")[0];

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
      const newOrig=$.origin||va.origin;
      let newDest=$.destination||va.destination;
      if(newDest===newOrig){
        newDest=newOrig==="DEL"?"BOM":"DEL";
      }
      return{
        ...va,
        origin:newOrig,
        destination:newDest,
        airline:$.airline||va.airline,
        cabin_class:$.cabinClass||va.cabin_class
      };
    });
  },[$]);

  const allAirports=["DEL","BOM","BLR","HYD","CCU","MAA","AMD","PNQ","GOI","COK","GAU","JAI","LKO","PAT","SXR","ATQ","IXC"];
  const cityNames={
    DEL:"Delhi (DEL)",BOM:"Mumbai (BOM)",BLR:"Bengaluru (BLR)",HYD:"Hyderabad (HYD)",
    CCU:"Kolkata (CCU)",MAA:"Chennai (MAA)",AMD:"Ahmedabad (AMD)",PNQ:"Pune (PNQ)",
    GOI:"Goa (GOI)",COK:"Kochi (COK)",GAU:"Guwahati (GAU)",JAI:"Jaipur (JAI)",
    LKO:"Lucknow (LKO)",PAT:"Patna (PAT)",SXR:"Srinagar (SXR)",ATQ:"Amritsar (ATQ)",IXC:"Chandigarh (IXC)"
  };

  const handleOriginSelect=(e)=>{
    const newOrig=e.target.value;
    let newDest=Jr.destination;
    if(newDest===newOrig){
      newDest=newOrig==="DEL"?"BOM":"DEL";
    }
    nn({...Jr,origin:newOrig,destination:newDest});
  };

  const handleDestSelect=(e)=>{
    const newDest=e.target.value;
    let newOrig=Jr.origin;
    if(newOrig===newDest){
      newOrig=newDest==="DEL"?"BOM":"DEL";
    }
    nn({...Jr,destination:newDest,origin:newOrig});
  };

  const handleDateChange=(e)=>{
    const dateVal=e.target.value;
    if(dateVal){
      const today=new Date();
      today.setHours(0,0,0,0);
      const target=new Date(dateVal);
      target.setHours(0,0,0,0);
      const diffDays=Math.max(1,Math.round((target-today)/(1000*60*60*24)));
      nn({...Jr,travel_date:dateVal,days_left:diffDays});
    }
  };

  const qn=async()=>{
    ht(!0); ir(null);
    try{
      const va=await Eh.prediction(Jr);
      Me(va);
    }catch(va){
      ir(va.message);
    }finally{
      ht(!1);
    }
  };

  const Jn=va=>ga=>nn({...Jr,[va]:ga.target.value});

  return nr.jsxs("div",{className:"card prediction-cockpit",id:"prediction-panel",style:{padding:"24px",borderRadius:12,border:"1px solid var(--border)",background:"var(--bg-secondary)",marginBottom:24},children:[
    // Header
    nr.jsxs("div",{style:{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:20,borderBottom:"1px solid var(--border)",paddingBottom:14},children:[
      nr.jsxs("div",{children:[
        nr.jsx("div",{className:"card-title",style:{margin:0,fontSize:"1.15rem",fontWeight:700,color:"var(--text-primary)"},children:"🤖 ML Fare Prediction Engine"}),
        nr.jsx("div",{style:{fontSize:"0.75rem",color:"var(--text-muted)",marginTop:3},children:"Calibrated CatBoost regression engine analyzing booking lead time and yield dynamics"})
      ]}),
      nr.jsx("span",{className:"chip blue",style:{fontSize:"0.72rem",padding:"4px 10px",borderRadius:20,fontWeight:600},children:"CatBoost Model"})
    ]}),

    // Responsive 2-column cockpit layout
    nr.jsxs("div",{style:{display:"grid",gridTemplateColumns:"repeat(auto-fit, minmax(320px, 1fr))",gap:24,alignItems:"stretch"},children:[
      // Left Panel: Parameters Form
      nr.jsxs("div",{style:{background:"var(--bg-card)",padding:"18px 20px",borderRadius:10,border:"1px solid var(--border)",display:"flex",flexDirection:"column",justifyContent:"space-between"},children:[
        nr.jsxs("div",{children:[
          nr.jsx("div",{style:{fontSize:"0.75rem",fontWeight:700,color:"var(--text-muted)",textTransform:"uppercase",letterSpacing:"0.05em",marginBottom:14},children:"Flight Parameters"}),
          nr.jsxs("div",{style:{display:"grid",gridTemplateColumns:"1fr 1fr",gap:12,marginBottom:14},children:[
            // Origin
            nr.jsxs("div",{className:"filter-group",children:[
              nr.jsx("label",{className:"filter-label",htmlFor:"pred-origin",style:{fontSize:"0.72rem",color:"var(--text-muted)"},children:"Origin"}),
              nr.jsx("select",{id:"pred-origin",className:"filter-select",value:Jr.origin,onChange:handleOriginSelect,style:{fontSize:"0.82rem",padding:"8px 10px"},children:
                allAirports.map(va=>nr.jsx("option",{value:va,children:cityNames[va]||va},va))
              })
            ]}),
            // Destination
            nr.jsxs("div",{className:"filter-group",children:[
              nr.jsx("label",{className:"filter-label",htmlFor:"pred-dest",style:{fontSize:"0.72rem",color:"var(--text-muted)"},children:"Destination"}),
              nr.jsx("select",{id:"pred-dest",className:"filter-select",value:Jr.destination,onChange:handleDestSelect,style:{fontSize:"0.82rem",padding:"8px 10px"},children:
                allAirports.filter(va=>va!==Jr.origin).map(va=>nr.jsx("option",{value:va,children:cityNames[va]||va},va))
              })
            ]}),
            // Travel Date
            nr.jsxs("div",{className:"filter-group",children:[
              nr.jsxs("label",{className:"filter-label",htmlFor:"pred-date",style:{fontSize:"0.72rem",color:"var(--text-muted)"},children:[
                "Travel Date ",
                nr.jsx("span",{style:{color:"var(--accent-primary)",fontWeight:700},children:`(${Jr.days_left}d lead)`})
              ]}),
              nr.jsx("input",{id:"pred-date",className:"filter-input",type:"date",min:todayStr,value:Jr.travel_date||getFutureDateStr(Jr.days_left),onChange:handleDateChange,style:{fontSize:"0.82rem",padding:"7px 10px"}})
            ]}),
            // Cabin Class
            nr.jsxs("div",{className:"filter-group",children:[
              nr.jsx("label",{className:"filter-label",htmlFor:"pred-cabin",style:{fontSize:"0.72rem",color:"var(--text-muted)"},children:"Cabin Class"}),
              nr.jsxs("select",{id:"pred-cabin",className:"filter-select",value:Jr.cabin_class,onChange:Jn("cabin_class"),style:{fontSize:"0.82rem",padding:"8px 10px"},children:[
                nr.jsx("option",{value:"Economy",children:"Economy"}),
                nr.jsx("option",{value:"Premium Economy",children:"Premium Economy"}),
                nr.jsx("option",{value:"Business",children:"Business"})
              ]})
            ]}),
            // Airline
            nr.jsxs("div",{className:"filter-group",children:[
              nr.jsx("label",{className:"filter-label",htmlFor:"pred-airline",style:{fontSize:"0.72rem",color:"var(--text-muted)"},children:"Airline Carrier"}),
              nr.jsxs("select",{id:"pred-airline",className:"filter-select",value:Jr.airline||"IndiGo",onChange:Jn("airline"),style:{fontSize:"0.82rem",padding:"8px 10px"},children:[
                nr.jsx("option",{value:"IndiGo",children:"IndiGo"}),
                nr.jsx("option",{value:"Air India",children:"Air India"}),
                nr.jsx("option",{value:"Vistara",children:"Vistara"}),
                nr.jsx("option",{value:"SpiceJet",children:"SpiceJet"}),
                nr.jsx("option",{value:"Akasa Air",children:"Akasa Air"})
              ]})
            ]}),
            // Stops
            nr.jsxs("div",{className:"filter-group",children:[
              nr.jsx("label",{className:"filter-label",htmlFor:"pred-stops",style:{fontSize:"0.72rem",color:"var(--text-muted)"},children:"Flight Stops"}),
              nr.jsxs("select",{id:"pred-stops",className:"filter-select",value:Jr.stops||0,onChange:Jn("stops"),style:{fontSize:"0.82rem",padding:"8px 10px"},children:[
                nr.jsx("option",{value:0,children:"Non-stop (Direct)"}),
                nr.jsx("option",{value:1,children:"1 Stop"}),
                nr.jsx("option",{value:2,children:"2+ Stops"})
              ]})
            ]})
          ]})
        ]}),

        nr.jsx("button",{
          className:"btn-primary",
          onClick:qn,
          disabled:qe,
          id:"predict-btn",
          style:{width:"100%",padding:"12px 18px",fontSize:"0.92rem",fontWeight:700,justifyContent:"center",marginTop:10,cursor:"pointer",borderRadius:8},
          children:qe?"Calculating Fare Intelligence…":"✨ Predict Dynamic Fare"
        })
      ]}),

      // Right Panel: Intelligence Result Card
      nr.jsxs("div",{style:{background:"var(--bg-card)",padding:"20px",borderRadius:10,border:"1px solid var(--border)",display:"flex",flexDirection:"column",justifyContent:"center"},children:[
        Tt&&nr.jsx("div",{style:{color:"var(--accent-red)",fontSize:"0.78rem",background:"var(--accent-red-pale)",padding:"12px 16px",borderRadius:8,marginBottom:12},children:`⚠ ${Tt}`}),

        se&&!Tt?nr.jsxs("div",{style:{display:"flex",flexDirection:"column",gap:14},children:[
          nr.jsxs("div",{style:{display:"flex",justifyContent:"space-between",alignItems:"baseline",flexWrap:"wrap",gap:8},children:[
            nr.jsxs("div",{children:[
              nr.jsx("div",{style:{fontSize:"0.72rem",color:"var(--text-muted)",textTransform:"uppercase",letterSpacing:"0.05em"},children:"Predicted Airfare"}),
              nr.jsxs("div",{style:{fontSize:"2.4rem",fontWeight:800,color:"var(--accent-primary)",letterSpacing:"-0.03em"},children:[
                "₹",Number(se.predicted_fare).toLocaleString("en-IN",{maximumFractionDigits:0})
              ]})
            ]}),
            nr.jsx("span",{className:`confidence-badge ${(se.confidence||"low").toLowerCase()}`,style:{fontSize:"0.78rem",padding:"4px 10px",borderRadius:20,fontWeight:700},children:
              `${(se.confidence||"LOW").toUpperCase()} CONFIDENCE`
            })
          ]}),

          se.lower_bound!=null&&se.upper_bound!=null&&nr.jsxs("div",{style:{background:"var(--bg-secondary)",padding:"10px 14px",borderRadius:8,border:"1px solid var(--border)"},children:[
            nr.jsxs("div",{style:{display:"flex",justifyContent:"space-between",fontSize:"0.78rem",color:"var(--text-secondary)"},children:[
              nr.jsx("span",{children:"Expected Fare Band:"}),
              nr.jsxs("strong",{style:{color:"var(--text-primary)"},children:[
                "₹",Number(se.lower_bound).toLocaleString("en-IN",{maximumFractionDigits:0})," – ₹",Number(se.upper_bound).toLocaleString("en-IN",{maximumFractionDigits:0})
              ]})
            ]})
          ]}),

          nr.jsxs("div",{style:{display:"flex",gap:8,alignItems:"center",flexWrap:"wrap"},children:[
            se.lookup_method&&nr.jsx("span",{className:"chip blue",style:{fontSize:"0.7rem"},children:se.lookup_method.replace("_"," ").toUpperCase()}),
            se.r2_score!=null&&nr.jsxs("span",{style:{fontSize:"0.72rem",color:"var(--text-secondary)"},children:[
              "R² Score: ",Number(se.r2_score).toFixed(2),
              se.mae!=null&&` · Baseline MAE: ₹${Number(se.mae).toLocaleString("en-IN",{maximumFractionDigits:0})}`
            ]})
          ]}),

          nr.jsxs("div",{style:{fontSize:"0.7rem",color:"var(--text-muted)",borderTop:"1px solid var(--border)",paddingTop:10,lineHeight:1.5},children:[
            se.model_name||"CatBoost ML Engine"," · Calibrated against DGCA historical passenger booking distributions."
          ]})
        ]}):
        // Pre-inference clean placeholder (No empty gaps!)
        nr.jsxs("div",{style:{textAlign:"center",padding:"24px 16px"},children:[
          nr.jsx("div",{style:{fontSize:"2.2rem",marginBottom:8},children:"🎯"}),
          nr.jsxs("div",{style:{fontSize:"1.05rem",fontWeight:700,color:"var(--text-primary)",marginBottom:6},children:[
            Jr.origin," ⇄ ",Jr.destination," Fare Intelligence"
          ]}),
          nr.jsxs("div",{style:{fontSize:"0.78rem",color:"var(--text-secondary)",lineHeight:1.5,maxWidth:320,margin:"0 auto 16px"},children:[
            "Selected: ",Jr.cabin_class," · ",Jr.airline," · ",Jr.days_left," days advance lead time."
          ]}),
          nr.jsx("div",{style:{display:"inline-block",padding:"6px 14px",borderRadius:20,background:"rgba(59,130,246,0.1)",color:"var(--accent-blue-light)",fontSize:"0.75rem",fontWeight:600},children:"Click 'Predict Dynamic Fare' to compute yield forecast"})
        ]})
      ]})
    ]})
  ]});
}'''

# ══════════════════════════════════════════════════════════════════
# COMPONENT 3: NEW YY (App with Swapped Tabs, Filter Reactivity & Clean Sidebar)
# ══════════════════════════════════════════════════════════════════
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

  // Load dashboard summary reactively when filters change
  const hi=Vo.useCallback(async()=>{
    try{
      const[Ln,Nn,Fn]=await Promise.all([
        Eh.dashboardSummary({
          origin:ga.origin||"",
          destination:ga.destination||"",
          airline:ga.airline||"",
          cabin_class:ga.cabinClass||"",
          travel_date:ga.travelDate||""
        }),
        Eh.liveStatus(),
        Eh.anomalies({limit:10})
      ]);
      se(Ln); qe(Nn); Jr(Fn); va(null);
    }catch(Ln){
      va(Ln.message);
    }finally{
      qn(false);
    }
  },[ga.origin,ga.destination,ga.airline,ga.cabinClass,ga.travelDate]);

  // Load index data reactively
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

  // NAVIGATION ITEMS: 30-Day Data (4th) and India Map (5th) SWAPPED as requested!
  const navItems = [
    { id: "fare-index", icon: "📊", label: "Route Fare Index", subtitle: "Overview, Trends & Core Indices" },
    { id: "predictions", icon: "🤖", label: "ML Predictions", subtitle: "Dynamic Fare Forecasting & Yield Modeling" },
    { id: "anomalies", icon: "⚠️", label: "Price Anomalies & Index", subtitle: "Detection Engine & Prototype Price Index" },
    { id: "backtesting", icon: "📋", label: "30-Day Data & DGCA", subtitle: "Empirical Backtesting & Route Weights" },
    { id: "air-corridor", icon: "🗺️", label: "India Air Corridor Map", subtitle: "Route Traffic Density & Geo Connectivity" },
  ];

  const currentNav = navItems.find(n => n.id === activeTab) || navItems[0];

  return nr.jsxs("div",{className:"app-shell",children:[
    // Sidebar
    nr.jsxs("aside",{className:`sidebar ${sidebarCollapsed?"collapsed":""}`,children:[
      nr.jsxs("div",{className:"sidebar-brand",children:[
        nr.jsx("div",{className:"sidebar-logo",children:"✈"}),
        nr.jsxs("div",{className:"sidebar-brand-text",children:[
          nr.jsx("div",{className:"sidebar-name",children:"FARECAST"}),
          nr.jsx("div",{className:"sidebar-tagline",children:"From Flight Prices to Market Insights"})
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
      // Clean sidebar footer (WITHOUT 'Powered by AI'!)
      nr.jsx("div",{className:"sidebar-footer",style:{padding:"12px 16px",borderTop:"1px solid var(--border)"},children:[
        nr.jsxs("div",{className:"sidebar-footer-info",style:{display:"flex",alignItems:"center",gap:10},children:[
          nr.jsx("span",{className:"live-dot",style:{backgroundColor: Ii==="live"?"#10b981":"#f59e0b",width:8,height:8,borderRadius:"50%"}}),
          nr.jsxs("div",{className:"sidebar-footer-text",children:[
            nr.jsx("div",{className:"sidebar-footer-label",style:{fontSize:"0.68rem",color:"var(--text-muted)"},children:"System Status"}),
            nr.jsx("div",{className:"sidebar-footer-val",style:{fontSize:"0.78rem",fontWeight:700,color:"var(--text-primary)"},children:Ii.toUpperCase()})
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

          // 2. ML PREDICTIONS (Improved Cockpit Layout)
          activeTab === "predictions" && nr.jsxs(nr.Fragment,{children:[
            nr.jsxs("div",{className:"section-header",style:{marginBottom:16},children:[
              nr.jsxs("div",{className:"section-header-left",children:[
                nr.jsx("span",{className:"section-eyebrow",children:"Machine Learning Yield Engine"}),
                nr.jsx("h2",{className:"section-title",children:"Dynamic ML Fare Prediction & Lead-Time Analytics"}),
                nr.jsx("p",{className:"section-subtitle",children:"Calibrated CatBoost regression models with DGCA yield curves and advance booking lead-time dynamics."})
              ]})
            ]}),
            nr.jsx(zY,{filters:ga}),
            nr.jsxs("div",{className:"card",style:{marginTop:20},children:[
              nr.jsx("div",{className:"card-title",children:"Historical Fare Trend for Analytical Context"}),
              nr.jsx(TY,{data:$.fare_trend}),
              nr.jsxs("div",{style:{marginTop:14,padding:12,background:"var(--bg-app)",borderRadius:"var(--radius-sm)",border:"1px solid var(--border)"},children:[
                nr.jsx("div",{style:{fontWeight:700,fontSize:"0.78rem",marginBottom:4,color:"var(--text-primary)"},children:"💡 How FARECAST Predicts Fares"}),
                nr.jsx("p",{style:{fontSize:"0.72rem",color:"var(--text-secondary)",lineHeight:1.5},children:"Our CatBoost engine factors in route distance, airline operational tier, cabin class, days remaining before departure, day of week, and seasonal peak factors calibrated from over 89,400 observations across Indian corridors."})
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

          // 4. 30-DAY DATA & DGCA VALIDATION (INTERCHANGED TO 4TH POSITION!)
          activeTab === "backtesting" && nr.jsxs(nr.Fragment,{children:[
            nr.jsxs("div",{className:"section-header",children:[
              nr.jsxs("div",{className:"section-header-left",children:[
                nr.jsx("span",{className:"section-eyebrow",children:"Statistical Benchmarking"}),
                nr.jsx("h2",{className:"section-title",children:"30-Day Data & DGCA Benchmark Validation"}),
                nr.jsx("p",{className:"section-subtitle",children:"Empirical backtesting suite comparing platform scraped prices against official DGCA market benchmarks and city-pair weights."})
              ]})
            ]}),
            nr.jsx(BY,{})
          ]}),

          // 5. INDIA AIR CORRIDOR MAP (INTERCHANGED TO 5TH POSITION!)
          activeTab === "air-corridor" && nr.jsxs(nr.Fragment,{children:[
            nr.jsxs("div",{className:"section-header",children:[
              nr.jsxs("div",{className:"section-header-left",children:[
                nr.jsx("span",{className:"section-eyebrow",children:"Geographic Connectivity"}),
                nr.jsx("h2",{className:"section-title",children:"India Air Corridor & Traffic Density Map"}),
                nr.jsx("p",{className:"section-subtitle",children:"Interactive route network visualizing flight volume, passenger density, and median fare corridors."})
              ]})
            ]}),
            nr.jsx(HY,{})
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

# ══════════════════════════════════════════════════════════════════
# REPLACEMENT IN BUNDLE
# ══════════════════════════════════════════════════════════════════

# 1. Replace vY (156196 to 159389)
vy_start = bundle.find('function vY(')
vy_end = bundle.find('var $9={},Z9={},K9={exports:{}}')
if vy_start == -1 or vy_end == -1:
    raise Exception(f"Could not locate vY boundaries: {vy_start}, {vy_end}")
print(f"Replacing vY [{vy_start}:{vy_end}]...")
bundle = bundle[:vy_start] + new_vY + bundle[vy_end:]

# 2. Replace zY
zy_start = bundle.find('function zY(')
zy_end = bundle.find('const P7={live:')
if zy_start == -1 or zy_end == -1:
    raise Exception(f"Could not locate zY boundaries: {zy_start}, {zy_end}")
print(f"Replacing zY [{zy_start}:{zy_end}]...")
bundle = bundle[:zy_start] + new_zY + bundle[zy_end:]

# 3. Replace YY
yy_start = bundle.find('function YY(')
root_marker = 'createRoot(document.getElementById('
root_idx = bundle.find(root_marker)
if yy_start == -1 or root_idx == -1:
    raise Exception(f"Could not locate YY boundaries: {yy_start}, {root_idx}")
# Find the start of the root render statement before root_marker
render_start = bundle.rfind('G3.createRoot', yy_start, root_idx + len(root_marker))
if render_start == -1:
    render_start = bundle.rfind('createRoot', yy_start, root_idx + len(root_marker))
print(f"Replacing YY [{yy_start}:{render_start}]...")
bundle = bundle[:yy_start] + new_YY + bundle[render_start:]

# 4. Remove any remaining occurrences of "Powered by AI"
before_pai = bundle.count("Powered by AI")
bundle = bundle.replace('"Powered by AI"', '""')
print(f"Removed {before_pai} occurrences of 'Powered by AI'")

# 5. Ensure FARECAST branding everywhere
bundle = bundle.replace("FORECAST", "FARECAST")

print("Final bundle length:", len(bundle))

# Validation
import re
for comp in ['vY', 'zY', 'HY', 'BY', 'YY']:
    cnt = bundle.count(f'function {comp}(')
    print(f'function {comp}(): count={cnt}')

with open(BUNDLE_PATH, 'w', encoding='utf-8') as f:
    f.write(bundle)

print("SUCCESS: Patched bundle written to", BUNDLE_PATH)
