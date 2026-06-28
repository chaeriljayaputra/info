# info.py - OUR VERSION (Vercel Ready, SG & ID Only)
# Owner : @vaibhavff570
# Join : @vaibhavapix, @vaibhavapisx

import json
import sys
import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

# Import proto dari folder
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from proto import FreeFire_pb2, main_pb2, AccountPersonalShow_pb2
from google.protobuf import json_format
from Crypto.Cipher import AES

# ==================== CONFIG ====================
G = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
F = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
REGNS = {"SG", "ID"}
SERVER_URL = "https://clientbp.ggpolarbear.com"

FAHHHH = Flask(__name__)
CORS(FAHHHH)

# ==================== HELPERS ====================
def BmwNoNoBmvYas(d):
    l = AES.block_size - (len(d) % AES.block_size)
    return d + bytes([l] * l)

def BmwNoiNoiBmvYasYas(k, i, d):
    a = AES.new(k, AES.MODE_CBC, i)
    return a.encrypt(BmwNoNoBmvYas(d))

def PoI(b, mt):
    m = mt()
    m.ParseFromString(b)
    return m

def QwE(jt, pt):
    json_format.ParseDict(json.loads(jt), pt)
    return pt.SerializeToString()

def AsD(reg):
    reg = reg.upper()
    if reg == "SG":
        return "uid=5374557838&password=ANONFK345213AKU"
    elif reg == "ID":
        return "uid=5374558199&password=ANONFK54734ULRW"
    else:
        return "uid=5374557838&password=ANONFK345213AKU"

# ==================== TOKEN GENERATOR (SYNC) ====================
def ZxV(acc):
    url = "https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant"
    data = acc + "&response_type=token&client_type=2&client_secret=2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3&client_id=100067"
    try:
        res = requests.post(url, data=data, headers={
            'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 13; CPH2095 Build/RKQ1.211119.001)",
            'Connection': "Keep-Alive",
            'Accept-Encoding': "gzip",
            'Content-Type': "application/x-www-form-urlencoded"
        }, timeout=30)
        d = res.json()
        return d.get("access_token", "0"), d.get("open_id", "0")
    except:
        return "0", "0"

def Bmw(reg):
    acc = AsD(reg)
    token, oid = ZxV(acc)
    if token == "0":
        return None
    
    body = json.dumps({"open_id": oid, "open_id_type": "4", "login_token": token, "orign_platform_type": "4"})
    pb = QwE(body, FreeFire_pb2.LoginReq())
    enc = BmwNoiNoiBmvYasYas(G, F, pb)
    
    try:
        res = requests.post(
            "https://loginbp.ggpolarbear.com/MajorLogin",
            data=enc,
            headers={
                'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 13; CPH2095 Build/RKQ1.211119.001)",
                'Connection': "Keep-Alive",
                'Accept-Encoding': "gzip",
                'Content-Type': "application/octet-stream",
                'Expect': "100-continue",
                'X-Unity-Version': "2018.4.11f1",
                'X-GA': "v1 1",
                'ReleaseVersion': "OB54"
            },
            timeout=30
        )
        
        if res.status_code == 200:
            msg = json.loads(json_format.MessageToJson(PoI(res.content, FreeFire_pb2.LoginRes)))
            return {
                'token': f"Bearer {msg.get('token','0')}",
                'region': msg.get('lockRegion','0'),
                'server': msg.get('serverUrl','0')
            }
        return None
    except:
        return None

def RtY(reg):
    return Bmw(reg)

# ==================== PLAYER FETCH (SYNC) ====================
def LoL(uid, unk, reg, ep):
    payload = QwE(json.dumps({'a': uid, 'b': unk}), main_pb2.GetPlayerPersonalShow())
    data_enc = BmwNoiNoiBmvYasYas(G, F, payload)
    
    token_info = RtY(reg)
    if not token_info:
        return None
    
    token = token_info['token']
    server = token_info.get('server', SERVER_URL)
    
    try:
        res = requests.post(
            server + ep,
            data=data_enc,
            headers={
                'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 13; CPH2095 Build/RKQ1.211119.001)",
                'Connection': "Keep-Alive",
                'Accept-Encoding': "gzip",
                'Content-Type': "application/octet-stream",
                'Expect': "100-continue",
                'Authorization': token,
                'X-Unity-Version': "2018.4.11f1",
                'X-GA': "v1 1",
                'ReleaseVersion': "OB54"
            },
            timeout=30
        )
        
        if res.status_code == 200:
            return json.loads(json_format.MessageToJson(PoI(res.content, AccountPersonalShow_pb2.AccountPersonalShowInfo)))
        return None
    except:
        return None

