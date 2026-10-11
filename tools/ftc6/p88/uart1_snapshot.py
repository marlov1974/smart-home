"""Pure decoder for newly traced diagnostic12 snapshots; never emits requests."""
LENGTHS={0:100,1:66,2:62,16:13}
FIELDS={0:{'effective_flow_target':(23,2),'dhw_target':(25,2),'flow_temperature':(62,2),'return_temperature':(64,2)},1:{'primary_flow_raw':(61,2)},2:{'native_request_raw':(26,1)}}
def decode(data):
    data=bytes(data)
    if len(data)<5 or data[0]!=0x12 or data[2] not in LENGTHS or data[3]!=2:
        raise ValueError('Not a qualified UART1 diagnostic12 snapshot')
    if data[1]!=len(data) or len(data)!=LENGTHS[data[2]] or sum(data)&255:
        raise ValueError('Wrong length/checksum')
    values={name:int.from_bytes(data[pos:pos+n],'little') for name,(pos,n) in FIELDS.get(data[2],{}).items()}
    return {'profile':'FTC20.01 static','subcommand':data[2],'raw_fields':values,'raw_hex':data.hex(),'physical_validation':False,'atomic':False}
