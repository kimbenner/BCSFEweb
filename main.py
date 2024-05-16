from flask import Flask, render_template, request, redirect, url_for, session
from BCSFE_Python_Discord import *
import os
import string
import random
from threading import Thread


def randomstring():
  characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
  return "".join(random.choice(characters) for _ in range(10))

app = Flask(__name__)
app.secret_key = 'alpha'  # Change this to a secure random key.

@app.route('/')
def index():
  return render_template('bcbackup.html')
  
@app.route('/bc_login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
      backupcode = request.form.get("username")
      path = "./bc_saves/{}/SAVE_DATA".format(backupcode)
      helper.set_save_path(path)
      data = helper.load_save_file(path)
      save_stats = data["save_stats"]
      save_data: bytes = data["save_data"]
      country_code = save_stats["version"]
      save_data = patcher.patch_save_data(save_data, country_code)
      save_stats = parse_save.start_parse(save_data, country_code)
      edits.save_management.save.save_save(save_stats)
      save_data = serialise_save.start_serialize(save_stats)
      helper.write_save_data(
          save_data, save_stats["version"], helper.get_save_path(), False
        )
      try:
        upload_data = server_handler.upload_handler(save_stats, helper.get_save_path())
        return "복구에 성공하였습니다.\n기종변경 코드: {}\n인증번호: {}".format(upload_data["transferCode"], upload_data["pin"])
      except:
        return "업로드에 실패했습니다.\n다시 시도해주세요."
        pass
    else:
      return render_template('bc_login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
      transfer_code = request.form.get("transfer_code")
      confirmation_code = request.form.get("password")
      game_version = request.form.get("game_version")
      country_code = request.form.get("country")
      backupcode = randomstring()
      os.mkdir("./bc_saves/{}".format(backupcode))
      path = "./bc_saves/{}/SAVE_DATA".format(backupcode)
      helper.set_save_path(path)
      game_version = helper.str_to_gv(game_version)
      save_data = server_handler.download_save(country_code, transfer_code, confirmation_code, game_version)
      save_data = patcher.patch_save_data(save_data, country_code)
      try:
        save_stats = parse_save.start_parse(save_data, country_code)
      except:
        return "세이브가 유효하지 않습니다. 코드를 다시 확인하거나 기종변경을 다시 해주세요."
      if save_stats == 0:
        return "세이브가 유효하지 않습니다. 코드를 다시 확인하거나 기종변경을 다시 해주세요."
      else:
        edits.save_management.save.save_save(save_stats)
        save_data = serialise_save.start_serialize(save_stats)
        helper.write_save_data(
					save_data, save_stats["version"], helper.get_save_path(), False
          )
        try:
          upload_data = server_handler.upload_handler(save_stats, helper.get_save_path())
          return "성공적으로 계정이 백업되었습니다.\n나중에 식별번호로 복구 하실 수 있습니다.\n기종변경 코드: {}\n인증번호: {}\n식별번호: {}".format(upload_data["transferCode"], upload_data["pin"], backupcode)
        except:
          return "업로드에 실패했습니다. 다시 시도해주세요."
          pass
    return render_template('bc_register.html')

if __name__ == '__main__':
  def run():
    app.run(host='0.0.0.0', port=8080, debug=False)
  t = Thread(target=run)
  t.start()
  




