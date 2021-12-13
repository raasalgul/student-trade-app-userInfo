from flask import Flask

from flask_cors import CORS

application = Flask(__name__)
CORS(application)

from userInfo import getUserInfo,updateUserInfo,uploadPicture,verificationDoc