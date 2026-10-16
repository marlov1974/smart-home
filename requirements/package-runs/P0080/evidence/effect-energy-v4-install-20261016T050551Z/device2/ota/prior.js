let u=UART.get(0),rx='',waiting=false,tx='',stray=0;
if(!u)throw new Error('UART_UNAVAILABLE');
u.recv(function(d){if(waiting){rx+=d;if(rx.length>512)rx=rx.slice(0,513);}else{stray+=d.length;}});
function baud(b){if(b!==9600&&b!==115200)throw new Error('BAUD');u.configure({baud:b,format:'8N1'});return true;}
function stage(b){if(waiting)throw new Error('BUSY');tx=atob(b);if(tx.length>252)throw new Error('FRAME');return tx.length;}
function send(){if(waiting||stray)throw new Error('BUSY');rx='';waiting=true;return u.send(tx);}
function result(){waiting=false;return btoa(rx);}
Timer.set(3600000,false,function(){u.configure({baud:115200,format:'8N1'});Shelly.call('Script.Stop',{id:8});});
