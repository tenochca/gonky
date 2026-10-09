"""Components package — imports all component types and builds the registry."""

from gonky.components.advanced.exec import ExecCommand
from gonky.components.display.clock import Clock, Date, Uptime
from gonky.components.display.text import CustomText
from gonky.components.system.cpu import CpuBar, CpuFreq, CpuGraph, CpuUsage, LoadAvg
from gonky.components.system.disk import DiskBar, DiskIO, DiskUsage
from gonky.components.system.memory import RamBar, RamGraph, RamUsage, SwapUsage
from gonky.models.component import COMPONENT_REGISTRY

COMPONENT_REGISTRY[CpuUsage.TYPE_KEY] = CpuUsage
COMPONENT_REGISTRY[CpuBar.TYPE_KEY] = CpuBar
COMPONENT_REGISTRY[CpuGraph.TYPE_KEY] = CpuGraph
COMPONENT_REGISTRY[CpuFreq.TYPE_KEY] = CpuFreq
COMPONENT_REGISTRY[LoadAvg.TYPE_KEY] = LoadAvg

COMPONENT_REGISTRY[RamUsage.TYPE_KEY] = RamUsage
COMPONENT_REGISTRY[RamBar.TYPE_KEY] = RamBar
COMPONENT_REGISTRY[RamGraph.TYPE_KEY] = RamGraph
COMPONENT_REGISTRY[SwapUsage.TYPE_KEY] = SwapUsage


COMPONENT_REGISTRY[DiskUsage.TYPE_KEY] = DiskUsage
COMPONENT_REGISTRY[DiskBar.TYPE_KEY] = DiskBar
COMPONENT_REGISTRY[DiskIO.TYPE_KEY] = DiskIO

COMPONENT_REGISTRY[Clock.TYPE_KEY] = Clock
COMPONENT_REGISTRY[Date.TYPE_KEY] = Date
COMPONENT_REGISTRY[Uptime.TYPE_KEY] = Uptime

COMPONENT_REGISTRY[CustomText.TYPE_KEY] = CustomText

COMPONENT_REGISTRY[ExecCommand.TYPE_KEY] = ExecCommand
