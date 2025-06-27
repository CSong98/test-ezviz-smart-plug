from homeassistant import config_entries
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD, CONF_URL, CONF_TIMEOUT, CONF_CUSTOMIZE
from .const import DOMAIN, DEFAULT_TIMEOUT, EU_URL, RUSSIA_URL, CONF_RFSESSION_ID, CONF_SESSION_ID
from pyezvizapi.client import EzvizClient
from pyezvizapi.exceptions import (
    AuthTestResultFailed,
    EzvizAuthVerificationCode,
    InvalidHost,
    InvalidURL,
    PyEzvizError,
)
import logging
import voluptuous as vol
from typing import Any, Dict

_LOGGER = logging.getLogger(__name__)

# TODO adjust the data schema to the data that you need
# 用户登录表单(像快递柜取件界面)
STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        # 邮箱相当于快递单号
        vol.Required(CONF_EMAIL): str,
        
        # 密码就像取件码
        vol.Required(CONF_PASSWORD): str,
        
        # 服务器选择就像选择快递公司
        vol.Required(CONF_URL, default=EU_URL): vol.In([EU_URL, RUSSIA_URL])
    }
)

# 账号验证器(像快递员检查取件信息)
def _validate_and_create_auth(data: dict) -> dict[str, Any]:
    # 尝试连接快递公司服务器(用用户提供的账号密码)
    ezviz_client = EzvizClient(
        data[CONF_EMAIL],
        data[CONF_PASSWORD],
        data[CONF_URL],
        data.get(CONF_TIMEOUT, DEFAULT_TIMEOUT),
    )

    # 获取登录凭证(像获得快递柜开箱密码)
    # pyezvizapi库的login方法可能返回不同的结构
    ezviz_token = ezviz_client.login()
    
    # 返回认证数据
    return {
        CONF_EMAIL: data[CONF_EMAIL],
        CONF_PASSWORD: data[CONF_PASSWORD],
        CONF_URL: data[CONF_URL],
        CONF_TIMEOUT: data.get(CONF_TIMEOUT, DEFAULT_TIMEOUT),
    }

# 配置流程管理器(像快递分拣中心)
class EzvizConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    
    # 处理用户输入(像快递员接收包裹)
    async def async_step_user(self, user_input=None):
        errors = {}
        
        if user_input is not None:
            try:
                # 验证用户输入并获取认证数据
                auth_data = await self.hass.async_add_executor_job(
                    _validate_and_create_auth, user_input
                )
                
                # 登录成功时创建配置条目(像生成快递单号)
                return self.async_create_entry(
                    title=user_input[CONF_EMAIL],
                    data=auth_data,
                    options={},
                )
            except InvalidHost:
                errors["base"] = "invalid_host"
            except InvalidURL:
                errors["base"] = "invalid_url"
            except EzvizAuthVerificationCode:
                errors["base"] = "mfa_required"
            except AuthTestResultFailed:
                errors["base"] = "invalid_auth"
            except PyEzvizError:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
        
        # 显示表单(像提供快递信息填写界面)
        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )
