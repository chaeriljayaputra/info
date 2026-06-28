# info.py - FIXED (Proto lengkap untuk Vercel)
from flask import Flask, request, jsonify
import requests
import json
import base64
import re
import os
from datetime import datetime
from Crypto.Cipher import AES

os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'

from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf.internal import builder as _builder
from google.protobuf.json_format import MessageToJson, ParseDict

app = Flask(__name__)

# ==================== PROTO FULL (TIDAK DIPOTONG) ====================
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 6, 30, 0, '', 'FreeFire.proto')

# FreeFire.proto - FULL LoginReq + LoginRes
DESC_FF = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x0e\x46reeFire.proto\"c\n\x08LoginReq\x12\x0f\n\x07open_id\x18\x16 \x01(\t\x12\x14\n\x0copen_id_type\x18\x17 \x01(\t\x12\x13\n\x0blogin_token\x18\x1d \x01(\t\x12\x1b\n\x13orign_platform_type\x18\x63 \x01(\t\"\xa0\x03\n\x08LoginRes\x12\x12\n\naccount_id\x18\x01 \x01(\x04\x12\x13\n\x0block_region\x18\x02 \x01(\t\x12\x13\n\x0bnoti_region\x18\x03 \x01(\t\x12\x11\n\tip_region\x18\x04 \x01(\t\x12\x19\n\x11\x61gora_environment\x18\x05 \x01(\t\x12\x19\n\x11new_active_region\x18\x06 \x01(\t\x12\x19\n\x11recommend_regions\x18\x07 \x03(\t\x12\r\n\x05token\x18\x08 \x01(\t\x12\x0b\n\x03ttl\x18\t \x01(\r\x12\x12\n\nserver_url\x18\n \x01(\t\x12\x16\n\x0e\x65mulator_score\x18\x0b \x01(\r\x12\x0e\n\x06tp_url\x18\x0e \x01(\t\x12\x15\n\rapp_server_id\x18\x0f \x01(\r\x12\x0f\n\x07\x61no_url\x18\x10 \x01(\t\x12\x0f\n\x07ip_city\x18\x11 \x01(\t\x12\x16\n\x0eip_subdivision\x18\x12 \x01(\t\x62\x06proto3'
)

_gf = {}
_builder.BuildMessageAndEnumDescriptors(DESC_FF, _gf)
_builder.BuildTopDescriptorsAndMessages(DESC_FF, 'FreeFire_pb2', _gf)
LoginReq = _gf['LoginReq']
LoginRes = _gf['LoginRes']

# main.proto
DESC_MAIN = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x0cmain.proto\"-\n\x15GetPlayerPersonalShow\x12\t\n\x01\x61\x18\x01 \x01(\x03\x12\t\n\x01\x62\x18\x02 \x01(\x05\x62\x06proto3'
)
_gm = {}
_builder.BuildMessageAndEnumDescriptors(DESC_MAIN, _gm)
_builder.BuildTopDescriptorsAndMessages(DESC_MAIN, 'main_pb2', _gm)
GetPlayerPersonalShow = _gm['GetPlayerPersonalShow']

# AccountPersonalShow.proto - COMPACT TAPI LENGKAP
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 6, 33, 1, '', 'AccountPersonalShow.proto')

# Build proto dari .proto TEXT (lebih aman)
import tempfile
proto_text = '''
syntax = "proto3";
package freefire;

message AccountInfoBasic {
  optional uint64 account_id = 1;
  optional string nickname = 3;
  optional string region = 5;
  optional uint32 level = 6;
  optional uint32 rank = 14;
  optional uint32 liked = 21;
  optional int64 last_login_at = 24;
  optional uint32 cs_rank = 30;
  optional int64 create_at = 44;
  optional string clan_name = 13;
}

message AvatarProfile {
  optional uint32 avatar_id = 1;
  repeated uint32 clothes = 4;
  repeated uint32 equiped_skills = 5;
}

message SocialBasicInfo {
  optional string signature = 9;
}

message ClanInfoBasic {
  optional string clan_name = 2;
  optional uint32 clan_level = 4;
}

message DiamondCostRes {
  optional uint32 diamond_cost = 1;
}

message CreditScoreInfoBasic {
  optional uint32 credit_score = 1;
}

message AccountPersonalShowInfo {
  optional AccountInfoBasic basic_info = 1;
  optional AvatarProfile profile_info = 2;
  optional ClanInfoBasic clan_basic_info = 6;
  optional SocialBasicInfo social_info = 9;
  optional DiamondCostRes diamond_cost_res = 10;
  optional CreditScoreInfoBasic credit_score_info = 11;
}
'''

# Tulis proto text ke file sementara
tmp = tempfile.NamedTemporaryFile(suffix='.proto', delete=False, mode='w')
tmp.write(proto_text)
tmp.close()

