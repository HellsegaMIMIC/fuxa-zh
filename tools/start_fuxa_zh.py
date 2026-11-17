"""Start a standalone, loopback-only PLCdev FUXA editor in its own profile."""

from pathlib import Path
import argparse
import json
import os
import signal
import socket
import subprocess
import sys
import threading
import time
import webbrowser

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / 'outputs' / 'fuxa-zh-standalone' / 'profile'
PORT = 18812
URL = f'http://127.0.0.1:{PORT}/editor'


def port_available():
    with socket.socket() as probe:
        try:
            probe.bind(('127.0.0.1', PORT))
        except OSError:
            return False
        return True


def safe_profile_settings(package):
    """Recognize the launcher-generated config before trusting its uiHost.

    Native UI preferences live in mysettings.json, not in this file. Refuse a
    hand-edited settings.js instead of silently binding to a wider interface.
    """
    settings = PROFILE / '_appdata' / 'settings.js'
    if not settings.exists():
        return True
    prefix = 'module.exports={...require(' + json.dumps(str(package / 'settings.default.js')) + ')'
    common = ',uiHost:"127.0.0.1",uiPort:' + str(PORT)
    tail = ',nodeRedEnabled:false,daqEnabled:false,secureEnabled:false,swaggerEnabled:false,logApiLevel:"none",hideEditorOnboarding:true};\n'
    return settings.read_text(encoding='utf-8') in {
        prefix + common + tail,
        prefix + common + ',language:"zh-cn"' + tail,
    }


def stop_child(process):
    if process.poll() is not None:
        return
    if os.name == 'nt':
        try:
            process.send_signal(signal.CTRL_BREAK_EVENT)
            process.wait(timeout=8)
            return
        except (OSError, subprocess.TimeoutExpired):
            # Only terminate this launcher's process tree, never a port owner.
            subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    else:
        process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--no-browser', action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args()
    package = ROOT / '.tools' / 'fuxa' / 'runtime' / 'node_modules' / '@frangoteam' / 'fuxa'
    if not (package / 'main.js').is_file():
        print('没有找到 FUXA。请先在项目根目录运行：python -X utf8 tools/install_fuxa.py')
        return 1
    if not safe_profile_settings(package):
        print('独立 profile 的 settings.js 已被修改，无法确认只监听本机；请先检查该文件。')
        return 1
    if not port_available():
        print(f'本机端口 {PORT} 已占用，本启动器不会接管或关闭现有程序。')
        return 1
    print('正在启动独立 FUXA 编辑器；不会启动 PLC 或 OIP。', flush=True)
    print(f'画面和设置保存在：{PROFILE}', flush=True)
    flags = subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
    proc = subprocess.Popen(
        [sys.executable, '-u', '-X', 'utf8', str(ROOT / 'tools' / 'run_fuxa.py'),
         '--profile', str(PROFILE), '--port', str(PORT)],
        cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, encoding='utf-8', errors='replace', creationflags=flags,
    )
    ready = threading.Event()

    def relay_output():
        for line in proc.stdout:
            print(line, end='', flush=True)
            # This message comes from our own FUXA listen callback, not another
            # process that might have won a port race after the probe.
            if 'WebServer is running' in line and f'127.0.0.1:{PORT}' in line:
                ready.set()

    threading.Thread(target=relay_output, daemon=True).start()
    try:
        deadline = time.monotonic() + 90
        while not ready.is_set() and proc.poll() is None and time.monotonic() < deadline:
            ready.wait(0.1)
        if not ready.is_set():
            print('FUXA 未能在 90 秒内就绪，请查看上方日志。')
            return 1
        print(f'编辑器已就绪：{URL}', flush=True)
        print('保存画面后，在此窗口按 Enter 停止 FUXA；仅关闭浏览器不会停止服务。', flush=True)
        if not args.no_browser:
            webbrowser.open(URL)
        entered = threading.Event()

        def wait_for_enter():
            try:
                input()
            except EOFError:
                pass
            entered.set()

        threading.Thread(target=wait_for_enter, daemon=True).start()
        while not entered.wait(0.2) and proc.poll() is None:
            pass
        return 0 if proc.poll() is None else proc.returncode
    except KeyboardInterrupt:
        print('\n正在停止 FUXA。')
        return 0
    finally:
        stop_child(proc)


if __name__ == '__main__':
    raise SystemExit(main())
