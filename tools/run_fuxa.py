"""Public standalone launcher. No credential reuse or model request helper."""
from pathlib import Path
import argparse, os, subprocess
from install_fuxa import ROOT, DEFAULT, install
from plcdev_environment import tool_path

def main():
    p=argparse.ArgumentParser();p.add_argument('--profile',type=Path,required=True)
    p.add_argument('--port',type=int,default=18812);a=p.parse_args()
    if not 1024<=a.port<=65535: raise ValueError('Invalid local port')
    package=Path(install(DEFAULT,skip_install=True)['packageRoot'])
    env={k:v for k,v in os.environ.items() if not k.startswith('PLCDEV_')}
    env.update(PLCDEV_FUXA_ROOT=str(package),PLCDEV_FUXA_PROFILE=str(a.profile.resolve()),
        PLCDEV_FUXA_PORT=str(a.port),PLCDEV_FUXA_EXTENSION=str(ROOT/'software/fuxa-integration/server-plugin.cjs'),
        PLCDEV_FUXA_AI_ENABLED='0')
    return subprocess.call([str(tool_path('node')),str(package/'main.js'),'--port',str(a.port),
        '--userDir',str(a.profile.resolve())],cwd=package,env=env)

if __name__=='__main__':raise SystemExit(main())