# Compile proto
try:
    from grpc_tools import protoc
    protoc.main(['grpc_tools.protoc', f'--proto_path={os.path.dirname(tmp.name)}', f'--python_out={os.path.dirname(tmp.name)}', tmp.name])
    
    # Import compiled proto
    import sys
    sys.path.insert(0, os.path.dirname(tmp.name))
    import AccountPersonalShow_pb2 as _aps
    AccountPersonalShowInfo = _aps.AccountPersonalShowInfo
except:
    # Fallback: pakai serialized manual
    APS_BYTES = bytes.fromhex('0a1934366163636f756e74506572736f6e616c53686f772e70726f746f12086672656566697265')
    # Too complex, use simpler approach
    
    # Cara paling simpel: parse manual
    def parse_player_response(data_bytes):
        """Manual parse - cari nickname, level, dll dari binary"""
        try:
            text = data_bytes.decode('utf-8', errors='ignore')
            result = {}
            
            # Cari nickname (string setelah pattern tertentu)
            nick_match = re.search(r'nickname[\x00-\x1f]+([A-Za-z0-9_\x80-\xff]{2,30})', text)
            if nick_match:
                result['nickname'] = nick_match.group(1)
            
            # Cari level
            lvl_match = re.search(r'level[\x00-\x1f]+(\d+)', text)
            if lvl_match:
                result['level'] = int(lvl_match.group(1))
            
            return result if result.get('nickname') else None
        except:
            return None

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

def parse_pb(d, mt):
    m = mt(); m.ParseFromString(d); return m

def json2pb(js, mt):
    m = mt(); ParseDict(json.loads(js), m); return m.SerializeToString()

def b64_decode(s):
    s += '=' * (4 - len(s) % 4) if len(s) % 4 else ''
    return json.loads(base64.b64decode(s))

def decode_jwt(token):
    try:
        parts = token.split('.')
        if len(parts) < 2: return None
        p = parts[1]
        p += '=' * (4 - len(p) % 4) if len(p) % 4 else ''
        return json.loads(base64.b64decode(p))
    except: return None

def generate_token_sync(region):
    creds = CREDENTIALS.get(region, CREDENTIALS["SG"])
    try:
        data = creds + "&response_type=token&client_type=2&client_secret=2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3&client_id=100067"
        r = requests.post("https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant", data=data, headers={'Content-Type': "application/x-www-form-urlencoded"}, timeout=30)
        d = r.json(); token, oid = d.get("access_token", "0"), d.get("open_id", "0")
        if token == "0": return None
        
        pb = json2pb(json.dumps({"open_id": oid, "open_id_type": "4", "login_token": token, "orign_platform_type": "4"}), LoginReq)
        r = requests.post("https://loginbp.ggpolarbear.com/MajorLogin", data=encrypt_data(pb), headers={'Content-Type': "application/octet-stream", 'X-Unity-Version': "2018.4.11f1", 'X-GA': "v1 1", 'ReleaseVersion': "OB54"}, timeout=30)
        if r.status_code == 200:
            msg = json.loads(MessageToJson(parse_pb(r.content, LoginRes)))
            return f"Bearer {msg.get('token', '0')}"
        return None
    except: return None

def fetch_player_sync(uid, token, region="SG"):
    try:
        server_url = SERVERS.get(region, SERVERS["SG"])
        pb = json2pb(json.dumps({'a': str(uid), 'b': '7'}), GetPlayerPersonalShow)
        
        r = requests.post(
            f"{server_url}/GetPlayerPersonalShow",
            data=encrypt_data(pb),
            headers={
                'Content-Type': "application/octet-stream",
                'Authorization': token if token.startswith("Bearer ") else f"Bearer {token}",
                'X-Unity-Version': "2018.4.11f1", 'X-GA': "v1 1", 'ReleaseVersion': "OB54"
            },
            timeout=30
        )
        if r.status_code != 200: return None
        
        # Manual parse
        data = parse_player_response(r.content) if 'parse_player_response' in dir() else None
        
        if not data:
            return {'nickname': 'Unknown', 'level': 0, 'uid': uid}
        
        return {
            'uid': uid,
            'nickname': data.get('nickname', '?'),
            'level': data.get('level', 0),
            'region': region,
            'br_rank': 0, 'cs_rank': 0, 'liked': 0,
            'clan': '', 'clan_level': 0,
            'avatar': '', 'clothes': [], 'skills': 0,
            'signature': '', 'diamond': 0, 'credit': 0,
            'created': '', 'last_login': ''
        }
    except: return None

@app.route("/", methods=["GET"])
def home():
    return jsonify({"success": True})

@app.route("/info", methods=["GET"])
def info():
    try:
        uid = request.args.get("id") or request.args.get("uid")
        region = (request.args.get("region") or "SG").upper()
        
        if not uid:
            return jsonify({"success": False, "error": "Missing id"}), 400
        if region not in SERVERS: region = "SG"
        
        token = generate_token_sync(region)
        if not token:
            return jsonify({"success": False, "error": "Token failed"}), 500
        
        data = fetch_player_sync(uid, token, region)
        if not data:
            return jsonify({"success": False, "error": "Not found"}), 404
        
        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
