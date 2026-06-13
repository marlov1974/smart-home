// spotprice 1.0.3-compact
(function(){
"use strict";
var AREA="SE3",TOM=1,VAT=0.25,SPOT_EX=1,MARKUP_EX=0.06,VARCOST_EX=0,ETAX_EX=0.36;
var GRID="time_tariff",GFLAT=0.305,GHIGH=0.765,GLOW=0.305,HM="1,2,3,11,12",HD="1,2,3,4,5",H0=6,H1=22;
var K2H="hp.price.2h",KD="hp.price.date",KA="hp.price.area",KS="hp.price.status",KU="hp.price.updated";
function log(s){print("spotprice "+String(s||""));}
function p2(n){n=Number(n);return n<10?"0"+n:String(n);}
function r3(n){return Math.round(n*1000)/1000;}
function iv(v){return v*(1+VAT);}
function has(csv,v){return (","+csv+",").indexOf(","+String(v)+",")>=0;}
function iso(){var d=new Date();return d.getFullYear()+"-"+p2(d.getMonth()+1)+"-"+p2(d.getDate())+"T"+p2(d.getHours())+":"+p2(d.getMinutes())+":"+p2(d.getSeconds());}
function tdate(){var d=new Date();if(TOM)d=new Date(d.getTime()+86400000);return d;}
function ds(d){return d.getFullYear()+"-"+p2(d.getMonth()+1)+"-"+p2(d.getDate());}
function url(d){return "https://www.elprisetjustnu.se/api/v1/prices/"+d.getFullYear()+"/"+p2(d.getMonth()+1)+"-"+p2(d.getDate())+"_"+AREA+".json";}
function wd(d){var w=d.getDay();return w===0?7:w;}
function high(m,w,h){return GRID==="time_tariff"&&has(HM,m)&&has(HD,w)&&h>=H0&&h<H1;}
function gp(m,w,h){if(GRID==="flat")return GFLAT;if(GRID==="time_tariff")return high(m,w,h)?GHIGH:GLOW;return GFLAT;}
function tp(spot,m,w,h){return (SPOT_EX?iv(spot):spot)+iv(MARKUP_EX)+iv(VARCOST_EX)+iv(ETAX_EX)+gp(m,w,h);}
function set(k,v,cb){Shelly.call("KVS.Set",{key:k,value:String(v)},function(res,err){if(err)log("KVS err "+k);if(cb)cb(!err);});}
function status(s){set(KS,s,null);}
function blocks(body,d){var key='"SEK_per_kWh":',pos=0,q=0,cnt=0,sum=0,out=[],m=d.getMonth()+1,w=wd(d);
 while(1){var i=body.indexOf(key,pos);if(i<0)break;i+=key.length;var j=i;
  while(j<body.length){var c=body.charAt(j);if((c>="0"&&c<="9")||c==="."||c==="-")j++;else break;}
  var spot=Number(body.substring(i,j));
  if(!isNaN(spot)){sum+=tp(spot,m,w,Math.floor(q/4));cnt++;q++;if(cnt===8){out.push(r3(sum/8));sum=0;cnt=0;}}
  pos=j;
 }
 if(q!==96||out.length!==12){log("bad q="+q+" b="+out.length);return null;}return out;
}
function save(b,d){var s=b.join(",");set(K2H,s,function(){set(KD,ds(d),function(){set(KA,AREA,function(){set(KU,iso(),function(){set(KS,"ok",function(){log("ok "+ds(d)+" "+s);});});});});});}
function run(){var d=tdate(),u=url(d);log("GET "+u);status("fetching");Shelly.call("HTTP.GET",{url:u,timeout:15},function(res,err){if(err||!res||!res.body){log("http");status("http_error");return;}var b=blocks(res.body,d);if(!b){status("bad_count");return;}save(b,d);});}
run();
})();
