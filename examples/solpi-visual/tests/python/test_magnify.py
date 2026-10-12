import unittest,tempfile,pathlib,subprocess,sys,json,hashlib,os
from unittest.mock import patch
from PIL import Image
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / 'src/scene'))
import magnify
class Tests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.p=pathlib.Path(self.tmp.name);self.im=self.p/'source.png';im=Image.new('RGB',(4,4));im.putdata([(x*40,y*40,0) for y in range(4) for x in range(4)]);im.save(self.im);self.before=self.im.read_bytes()
 def tearDown(self):self.tmp.cleanup()
 def test_exact_pixels(self):
  import io
  raw,m=magnify.extract(self.im,[1,1,3,3],2,'nearest');im=Image.open(io.BytesIO(raw));self.assertEqual(im.size,(4,4));self.assertEqual(im.getpixel((0,0)),(40,40,0));self.assertEqual(im.getpixel((3,3)),(80,80,0));self.assertTrue(m['source_unchanged']);self.assertEqual(self.before,self.im.read_bytes())
 def test_max_side(self):
  with self.assertRaises(ValueError):magnify.extract(self.im,[0,0,4,4],2,'nearest',7)
 def test_bounds(self):
  for box in [[-1,0,2,2],[0,0,5,3],[2,2,2,3]]:
   with self.assertRaises(ValueError):magnify.extract(self.im,box,2,'bicubic')
 def test_rejects_oversized_or_nonregular_sources(self):
  large=self.p/'large.png'
  with large.open('wb') as f:f.truncate(magnify.MAX_SOURCE_BYTES+1)
  with self.assertRaisesRegex(ValueError,'64MiB'):magnify.extract(large,[0,0,1,1],1,'nearest')
  if hasattr(os,'mkfifo'):
   fifo=self.p/'fifo';os.mkfifo(fifo)
   with self.assertRaisesRegex(ValueError,'regular file'):magnify.extract(fifo,[0,0,1,1],1,'nearest')
 def test_rejects_unsupported_format_and_large_encoded_output(self):
  from PIL import UnidentifiedImageError
  bmp=self.p/'source.bmp';Image.open(self.im).save(bmp)
  with self.assertRaises(UnidentifiedImageError):magnify.extract(bmp,[0,0,2,2],1,'nearest')
  with patch.object(magnify,'MAX_OUTPUT_BYTES',1):
   with self.assertRaisesRegex(ValueError,'reduce bbox or scale'):magnify.extract(self.im,[0,0,2,2],1,'nearest')
 def test_pair_cache_and_integrity(self):
  cmd=[sys.executable,str(pathlib.Path(magnify.__file__)),'--image',str(self.im),'--bbox','0','0','2','2','--reference',str(self.im),'--reference-bbox','2','2','4','4','--interpolation','nearest','--output-root',str(self.p/'out')]
  a=json.loads(subprocess.check_output(cmd));b=json.loads(subprocess.check_output(cmd));self.assertFalse(a['cached']);self.assertTrue(b['cached']);self.assertEqual(a['artifact_id'],b['artifact_id']);r=json.loads(pathlib.Path(a['receipt']).read_text());self.assertEqual(len(r['images']),2)
  with Image.open(r['images']['crop']['output_path']) as crop,Image.open(r['images']['reference_crop']['output_path']) as ref:
   self.assertEqual(crop.getpixel((0,0)),(0,0,0));self.assertEqual(ref.getpixel((0,0)),(80,80,0))
  for m in r['images'].values():self.assertEqual(hashlib.sha256(pathlib.Path(m['output_path']).read_bytes()).hexdigest(),m['output_sha256'])
  pathlib.Path(r['images']['crop']['output_path']).write_bytes(b'changed');self.assertNotEqual(subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE).returncode,0)
 def test_concurrent_identical_requests(self):
  cmd=[sys.executable,str(pathlib.Path(magnify.__file__)),'--image',str(self.im),'--bbox','0','0','2','2','--output-root',str(self.p/'parallel')]
  jobs=[subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE) for _ in range(4)]
  receipts=[]
  for job in jobs:
   out,err=job.communicate(timeout=10);self.assertEqual(job.returncode,0,err.decode());receipts.append(json.loads(out))
  self.assertEqual(len({r['artifact_id'] for r in receipts}),1)
if __name__=='__main__':unittest.main()
