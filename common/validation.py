import re


# 자주 사용하는 유효성 검사
class Validation():
    """
        유효성검사를 위한 체크 리스트
        유효성 검사에 실패하면 True,
        유효성 검사에 성공하면 False를 리턴합니다.
    """
    # 숫자형 체크
    @classmethod
    def checkInt(cls, data, _unit=None) -> bool:
        """
            입력된 data가 숫자로 이루어져 있는지 체크합니다.\n
            data : 검사 항목\n
            _unit : 자리수 -> 3인 경우 세자리수인지 체크합니다
        """
        if not data:
            return False

        _rex = r'\d+$' if not _unit else fr'\d{{{_unit}}}$'

        if re.match(_rex, str(data)):
            return False
        return True

    # 일반 정규식 체크
    @classmethod
    def checkRex(cls, data: str, _rex: str) -> bool:
        """
            입력된 data가 특정 정규식에 해당되는지 체크\n
            data : 검사 항목\n
            _rex : 정규식
        """
        if not data:
            return False

        if re.match(_rex, str(data)):
            return False
        return True

    # 특정 리스트 안에 존재하는지 체크
    @classmethod
    def checkList(cls, data: str, _list: list) -> bool:
        """
            입력된 data가 해당 리스트에 존재하는지 체크
            data : 검사 항목
            _list : 체크 리스트
            예 )
            data : 'Y' , _list : ['Y','N'] -> False
            data : 'A' , _list : ['Y','N'] -> True
        """
        if not data:
            return False

        if data in _list:
            return False
        return True

    # 날자 포맷이 맞는지 체크
    @classmethod
    def checkDateFormat(cls, data: str) -> bool:
        """
            날짜 포맷 여부 체크
            예시 리스트)
            "2023-10-10": 통과,
            "2023-13-10": 실패,
            "2023-12-34": 실패,
            "2023년1월3일": 통과,
            "2023년 1월 3일": 실패,
            "2023년 1월 35일": 실패,
            "2023-10-22": 통과,
            "2022-11-35": 실패,
            "2023년 01월 03일": 실패,
            "2023년01월03일": 통과,
            "2023.1.1": 통과,
            "2023.01.01": 통과,
            "2023.1.04": 통과,
            "2023.13.10": 실패,
            "2023.11.35": 실패
        """
        if not data:
            return False

        _rex = r'((\d{4})|\d{2})?(-|/|.)?(?P<month>[1-9]|0[1-9]|1[0-2])(-|/|.|월 )(?P<date>([1-9]|0[1-9]|[1-2][0-9]|3[01]))일?$'
        _res = re.match(_rex, data)
        if _res and ((1 if (int(_res.group('date')) <= 28) else 0) if int(_res.group('month')) == 2 else 1):
            return False
        return True

    # 이메일 포맷 체크
    @classmethod
    def checkEmail(cls, data: str) -> bool:
        """
            이메일 포맷 체크
        """
        if not data:
            return False

        _rex = r'^[a-zA-Z0-9+-_.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if re.match(_rex, str(data)):
            return False
        return True

    # 비밀번호 포맷 체크
    @classmethod
    def checkPasswd(cls, data: str) -> bool:
        """
            비밀번호 포맷 체크
            영어, 특수문자, 숫자 포함 여부 + 8~50글자 체크
        """
        if not data:
            return False

        _rex = r'(?=.*\d{1,50})(?=.*[~`!@#$%\^&*()-+=]{1,50})(?=.*[a-zA-Z]{2,50}).{8,50}$'
        data = str(data)
        if re.match(_rex, data):
            _rex = '(([a-zA-Z0-9])\\2{2,})'
            if re.search(_rex, data):
                return True
            return False

        return True

    # 필수 조건 체크
    @classmethod
    def requireCheck(cls, data: dict, param: list) -> str:
        """
            필수 파라미터가 존재하는지 체크합니다.
            data : 파라미터 내부에 해당 키가 존재하는지 그리고 빈 리스트가 존재하는지 체크합니다.
            예)
            data = {
                'a': 'k',
                'b': ''
            }
            param = ['a','b']
            -> 'b'
            DATA['b']에 데이터가 존재하지 않습니다.
            ----------------------
            data = {
                'a': 'k'
            }
            param = ['a','b']
            -> 'b'
            data에 키 b가 존재하지 않습니다.
            ----------------------
            data = {
                'a': 'k',
                'b': '1',
                'c': ''
            }
            param = ['a','b']
            -> None
            data에 a,b 모두 키와 데이터가 존재합니다.
        """
        for p in param:
            if not data.get(p):
                return p

        return None

    # 리스트 내부 조건 값 체크
    @classmethod
    def checkListValues(cls, data: list, keys: list) -> bool:
        """
            리스트 내부 조건 값을 체크합니다.
            예)
            data = ['물품','용역'], keys = ['물품', '용역', '공사'] => False(성공)
            -------------
            data = ['더비데이터','용역'], keys = ['물품', '용역', '공사'] => True(실패)
        """
        if not data:
            return False

        if type(data) != list:
            return True

        if set(data) - set(keys):
            return True

        return False
