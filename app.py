# info.py - VERCEL READY (Sync, Flask, All Endpoints)
from flask import Flask, request, jsonify
import requests
import json
import base64
import re
from datetime import datetime
from Crypto.Cipher import AES
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf.internal import builder as _builder
from google.protobuf.json_format import MessageToJson, ParseDict
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

# ==================== EMBED PROTOBUF ====================
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 6, 30, 0, '', 'FreeFire.proto')
DESC_FF = _descriptor_pool.Default().AddSerializedFile(b'\n\x0e\x46reeFire.proto\"c\n\x08LoginReq\x12\x0f\n\x07open_id\x18\x16 \x01(\t\x12\x14\n\x0copen_id_type\x18\x17 \x01(\t\x12\x13\n\x0blogin_token\x18\x1d \x01(\t\x12\x1b\n\x13orign_platform_type\x18\x63 \x01(\t\"]\n\x10\x42lacklistInfoRes\x12\x1e\n\nban_reason\x18\x01 \x01(\x0e\x32\n.BanReason\x12\x17\n\x0f\x65xpire_duration\x18\x02 \x01(\r\x12\x10\n\x08\x62\x61n_time\x18\x03 \x01(\r\"f\n\x0eLoginQueueInfo\x12\r\n\x05\x61llow\x18\x01 \x01(\x08\x12\x16\n\x0equeue_position\x18\x02 \x01(\r\x12\x16\n\x0eneed_wait_secs\x18\x03 \x01(\r\x12\x15\n\rqueue_is_full\x18\x04 \x01(\x08\"\xa0\x03\n\x08LoginRes\x12\x12\n\naccount_id\x18\x01 \x01(\x04\x12\x13\n\x0block_region\x18\x02 \x01(\t\x12\x13\n\x0bnoti_region\x18\x03 \x01(\t\x12\x11\n\tip_region\x18\x04 \x01(\t\x12\x19\n\x11\x61gora_environment\x18\x05 \x01(\t\x12\x19\n\x11new_active_region\x18\x06 \x01(\t\x12\x19\n\x11recommend_regions\x18\x07 \x03(\t\x12\r\n\x05token\x18\x08 \x01(\t\x12\x0b\n\x03ttl\x18\t \x01(\r\x12\x12\n\nserver_url\x18\n \x01(\t\x12\x16\n\x0e\x65mulator_score\x18\x0b \x01(\r\x12$\n\tblacklist\x18\x0c \x01(\x0b\x32\x11.BlacklistInfoRes\x12#\n\nqueue_info\x18\r \x01(\x0b\x32\x0f.LoginQueueInfo\x12\x0e\n\x06tp_url\x18\x0e \x01(\t\x12\x15\n\rapp_server_id\x18\x0f \x01(\r\x12\x0f\n\x07\x61no_url\x18\x10 \x01(\t\x12\x0f\n\x07ip_city\x18\x11 \x01(\t\x12\x16\n\x0eip_subdivision\x18\x12 \x01(\t*\xa8\x01\n\tBanReason\x12\x16\n\x12\x42\x41N_REASON_UNKNOWN\x10\x00\x12\x1b\n\x17\x42\x41N_REASON_IN_GAME_AUTO\x10\x01\x12\x15\n\x11\x42\x41N_REASON_REFUND\x10\x02\x12\x15\n\x11\x42\x41N_REASON_OTHERS\x10\x03\x12\x16\n\x12\x42\x41N_REASON_SKINMOD\x10\x04\x12 \n\x1b\x42\x41N_REASON_IN_GAME_AUTO_NEW\x10\xf6\x07\x62\x06proto3')
_gf = {}
_builder.BuildMessageAndEnumDescriptors(DESC_FF, _gf)
_builder.BuildTopDescriptorsAndMessages(DESC_FF, 'FreeFire_pb2', _gf)
LoginReq = _gf['LoginReq']
LoginRes = _gf['LoginRes']

MAIN_DESC = _descriptor_pool.Default().AddSerializedFile(b'\n\x0csample.proto\"*\n\x12SearchWorkshopCode\x12\t\n\x01\x61\x18\x01 \x01(\t\x12\t\n\x01\x62\x18\x02 \x01(\x05\"-\n\x15GetPlayerPersonalShow\x12\t\n\x01\x61\x18\x01 \x01(\x03\x12\t\n\x01\x62\x18\x02 \x01(\x05\x62\x06proto3')
_gm = {}
_builder.BuildMessageAndEnumDescriptors(MAIN_DESC, _gm)
_builder.BuildTopDescriptorsAndMessages(MAIN_DESC, 'main_pb2', _gm)
GetPlayerPersonalShow = _gm['GetPlayerPersonalShow']

