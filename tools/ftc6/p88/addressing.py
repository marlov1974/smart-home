"""Manual-qualified address-register-relative bit address; no emulator patch."""
def bit_address(base,index):
    if not 0<=base<=0xffff or not 0<=index<=0xffff:raise ValueError('uint16 operands required')
    return ((base+(index>>3))&0xffff,index&7)
