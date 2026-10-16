/* P0080 supervised command adapter. Gain import is RAM-only and uses the same
 * addressed, CRC-protected atomic FC16 boundary as heating control. */
#include "cn105.h"
#include "effect_model.h"
#include "identity.h"
#include <stdint.h>

#ifndef UNIT_TEST
#define GAIN_SEED_MAGIC 0xc077u
static uint8_t gain_seed(const uint16_t w[8]){
    if(w[1]<700 || w[1]>2000)return 3;
    /* All96 factory UID bits are carried without truncation or hashing. */
    for(unsigned i=0;i<6;++i)if(w[2+i]!=identity_read(78+i))return 3;
    /* The first accepted seed owns this boot. Its exact retry is successful
       even if a control session has since made the maintenance gate busy. */
    if(effect_model_seeded())return w[1]==effect_model_seeded_gain()?0:3;
    /* Stronger than controller IDLE alone: no CN105 owner/diagnostic is active,
       native curve guards are fresh, and no supervised session owns settings. */
    if(!maintenance_ready())return 6;
    if(!effect_model_seed_gain(w[1]))return 3;
    return 0;
}
uint8_t debug_command(const uint16_t words[8]) {
    return words[0]==GAIN_SEED_MAGIC?gain_seed(words):cn_command(words);
}
#else
uint8_t debug_command(const uint16_t words[8]) { return cn_command(words); }
#endif
