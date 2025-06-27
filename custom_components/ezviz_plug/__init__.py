"""Ezviz Smart Plug integration."""

from homeassistant import config_entries, core
from .const import DOMAIN


"""Ezviz智能插座集成(像乐高积木连接器)

这里的工作相当于在智能家居系统中:
1. 准备工具箱：当用户添加设备时，准备好所有需要的工具
2. 建立通讯录：把账号信息存到系统记事本(hass.data)里
3. 设置自动更新：当用户修改设置时自动刷新连接
"""

# 相当于设备注册中心(像学校新生报到处的登记表)
async def async_setup_entry(hass: core.HomeAssistant, entry: config_entries.ConfigEntry) -> bool:
    # 在系统记事本里新建智能插座专属页面
    hass.data.setdefault(DOMAIN, {})
    # 把用户填写的账号密码抄写到本地通讯录
    hass_data = dict(entry.data)

    # 设置自动提醒功能：当设置变更时自动更新(像班级微信群的通知功能)
    unsub_options_update_listener = entry.add_update_listener(options_update_listener)

    # 把通知功能的开关存到工具箱里
    hass_data["unsub_options_update_listener"] = unsub_options_update_listener
    hass.data[DOMAIN][entry.entry_id] = hass_data

    # 启动开关模块(像给新同学分配班级座位)
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "switch")
    )
    return True


# 设置变更提醒器(像微信群里的@全体成员功能)
async def options_update_listener(hass: core.HomeAssistant, config_entry: config_entries.ConfigEntry):
    # 当设置变更时，重新加载整个配置
    await hass.config_entries.async_reload(config_entry.entry_id)


# 旧式配置方法(保留给老用户使用，像传统纸质登记表)
async def async_setup(hass: core.HomeAssistant, config: dict) -> bool:
    hass.data.setdefault(DOMAIN, {})
    return True
