from events.Events import *
from module.modules.IModule import IModule
from utils.EvictingList import EvictingList
import time
import utils.mathUtils as mathUtils


TIME_SAMPLES = {}
avg_samples = {}
VLs = {}
times = {}
init_time = time.time()


class AntiSpam(IModule):
    def process(self, event: Event) -> None:
        if isinstance(event, GroupMessageEvent):
            msg = event.get_message()
            if msg.group.id not in TIME_SAMPLES:
                TIME_SAMPLES[msg.group.id] = {}
            if msg.sender.id not in TIME_SAMPLES[msg.group.id]:
                TIME_SAMPLES[msg.group.id][msg.sender.id] = EvictingList(10)
            if msg.group.id not in times:
                times[msg.group.id] = {}
            if msg.sender.id not in avg_samples:
                avg_samples[msg.sender.id] = EvictingList(7)

            if msg.sender.id not in times[msg.group.id]:
                times[msg.group.id][msg.sender.id] = get_cur_time()
                return

            e_list: EvictingList = TIME_SAMPLES[msg.group.id][msg.sender.id]
            e_list.add(get_cur_time() - times[msg.group.id][msg.sender.id])
            times[msg.group.id][msg.sender.id] = get_cur_time()

            if e_list.size() >= e_list.get_max_size():
                delta_time = 0.0
                for i in e_list.get_list():
                    delta_time += i
                divisor = delta_time / e_list.get_max_size() / 10

                e: EvictingList = avg_samples[msg.sender.id]
                e.add(1 / divisor)
                std = mathUtils.stdev(e.get_list())
                if std < 0.01 and e.size() >= e.get_max_size():
                    event.get_message().mute(86400, r=f"spam-A2, flag(d: {std})")
                    e.clear()


def prediction(msg):
    pass


def get_cur_time():
    return mathUtils.floor((time.time() - init_time) * 10)
