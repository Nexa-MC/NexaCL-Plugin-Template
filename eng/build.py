#!/usr/bin/env python3
"""Build an import-free Wasm page/action plugin and a deterministic verified ZIP."""
import argparse,hashlib,json,re,subprocess,zipfile
from pathlib import Path
from xml.sax.saxutils import escape
from consume_sdk import prepare
root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--clang',default='clang');parser.add_argument('--sdk-root',type=Path);parser.add_argument('--config',type=Path,default=root/'plugin.config.json');parser.add_argument('--out',type=Path,default=root/'artifacts/plugin.zip');args=parser.parse_args()
config=json.loads(args.config.read_text());identity=config['id'];version=config['version'];title=config['title']
if not re.fullmatch('[a-z][a-z0-9.-]{1,63}',identity) or not re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+(?:-[A-Za-z0-9.-]+)?',version) or not isinstance(title,str) or not 0<len(title)<=128:raise ValueError('Invalid plugin identity, version or title')
required=['nexa.files.read','nexa.ui.write','nexa.actions.write','nexa.actions.read','nexa.tasks.read']
permissions=config.get('permissions',required)
if not isinstance(permissions,list) or len(permissions)>64 or any(not isinstance(p,str) or not re.fullmatch('[a-z][a-z0-9.-]+',p) for p in permissions) or len(set(permissions))!=len(permissions) or not set(required)<=set(permissions):raise ValueError('Invalid or incomplete permission list')
sdk=args.sdk_root
if sdk is None:prepare(root/'sdk.lock.json',root/'.sdk');sdk=root/'.sdk'
header=sdk/'sdk/wasm/include'
if not (header/'nexa/abi100.h').is_file():raise ValueError('Missing SDK headers')
output=args.out.resolve();output.parent.mkdir(parents=True,exist_ok=True);wasm=output.parent/(output.stem+'.wasm')
subprocess.run([args.clang,'--target=wasm32-unknown-unknown','-std=c11','-O2','-Wall','-Wextra','-Werror','-ffreestanding','-fno-builtin','-nostdlib','-I',str(header),'-DPLUGIN_ID="'+identity+'"',str(root/'wasm/plugin.c'),'-Wl,--no-entry','-Wl,--export-memory','-Wl,-z,stack-size=131072','-Wl,--initial-memory=1048576','-Wl,--max-memory=1048576','-o',str(wasm)],check=True)
files={'plugin.wasm':wasm.read_bytes(),'page.nxml':(root/'wasm/page.nxml').read_text().replace('{{PLUGIN_ID}}',identity).replace('{{TITLE}}',escape(title,{'"':'&quot;'})).encode()}
manifest={'manifestVersion':1,'pluginId':identity,'pluginVersion':version,'bootstrapVersion':1,'entry':{'assembly':'','type':''},'target':{'operatingSystems':[],'architectures':[],'runtime':'nexa-wasm-1'},'declaredAbiCandidates':[100],'requiredDependencies':[],'optionalDependencies':[],'conflicts':[],'requestedPermissions':permissions,'requiredCapabilities':[{'contractId':c,'minimumVersion':1} for c in ['nexa.files','nexa.ui','nexa.actions','nexa.tasks']],'optionalCapabilities':config.get('optionalCapabilities',[]),'webAssemblyEntryPath':'plugin.wasm','payloads':[{'path':name,'size':len(data),'sha256':hashlib.sha256(data).hexdigest()} for name,data in sorted(files.items())]}
files['plugin.json']=(json.dumps(manifest,sort_keys=True,separators=(',',':'))+'\n').encode()
with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED) as archive:
 for name,data in sorted(files.items()):
  info=zipfile.ZipInfo(name,(1980,1,1,0,0,0));info.external_attr=0o100644<<16;info.compress_type=zipfile.ZIP_DEFLATED;archive.writestr(info,data)
print(output)
