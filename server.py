import http.server
import urllib.request
import urllib.parse
import json
import os
import subprocess
import time
import threading

TG_TOKEN = '8612932015:AAGXECyzfijn8RD6Yw4xzsTMHENdKaylzDg'
TG_CHAT_ID = '515406098'
PORT = 8080

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/api/send-telegram':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            data = json.loads(body)
            msg = (
                f"<b>🔥 Новая заявка на тренера!</b>\n\n"
                f"<b>Ник:</b> {data.get('nick', '?')}\n"
                f"<b>Возраст:</b> {data.get('age', '?')}\n"
                f"<b>Контакты:</b> {data.get('contact', '?')}\n"
                f"<b>Уровень:</b> {data.get('level', '?')}\n"
                + (f"<b>Техники:</b> {data.get('goals', '')}\n" if data.get('goals') else "") +
                (f"<b>Время:</b> {data.get('time', '')} ч/нед\n" if data.get('time') else "") +
                f"<b>Цель:</b> {data.get('goalFinal', '?')}\n"
                f"<b>Дата:</b> {data.get('date', '?')}"
            )
            tg_url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
            tg_data = urllib.parse.urlencode({
                'chat_id': TG_CHAT_ID, 'text': msg, 'parse_mode': 'HTML'
            }).encode()
            try:
                urllib.request.urlopen(tg_url, data=tg_data, timeout=10)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'ok': True}).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'ok': False, 'error': str(e)}).encode())
        else:
            self.send_error(404)

    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
        return super().do_GET()

def start_tunnel():
    time.sleep(2)
    ssh_path = r'C:\Windows\System32\OpenSSH\ssh.exe'
    log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tunnel.log')
    with open(log_file, 'w') as f:
        proc = subprocess.Popen(
            [ssh_path, '-o', 'StrictHostKeyChecking=no',
             '-o', 'ServerAliveInterval=30',
             '-R', '80:localhost:' + str(PORT),
             'nokey@localhost.run'],
            stdout=f, stderr=subprocess.STDOUT,
            creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
            close_fds=True
        )
    print(f'Туннель запущен (PID: {proc.pid})')
    time.sleep(8)
    try:
        with open(log_file, 'r') as f:
            content = f.read()
        for line in content.split('\n'):
            if 'https://' in line:
                url = line.strip()
                print(f'\n🌐 ПУБЛИЧНЫЙ АДРЕС: {url}\n')
                break
    except:
        pass

    import atexit
    atexit.register(lambda: None)

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    threading.Thread(target=start_tunnel, daemon=True).start()
    server = http.server.HTTPServer(('0.0.0.0', PORT), Handler)
    print(f'Сервер запущен: http://localhost:{PORT}')
    server.serve_forever()
