# P0086: synthetic tests, no transport.
import contextlib
import io
import json
from pathlib import Path
import socket
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import energy
import reader
import settings
import uart1 as u
import verify_local

def a3fixture(code, value):
    f=bytearray.fromhex('fc62027a10')+bytearray(16)
    f[5]=0xa3;f[6:8]=code.to_bytes(2,'big');f[8]=1;f[9:11]=value.to_bytes(2,'little')
    f.append((0xfc-sum(f))&255)
    return f.hex()

class EnergyTests(unittest.TestCase):
    def test_bcd_exhaustive(self):
        for word in range(65536):
            digits=[(word>>n)&15 for n in (12,8,4,0)]
            if max(digits)>9:
                with self.assertRaises(ValueError): energy.bcd(word)
            else: self.assertEqual(energy.bcd(word), int(f'{word:04x}'))
    def test_pairs(self):
        for selector in energy.PAIRS:
            self.assertEqual(energy.pair(selector,0x1234,0x5600)['raw_units'],1234560)
            self.assertTrue(energy.pair(selector,0x9999,0x9900)['censored'])
            self.assertEqual(energy.pair(selector,0x1234,0x9900,0)['consistency'],'changed')
        with self.assertRaises(ValueError): energy.pair(522,1,1)
    def test_carry_reset(self):
        a=energy.pair(522,0x0001,0x9900); b=energy.pair(522,0x0002,0)
        self.assertEqual(energy.delta(a,b)['delta_raw_units'],10)
        self.assertIsNone(energy.delta(b,a)['delta_raw_units'])
        self.assertIsNone(energy.delta(a,energy.pair(522,0x9999,0x9900))['delta_raw_units'])
    def test_exclusions(self):
        for code in range(1000):
            if code in energy.CODES: self.assertEqual(energy.api600(code)[5],code)
            else:
                with self.assertRaises(ValueError): energy.api600(code)
    def test_a3_correlation(self):
        f=bytes.fromhex(a3fixture(522,0x1234))
        self.assertEqual(energy.a3(f,522),0x1234)
        for code in (520,523,532):
            with self.assertRaises(ValueError): energy.a3(f,code)
        for n in range(22):
            with self.assertRaises(ValueError): energy.a3(f[:n],522)
    def test_fold_loss(self):
        self.assertEqual(energy.fold(59)+energy.fold(59),0)
        self.assertEqual(energy.fold(118),1)
        self.assertEqual(energy.fold(118,2),118)
    def test_get07(self):
        f=bytearray.fromhex('fc62027a10')+bytearray(16); f[5]=7
        f[8:12]=bytes.fromhex('01230234');f[16:18]=bytes.fromhex('1234')
        f.append((0xfc-sum(f))&255)
        self.assertEqual(energy.get07(f)['consumed_raw'],291)
        self.assertEqual(energy.get07(f)['produced_raw'],564)
        for n in range(22):
            with self.assertRaises(ValueError): energy.get07(f[:n])
    def test_observations(self):
        row=dict(selector=522,correlation=1,format=1,high=1,low=0,repeat_low=0,
                 high_at='2026-10-11T00:00:00+00:00',low_at='2026-10-11T00:00:01+00:00',repeat_at='2026-10-11T00:00:02+00:00',raw_frames=[a3fixture(522,1),a3fixture(523,0),a3fixture(523,0)])
        self.assertFalse(energy.observations([row])[0]['atomic'])
        row['format']=2
        with self.assertRaises(ValueError): energy.observations([row])

class UARTTests(unittest.TestCase):
    def test_vectors(self):
        for op,expected in [('open','0000000000'),('close','0f000000f1'),('log','02f000000e')]:
            self.assertEqual(u.request(op).hex(),expected)
        self.assertEqual(u.memory(0x400,1).hex(),'01000400fb')
        for n in (1,2,4,8,16,32,64):
            self.assertEqual(sum(u.memory(0x400,n))&255,0)
    def test_profile(self):
        for name,sha in [(u.PROFILES[1],u.IMAGE_SHA),('21.00',u.IMAGE_SHA),(u.PROFILES[0],'bad')]:
            with self.assertRaises(ValueError): u.profile(name,sha)
    def test_address_bounds(self):
        for address in (0x400,0xfffe,0xffff,0x10000,0x80000,0x80400,0xffffe):
            self.assertEqual(u.effective_addresses(address,1),[address&65535])
        self.assertEqual(u.effective_addresses(0xffff,2),[65535,0])
        self.assertFalse(u.parser_accepts(0xfffff,1))
        for address,n in [(0,1),(0x3ff,1),(0x5000,1),(0x4fff,2),(0x80000,1),(0x400,3),(0x400,0)]:
            with self.assertRaises(ValueError): u.memory(address,n)
    def test_response(self):
        self.assertEqual(u.response(bytes.fromhex('0003fd'),'open'),b'')
        self.assertEqual(u.response(u.checksum(bytes([1,4,90])),'read',1),b'Z')
        for data in (b'',b'\x00\x03',b'\x00\x03\xfc',bytes(78),bytes.fromhex('0f03ee')):
            with self.assertRaises(ValueError): u.response(data,'open')
    def test_normal(self):
        self.assertEqual(u.normal52(255)['address'],0xfe3)
        self.assertEqual(u.normal52(256)['address'],0xae4)
        self.assertEqual(u.normal52(512)['kind'],'table_lookup')
        self.assertEqual(u.normal52(0x3fff)['address'],0x3fff)
        with self.assertRaises(ValueError): u.normal52(0x80000)
    def test_log(self):
        records=bytes([6])+bytes(range(11))+bytes([0x86])+bytes(range(11,21))+b'\x00'+bytes(48)
        f=u.checksum(bytes.fromhex('024df002')+records)
        result=u.logs(f)
        self.assertEqual(result['packets'][0]['observed_hex'],bytes(range(21)).hex())
        self.assertFalse(result['packets'][0]['checksum_captured'])
        self.assertIsNone(result['records'][0]['timestamp'])
        bad=bytearray(f[:-1]);bad[4]|=32
        self.assertEqual(u.logs(u.checksum(bad))['packets'],[])
        self.assertTrue(u.logs(f)['drains_buffer'])
        self.assertEqual(u.logs(u.checksum(bytes.fromhex('024df002')+bytes(72)))['packets'],[])
    def test_log_orphan_and_direction(self):
        f=u.checksum(bytes.fromhex('024df002')+bytes([0xc6])+bytes(11)+bytes([0x43])+bytes(11)+bytes(48))
        out=u.logs(f)
        self.assertTrue(out['records'][0]['orphan_continuation'])
        self.assertEqual(out['records'][1]['source'],'D')
        self.assertEqual(out['records'][1]['direction'],'TX')

