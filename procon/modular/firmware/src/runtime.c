/* Freestanding compiler support: no heap or peripheral access. */
#include <stddef.h>
void *memset(void *destination,int value,size_t count) {
    volatile unsigned char *out=destination;
    for(size_t i=0;i<count;++i)out[i]=(unsigned char)value;
    return destination;
}
