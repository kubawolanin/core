"""Constants for the Nina integration."""
from __future__ import annotations

from datetime import timedelta
from logging import Logger, getLogger
from typing import Final

_LOGGER: Logger = getLogger(__package__)

SCAN_INTERVAL: timedelta = timedelta(minutes=5)

DOMAIN: str = "nina"

CONF_REGIONS: str = "regions"
CONF_MESSAGE_SLOTS: str = "slots"
CONF_FILTER_CORONA: str = "corona_filter"

ATTR_HEADLINE: str = "Headline"
ATTR_ID: str = "ID"
ATTR_SENT: str = "Sent"
ATTR_START: str = "Start"
ATTR_EXPIRES: str = "Expires"

CONST_LIST_A_TO_D: list[str] = ["A", "Ä", "B", "C", "D"]
CONST_LIST_E_TO_H: list[str] = ["E", "F", "G", "H"]
CONST_LIST_I_TO_L: list[str] = ["I", "J", "K", "L"]
CONST_LIST_M_TO_Q: list[str] = ["M", "N", "O", "Ö", "P", "Q"]
CONST_LIST_R_TO_U: list[str] = ["R", "S", "T", "U", "Ü"]
CONST_LIST_V_TO_Z: list[str] = ["V", "W", "X", "Y"]

CONST_REGION_A_TO_D: Final = "_a_to_d"
CONST_REGION_E_TO_H: Final = "_e_to_h"
CONST_REGION_I_TO_L: Final = "_i_to_l"
CONST_REGION_M_TO_Q: Final = "_m_to_q"
CONST_REGION_R_TO_U: Final = "_r_to_u"
CONST_REGION_V_TO_Z: Final = "_v_to_z"
CONST_REGIONS: Final = [
    CONST_REGION_A_TO_D,
    CONST_REGION_E_TO_H,
    CONST_REGION_I_TO_L,
    CONST_REGION_M_TO_Q,
    CONST_REGION_R_TO_U,
    CONST_REGION_V_TO_Z,
]

CONST_REGION_MAPPING: dict[str, list[str]] = {
    CONST_REGION_A_TO_D: CONST_LIST_A_TO_D,
    CONST_REGION_E_TO_H: CONST_LIST_E_TO_H,
    CONST_REGION_I_TO_L: CONST_LIST_I_TO_L,
    CONST_REGION_M_TO_Q: CONST_LIST_M_TO_Q,
    CONST_REGION_R_TO_U: CONST_LIST_R_TO_U,
    CONST_REGION_V_TO_Z: CONST_LIST_V_TO_Z,
}
