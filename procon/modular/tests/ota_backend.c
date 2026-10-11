/* P0080 test-only flash backend. Whole operations may be cut between doublewords. */
#include <stdint.h>
#include <string.h>
#include "layout.h"
static uint8_t memory[131072];
static int budget=-1,writes,erases;
void reset_image(const uint8_t *p){memset(memory,255,sizeof(memory));memcpy(memory+32768,p,98304);budget=-1;writes=erases=0;}
const uint8_t *flash_at(uint32_t a){return memory+a-0x08000000u;}
uint32_t platform_uid_word(unsigned i){return i+1;}
void watchdog_refresh(void){}
void set_cut(int n){budget=n;}
int count_write(void){return writes;}
int count_erase(void){return erases;}
int flash_erase(unsigned a){if(a<UPDATE_BASE||a>=UPDATE_END||(a&2047))return 0;if(budget==0)return 0;if(budget>0)--budget;memset(memory+a-0x08000000u,255,2048);++erases;return 1;}
int flash_write(uint32_t a,const uint8_t *p,unsigned n){
 if(a<UPDATE_BASE||a+n>UPDATE_END||(a&7)||(n&7)||!n||n>240)return 0;
 for(unsigned i=0;i<n;i+=8){if(budget==0)return 0;if(budget>0)--budget;for(unsigned j=0;j<8;++j)if(memory[a-0x08000000u+i+j]!=255)return 0;memcpy(memory+a-0x08000000u+i,p+i,8);++writes;}return 1;
}
