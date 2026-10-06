/* P0071. Signed little-endian interpretation is reference-backed, provisional. */
#include "service.h"
#define AGE_MAX 65535000u
#define RETRY_MS 1000u
#define MAX_ATTEMPTS 10u
#define TTL_MS 60000u
enum { IDLE, READY, WAIT_REPLY, WAIT_RETRY, DONE, LINK_DOWN };
typedef struct {
    uint8_t payload[16], valid, ever;
    uint16_t raw, status, completions;
    uint32_t age;
} sample;
static sample samples[2];
static uint8_t state, index, attempts, wire_payload[16], had_request;
static uint16_t last_status, accepted, failures, exhausted, seen, gap_ms, cycles;
static uint32_t request_at, previous_request;
static uint16_t pair(const uint8_t *p) { return (uint16_t)((uint16_t)p[0] | ((uint16_t)p[1]<<8)); }
void svc_init(void) {
    for(unsigned i=0;i<2;++i) {
        for(unsigned b=0;b<16;++b)samples[i].payload[b]=0;
        samples[i].valid=samples[i].ever=0;
        samples[i].raw=samples[i].completions=0;samples[i].age=0;
        samples[i].status=65535;
    }
    for(unsigned i=0;i<16;++i)wire_payload[i]=0;
    state=IDLE; index=attempts=had_request=0;
    last_status=65535;accepted=failures=exhausted=seen=gap_ms=cycles=0;
    request_at=previous_request=0;
}
void svc_start_cycle(void) {state=READY;index=attempts=0;}
void svc_link(int up, uint32_t t) {
    (void)t;
    if(up) svc_start_cycle();
    else {
        state=LINK_DOWN;attempts=0;
        samples[0].valid=samples[1].valid=0;
    }
}
void svc_tick(uint32_t dt, uint32_t t) {
    for(unsigned i=0;i<2;++i)if(samples[i].ever) {
        sample *s=&samples[i];
        s->age=dt>=AGE_MAX-s->age?AGE_MAX:s->age+dt;
        if(s->age>=TTL_MS)s->valid=0;
    }
    (void)t; /* DONE waits for the next normal query, no timed restart. */
}
int svc_due(uint32_t t, uint8_t *code) {
    if(state==READY || (state==WAIT_RETRY && t-request_at>=RETRY_MS)) {
        *code=(uint8_t)(27u+index);return 1;
    }
    return 0;
}
void svc_sent(uint32_t t) {
    uint32_t gap=t-previous_request;
    gap_ms=had_request?(gap>65535u?65535:(uint16_t)gap):0;
    had_request=1;previous_request=request_at=t;
    ++attempts;state=WAIT_REPLY;
}
static void advance(uint32_t t) {
    (void)t;
    attempts=0;
    if(index==0) {index=1;state=READY;}
    else {state=DONE;++cycles;}
}
static void retry(uint32_t t) {
    if(attempts>=MAX_ATTEMPTS) {
        ++exhausted;samples[index].valid=0;advance(t);
    } else state=WAIT_RETRY;
}
int svc_reply(const uint8_t p[16], uint32_t t, int owned) {
    ++seen;
    for(unsigned i=0;i<16;++i)wire_payload[i]=p[i];
    last_status=p[3];
    if(!owned || state!=WAIT_REPLY || p[1]!=0 || p[2]!=27u+index) {++failures;return 0;}
    ++accepted;sample *s=&samples[index];s->status=p[3];
    if(p[3]==1 || p[3]==2) {
        for(unsigned i=0;i<16;++i)s->payload[i]=p[i];
        s->raw=pair(p+4);s->age=0;s->valid=s->ever=1;++s->completions;
        advance(t);
    } else if(p[3]==0)retry(t);
    else {++failures;s->valid=0;advance(t);}
    return 1;
}
void svc_timeout(uint32_t t) {++failures;if(state==WAIT_REPLY)retry(t);}
void svc_bad_frame(void) {++failures;}
uint16_t svc_read(unsigned a) {
    if(a>=16 && a<32) {
        sample *s=&samples[(a-16)/8];
        switch((a-16)%8) {
        case 0:return s->ever?s->raw:65535; /* Raw retained after stale/failure. */
        case 1:return s->valid?s->raw:65535; /* Reinterpret as int16, scale1 candidate. */
        case 2:return s->valid;
        case 3:return s->ever?(uint16_t)(s->age/1000u):65535;
        case 4:return s->status;
        case 5:return s->completions;
        case 6:return s->ever;
        default:return 0;
        }
    }
    if(a>=44 && a<52)return pair(wire_payload+2*(a-44));
    if(a>=52 && a<60)return pair(samples[0].payload+2*(a-52));
    if(a>=60 && a<68)return pair(samples[1].payload+2*(a-60));
    switch(a) {
    case 32:return state;
    case 33:return (state==READY || state==WAIT_REPLY || state==WAIT_RETRY)?(uint16_t)(27+index):0;
    case 34:return last_status;
    case 35:return attempts?attempts-1u:0;
    case 36:return accepted;
    case 37:return failures;
    case 38:return exhausted;
    case 40:return seen;
    case 41:return gap_ms;
    case 42:return cycles;
    case 43:return 1; /* Reference parser only; no hardware correlation claim. */
    default:return 0;
    }
}
