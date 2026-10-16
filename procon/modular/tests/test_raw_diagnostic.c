/* P0081 real arbiter + addressed Modbus diagnostics regression. */
#include "cn105.h"
#include "modbus.h"
#include "identity.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static unsigned t, diag_tx, normal_tx, badmode, pending;
static uint8_t packet[22];
static unsigned response_delay, queued_at, queued_length, trace_on, trace_count;
static uint8_t queued_packet[22];
static struct {unsigned at, owner, query, code;} trace[128];
static void respond(const uint8_t *tx,unsigned n){
 uint8_t r[22]={252,0x62,2,0x7a,16};unsigned len=22,sum=0;
 if(n==8){r[1]=0x7a;r[4]=1;len=7;}
 else {assert(tx[1]==0x42);r[5]=tx[5];r[6]=tx[6];r[7]=tx[7];r[8]=1;
  if(cn_read(39)==5){diag_tx++;memcpy(packet,tx,22);if(badmode==1)return;
   if(badmode==2)r[5]^=1;
   if(tx[5]==0xa3 && pending){pending--;r[8]=0;}
  }else {assert(cn_read(606)!=2);normal_tx++;}
 }
 for(unsigned i=0;i<len-1;i++)sum+=r[i];r[len-1]=(uint8_t)(252-sum);
 if(badmode==3 && cn_read(39)==5)r[len-1]^=1;
 for(unsigned i=0;i<len;i++)cn_feed(r[i],t+1,0);
}
static void step(void){
 uint8_t tx[22];unsigned n=0;cn_tick(++t);
 if(queued_length && t>=queued_at){respond(queued_packet,queued_length);queued_length=0;}
 while(cn_tx_byte(tx+n)){cn_tx_sent();n++;assert(n<=22);}
 if(n){
  if(trace_on){assert(trace_count<128);trace[trace_count].at=t;trace[trace_count].owner=cn_read(39);trace[trace_count].query=tx[5];trace[trace_count++].code=tx[7];}
  if(response_delay){assert(!queued_length);memcpy(queued_packet,tx,n);queued_length=n;queued_at=t+response_delay;}
  else respond(tx,n);
 }
}
static void warm(void){const uint32_t uid[]={1,2,3};identity_init_dip(uid,0x61,1);cn_init();t=diag_tx=normal_tx=badmode=pending=0;response_delay=queued_length=trace_on=trace_count=0;for(unsigned i=0;i<4000;i++)step();}
static unsigned submit(unsigned addr,uint16_t id,uint16_t kind,uint16_t code){
 uint16_t w[]={0x81d1,1,0xfd,id,kind,code,0,0};uint8_t b[25]={1,16,addr>>8,addr,0,8,16},r[32];
 for(unsigned i=0;i<8;i++){b[7+i*2]=w[i]>>8;b[8+i*2]=w[i];}
 uint16_t c=crc16(b,23);b[23]=c;b[24]=c>>8;
 unsigned n=modbus_reply(b,25,r,sizeof r);assert(n==5||n==8);return n==8?0:r[2];
}
static void done(void){unsigned deadline=t+31000;while(cn_read(606)<3 && t<deadline)step();assert(cn_read(606)>=3);}
static void dense_diagnostics(void){
 static const unsigned fast[]={4,0x0c,0x14,0x0b,9,0x15,0x26,0x28};
 static const unsigned service[]={27,28,18,19,16,17};
 warm();response_delay=220;pending=5;
 assert(submit(600,1,2,17)==0);done();assert(cn_read(606)==3 && cn_read(612)==6);
 for(unsigned id=2;id<=3;id++){
  trace_count=0;trace_on=1;
  step(); /* respond() timestamps its final byte one tick ahead. */
  assert(submit(600,id,2,17)==6); /* The existing quarantine is retained. */
  for(unsigned i=0;i<1001;i++)step();
  pending=5;assert(submit(600,id,2,17)==0);done();
  assert(cn_read(606)==3 && cn_read(612)==6 && trace_count==14);
  for(unsigned i=0;i<8;i++)assert(trace[i].owner==2 && trace[i].query==fast[i]);
  for(unsigned i=8;i<14;i++){
   assert(trace[i].owner==5 && trace[i].query==0xa3 && trace[i].code==17);
   if(i>8)assert(trace[i].at-trace[i-1].at==1000);
  }
 }
 /* No profile remains enabled: six ordinary service jobs resume when the
    host stops submitting, each still preceded by the full FAST round. */
 trace_count=0;unsigned jobs=0,deadline=t+20000;
 while(jobs<6 && t<deadline){
  unsigned before=trace_count;step();
  if(trace_count!=before && trace[before].owner==3)jobs++;
 }
 assert(jobs==6 && trace_count==54);
 unsigned first=0;while(first<6 && service[first]!=trace[8].code)first++;
 assert(first<6);
 for(unsigned j=0;j<6;j++){
  for(unsigned i=0;i<8;i++)assert(trace[j*9+i].owner==2 && trace[j*9+i].query==fast[i]);
  assert(trace[j*9+8].owner==3 && trace[j*9+8].query==0xa3 && trace[j*9+8].code==service[(first+j)%6]);
 }
 /* Pending results and missing replies both retain the entire diagnostic
    operation; the new admission boundary cannot insert unrelated traffic. */
 for(unsigned missing=0;missing<2;missing++){
  warm();response_delay=220;pending=20;badmode=missing;trace_on=1;
  assert(submit(600,1,2,17)==0);done();assert(cn_read(606)==4 && cn_read(612)==10);
  unsigned first_diag=0;while(first_diag<trace_count && trace[first_diag].owner!=5)first_diag++;
  assert(trace_count-first_diag==10);
  for(unsigned i=first_diag;i<trace_count;i++){
   assert(trace[i].owner==5 && trace[i].query==0xa3 && trace[i].code==17);
   if(i>first_diag)assert(trace[i].at-trace[i-1].at==1000);
  }
 }
 puts("PASS dense diagnostic boundary: six-attempt A3/17 jobs, full FAST refresh, no background insertion, quarantine/retry/timeout preserved, ordinary queue resumes");
}
int main(void){
 dense_diagnostics();
 warm();assert(submit(300,1,1,7)==3);assert(submit(600,1,1,7)==0);assert(cn_read(606)==1);
 assert(submit(600,1,1,7)==0);assert(submit(600,1,1,8)==3);assert(submit(600,2,1,8)==6);
 done();assert(cn_read(606)==3 && cn_read(609)==1 && diag_tx==1 && packet[5]==7);
 for(unsigned i=6;i<21;i++)assert(packet[i]==0);
 uint16_t gen=cn_read(610);for(unsigned i=0;i<2000;i++)step();assert(cn_read(610)==gen && cn_read(603)==1);
 assert(submit(600,1,1,7)==0 && diag_tx==1);assert(submit(600,2,2,200)==0);assert(cn_read(606)==5 && diag_tx==1);
 warm();pending=2;assert(submit(600,1,2,540)==0);done();assert(cn_read(606)==3 && diag_tx==3 && packet[6]==2 && packet[7]==28);
 assert(cn_read(612)==3);assert(normal_tx>0);
 for(unsigned m=1;m<=3;m++){warm();badmode=m;assert(submit(600,1,1,0xa1)==0);done();assert(cn_read(606)==(m==1?4:6));assert(!cn_read(609));}
 warm();pending=20;assert(submit(600,1,2,27)==0);done();assert(cn_read(606)==4 && diag_tx==10 && !cn_read(609));
 warm();assert(submit(600,1,1,0x100)==3);
 /* A control request cannot steal diagnostic ownership. */
 warm();assert(submit(600,1,2,27)==0);uint16_t control[]={0xc072,1,2,3800,0,30,1,2};assert(cn_command(control)==6);
 /* Explicit30s queue expiration even without a background completion. */
 cn_tick(t+30001);assert(cn_read(606)==4 && cn_read(608)==5);
 /* No reply is valid zero; repeat known request preserves terminal result. */
 assert(submit(600,1,2,27)==0 && !cn_read(609));
 for(unsigned c=0;c<256;c++){warm();assert(submit(600,1,1,c)==0);done();assert(cn_read(606)==3 && packet[5]==c);}
 puts("PASS P0081 real arbiter/Modbus:256 direct codes, A3>255 exclusive retry, hazards, sticky/idempotency/conflict, CRC/wrong/timeout/pending");
}
