"""Verify the built example's manifest and payload identities."""
import hashlib,json,sys,zipfile
from pathlib import Path
path=Path(sys.argv[1] if len(sys.argv)>1 else 'artifacts/plugin.zip')
with zipfile.ZipFile(path) as archive:
 names=archive.namelist();manifest=json.loads(archive.read('plugin.json'))
 assert len(names)==len(set(names)) and set(names)=={'plugin.json','plugin.wasm','page.nxml'}
 assert manifest['target']['runtime']=='nexa-wasm-1' and manifest['declaredAbiCandidates']==[100]
 assert archive.read('plugin.wasm').startswith(b'\0asm\x01\0\0\0')
 assert len(manifest['payloads'])==2
 for payload in manifest['payloads']:
  data=archive.read(payload['path']);assert len(data)==payload['size'] and hashlib.sha256(data).hexdigest()==payload['sha256']
 assert '{{PLUGIN_ID}}' not in archive.read('page.nxml').decode()
print('PASS: template payload identities, Wasm header and manifest.')