def HeHe(d):
    return d

# ==================== ROUTES (MIRIP ASLI) ====================
@FAHHHH.route('/Bmw')
def OMG():
    uid = request.args.get('uid')
    if not uid:
        return jsonify({"error": "Please provide UID."}), 400
    
    for reg in REGNS:
        try:
            data = LoL(uid, "7", reg, "/GetPlayerPersonalShow")
            if data:
                data = HeHe(data)
                return json.dumps(data, indent=2, ensure_ascii=False), 200, {'Content-Type': 'application/json; charset=utf-8'}
        except:
            continue
    
    return jsonify({"error": "UID not found in any region."}), 404

@FAHHHH.route('/info')
def info():
    uid = request.args.get('id') or request.args.get('uid')
    if not uid:
        return jsonify({"error": "Please provide UID."}), 400
    
    for reg in REGNS:
        try:
            data = LoL(uid, "7", reg, "/GetPlayerPersonalShow")
            if data:
                data = HeHe(data)
                return json.dumps(data, indent=2, ensure_ascii=False), 200, {'Content-Type': 'application/json; charset=utf-8'}
        except:
            continue
    
    return jsonify({"error": "UID not found in any region."}), 404

@FAHHHH.route('/lookup')
def lookup():
    jwt_token = request.args.get('jwt') or request.args.get('token')
    if not jwt_token:
        return jsonify({"error": "Please provide JWT token."}), 400
    
    # Decode JWT
    import base64
    try:
        parts = jwt_token.split('.')
        if len(parts) >= 2:
            p = parts[1]
            p += '=' * (4 - len(p) % 4) if len(p) % 4 else ''
            jwt_data = json.loads(base64.b64decode(p))
            uid = jwt_data.get("account_id")
            
            if uid:
                for reg in REGNS:
                    try:
                        # Fetch dengan JWT langsung
                        payload = QwE(json.dumps({'a': str(uid), 'b': '7'}), main_pb2.GetPlayerPersonalShow())
                        data_enc = BmwNoiNoiBmvYasYas(G, F, payload)
                        
                        res = requests.post(
                            f"{SERVER_URL}/GetPlayerPersonalShow",
                            data=data_enc,
                            headers={
                                'User-Agent': "Dalvik/2.1.0",
                                'Content-Type': "application/octet-stream",
                                'Authorization': f"Bearer {jwt_token}",
                                'X-Unity-Version': "2018.4.11f1",
                                'X-GA': "v1 1",
                                'ReleaseVersion': "OB54"
                            },
                            timeout=30
                        )
                        
                        if res.status_code == 200:
                            data = json.loads(json_format.MessageToJson(PoI(res.content, AccountPersonalShow_pb2.AccountPersonalShowInfo)))
                            return json.dumps(data, indent=2, ensure_ascii=False), 200, {'Content-Type': 'application/json; charset=utf-8'}
                    except:
                        continue
    except:
        pass
    
    return jsonify({"error": "Invalid token or player not found."}), 404

@FAHHHH.route('/', methods=['GET'])
def home():
    return jsonify({
        "success": True,
        "message": "Free Fire Player Lookup",
        "owner": "@vaibhavff570",
        "join": ["@vaibhavapix", "@vaibhavapisx"],
        "endpoints": {
            "/Bmw": "Get player by UID",
            "/info": "Get player by UID (alternate)",
            "/lookup": "Get player by JWT token"
        }
    })

# ==================== MAIN ====================
if __name__ == "__main__":
    print("🔥 Free Fire API - SG & ID Only")
    print("Owner: @vaibhavff570")
    FAHHHH.run(host="0.0.0.0", port=5000)
