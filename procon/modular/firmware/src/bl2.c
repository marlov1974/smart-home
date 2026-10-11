/* P0080 resident boot, system routing, WAIT and autonomous repair. */
#include "platform.h"
#include "identity.h"
#include "cn105.h"
#include "modbus.h"
#include "ota.h"
#include "layout.h"
#define R(a) (*(volatile uint32_t *)(uintptr_t)(a))
static uint32_t last_us,time_ms,remainder,wait_at,activity;
static int valid,mode; /* 0 normal,1 WAIT,2 uploader */
void cn_service(void){
 if(!valid||mode==2)return;
 uint32_t us=micros(),d=us-last_us;last_us=us;time_ms+=d/1000;remainder+=d%1000;time_ms+=remainder/1000;remainder%=1000;
 cn_tick(time_ms);uint8_t b;int e;
 for(unsigned i=0;i<8;++i){if(!cn_uart_receive(&b,&e))break;cn_feed(b,time_ms,e);}
 if(cn_uart_ready()&&cn_tx_byte(&b)){cn_uart_write(b);cn_tx_sent();}
}
static unsigned crc16_local(const uint8_t *p,unsigned n){unsigned c=65535;while(n--){c^=*p++;for(unsigned j=0;j<8;++j)c=(c>>1)^((c&1)?0xa001:0);}return c;}
static unsigned reply_crc(uint8_t *p,unsigned n){unsigned c=crc16_local(p,n);p[n]=c;p[n+1]=c>>8;return n+2;}
/* System envelope FC16 raw address384,count4: magic B180, FF/FE, nonce, seconds.
 * STATUS FC04 raw384,count16 is always resident when addressed and not WAIT. */
static __attribute__((noinline)) unsigned normal(const uint8_t *r,unsigned n,uint8_t *out){
 unsigned id=modbus_address();if(!id||n<4||r[0]!=id||crc16_local(r,n))return 0;
 if(n==8&&r[1]==4&&r[2]==1&&r[3]==128&&r[4]==0&&r[5]==16){
  uint16_t w[16]={0};w[0]=0xb180;w[1]=2;w[2]=valid;w[3]=mode;w[4]=(uint16_t)(LAYOUT_ID>>16);w[5]=(uint16_t)LAYOUT_ID;
  uint32_t c=(valid||modules_valid())?crc32(flash_at(MANIFEST_ADDR),56):0;w[6]=c>>16;w[7]=c;
  for(unsigned i=0;i<3;++i){uint32_t u=platform_uid_word(i);w[8+2*i]=u>>16;w[9+2*i]=u;}
  w[14]=valid?maintenance_ready():1;w[15]=1;
  out[0]=id;out[1]=4;out[2]=32;for(unsigned i=0;i<16;++i){out[3+2*i]=w[i]>>8;out[4+2*i]=w[i];}return reply_crc(out,35);
 }
 if(n==17&&r[1]==16&&r[2]==1&&r[3]==128&&r[4]==0&&r[5]==4&&r[6]==8){
  unsigned cmd=(r[9]<<8)|r[10],secs=(r[13]<<8)|r[14];uint8_t err=0;
  if(r[7]!=0xb1||r[8]!=0x80||(cmd!=254&&cmd!=255)||!secs||secs>3600||(!r[11]&&!r[12]))err=3;
  else if(identity_read(77)!=1)err=4;
  else if(valid&&!maintenance_ready())err=6;
  if(err){out[0]=id;out[1]=0x90;out[2]=err;return reply_crc(out,3);}
  for(unsigned i=0;i<6;++i)out[i]=r[i];
  unsigned len=reply_crc(out,6);
  if(!uart_send(out,len))return 0;
  if(cmd==254){mode=1;wait_at=micros();activity=secs*1000000u;}
  else {mode=2;uart_baud(115200);ota_reset();activity=micros();}
  return 0;
 }
 if(valid)return modbus_reply(r,n,out,64);
 out[0]=id;out[1]=r[1]|128;out[2]=4;return reply_crc(out,3);
}
int main(void){
 platform_init();uint32_t uid[3];for(unsigned i=0;i<3;++i)uid[i]=platform_uid_word(i);
 uint8_t dip=platform_dip_read();int stable=1;
 for(unsigned i=0;i<2;++i){uint32_t t=micros();while(micros()-t<5000)watchdog_refresh();if(platform_dip_read()!=dip)stable=0;}
 identity_init_dip(uid,dip,stable);uart_init();valid=modules_valid();
 if(valid){modules_load();cn_init();cn_uart_init();}last_us=micros();
 uint8_t rx[256],out[64],b;unsigned used=0;int bad=0,e;uint32_t last=0;
 for(;;){
  watchdog_refresh();heartbeat(micros());cn_service();uint32_t t=micros();
  if(mode==1&&t-wait_at>=activity){mode=0;used=0;bad=0;}
  if(mode==2&&t-activity>120000000u){mode=0;valid=0;uart_baud(9600);used=0;bad=0;} /* explicit recovery, no automatic module restart */
  if(used&&t-last>=(mode==2?2000u:4000u)){
   unsigned n=0;
   if(!bad&&mode!=1){if(mode==2){n=ota_handle(rx,used,out,64);if(n)activity=t;}else n=normal(rx,used,out);}
   used=0;bad=0;if(n)uart_send(out,n);
   if(mode==2&&ota_exit_ready()){R(0xe000ed0c)=0x05fa0004;__asm volatile("dsb\nisb":::"memory");for(;;);}
  }
  if(uart_receive(&b,&e)){if(e || (used && mode!=2 && micros()-last>1563u))bad=1;if(used<256)rx[used++]=b;else bad=1;last=micros();}
 }
}
