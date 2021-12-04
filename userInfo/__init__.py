from flask import Flask

app = Flask(__name__)

from userInfo import getUserInfo,updateUserInfo,uploadPicture,verificationDoc