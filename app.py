# info.py - TEST DENGAN API EXTERNAL DULU
from flask import Flask, request, jsonify
import requests
import json
import base64
import re
import os
from datetime import datetime
from Crypto.Cipher import AES

os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'

app = Flask(__name__)

# ==================== CONFIG ====================
CREDENTIALS = {
    "SG": "uid=5374557838&password=ANONFK345213AKU",
    "ID": "uid=5374558199&password=ANONFK54734ULRW",
}
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

# ==================== MANUAL PROTOBUF ====================
def make_varint(n):
    result = []
    while n > 127:
        result.append((n & 0x7F) | 0x80)
        n >>= 7
    result.append(n)
    return bytes(result)

def make_string(field_num, s):
    tag = make_varint((field_num << 3) | 2)
    data = s.encode()
    return tag + make_varint(len(data)) + data

def make_int64(field_num, val):
    return make_varint((field_num << 3) | 0) + make_varint(val)

def make_int32(field_num, val):
    return make_varint((field_num << 3) | 0) + make_varint(val)

def build_login_req(open_id, token):
    body = b''
    body += make_string(22, open_id)
    body += make_string(23, '4')
    body += make_string(29, token)
    body += make_string(99, '4')
    return body

def build_player_show_req(uid):
    body = b''
    body += make_int64(1, int(uid))
    body += make_int32(2, 7)
    return body

# ==================== FUNCTIONS ====================
def generate_token(region):
    creds = CREDENTIALS.get(region, CREDENTIALS["SG"])
    try:
        # Step 1: OAuth
        data = creds + "&response_type=token&client_type=2&client_secret=2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3&client_id=100067"
        r = requests.post("https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant", data=data, headers={'Content-Type': "application/x-www-form-urlencoded"}, timeout=30)
        d = r.json()
        oauth_token, oid = d.get("access_token", "0"), d.get("open_id", "0")
        if oauth_token == "0": return None, None
        
        # Step 2: MajorLogin
        pb = build_login_req(oid, oauth_token)
        encrypted = encrypt_data(pb)
        
        r = requests.post("https://loginbp.ggpolarbear.com/MajorLogin", data=encrypted, headers={'Content-Type': "application/octet-stream", 'X-Unity-Version': "2018.4.11f1", 'X-GA': "v1 1", 'ReleaseVersion': "OB54"}, timeout=30)
        
        # Parse token dari response (cari JWT pattern)
        text = r.text
        jwt_match = re.search(r'eyJ[A-Za-z0-9_\-\.]{100,}', text)
        if jwt_match:
            return jwt_match.group(0), oauth_token
        
        return None, None
    except Exception as e:
        print(f"Token error: {e}")
        return None, None

@app.route("/", methods=["GET"])
def home():
    return jsonify({"success": True, "endpoints": {"/info": "?id=UID", "/test": "test endpoint"}})

@app.route("/test", methods=["GET"])
def test():
    """Test endpoint - cek apa yang work"""
    result = {}
    
    # Test 1: OAuth
    try:
        creds = CREDENTIALS["SG"]
        data = creds + "&response_type=token&client_type=2&client_secret=2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3&client_id=100067"
        r = requests.post("https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant", data=data, headers={'Content-Type': "application/x-www-form-urlencoded"}, timeout=30)
        result['oauth_status'] = r.status_code
        result['oauth_keys'] = list(r.json().keys()) if r.status_code == 200 else 'N/A'
    except Exception as e:
        result['oauth_error'] = str(e)
    
    # Test 2: Token gen
    jwt, access = generate_token("SG")
    result['jwt_generated'] = bool(jwt)
    result['jwt_preview'] = jwt[:50] + '...' if jwt else None
    
    # Test 3: Fetch player (pake API external)
    if jwt:
        try:
            uid = "290012951"
            r = requests.get(f"https://ff.ggbluewhale.store/api/data?region=id&uid={uid}&key=kenn", timeout=10)
            result['player_api_status'] = r.status_code
            if r.status_code == 200:
                d = r.json()
                result['player_found'] = bool(d.get('basicInfo'))
                result['player_name'] = d.get('basicInfo', {}).get('nickname', '?')
        except Exception as e:
            result['player_api_error'] = str(e)
    
    return jsonify(result)

@app.route("/info", methods=["GET"])
def info():
    uid = request.args.get("id") or request.args.get("uid")
    
    if not uid:
        return jsonify({"success": False, "error": "Missing id"}), 400
    
    # Generate token
    jwt_token, access_token = generate_token("SG")
    if not jwt_token:
        return jsonify({"success": False, "error": "Token generation failed"}), 500
    
    # Coba fetch dari API external
    try:
        r = requests.get(f"https://ff.ggbluewhale.store/api/data?region=id&uid={uid}&key=kenn", timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data.get('basicInfo'):
                basic = data['basicInfo']
                social = data.get('socialInfo', {})
                clan = data.get('clanBasicInfo', {})
                
                return jsonify({
                    "success": True,
                    "data": {
                        "uid": uid,
                        "nickname": basic.get('nickname', '?'),
                        "level": basic.get('level', 0),
                        "region": basic.get('region', 'ID'),
                        "br_rank": basic.get('rank', 0),
                        "cs_rank": basic.get('csRank', 0),
                        "liked": basic.get('likes', 0),
                        "clan": clan.get('clanName', ''),
                        "signature": social.get('signature', ''),
                        "diamond": data.get('diamondCostRes', {}).get('diamondCost', 0),
                    },
                    "jwt_generated": True,
                    "source": "api"
                })
    except: pass
    
    return jsonify({"success": False, "error": "Not found"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
