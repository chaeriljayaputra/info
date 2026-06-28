# info.py - DEBUG VERSION (Cek error satu-satu)
from flask import Flask, request, jsonify
import traceback
import os

os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"success": True, "message": "OK"})

@app.route("/info", methods=["GET"])
def info():
    try:
        uid = request.args.get("id") or request.args.get("uid")
        region = request.args.get("region", "SG")
        
        if not uid:
            return jsonify({"success": False, "error": "Missing id"}), 400
        
        # Test import satu-satu
        errors = []
        
        # Test 1: requests
        try:
            import requests
            errors.append("1.requests: OK")
        except Exception as e:
            errors.append(f"1.requests: FAIL - {str(e)}")
        
        # Test 2: json
        try:
            import json
            errors.append("2.json: OK")
        except Exception as e:
            errors.append(f"2.json: FAIL - {str(e)}")
        
        # Test 3: base64
        try:
            import base64
            errors.append("3.base64: OK")
        except Exception as e:
            errors.append(f"3.base64: FAIL - {str(e)}")
        
        # Test 4: Crypto
        try:
            from Crypto.Cipher import AES
            errors.append("4.Crypto: OK")
        except Exception as e:
            errors.append(f"4.Crypto: FAIL - {str(e)}")
        
        # Test 5: protobuf
        try:
            from google.protobuf import descriptor_pool
            from google.protobuf import runtime_version
            from google.protobuf.internal import builder
            from google.protobuf.json_format import MessageToJson, ParseDict
            errors.append("5.protobuf: OK")
        except Exception as e:
            errors.append(f"5.protobuf: FAIL - {str(e)}")
        
        # Test 6: Build proto
        try:
            from google.protobuf import descriptor_pool as _descriptor_pool
            from google.protobuf import runtime_version as _runtime_version
            from google.protobuf.internal import builder as _builder
            
            _runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 6, 30, 0, '', 'FreeFire.proto')
            DESC = _descriptor_pool.Default().AddSerializedFile(b'\n\x0e\x46reeFire.proto\"c\n\x08LoginReq\x12\x0f\n\x07open_id\x18\x16 \x01(\t\x12\x14\n\x0copen_id_type\x18\x17 \x01(\t\x12\x13\n\x0blogin_token\x18\x1d \x01(\t\x12\x1b\n\x13orign_platform_type\x18\x63 \x01(\t\"\xa0\x03\n\x08LoginRes\x12\x12\n\naccount_id\x18\x01 \x01(\x04\x12\x13\n\x0block_region\x18\x02 \x01(\t\x12\x13\n\x0bnoti_region\x18\x03 \x01(\t\x12\r\n\x05token\x18\x08 \x01(\t\x12\x12\n\nserver_url\x18\n \x01(\t\x12\x16\n\x0e\x65mulator_score\x18\x0b \x01(\r\x62\x06proto3')
            _g = {}
            _builder.BuildMessageAndEnumDescriptors(DESC, _g)
            errors.append("6.proto_build: OK")
        except Exception as e:
            errors.append(f"6.proto_build: FAIL - {str(e)}")
        
        # Test 7: requests POST
        try:
            import requests
            r = requests.get("https://httpbin.org/get", timeout=10)
            errors.append(f"7.requests_get: OK (status={r.status_code})")
        except Exception as e:
            errors.append(f"7.requests_get: FAIL - {str(e)}")
        
        return jsonify({
            "success": True,
            "uid": uid,
            "region": region,
            "debug": errors,
            "python_version": os.sys.version
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
