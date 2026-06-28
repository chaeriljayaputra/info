# info.py - OUR VERSION (Vercel Ready, Proto Folder)
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

CREDENTIALS = {
    "SG": "uid=5374557838&password=ANONFK345213AKU",
    "ID": "uid=5374558199&password=ANONFK54734ULRW",
}

app = Flask(__name__)
CORS(app)

# ==================== HELPERS ====================
def pad(d):
    l = AES.block_size - (len(d) % AES.block_size)
    return d + bytes([l] * l)

def encrypt(k, i, d):
    return AES.new(k, AES.MODE_CBC, i).encrypt(pad(d))

def parse_pb(b, mt):
    m = mt()
    m.ParseFromString(b)
    return m

def json2pb(js, pt):
    json_format.ParseDict(json.loads(js), pt)
    return pt.SerializeToString()

# ==================== TOKEN GENERATOR ====================
def generate_token(region):
    """Generate token - SYNC"""
    creds = CREDENTIALS.get(region, CREDENTIALS["SG"])
    try:
        # Step 1: OAuth
        data = creds + "&response_type=token&client_type=2&client_secret=2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3&client_id=100067"
        r = requests.post(
            "https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant",
            data=data,
            headers={'Content-Type': "application/x-www-form-urlencoded", 'User-Agent': "Dalvik/2.1.0"},
            timeout=30
        )
        d = r.json()
        token, oid = d.get("access_token", "0"), d.get("open_id", "0")
        if token == "0": return None
        
        # Step 2: MajorLogin
        body = json.dumps({"open_id": oid, "open_id_type": "4", "login_token": token, "orign_platform_type": "4"})
        pb = json2pb(body, FreeFire_pb2.LoginReq())
        enc = encrypt(G, F, pb)
        
        r = requests.post(
            "https://loginbp.ggpolarbear.com/MajorLogin",
            data=enc,
            headers={
                'Content-Type': "application/octet-stream",
                'X-Unity-Version': "2018.4.11f1",
                'X-GA': "v1 1",
                'ReleaseVersion': "OB54",
                'User-Agent': "Dalvik/2.1.0"
            },
            timeout=30
        )
        
        if r.status_code == 200:
            msg = json.loads(json_format.MessageToJson(parse_pb(r.content, FreeFire_pb2.LoginRes)))
            return f"Bearer {msg.get('token', '0')}"
        return None
    except Exception as e:
        print(f"Token error: {e}")
        return None

# ==================== PLAYER FETCH ====================
def fetch_player(uid, token):
    """Fetch player data - SYNC"""
    try:
        body = json.dumps({'a': str(uid), 'b': '7'})
        pb = json2pb(body, main_pb2.GetPlayerPersonalShow())
        enc = encrypt(G, F, pb)
        
        r = requests.post(
            "https://clientbp.ggpolarbear.com/GetPlayerPersonalShow",
            data=enc,
            headers={
                'Content-Type': "application/octet-stream",
                'Authorization': token if token.startswith("Bearer ") else f"Bearer {token}",
                'X-Unity-Version': "2018.4.11f1",
                'X-GA': "v1 1",
                'ReleaseVersion': "OB54",
                'User-Agent': "Dalvik/2.1.0"
            },
            timeout=30
        )
        
        if r.status_code == 200:
            data = json.loads(json_format.MessageToJson(parse_pb(r.content, AccountPersonalShow_pb2.AccountPersonalShowInfo)))
            return data
        return None
    except Exception as e:
        print(f"Fetch error: {e}")
        return None

# ==================== ROUTES ====================
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "success": True,
        "message": "Free Fire Player Lookup",
        "endpoints": {
            "/info": "Get player info by UID",
            "/lookup": "Lookup by JWT Token"
        },
        "owner": "@vaibhavff570",
        "join": ["@vaibhavapix", "@vaibhavapisx"]
    })

@app.route("/info", methods=["GET"])
def info():
    uid = request.args.get("id") or request.args.get("uid")
    region = (request.args.get("region") or "SG").upper()
    
    if not uid:
        return jsonify({"error": "Please provide UID."}), 400
    
    # Generate token
    token = generate_token(region)
    if not token:
        return jsonify({"error": "Failed to generate token."}), 500
    
    # Fetch player
    data = fetch_player(uid, token)
    if not data:
        return jsonify({"error": "Player not found."}), 404
    
    return json.dumps(data, indent=2, ensure_ascii=False), 200, {'Content-Type': 'application/json; charset=utf-8'}

@app.route("/lookup", methods=["GET"])
def lookup():
    jwt_token = request.args.get("jwt") or request.args.get("token")
    
    if not jwt_token:
        return jsonify({"error": "Please provide JWT token."}), 400
    
    # Decode JWT untuk dapet UID
    import base64
    try:
        parts = jwt_token.split('.')
        if len(parts) >= 2:
            p = parts[1]
            p += '=' * (4 - len(p) % 4) if len(p) % 4 else ''
            jwt_data = json.loads(base64.b64decode(p))
            uid = jwt_data.get("account_id")
            
            if uid:
                data = fetch_player(str(uid), jwt_token)
                if data:
                    return json.dumps(data, indent=2, ensure_ascii=False), 200, {'Content-Type': 'application/json; charset=utf-8'}
    except:
        pass
    
    return jsonify({"error": "Invalid token or player not found."}), 404

# ==================== MAIN ====================
if __name__ == "__main__":
    print("🔥 Free Fire API - Our Version")
    print("Owner: @vaibhavff570")
    app.run(host="0.0.0.0", port=5000)