_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 6, 33, 1, '', 'AccountPersonalShow.proto')
APS_DESC = _descriptor_pool.Default().AddSerializedFile(b'\n\x19\x41\x63\x63ountPersonalShow.proto\x12\x08\x66reefire\"\xac\x17\n\x10\x41\x63\x63ountInfoBasic\x12\x17\n\naccount_id\x18\x01 \x01(\x04H\x00\x88\x01\x01\x12\x15\n\x08nickname\x18\x03 \x01(\tH\x02\x88\x01\x01\x12\x13\n\x06region\x18\x05 \x01(\tH\x04\x88\x01\x01\x12\x12\n\x05level\x18\x06 \x01(\rH\x05\x88\x01\x01\x12\x11\n\x04rank\x18\x0e \x01(\rH\r\x88\x01\x01\x12\x12\n\x05liked\x18\x15 \x01(\rH\x14\x88\x01\x01\x12\x1a\n\rlast_login_at\x18\x18 \x01(\x03H\x17\x88\x01\x01\x12\x14\n\x07\x63s_rank\x18\x1e \x01(\rH\x1d\x88\x01\x01\x12\x16\n\tcreate_at\x18, \x01(\x03H*\x88\x01\x01\x12\x16\n\tclan_name\x18\r \x01(\tH\x0c\x88\x01\x01\"\x98\x05\n\rAvatarProfile\x12\x16\n\tavatar_id\x18\x01 \x01(\rH\x00\x88\x01\x01\x12\x0f\n\x07\x63lothes\x18\x04 \x03(\r\x12\x16\n\x0e\x65quiped_skills\x18\x05 \x03(\r\"\xd5\x05\n\x0fSocialBasicInfo\x12\x16\n\tsignature\x18\t \x01(\tH\x06\x88\x01\x01\"\x9d\x02\n\rClanInfoBasic\x12\x16\n\tclan_name\x18\x02 \x01(\tH\x01\x88\x01\x01\x12\x17\n\nclan_level\x18\x04 \x01(\rH\x03\x88\x01\x01\"<\n\x0e\x44iamondCostRes\x12\x19\n\x0c\x64iamond_cost\x18\x01 \x01(\rH\x00\x88\x01\x01\"\xfd\x03\n\x14\x43reditScoreInfoBasic\x12\x19\n\x0c\x63redit_score\x18\x01 \x01(\rH\x00\x88\x01\x01\"\xfa\x06\n\x17\x41\x63\x63ountPersonalShowInfo\x12\x33\n\nbasic_info\x18\x01 \x01(\x0b\x32\x1a.freefire.AccountInfoBasicH\x00\x88\x01\x01\x12\x32\n\x0cprofile_info\x18\x02 \x01(\x0b\x32\x17.freefire.AvatarProfileH\x01\x88\x01\x01\x12\x35\n\x0f\x63lan_basic_info\x18\x06 \x01(\x0b\x32\x17.freefire.ClanInfoBasicH\x03\x88\x01\x01\x12\x33\n\x0bsocial_info\x18\t \x01(\x0b\x32\x19.freefire.SocialBasicInfoH\x06\x88\x01\x01\x12\x37\n\x10\x64iamond_cost_res\x18\n \x01(\x0b\x32\x18.freefire.DiamondCostResH\x07\x88\x01\x01\x12>\n\x11\x63redit_score_info\x18\x0b \x01(\x0b\x32\x1e.freefire.CreditScoreInfoBasicH\x08\x88\x01\x01\x62\x06proto3')
_ga = {}
_builder.BuildMessageAndEnumDescriptors(APS_DESC, _ga)
_builder.BuildTopDescriptorsAndMessages(APS_DESC, 'AccountPersonalShow_pb2', _ga)
AccountPersonalShowInfo = _ga['AccountPersonalShowInfo']

# ==================== CONFIG ====================
CREDENTIALS = {
    "SG": "uid=5374557838&password=ANONFK345213AKU",
    "ID": "uid=5374558199&password=ANONFK54734ULRW",
}
SERVERS = {"SG": "https://clientbp.ggpolarbear.com", "ID": "https://clientbp.ggpolarbear.com"}
G = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
F = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
BOT_TOKEN = "8965307683:AAGXwuIge4QKuYXtrkXhG4AahxDrynqi7SY"
OWNER_ID = 8660700322

# ==================== HELPERS (SYNC) ====================
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

# ==================== TOKEN GENERATOR (SYNC) ====================
def generate_token_sync(region):
    creds = CREDENTIALS.get(region, CREDENTIALS["SG"])
    try:
        data = creds + "&response_type=token&client_type=2&client_secret=2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3&client_id=100067"
        r = requests.post("https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant", data=data, headers={'Content-Type': "application/x-www-form-urlencoded"}, timeout=30, verify=False)
        d = r.json(); token, oid = d.get("access_token", "0"), d.get("open_id", "0")
        if token == "0": return None
        
        pb = json2pb(json.dumps({"open_id": oid, "open_id_type": "4", "login_token": token, "orign_platform_type": "4"}), LoginReq)
        r = requests.post("https://loginbp.ggpolarbear.com/MajorLogin", data=encrypt_data(pb), headers={'Content-Type': "application/octet-stream", 'X-Unity-Version': "2018.4.11f1", 'X-GA': "v1 1", 'ReleaseVersion': "OB54"}, timeout=30, verify=False)
        if r.status_code == 200:
            msg = json.loads(MessageToJson(parse_pb(r.content, LoginRes)))
            return f"Bearer {msg.get('token', '0')}"
        return None
    except: return None

