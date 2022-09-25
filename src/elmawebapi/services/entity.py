from typing import TYPE_CHECKING

from . import base, decorators
from ..structure import Parser

if TYPE_CHECKING:
    from requests import Response


COUNT = "/API/REST/Entity/Count"
LOAD = "/API/REST/Entity/Load"
QUERY = "/API/REST/Entity/Query"
INSERT = "/API/REST/Entity/Insert/{typeuid}"
UPDATE = "/API/REST/Entity/Update/{typeuid}/{entityid}"


class EntityService(base.Service):
    """
    Реализация сервиса работы с объектами IEntityService.
    """

    @decorators.needs_auth
    @decorators.get(url=LOAD)
    def Load(self, result: "Response", *args, **kwargs) -> dict:
        """
        Получить сущность по типу и идентификатору.

        Параметры (для передачи через `params`):
            - type (str): идентификатор типа сущности
            - id (int): идентификатор объекта

        Returns:
            dict: нормализованный словарь с данными объекта
        """
        return Parser.normalize(result.json())

    @decorators.needs_auth
    @decorators.get(url=COUNT)
    def Count(self, result: "Response", *args, **kwargs) -> int:
        """
        Получить количество сущностей данного типа.

        Параметры (для передачи через `params`):
            - type (str): идентификатор типа сущности
            - q (str): запрос на языке EQL. Может быть пустой
            - filterProviderUid (str): уникальный идентификатор провайдера фильтрации
            - filterProviderData (str): данные для провайдера фильтрации
            - filter (str): значения полей для фильтра сущности в формате: Property1:Значение1,Property2:Значение2.
                          Наименование свойства возможно задавать с точкой (.) для получения доступа к подсвойству:
                          Property1.Property2:Значение1. Для указания в значении свойства символа : (двоеточие),
                          \\ (обратный слэш) или , (запятая), его нужно экранировать через \\ (обратный слэш).

        Returns:
            int: количество объектов
        """
        return int(result.text)

    @decorators.needs_auth
    @decorators.get(url=QUERY)
    def Query(self, result: "Response", *args, **kwargs) -> list:
        """
        Получить все сущности данного типа, отфильтрованные по запросу.

        Параметры (для передачи через `params`):
            - type (str): идентификатор типа сущности.
            - q (str): запрос на языке EQL. Может быть пустой
            - sort (str): сортировка
            - limit (int): количество элементов
            - offset (int): начальный элемент
            - filterProviderUid (str): уникальный идентификатор провайдера фильтрации
            - filterProviderData (str): данные для провайдера фильтрации
            - filter (str): значения полей для фильтра сущности в формате: Property1:Значение1,Property2:Значение2.
                          Наименование свойства возможно задавать с точкой (.) для получения доступа к подсвойству:
                          Property1.Property2:Значение1. Для указания в значении свойства символа : (двоеточие),
                          \\ (обратный слэш) или , (запятая), его нужно экранировать через \\ (обратный слэш)

        Returns:
            list: список нормализованных словарей с данными объектов
        """
        return Parser.normalize(result.json())

    @decorators.needs_auth
    @decorators.post(url=INSERT)
    def _insert(self, result: "Response", *args, **kwargs) -> int:
        return int(result.text.replace('"', ""))

    def Insert(self, entityData: dict, typeuid: str, *args, **kwargs) -> int:
        """
        Сохранить новый объект в системе.

        Args:
            typeuid: идентификатор типа сущности
            entityData: данные объекта в формате WebData

        Returns:
            int: id нового объекта
        """
        return self._insert(data=entityData, uri=INSERT.format(typeuid=typeuid), *args, **kwargs)

    @decorators.needs_auth
    @decorators.post(url=UPDATE)
    def _update(self, result: "Response", *args, **kwargs) -> int:
        return int(result.text.replace('"', ""))

    def Update(self, entityData: dict, typeuid: str, entityid: int, *args, **kwargs) -> int:
        """
        Обновить существующий объект в системе.

        Args:
            typeuid: идентификатор типа сущности
            entityid: идентификатор объекта
            entityData: данные объекта в формате WebData

        Returns:
            int: id измененного объекта, должен совпадать с переданным entityid
        """
        return self._update(data=entityData, uri=UPDATE.format(typeuid=typeuid, entityid=entityid), *args, **kwargs)
