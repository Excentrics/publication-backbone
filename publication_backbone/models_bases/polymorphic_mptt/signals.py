# -*- coding: utf-8 -*-
from django.dispatch import Signal

move_to_done = Signal(providing_args=["instance", "target", "position"])

pre_save_polymorphic_mptt = Signal(providing_args=["instance"])

post_save_polymorphic_mptt = Signal(providing_args=["instance"])