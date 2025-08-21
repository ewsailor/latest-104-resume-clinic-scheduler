"""
參數驗證工具測試模組。

測試參數驗證工具的各種功能。
"""

from datetime import date, time

import pytest

from app.enums.models import ScheduleStatusEnum
from app.errors import ValidationError
from app.utils.validators import validate_parameters, validator


class TestParameterValidator:
    """測試 ParameterValidator 類別"""

    def test_validate_positive_int_success(self):
        """測試正整數驗證成功"""
        result = validator.validate_positive_int(5, "test_param")
        assert result == 5

    def test_validate_positive_int_failure(self):
        """測試正整數驗證失敗"""
        with pytest.raises(ValidationError, match="無效的 test_param: 5，必須為正整數"):
            validator.validate_positive_int("5", "test_param")

        with pytest.raises(ValidationError, match="無效的 test_param: 0，必須為正整數"):
            validator.validate_positive_int(0, "test_param")

        with pytest.raises(
            ValidationError, match="無效的 test_param: -1，必須為正整數"
        ):
            validator.validate_positive_int(-1, "test_param")

    def test_validate_optional_positive_int_success(self):
        """測試可選正整數驗證成功"""
        result = validator.validate_optional_positive_int(5, "test_param")
        assert result == 5

        result = validator.validate_optional_positive_int(None, "test_param")
        assert result is None

    def test_validate_optional_positive_int_failure(self):
        """測試可選正整數驗證失敗"""
        with pytest.raises(ValidationError):
            validator.validate_optional_positive_int(0, "test_param")

    def test_validate_string_success(self):
        """測試字串驗證成功"""
        result = validator.validate_string("test", "test_param")
        assert result == "test"

        result = validator.validate_string("test", "test_param", min_length=4)
        assert result == "test"

    def test_validate_string_failure(self):
        """測試字串驗證失敗"""
        with pytest.raises(ValidationError):
            validator.validate_string(123, "test_param")

        with pytest.raises(ValidationError, match="test_param 長度不能小於 5"):
            validator.validate_string("test", "test_param", min_length=5)

    def test_validate_optional_string_success(self):
        """測試可選字串驗證成功"""
        result = validator.validate_optional_string("test", "test_param")
        assert result == "test"

        result = validator.validate_optional_string(None, "test_param")
        assert result is None

    def test_validate_list_success(self):
        """測試列表驗證成功"""
        result = validator.validate_list([1, 2, 3], "test_param")
        assert result == [1, 2, 3]

        result = validator.validate_list([1, 2, 3], "test_param", int)
        assert result == [1, 2, 3]

    def test_validate_list_failure(self):
        """測試列表驗證失敗"""
        with pytest.raises(ValidationError):
            validator.validate_list("not_a_list", "test_param")

        with pytest.raises(ValidationError, match="test_param\\[0\\] 類型錯誤"):
            validator.validate_list(["1", 2, 3], "test_param", int)

    def test_validate_date_success(self):
        """測試日期驗證成功"""
        test_date = date(2024, 1, 1)
        result = validator.validate_date(test_date, "test_param")
        assert result == test_date

    def test_validate_date_failure(self):
        """測試日期驗證失敗"""
        with pytest.raises(ValidationError):
            validator.validate_date("2024-01-01", "test_param")

    def test_validate_time_success(self):
        """測試時間驗證成功"""
        test_time = time(10, 30)
        result = validator.validate_time(test_time, "test_param")
        assert result == test_time

    def test_validate_time_failure(self):
        """測試時間驗證失敗"""
        with pytest.raises(ValidationError):
            validator.validate_time("10:30", "test_param")

    def test_validate_time_range_success(self):
        """測試時間範圍驗證成功"""
        start_time = time(10, 0)
        end_time = time(11, 0)
        validator.validate_time_range(start_time, end_time)

    def test_validate_time_range_failure(self):
        """測試時間範圍驗證失敗"""
        start_time = time(11, 0)
        end_time = time(10, 0)

        with pytest.raises(ValidationError, match="start_time 必須早於 end_time"):
            validator.validate_time_range(start_time, end_time)

        with pytest.raises(ValidationError, match="start_time 必須早於 end_time"):
            validator.validate_time_range(start_time, start_time)

    def test_validate_enum_value_success(self):
        """測試枚舉值驗證成功"""
        result = validator.validate_enum_value(
            "AVAILABLE", "test_param", ScheduleStatusEnum
        )
        assert result == "AVAILABLE"

    def test_validate_enum_value_failure(self):
        """測試枚舉值驗證失敗"""
        with pytest.raises(ValidationError, match="無效的 test_param 值"):
            validator.validate_enum_value(
                "INVALID_STATUS", "test_param", ScheduleStatusEnum
            )


