"""P0076 offline two-unit identity mapping; no network or hardware fixtures."""
import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from commission_units import decode_identity, decode_dip, normalize_uid, validate_manifest, validate_commissioning

UID1='0123456789abcdef13572468'
UID2='2233445566778899aabbccdd'


def words(slave,uid,source=3):
    return [1,slave,slave,source,1,1]+[int(uid[offset:offset+4],16) for offset in range(0,24,4)]


def manifest():
    return {'schema':1,'units':[{'name':'VP1','slave_id':1,'uid96':UID1},{'name':'VP2','slave_id':2,'uid96':UID2}]}


def observations():
    return [{'name':'VP1','slave_id':1,'identity_words_72_83':words(1,UID1),'dip_words_84_86':[0x61,1,0]},
            {'name':'VP2','slave_id':2,'identity_words_72_83':words(2,UID2),'dip_words_84_86':[0x62,1,0]}]


class CommissionTests(unittest.TestCase):
    def test_exact_word_order_and_sources(self):
        for source in (1,2,3):
            value=decode_identity(words(1,UID1,source),requested_slave=1)
            self.assertEqual(value['uid96'],UID1)
            self.assertEqual(value['uid_words'],[0x01234567,0x89abcdef,0x13572468])
        self.assertEqual(normalize_uid(UID1.upper()),UID1)

    def test_mapping_match_is_not_physical_or_control_authorization(self):
        result=validate_commissioning(manifest(),observations())
        self.assertEqual(result['status'],'OFFLINE_IDENTITY_MATCH')
        self.assertFalse(result['control_authorized'])
        self.assertFalse(result['physical_isolation_verified'])
        self.assertFalse(result['shared_bus_verified'])
        self.assertEqual(result['units'][1]['slave_id'],2)

    def test_duplicate_expected_sid_and_uid_rejected(self):
        for field,value in (('slave_id',1),('uid96',UID1),('name','VP1')):
            data=manifest();data['units'][1][field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):validate_manifest(data)

    def test_invalid_expected_uid_and_addresses(self):
        for value in ('0'*24,'f'*24,'1'*23,'z'*24,None,True,123):
            data=manifest();data['units'][1]['uid96']=value
            with self.subTest(value=value),self.assertRaises(ValueError):validate_manifest(data)
        for value in (0,248,True,'2'):
            data=manifest();data['units'][1]['slave_id']=value
            with self.subTest(value=value),self.assertRaises(ValueError):validate_manifest(data)
        for data in ({'schema':True,'units':manifest()['units']},{'schema':1,'units':[]},[],None):
            with self.assertRaises(ValueError):validate_manifest(data)

    def test_observed_wrong_sid_or_uid_refused(self):
        actual=observations();actual[1]['identity_words_72_83']=words(2,UID1)
        with self.assertRaises(ValueError):validate_commissioning(manifest(),actual)
        actual=observations();actual[1]['identity_words_72_83']=words(1,UID2)
        with self.assertRaises(ValueError):validate_commissioning(manifest(),actual)
        actual=observations();actual[1]['identity_words_72_83']=words(2,'abcdef012345678913572468')
        with self.assertRaises(ValueError):validate_commissioning(manifest(),actual)
        actual=observations();actual[0]['name'],actual[1]['name']='VP2','VP1'
        with self.assertRaises(ValueError):validate_commissioning(manifest(),actual)

    def test_duplicate_observed_address_even_with_different_uid_refused(self):
        actual=observations();actual[1]['slave_id']=1;actual[1]['identity_words_72_83']=words(1,UID2)
        with self.assertRaises(ValueError):validate_commissioning(manifest(),actual)
        actual=observations();actual[1]['name']='VP1'
        with self.assertRaises(ValueError):validate_commissioning(manifest(),actual)

    def test_identity_invalid_status_source_and_bounds_refused(self):
        for index,value in ((0,2),(1,0),(2,2),(3,0),(3,4),(4,0),(4,2),(5,0),(5,2),(6,True),(6,65536)):
            block=words(1,UID1);block[index]=value
            with self.subTest(index=index,value=value),self.assertRaises(ValueError):decode_identity(block,1)
        for block in (words(1,'0'*24),words(1,'f'*24),words(2,UID2,source=1),words(1,UID1)[:-1],None):
            with self.assertRaises(ValueError):decode_identity(block)
        with self.assertRaises(ValueError):decode_identity(words(2,UID2),requested_slave=1)

    def test_dip_bounds_stability_and_raw_address(self):
        identity=decode_identity(words(2,UID2),2)
        self.assertEqual(decode_dip([0x62,1,0],identity)['raw'],0x62)
        self.assertEqual(decode_dip([0xe2,1,0],identity)['raw'],0xe2)
        for block in ([0x62,0,1],[0x62,1,4],[0x02,1,0],[0x60,1,0],[0x7f,1,0],[0x61,1,0],[0x162,1,0],[0x62,True,0],None):
            with self.subTest(block=block),self.assertRaises(ValueError):decode_dip(block,identity)
        with self.assertRaises(ValueError):decode_identity(words(31,UID2),31)
        missing=observations();del missing[1]['dip_words_84_86']
        with self.assertRaises(ValueError):validate_commissioning(manifest(),missing)

    def test_invalid_observation_shapes(self):
        for actual in (None,[],observations()[:1],[None,None],[{'name':[]},{}]):
            with self.assertRaises(ValueError):validate_commissioning(manifest(),actual)


if __name__=='__main__':unittest.main()
