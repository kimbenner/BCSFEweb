from BCSFE_Python_Discord import *
import os
import string
import random
from fastapi import FastAPI, Request, Form

app = FastAPI()

def randomstring():
    characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return "".join(random.choice(characters) for _ in range(10))

@app.get('/')
def index():
    return "<h1>Hello, World!</h1>"

@app.post('/bc_login')
async def login(username: str = Form(...)):
    backupcode = username
    path = f"./bc_saves/{backupcode}/SAVE_DATA"
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
        return {"message": f"복구에 성공하였습니다. 기종변경 코드: {upload_data['transferCode']}, 인증번호: {upload_data['pin']}"}
    except:
        return {"message": "업로드에 실패했습니다. 다시 시도해주세요."}

@app.post('/register')
async def register(transfer_code: str = Form(...), password: str = Form(...), game_version: str = Form(...), country: str = Form(...)):
    backupcode = randomstring()
    os.mkdir(f"./bc_saves/{backupcode}")
    path = f"./bc_saves/{backupcode}/SAVE_DATA"
    helper.set_save_path(path)
    game_version = helper.str_to_gv(game_version)
    save_data = server_handler.download_save(country, transfer_code, password, game_version)
    save_data = patcher.patch_save_data(save_data, country)
    try:
        save_stats = parse_save.start_parse(save_data, country)
    except:
        return {"message": "세이브가 유효하지 않습니다. 코드를 다시 확인하거나 기종변경을 다시 해주세요."}
    if save_stats == 0:
        return {"message": "세이브가 유효하지 않습니다. 코드를 다시 확인하거나 기종변경을 다시 해주세요."}
    else:
        edits.save_management.save.save_save(save_stats)
        save_data = serialise_save.start_serialize(save_stats)
        helper.write_save_data(
            save_data, save_stats["version"], helper.get_save_path(), False
        )
        try:
            upload_data = server_handler.upload_handler(save_stats, helper.get_save_path())
            return {"message": f"성공적으로 계정이 백업되었습니다. 나중에 식별번호로 복구 하실 수 있습니다. 기종변경 코드: {upload_data['transferCode']}, 인증번호: {upload_data['pin']}, 식별번호: {backupcode}"}
        except:
            return {"message": "업로드에 실패했습니다. 다시 시도해주세요."}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8080)
