from datetime import datetime, timedelta
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_PKCS1_v1_5
from base64 import b64encode, b64decode
import jwt
import bcrypt
import os


# JWT 토큰
class JsonToken():
    """
        JWT 토큰 생성 및 토큰 디코드 지원
    """
    access_timeout = 10     # access token 유효기간, 분단위
    refresh_timeout = 1     # refresh token 유효기간, 일단위
    JWT_KEY = ''            # acceess token 키
    JWT_REFRESH_KEY = ''    # refresh token 키
    require_parameter = [   # 토큰에 사용되는 변수 리스트
    ]

    @classmethod
    def encode_token(cls, data: dict) -> dict:
        """
            입력받은 data를 바탕으로 JWT 토큰 생성\n
            ACCESS, REFRESH TOKEN을 리턴\n
            \n
            data : 사용할 유저정보
        """
        now_time = datetime.utcnow()
        parameters = {}
        for _key in cls.require_parameter:
            parameters[_key] = data[_key]

        access_encoded = jwt.encode(
            dict({
                'category': 'access',
                'exp': now_time + timedelta(minutes=cls.access_timeout)
            }, **parameters),
            cls.JWT_KEY,
            algorithm='HS256')

        refresh_encode = jwt.encode(
            dict({
                'category': 'refresh',
                'exp': now_time + timedelta(days=cls.refresh_timeout)
            }, **parameters),
            cls.JWT_REFRESH_KEY,
            algorithm='HS256')

        return {
            'access': access_encoded,
            'refresh': refresh_encode
        }

    @classmethod
    def decode_token(cls, token: str, is_access: bool = True) -> dict:
        """
            입력받은 토큰을 디코드\n
            token : 토큰 문자열\n
            is_access : access token 여부 체크 (default -> True)
        """
        key = cls.JWT_KEY if is_access else cls.JWT_REFRESH_KEY
        return jwt.decode(token, key, algorithms='HS256')


# 비밀번호 인코딩
class Bcrypt():
    """
        비밀번호 인코딩 및 비밀번호 검증
    """
    @classmethod
    def encrypt(cls, pwd: str) -> str:
        """
            비밀번호를 입력받아 암호화\n
            pwd : 비밀번호 문자열
        """
        try:
            enc_pwd = pwd.encode('utf-8')
            pwd_crypt = bcrypt.hashpw(enc_pwd, bcrypt.gensalt())
            pwd_crypt = pwd_crypt.decode('utf-8')
            return pwd_crypt
        except Exception:
            return None

    @classmethod
    def verify(cls, pwd: str, target: str) -> bool:
        """
            유요한 비밀번호인지 체크\n
            pwd : 입력된 비밀번호 문자열\n
            target : 인코딩되어 암호화된 비밀번호 문자열\n
            True 리턴 시 비밀번호 맞음, False 시 비밀번호가 맞지 않음
        """
        try:
            return bcrypt.checkpw(pwd.encode('utf-8'), target.encode('utf-8'))
        except Exception:
            return False


# RSA 암호화 모듈
class RSAUtility():
    """
        RSA 암호화 사용을 위한 LIB\n
        private_path : 개인키 경로\n
        public_path : 공개키 경로
    """
    def __init__(self, private_path: str = None, public_path: str = None):
        self.private_path = private_path
        self.public_path = public_path

    def setting_key(self, key_path: str) -> object:
        """
            키 파일 로드
        """
        if not os.path.exists(key_path):
            raise FileNotFoundError('KEY 파일이 존재하지 않습니다.')

        with open(key_path, 'r') as k_file:
            _k = k_file.read()
            k = RSA.importKey(_k)
        return k

    def make_private_key(self, path: str = None) -> None:
        """
            개인키 생성\n
            path : 키를 생성할 경로 설정, path를 입력하지 않는 경우 객체 생성 시 사용한 private key 경로를 사용합니다.
        """
        _path = path if path is not None else self.private_path
        if _path:
            raise ValueError('경로가 입력되지 않았습니다.')

        if os.path.exists(_path):
            raise FileExistsError('경로에 파일이 존재합니다.')

        pr_key = RSA.generate(2048)
        with open(path, 'wb') as f:
            f.write(pr_key.export_key('PEM'))

    def make_public_key(self, private_path: str = None, public_path: str = None, is_make_file: bool = True) -> None:
        """
            개인키를 사용하여 공개키 생성\n
            private_path : 개인키 경로(필수)\n
            public_path : 저장할 공개키 경로\n
            is_make_file : 파일로 저장할지 여부\n
            각 경로가 None인 경우 클래스 생성 시 입력된 path를 따릅니다.
        """
        _private_path = private_path if private_path else self.private_path
        _public_path = public_path if public_path else self.public_path
        if _private_path is None or _public_path is None:
            raise ValueError('키를 생성하기위한 경로가 필요합니다.')

        if os.path.exists(_private_path) is False:
            raise FileNotFoundError('개인키가 존재하지 않습니다.')

        if os.path.exists(_public_path) is True:
            raise FileExistsError('경로에 파일이 존재합니다.')

        with open(_private_path, 'r') as k_file:
            _k = k_file.read()
            public = RSA.importKey(_k).public_key()
        if is_make_file:
            with open(_public_path, 'wb') as k_file:
                k_file.write(public.export_key('PEM'))
        else:
            return public.export_key('PEM')

    def encode(self, txt: str) -> str:
        """
            일반 텍스트를 암호화된 텍스트로 변경\n
            public key는 클래스 생성 시 입력한 경로를 따릅니다.
        """
        keyPub = self.setting_key(self.public_path)
        cipher = Cipher_PKCS1_v1_5.new(keyPub)
        cipher_text = cipher.encrypt(txt.encode())
        emsg = b64encode(cipher_text)
        encryptedText = emsg.decode('utf-8')

        return encryptedText

    def decode(self, en_txt: str) -> str:
        """
            암호화된 텍스트를 일반 텍스트로 변경해줍니다.\n
            private key는 클래스 생성 시 입력한 경로를 따릅니다.
        """
        encoded_msg = b64decode(en_txt)
        pr_key = self.setting_key(self.private_path)
        cipher = Cipher_PKCS1_v1_5.new(pr_key)
        decrypt_text = cipher.decrypt(encoded_msg, None).decode()

        return decrypt_text
