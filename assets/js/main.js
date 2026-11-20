/* KRUPKA CAVE RESORT — shared JS: language toggle + scrollspy nav + reveal */
(function(){
  var LANGS=["ru","cz","en"];
  function setLang(l){
    if(LANGS.indexOf(l)<0) l="ru";
    document.documentElement.setAttribute("lang",l);
    try{localStorage.setItem("kcr_lang",l);}catch(e){}
    document.querySelectorAll(".langs button").forEach(function(b){
      b.classList.toggle("on", b.getAttribute("data-set")===l);
    });
  }
  window.kcrSetLang=setLang;
  document.addEventListener("DOMContentLoaded",function(){
    var saved="ru";
    try{saved=localStorage.getItem("kcr_lang")||"ru";}catch(e){}
    setLang(saved);

    // ---- scrollspy: highlight the nav anchor of the section in view ----
    var navLinks=[].slice.call(document.querySelectorAll('.nav-links a[href^="#"]'));
    var targets=navLinks.map(function(a){
      return document.getElementById(a.getAttribute("href").slice(1));
    }).filter(Boolean);
    function spy(){
      var y=window.scrollY+100, active=null;
      for(var i=0;i<targets.length;i++){
        if(targets[i].offsetTop<=y) active=targets[i].id;
      }
      // bottom of page -> last section
      if(window.innerHeight+window.scrollY>=document.body.scrollHeight-4 && targets.length)
        active=targets[targets.length-1].id;
      navLinks.forEach(function(a){
        a.classList.toggle("active", a.getAttribute("href")==="#"+active);
      });
      var cur=document.querySelector(".nav-links a.active");
      if(cur && cur.scrollIntoView) try{cur.scrollIntoView({block:"nearest",inline:"nearest"});}catch(e){}
    }
    var ticking=false;
    window.addEventListener("scroll",function(){
      if(!ticking){requestAnimationFrame(function(){spy();ticking=false;});ticking=true;}
    },{passive:true});
    spy();

    // smooth scroll for in-page anchors (html{scroll-behavior:smooth} does the easing;
    // this just closes the gap for browsers ignoring it and sets focus target)
    document.querySelectorAll('a[href^="#"]').forEach(function(a){
      a.addEventListener("click",function(ev){
        var id=a.getAttribute("href").slice(1), el=document.getElementById(id);
        if(el){ev.preventDefault();el.scrollIntoView({behavior:"smooth"});history.replaceState(null,"","#"+id);}
      });
    });

    // reveal on scroll
    if("IntersectionObserver" in window){
      var io=new IntersectionObserver(function(es){es.forEach(function(e){
        if(e.isIntersecting){e.target.style.opacity=1;e.target.style.transform="none";io.unobserve(e.target);}
      });},{threshold:.08});
      document.querySelectorAll(".card,.ph,section h2").forEach(function(el){
        el.style.opacity=0;el.style.transform="translateY(14px)";
        el.style.transition="opacity .6s ease,transform .6s ease";io.observe(el);
      });
    }
    // scenario switcher (financials): buttons [data-scen] toggle rows/cells [data-scenval]
    document.querySelectorAll("[data-scen]").forEach(function(b){
      b.addEventListener("click",function(){
        var s=b.getAttribute("data-scen");
        document.querySelectorAll("[data-scen]").forEach(function(x){x.classList.toggle("on",x===b);});
        document.querySelectorAll("[data-scenval]").forEach(function(el){
          el.style.display=(el.getAttribute("data-scenval")===s)?"":"none";
        });
      });
    });
    var first=document.querySelector('[data-scen="base"]'); if(first) first.click();
  });
})();
/* sync 3D iframe language with page language */
(function(){
  var orig=window.kcrSetLang;
  window.kcrSetLang=function(l){orig(l);var f=document.getElementById("kcr3d");
    if(f){try{f.contentWindow.postMessage({kcrLang:l},"*");}catch(e){}
    var base=f.getAttribute("src").split("?")[0]; if(f.getAttribute("data-curlang")!==l){f.setAttribute("src",base+"?lang="+l);f.setAttribute("data-curlang",l);}}};
})();
