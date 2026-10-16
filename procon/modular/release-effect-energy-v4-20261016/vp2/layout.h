#ifndef LAYOUT_H
#define LAYOUT_H
#define LAYOUT_ID 3833993797u
#define MANIFEST_ADDR 0x8015000u
#define UPDATE_BASE 0x800a000u
#define UPDATE_END 0x8015800u
#define ABI_VERSION 1u
#define SLOT_COUNT 7u
static const unsigned slot_addr[7]={0x800a000,0x800d000,0x800e000,0x8011000,0x8012000,0x8013000,0x8014000};
static const unsigned slot_size[7]={12288,4096,12288,4096,4096,4096,4096};
static const unsigned slot_ram[7]={0x20001000,0x20001800,0x20001900,0x20002900,0x20003100,0x20003500,0x20003600};
static const unsigned slot_ramsize[7]={2048,256,4096,2048,1024,256,256};
static const unsigned slot_exports[7]={8,1,15,6,10,1,1};
#endif