# ==================== PLAYER FETCH (SYNC) ====================
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
            timeout=30, verify=False
        )
        if r.status_code != 200: return None
        
        data = json.loads(MessageToJson(parse_pb(r.content, AccountPersonalShowInfo)))
        basic = data.get('basicInfo', {})
        if not basic.get('nickname'): return None
        
        profile = data.get('profileInfo', {}); social = data.get('socialInfo', {}); clan = data.get('clanBasicInfo', {})
        return {
            'uid': uid, 'nickname': basic.get('nickname', '?'), 'level': basic.get('level', 0),
            'region': basic.get('region', region), 'br_rank': basic.get('rank', 0),
            'cs_rank': basic.get('csRank', 0), 'liked': basic.get('liked', 0),
            'clan': clan.get('clanName', ''), 'clan_level': clan.get('clanLevel', 0),
            'avatar': profile.get('avatarId', ''), 'clothes': profile.get('clothes', []),
            'skills': len(profile.get('equipedSkills', [])), 'signature': social.get('signature', ''),
            'diamond': data.get('diamondCostRes', {}).get('diamondCost', 0),
            'credit': data.get('creditScoreInfo', {}).get('creditScore', 100),
            'created': basic.get('createAt', ''), 'last_login': basic.get('lastLoginAt', ''),
        }
    except: return None

# ==================== TELEGRAM ====================
def send_to_telegram(uid, text):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        r = requests.post(url, data={'chat_id': OWNER_ID, 'text': text[:4000]}, timeout=10)
        return r.status_code == 200
    except: return False

# ==================== ROUTES ====================
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "success": True,
        "message": "Free Fire Player Lookup API",
        "endpoints": {
            "/info": "Get player info by UID",
            "/lookup": "Lookup by JWT Token",
        }
    })

@app.route("/info", methods=["GET"])
def info():
    uid = request.args.get("id") or request.args.get("uid")
    region = (request.args.get("region") or "SG").upper()
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    
    if not uid:
        return jsonify({"success": False, "error": "Missing id parameter", "usage": "/info?id=290012951&region=SG"}), 400
    
    if region not in SERVERS: region = "SG"
    
    token = generate_token_sync(region)
    if not token:
        return jsonify({"success": False, "error": "Failed to generate token"}), 500
    
    data = fetch_player_sync(uid, token, region)
    if not data:
        return jsonify({"success": False, "error": "Player not found"}), 404
    
    # Format output
    sig = re.sub(r'\[.*?\]', '', data.get('signature', ''))[:80]
    created = datetime.fromtimestamp(int(data['created'])).strftime('%d/%m/%Y') if data.get('created') else '?'
    last = datetime.fromtimestamp(int(data['last_login'])).strftime('%d/%m/%Y %H:%M') if data.get('last_login') else '?'
    
    # Kirim ke Telegram
    telegram_text = f"""🔥 FREE FIRE PLAYER INFO 🔥

👤 Name       : {data['nickname']}
🆔 Account ID : {data['uid']}
📊 Level      : {data['level']}
🏆 BR Rank    : {data['br_rank']} pts
⭐ CS Rank    : {data['cs_rank']} pts
👍 Liked      : {data['liked']}
💎 Diamond    : {data['diamond']}
⭐ Credit     : {data['credit']}
🌍 Region     : {data['region']}
{f"🏠 Clan       : {data['clan']} (Lv.{data['clan_level']})" if data['clan'] else ""}
💬 Signature  : {sig}...
🎒 Avatar     : {data['avatar']}
👕 Clothes    : {len(data['clothes'])} items
⚔️ Skills     : {data['skills']} slots
📅 Created    : {created}
🔐 Last Login : {last}

📞 IP   : {client_ip}
⏰ Time : {datetime.now().strftime('%H:%M:%S %d/%m/%Y')}
💡 @dindingijo"""
    
    send_to_telegram(uid, telegram_text)
    
    return jsonify({
        "success": True,
        "data": data,
        "created": created,
        "last_login": last,
        "ip": client_ip
    })

@app.route("/lookup", methods=["GET"])
def lookup():
    jwt_token = request.args.get("jwt")
    region = (request.args.get("region") or "SG").upper()
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    
    if not jwt_token:
        return jsonify({"success": False, "error": "Missing jwt parameter"}), 400
    
    jwt_data = decode_jwt(jwt_token)
    if not jwt_data:
        return jsonify({"success": False, "error": "Invalid JWT"}), 400
    
    uid = jwt_data.get("account_id")
    if not uid:
        return jsonify({"success": False, "error": "No account_id in JWT"}), 400
    
    if region not in SERVERS: region = "SG"
    
    data = fetch_player_sync(str(uid), jwt_token, region)
    if not data:
        return jsonify({"success": False, "error": "Player not found"}), 404
    
    return jsonify({"success": True, "data": data, "ip": client_ip})

# ============ MAIN ============
if __name__ == "__main__":
    print("🚀 Free Fire API - Vercel Ready")
    app.run(host="0.0.0.0", port=5000)
