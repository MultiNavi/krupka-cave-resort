/* KRUPKA CAVE RESORT — shared JS: language toggle + nav + reveal */
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
    // active nav link
    var here=location.pathname.split("/").pop()||"index.html";
    document.querySelectorAll(".nav-links a").forEach(function(a){
      if(a.getAttribute("href")===here) a.classList.add("active");
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
