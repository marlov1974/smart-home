/* P0080 real dispatcher + telemetry, no device access. */
#include "modbus.h"
#include "cn105.h"
#include "telemetry.h"
#include "identity.h"
#include <assert.h>
#include <string.h>
#include <stdio.h>
static unsigned rd(unsigned a,unsigned n,uint16_t *w,unsigned cap,unsigned sid,int corrupt){
 uint8_t b[8]={sid,4,a>>8,a,n>>8,n,0,0},out[256];uint16_t c=crc16(b,6);b[6]=c;b[7]=c>>8;if(corrupt)b[7]^=1;
 unsigned len=modbus_reply(b,8,out,cap);
 if(len>5){assert(out[1]==4&&crc16(out,len)==0);for(unsigned i=0;i<n;++i)w[i]=(out[3+2*i]<<8)|out[4+2*i];}return len;
}
static void temperatures(unsigned f,unsigned r){uint8_t p[16]={0x0c};p[1]=f>>8;p[2]=f;p[4]=r>>8;p[5]=r;tele_accept(p);}
int main(void){
 uint32_t uid[3]={1,2,3};identity_init_dip(uid,0x61,1);cn_init();uint16_t h[16],a[16],b[16];
 assert(rd(402,2,h,256,1,0)==9&&h[0]==0&&h[1]==0);
 temperatures(3200,3050);uint8_t p[16]={0x14};p[12]=13;tele_accept(p);tele_tick(1234);
 assert(rd(400,8,h,256,1,0)==21&&h[0]==0x5380&&h[3]==1&&h[5]==20);
 assert(rd(426,6,a,256,1,0)==17&&a[1]==3200&&a[2]==1&&a[4]==1234);
 assert(rd(450,6,b,256,1,0)==17&&b[1]==1358&&b[2]==1);
 tele_tick(40000);tele_invalidate();temperatures(3400,3600);
 assert(rd(426,6,b,256,1,0)==17&&memcmp(a,b,12)==0);
 assert(rd(400,8,b,20,1,0)==0);assert(rd(400,8,b,256,0,0)==0);assert(rd(400,8,b,256,1,1)==0);
 assert(rd(400,17,b,256,1,0)==5);assert(rd(399,2,b,256,1,0)==5);assert(rd(527,2,b,256,1,0)==5);
 rd(402,2,b,256,1,0);assert(b[1]==1);
 rd(400,8,h,256,1,0);assert(h[3]==2&&h[4]==0);
 rd(450,6,b,256,1,0);assert(b[0]==0x8000&&b[1]==0&&b[2]!=1);
 tele_accept(p);rd(400,8,h,256,1,0);rd(450,6,b,256,1,0);assert(b[0]==0xffff&&b[1]==(uint16_t)-1811&&b[2]==1);
 rd(468,6,b,256,1,0);assert(b[0]==0x8000&&b[2]==0);
 tele_invalidate();rd(400,8,h,256,1,0);assert(h[4]==1);
 tele_init();rd(402,2,h,256,1,0);assert(h[0]==0&&h[1]==0);
 puts("PASS snapshot: freeze, stale/skew/signed/unavailable, refresh, reset, bounds, CRC, broadcast, short buffer");
}
