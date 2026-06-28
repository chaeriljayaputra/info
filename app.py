# info.py - VERCEL FINAL (Generate proto from .proto text)
from flask import Flask, request, jsonify
import requests
import json
import base64
import re
import os
import sys
from datetime import datetime
from Crypto.Cipher import AES

os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'

app = Flask(__name__)

# ==================== CONFIG ====================
CREDENTIALS = {
    "SG": "uid=5374557838&password=ANONFK345213AKU",
    "ID": "uid=5374558199&password=ANONFK54734ULRW",
}
SERVERS = {"SG": "https://clientbp.ggpolarbear.com", "ID": "https://clientbp.ggpolarbear.com"}
G = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
F = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])

def pad_data(d):
    l = AES.block_size - (len(d) % AES.block_size)
    return d + bytes([l] * l)

def encrypt_data(d):
    return AES.new(G, AES.MODE_CBC, F).encrypt(pad_data(d))

def b64_decode(s):
    s += '=' * (4 - len(s) % 4) if len(s) % 4 else ''
    return json.loads(base64.b64decode(s))

# ==================== SIMPLE PROTOBUF BUILDER ====================
# Build proto dari teks .proto langsung saat runtime

PROTO_TEXT = """
syntax = "proto3";

message LoginReq {
  string open_id = 22;
  string open_id_type = 23;
  string login_token = 29;
  string orign_platform_type = 99;
}

message LoginRes {
  uint64 account_id = 1;
  string lock_region = 2;
  string noti_region = 3;
  string ip_region = 4;
  string token = 8;
  uint32 ttl = 9;
  string server_url = 10;
  uint32 emulator_score = 11;
}

message GetPlayerPersonalShow {
  int64 a = 1;
  int32 b = 2;
}
"""

def build_proto_from_text(proto_text, message_name):
    """Build protobuf class from .proto text"""
    from google.protobuf import descriptor_pb2
    from google.protobuf import descriptor_pool
    from google.protobuf import message_factory
    import subprocess
    import tempfile
    
    # Tulis ke file sementara
    tmp_proto = tempfile.NamedTemporaryFile(suffix='.proto', delete=False, mode='w')
    tmp_proto.write(proto_text)
    tmp_proto.close()
    
    tmp_dir = os.path.dirname(tmp_proto.name)
    
    try:
        # Compile proto
        subprocess.run([
            sys.executable, '-m', 'grpc_tools.protoc',
            f'--proto_path={tmp_dir}',
            f'--python_out={tmp_dir}',
            tmp_proto.name
        ], check=True, capture_output=True, timeout=30)
        
        # Import hasil compile
        sys.path.insert(0, tmp_dir)
        pb2_name = os.path.splitext(os.path.basename(tmp_proto.name))[0] + '_pb2'
        module = __import__(pb2_name)
        
        # Cleanup
        os.unlink(tmp_proto.name)
        try: os.unlink(os.path.join(tmp_dir, pb2_name + '.py'))
        except: pass
        
        return getattr(module, message_name)
    except:
        os.unlink(tmp_proto.name)
        return None

# ==================== FALLBACK: Manual protobuf ====================
def make_varint(n):
    """Encode varint manually"""
    result = []
    while n > 127:
        result.append((n & 0x7F) | 0x80)
        n >>= 7
    result.append(n)
    return bytes(result)

def make_length_delimited(field_num, data):
    """Tag + length + data"""
    tag = make_varint((field_num << 3) | 2)
    length = make_varint(len(data))
    return tag + length + data

def make_uint64(field_num, val):
    return make_varint((field_num << 3) | 0) + make_varint(val)

def make_int64(field_num, val):
    return make_varint((field_num << 3) | 0) + make_varint(val)

def make_string(field_num, s):
    return make_length_delimited(field_num, s.encode())

def build_login_req(open_id, token):
    """Manual build LoginReq protobuf"""
    body = b''
    body += make_string(22, open_id)
    body += make_string(23, '4')
    body += make_string(29, token)
    body += make_string(99, '4')
    return body

def build_player_show_req(uid):
    """Manual build GetPlayerPersonalShow"""
    body = b''
    body += make_int64(1, int(uid))
    body += make_varint((2 << 3) | 0) + make_varint(7)
    return body

def parse_login_res(data):
    """Simple parser for LoginRes"""
    try:
        # Cari token di response
        text = data.decode('latin-1')
        token_match = re.search(r'token[\x00-\x1f]+([A-Za-z0-9_\-\.]{50,})', text)
        if token_match:
            return {'token': token_match.group(1)}
        return {'token': '0'}
    except:
        return {'token': '0'}