class SessionTests(unittest.TestCase):
    def test_observed_read_close(self):
        s=settings.ReadSession()
        for e in ('open_intent','observed_read_gate_7','observed_internal_ack_9'): s.event(e)
        for selector,index in [(0x65,10),(0x79,7)]:
            b=bytearray(range(16));b[index]=5
            self.assertEqual(s.capture(selector,b),5)
            candidate=s.proposed_block(selector,4)
            self.assertEqual([i for i in range(16) if b[i]!=candidate[i]],[index])
        with self.assertRaises(settings.Blocked):s.apply()
        s.event('close_intent');s.event('observed_state0_and_prior_control')
        self.assertTrue(s.closure_verified)
    def test_bad_state_category_timeout(self):
        for kwargs in ({'category':5},{'elapsed':11},{'event':'bad_reply'}):
            s=settings.ReadSession(); s.event('open_intent')
            self.assertEqual(s.event(**{'event':'observed_read_gate_7',**kwargs}),'closure_required')
        with self.assertRaises(settings.Blocked): settings.ReadSession().event('observed_internal_ack_9')
        with self.assertRaises(settings.Blocked): settings.ReadSession().capture(0x65,bytes(16))

class ReaderTests(unittest.TestCase):
    def fixture(self):return [dict(elapsed=.1,response_hex='0003fd'),dict(elapsed=.1,response_hex='')]
    def test_replay(self):
        self.assertEqual(reader.replay(reader.plan('session'),self.fixture())['status'],'PASS')
        self.assertFalse(reader.replay(reader.plan('session'),self.fixture())['closure_verified'])
    def test_timeout_cancel_raw_retained(self):
        for bad in [dict(elapsed=3,response_hex='dead'),dict(cancelled=True),dict(elapsed=.1,response_hex='00')]:
            out=reader.replay(reader.plan('session'),[bad])
            self.assertEqual(out['status'],'FAIL');self.assertEqual(out['evidence'][0]['raw_fixture'],bad)
            self.assertEqual(len(out['evidence']),1)
        out=reader.replay(reader.plan('session'),self.fixture(),total_timeout=.15)
        self.assertEqual(out['status'],'FAIL')
        with self.assertRaises(ValueError):reader.replay([],[],total_timeout=float('nan'))
    def test_no_transport_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as d, patch.object(socket,'socket',side_effect=AssertionError('network opened')):
            dest=Path(d)/'capture.json'
            args=['--profile',u.PROFILES[0],'--output',str(dest)]
            self.assertEqual(reader.main(args),0)
            before=dest.read_bytes()
            with contextlib.redirect_stderr(io.StringIO()),self.assertRaises(SystemExit): reader.main(args)
            self.assertEqual(dest.read_bytes(),before)
            with contextlib.redirect_stderr(io.StringIO()),self.assertRaises(SystemExit):reader.main(['--profile',u.PROFILES[0],'--execute'])
        for module in (reader,u,energy,settings):
            source=Path(module.__file__).read_text()
            self.assertNotIn('import serial',source);self.assertNotIn('import socket',source)

class EvidenceTests(unittest.TestCase):
    def test_changed_inputs_fail(self):
        with self.assertRaises(ValueError):verify_local.derive(b'wrong', 'header')
        rows='header\n'+'\n'.join(f'ram:{a}\t{t}\troot' for a,t in verify_local.OPERANDS.items())
        fake=bytearray(0x1e9a0);fake[0x1e99c:]=bytes.fromhex('726d4813')
        # Hash mocking isolates operand rejection only; actual hash verified by local verifier.
        with patch.object(verify_local,'sha',return_value=u.IMAGE_SHA):
            self.assertEqual(verify_local.derive(fake,rows)['load_opcode'],'726d4813')
            with self.assertRaises(ValueError):verify_local.derive(fake,rows.replace('MOV.b [A0]','LDE.b [A0]'))
            with self.assertRaises(ValueError):verify_local.derive(fake,'header')
            fake[0x1e99c]=0
            with self.assertRaises(ValueError):verify_local.derive(fake,rows)

if __name__=='__main__':unittest.main()
