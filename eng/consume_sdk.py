#!/usr/bin/env python3
"""Fetch and verify an immutable SDK bundle into an owned, rebuildable cache."""
import argparse,hashlib,io,json,os,re,shutil,tempfile,urllib.request,zipfile
from pathlib import Path,PurePosixPath

def digest(data):return hashlib.sha256(data).hexdigest()
def checked_files(payload,lock):
 if len(payload)!=lock['size'] or digest(payload)!=lock['sha256']:raise ValueError('SDK bundle integrity mismatch')
 with zipfile.ZipFile(io.BytesIO(payload)) as archive:
  entries=archive.infolist();names=[entry.filename for entry in entries]
  if len(names)>4096 or len(names)!=len(set(names)) or sum(e.file_size for e in entries)>64*1024*1024:raise ValueError('SDK archive budget exceeded')
  for entry in entries:
   path=PurePosixPath(entry.filename)
   if path.is_absolute() or any(p in {'..','.'} for p in path.parts) or '\\' in entry.filename or ':' in entry.filename or entry.is_dir() or (entry.external_attr>>16)&0o170000==0o120000:raise ValueError('Invalid SDK archive path')
  files={name:archive.read(name) for name in names}
 manifest=json.loads(files['sdk-manifest.json']);hashes=json.loads(files['SHA256.json'])
 if manifest['version']!=lock['version'] or manifest['commit']!=lock['commit'] or manifest['repository']!=lock['repository']:raise ValueError('SDK manifest identity mismatch')
 if set(hashes)!=set(files)-{'SHA256.json'} or any(digest(files[name])!=value for name,value in hashes.items()):raise ValueError('SDK member integrity mismatch')
 return files

def prepare(lock_path,output,bundle=None):
 lock=json.loads(Path(lock_path).read_text());output=Path(output)
 if output.is_symlink():raise ValueError('SDK cache must not be a symlink')
 output=output.resolve()
 if not re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+(?:-[A-Za-z0-9.-]+)?',lock['version']) or not re.fullmatch('[0-9a-f]{40}',lock['commit']) or lock['repository']!='Nexa-MC/NexaCL-Plugin-SDK' or lock['release']!='v'+lock['version'] or lock['file']!=f"Nexa.Plugin.Sdk.Bundle.{lock['version']}.zip" or not 0<lock['size']<=32*1024*1024:raise ValueError('Unexpected SDK identity')
 source=output/'.source.zip'
 if output.is_symlink():raise ValueError('SDK cache must not be a symlink')
 payload=None
 if source.is_file():
  try:
   payload=source.read_bytes();files=checked_files(payload,lock)
   if all((output/name).is_file() and not (output/name).is_symlink() and digest((output/name).read_bytes())==digest(data) for name,data in files.items()):print('Pinned independent SDK verified.');return
  except (OSError,ValueError,KeyError,zipfile.BadZipFile):payload=None
 if bundle is not None:payload=Path(bundle).read_bytes()
 elif payload is None:
  url=f"https://github.com/{lock['repository']}/releases/download/{lock['release']}/{lock['file']}"
  with urllib.request.urlopen(url,timeout=60) as response:payload=response.read(lock['size']+1)
 files=checked_files(payload,lock)
 if output.exists() and any(output.iterdir()) and not source.exists():raise ValueError('Refusing to replace a directory not owned by the SDK cache')
 output.parent.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory(prefix='nexa-sdk-',dir=output.parent) as temporary:
  staged=Path(temporary)/'cache';staged.mkdir()
  for name,data in files.items():path=staged/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
  (staged/'.source.zip').write_bytes(payload)
  if output.exists():shutil.rmtree(output)
  os.replace(staged,output)
 print('Pinned independent SDK prepared.')
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--lock',default='sdk.lock.json');parser.add_argument('--output',default='.sdk');parser.add_argument('--bundle');args=parser.parse_args();prepare(args.lock,args.output,args.bundle)