class TestValidateParametersDecorator:
    """測試 validate_parameters 裝飾器"""

    def test_validate_parameters_success(self):
        """測試參數驗證裝飾器成功"""

        @validate_parameters(
            user_id=dict(type=int, min_value=1),
            name=dict(type=str, min_length=1),
            age=dict(type=int, min_value=0, optional=True),
        )
        def test_func(user_id: int, name: str, age: int | None = None):
            return f"{user_id}:{name}:{age}"

        result = test_func(1, "test", 25)
        assert result == "1:test:25"

        result = test_func(1, "test")
        assert result == "1:test:None"

    def test_validate_parameters_failure(self):
        """測試參數驗證裝飾器失敗"""

        @validate_parameters(
            user_id=dict(type=int, min_value=1), name=dict(type=str, min_length=1)
        )
        def test_func(user_id: int, name: str):
            return f"{user_id}:{name}"

        # 測試型別錯誤
        with pytest.raises(ValidationError):
            test_func("1", "test")

        # 測試數值範圍錯誤
        with pytest.raises(ValidationError):
            test_func(0, "test")

        # 測試字串長度錯誤
        with pytest.raises(ValidationError):
            test_func(1, "")

    def test_validate_parameters_with_enum(self):
        """測試參數驗證裝飾器與枚舉"""

        @validate_parameters(status=dict(enum_class=ScheduleStatusEnum))
        def test_func(status: str):
            return status

        result = test_func("AVAILABLE")
        assert result == "AVAILABLE"

        with pytest.raises(ValidationError):
            test_func("INVALID_STATUS")

    def test_validate_parameters_with_date_time(self):
        """測試參數驗證裝飾器與日期時間"""

        @validate_parameters(
            schedule_date=dict(type=date),
            start_time=dict(type=time),
            end_time=dict(type=time),
        )
        def test_func(schedule_date: date, start_time: time, end_time: time):
            return f"{schedule_date}:{start_time}:{end_time}"

        test_date = date(2024, 1, 1)
        start_time = time(10, 0)
        end_time = time(11, 0)

        result = test_func(test_date, start_time, end_time)
        assert result == f"{test_date}:{start_time}:{end_time}"

        # 測試日期型別錯誤
        with pytest.raises(ValidationError):
            test_func("2024-01-01", start_time, end_time)


class TestRealWorldScenario:
    """測試真實世界場景"""

    def test_schedule_validation_simulation(self):
        """模擬時段驗證場景"""
        # 模擬 schedule.py 中的驗證邏輯
        giver_id = validator.validate_positive_int(1, "giver_id")
        schedule_date = validator.validate_date(date(2024, 1, 1), "schedule_date")
        start_time = validator.validate_time(time(10, 0), "start_time")
        end_time = validator.validate_time(time(11, 0), "end_time")

        # 驗證時間範圍
        validator.validate_time_range(start_time, end_time)

        assert giver_id == 1
        assert schedule_date == date(2024, 1, 1)
        assert start_time == time(10, 0)
        assert end_time == time(11, 0)

    def test_schedule_validation_failure_simulation(self):
        """模擬時段驗證失敗場景"""
        with pytest.raises(ValidationError, match="無效的 giver_id: 1，必須為正整數"):
            validator.validate_positive_int("1", "giver_id")

        with pytest.raises(ValidationError, match="start_time 必須早於 end_time"):
            validator.validate_time_range(time(11, 0), time(10, 0))