def parse_player_res(data):
    """Parse player response"""
    try:
        text = data.decode('utf-8', errors='ignore')
        result = {}
        
        # Cari nickname
        nick_match = re.search(r'nickname[\x00-\x1f\x20]+([^\x00-\x1f]{2,30})', text)
        if nick_match:
            result['nickname'] = nick_match.group(1).strip()
        
        # Cari level
        lvl_match = re.search(r'level[\x00-\x1f]+(\d+)', text)
        if lvl_match:
            result['level'] = int(lvl_match.group(1))
        
        # Cari region
        reg_match = re.search(r'region[\x00-\x1f]+([A-Z]{2})', text)
        if reg_match:
            result['region'] = reg_match.group(1)
        
        return result if result.get('nickname') else None
    except:
        return None

# ==================== FUNCTIONS ====================
def generate_token(region):
    creds = CREDENTIALS.get(region, CREDENTIALS["SG"])
    try:
        data = creds + "&response_type=token&client_type=2&client_secret=2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3&client_id=100067"
        r = requests.post("https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant", data=data, headers={'Content-Type': "application/x-www-form-urlencoded"}, timeout=30)
        d = r.json()
        token, oid = d.get("access_token", "0"), d.get("open_id", "0")
        if token == "0": return None
        
        # Build LoginReq manual
        pb = build_login_req(oid, token)
        encrypted = encrypt_data(pb)
        
        r = requests.post("https://loginbp.ggpolarbear.com/MajorLogin", data=encrypted, headers={'Content-Type': "application/octet-stream", 'X-Unity-Version': "2018.4.11f1", 'X-GA': "v1 1", 'ReleaseVersion': "OB54"}, timeout=30)
        if r.status_code == 200:
            msg = parse_login_res(r.content)
            return f"Bearer {msg.get('token', '0')}"
        return None
    except Exception as e:
        print(f"Token error: {e}")
        return None

def fetch_player(uid, token, region="SG"):
    try:
        server_url = SERVERS.get(region, SERVERS["SG"])
        pb = build_player_show_req(uid)
        encrypted = encrypt_data(pb)
        
        r = requests.post(
            f"{server_url}/GetPlayerPersonalShow",
            data=encrypted,
            headers={
                'Content-Type': "application/octet-stream",
                'Authorization': token if token.startswith("Bearer ") else f"Bearer {token}",
                'X-Unity-Version': "2018.4.11f1", 'X-GA': "v1 1", 'ReleaseVersion': "OB54"
            },
            timeout=30
        )
        if r.status_code != 200: return None
        
        data = parse_player_res(r.content)
        if not data: return None
        
        return {
            'uid': uid, 'nickname': data.get('nickname', '?'),
            'level': data.get('level', 0), 'region': data.get('region', region),
            'br_rank': 0, 'cs_rank': 0, 'liked': 0,
            'clan': '', 'clan_level': 0,
            'avatar': '', 'clothes': [], 'skills': 0,
            'signature': '', 'diamond': 0, 'credit': 0,
            'created': '', 'last_login': ''
        }
    except Exception as e:
        print(f"Fetch error: {e}")
        return None

# ==================== ROUTES ====================
@app.route("/", methods=["GET"])
def home():
    return jsonify({"success": True, "message": "Free Fire API", "endpoints": {"/info": "?id=UID&region=SG", "/lookup": "?jwt=TOKEN"}})

@app.route("/info", methods=["GET"])
def info():
    uid = request.args.get("id") or request.args.get("uid")
    region = (request.args.get("region") or "SG").upper()
    
    if not uid: return jsonify({"success": False, "error": "Missing id"}), 400
    if region not in SERVERS: region = "SG"
    
    token = generate_token(region)
    if not token: return jsonify({"success": False, "error": "Token failed"}), 500
    
    data = fetch_player(uid, token, region)
    if not data: return jsonify({"success": False, "error": "Not found"}), 404
    
    return jsonify({"success": True, "data": data})

@app.route("/lookup", methods=["GET"])
def lookup():
    jwt_token = request.args.get("jwt")
    region = (request.args.get("region") or "SG").upper()
    
    if not jwt_token: return jsonify({"success": False, "error": "Missing jwt"}), 400
    
    jwt_data = b64_decode(jwt_token) if jwt_token.count('.') >= 2 else None
    if not jwt_data: return jsonify({"success": False, "error": "Invalid JWT"}), 400
    
    uid = jwt_data.get("account_id")
    if not uid: return jsonify({"success": False, "error": "No account_id"}), 400
    
    data = fetch_player(str(uid), jwt_token, region)
    if not data: return jsonify({"success": False, "error": "Not found"}), 404
    
    return jsonify({"success": True, "data": data})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
