from pathlib import Path
from typing import Union, Any
import tomllib

class Config():

    def __init__(self, path: Union[str, Path] = ""):
        
        path = path or Path(r"D:\Projects\Eve-Online-Mining-Bot\cv_eve\config.toml")
        with open(path, "rb") as f:
            self.cfg = tomllib.load(f)

    @staticmethod
    def _get_value(cfg: dict, name: str) -> Any:
        """Получение значения настройки"""

        return cfg.get(name)

    def _find_option(self, name):

        for section, options in self.cfg.items():
            if section == name:
                return self.cfg[section]
            elif name in options:
                return self._get_value(options, name)
        return None


    def get(self, option: str, section: str | None = None):
        """Возвращает значение опции

        :param option: имя опции заглавными буквами
        :param section: имя секции

        | Если опция задана в config вернёт её значение
        | Если нет задана, вернёт None
        """
        if section:
            result = self._get_value(self.options[section], option)
        else:  # FIXME надо от этого отказаться
            result = self._find_option(option)
        return result