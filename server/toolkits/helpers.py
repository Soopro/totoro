# coding=utf-8
from __future__ import absolute_import

from document import MongodbConn

from common_models import (User, Invite, OAuth, UserBehavior,
                           UserExternalStorage,
                           App, Media, Menu, Slot,
                           Member, MemberRole,
                           Activity, Appointment,
                           Assistant,
                           Theme, ThemePayload, Template,
                           Extension, ExtensionInstaller,
                           ContentType, ContentFile,
                           Category, Term,
                           Commodity, CommoditySku, Discount, Order)

from blueprints.wechat_mina.models import MinaConfig

from blueprints.wechat.models import (WxConfig,
                                      WxResponse,
                                      WxSubscriber,
                                      WxBroadcast,
                                      WxMaterial)


models = [
    User, Invite, OAuth, UserBehavior,
    UserExternalStorage,
    App, Media, Menu, Slot,
    Member, MemberRole,
    Activity, Appointment,
    Assistant,
    Theme, ThemePayload, Template,
    Extension, ExtensionInstaller,
    ContentType, ContentFile,
    Category, Term,
    Commodity, CommoditySku, Discount, Order,

    MinaConfig,

    WxConfig, WxBroadcast, WxMaterial,
    WxResponse, WxSubscriber,
]


def connect_mongodb(cfg):
    mongodb_conn = MongodbConn(
        host=cfg.MONGODB_HOST,
        port=cfg.MONGODB_PORT,
        max_pool_size=cfg.MONGODB_MAX_POOL_SIZE,
    )

    mongodb_conn.register(models)

    mongodb = mongodb_conn[cfg.MONGODB_DATABASE]
    if cfg.MONGODB_USER and cfg.MONGODB_PASSWD:
        mongodb.authenticate(cfg.MONGODB_USER, cfg.MONGODB_PASSWD)

    return mongodb_conn, mongodb
