from flask import Flask

application = Flask(__name__)

from userInfo import getUserInfo,updateUserInfo,uploadPicture,verificationDoc