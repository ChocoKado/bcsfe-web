"""
Flask Backend for BCSFE (Battle Cats Save File Editor Web)
"""

import io
import os
from flask import Flask, jsonify, request, send_file, send_from_directory
from bcsfe_service import service

app = Flask(__name__, static_folder="static", static_url_path="")
app.config["MAX_CONTENT_LENGTH"] = 32 * 1024 * 1024  # 32MB max upload


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/api/status", methods=["GET"])
def get_status():
    try:
        status = service.get_status()
        return jsonify({"success": True, "data": status})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/save/new_test", methods=["POST"])
def create_test_save():
    try:
        data = request.get_json() or {}
        cc = data.get("cc", "tw")
        gv = data.get("gv", "14.2.0")
        status = service.create_test_save(cc_str=cc, gv_str=gv)
        return jsonify({"success": True, "message": "測試存檔建立成功！", "data": status})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/save/upload", methods=["POST"])
def upload_save():
    try:
        if "file" not in request.files:
            return jsonify({"success": False, "error": "未提供存檔檔案"}), 400
        file = request.files["file"]
        if not file.filename:
            return jsonify({"success": False, "error": "檔名不可為空"}), 400

        content = file.read()
        cc_str = request.form.get("cc")
        status = service.load_from_bytes(content, cc_str=cc_str)
        return jsonify({"success": True, "message": "存檔載入成功！", "data": status})
    except Exception as e:
        return jsonify({"success": False, "error": f"載入失敗: {str(e)}"}), 500


@app.route("/api/save/download_transfer", methods=["POST"])
def download_transfer():
    try:
        data = request.get_json() or {}
        transfer_code = data.get("transfer_code", "").strip()
        confirmation_code = data.get("confirmation_code", "").strip()
        cc = data.get("cc", "tw").strip()
        gv = data.get("gv", "14.2.0").strip()

        if not transfer_code or not confirmation_code:
            return jsonify({"success": False, "error": "請輸入引繼碼與認證碼"}), 400

        status = service.download_from_server(
            transfer_code=transfer_code,
            confirmation_code=confirmation_code,
            cc_str=cc,
            gv_str=gv,
        )
        return jsonify({"success": True, "message": "伺服器存檔下載成功！", "data": status})
    except Exception as e:
        return jsonify({"success": False, "error": f"下載失敗: {str(e)}"}), 500


@app.route("/api/save/upload_transfer", methods=["POST"])
def upload_transfer():
    try:
        data = request.get_json(silent=True) or {}
        codes = service.upload_to_server(data)
        return jsonify({
            "success": True,
            "message": "存檔已成功上傳至官方伺服器！",
            "data": codes,
        })
    except Exception as e:
        return jsonify({"success": False, "error": f"上傳失敗: {str(e)}"}), 500


@app.route("/api/save/export", methods=["GET", "POST"])
def export_save():
    try:
        save_data_b64 = None
        if request.method == "POST":
            data = request.get_json(silent=True) or {}
            save_data_b64 = data.get("save_data")
        content = service.export_bytes(save_data_b64=save_data_b64)
        return send_file(
            io.BytesIO(content),
            mimetype="application/octet-stream",
            as_attachment=True,
            download_name="SAVE_DATA",
        )
    except Exception as e:
        return jsonify({"success": False, "error": f"匯出失敗: {str(e)}"}), 500


@app.route("/api/edit/currencies", methods=["POST"])
def edit_currencies():
    try:
        data = request.get_json() or {}
        status = service.edit_currencies(data)
        return jsonify({"success": True, "message": "貨幣與基礎道具已更新！", "data": status})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/edit/battle_items", methods=["POST"])
def edit_battle_items():
    try:
        data = request.get_json() or {}
        status = service.edit_battle_items(data)
        return jsonify({"success": True, "message": "戰鬥道具已更新！", "data": status})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/edit/catfruit", methods=["POST"])
def edit_catfruit():
    try:
        data = request.get_json() or {}
        status = service.edit_catfruit(data)
        return jsonify({"success": True, "message": "貓薄荷已更新！", "data": status})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/edit/catseyes", methods=["POST"])
def edit_catseyes():
    try:
        data = request.get_json() or {}
        status = service.edit_catseyes(data)
        return jsonify({"success": True, "message": "貓目石已更新！", "data": status})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/edit/catamins", methods=["POST"])
def edit_catamins():
    try:
        data = request.get_json() or {}
        status = service.edit_catamins(data)
        return jsonify({"success": True, "message": "喵力達已更新！", "data": status})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/edit/cats", methods=["POST"])
def edit_cats():
    try:
        data = request.get_json() or {}
        status = service.edit_cats(data)
        return jsonify({"success": True, "message": "貓咪角色與本能已更新！", "data": status})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/edit/stages", methods=["POST"])
def edit_stages():
    try:
        data = request.get_json() or {}
        status = service.edit_stages(data)
        return jsonify({"success": True, "message": "關卡與寶物進度已更新！", "data": status})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/edit/gamatoto_base", methods=["POST"])
def edit_gamatoto_base():
    try:
        data = request.get_json() or {}
        status = service.edit_gamatoto_and_base(data)
        return jsonify({"success": True, "message": "加碼多多與奧托托基地已更新！", "data": status})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/edit/fixes_extras", methods=["POST"])
def edit_fixes_extras():
    try:
        data = request.get_json() or {}
        status = service.edit_fixes_and_extras(data)
        return jsonify({"success": True, "message": "修復與特殊項目已更新！", "data": status})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/edit/one_click", methods=["POST"])
def edit_one_click():
    try:
        data = request.get_json() or {}
        safe_mode = data.get("safe_mode", True)
        status = service.apply_one_click(safe_mode=safe_mode, data=data)
        mode_text = "安全模式" if safe_mode else "極致畢業模式"
        return jsonify({"success": True, "message": f"一鍵全滿成功 ({mode_text})！", "data": status})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
