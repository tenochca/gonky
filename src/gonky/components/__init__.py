"""Components package — imports all component types and builds the registry."""

from gonky.components.advanced.exec import ExecCommand
from gonky.components.advanced.lua_snippet import LuaSnippet
from gonky.components.display.bar import GenericBar
from gonky.components.display.clock import Clock, Date, Uptime
from gonky.components.display.graph import GenericGraph
from gonky.components.display.separator import Separator
from gonky.components.display.spacer import Spacer
from gonky.components.display.text import CustomText
from gonky.components.system.battery import BatteryBar, BatteryPercent, BatteryTime
from gonky.components.system.cpu import CpuBar, CpuFreq, CpuGraph, CpuUsage, LoadAvg
from gonky.components.system.disk import DiskBar, DiskIO, DiskIOGraph, DiskUsage
from gonky.components.system.memory import RamBar, RamGraph, RamUsage, SwapUsage
from gonky.components.system.network import (
    NetDownload,
    NetDownloadGraph,
    NetIp,
    NetUpload,
    NetUploadGraph,
)
from gonky.components.system.processes import ProcessCount, Processes
from gonky.components.system.temperature import Temperature
from gonky.models.component import COMPONENT_REGISTRY

# --- System: CPU ---
COMPONENT_REGISTRY[CpuUsage.TYPE_KEY] = CpuUsage
COMPONENT_REGISTRY[CpuBar.TYPE_KEY] = CpuBar
COMPONENT_REGISTRY[CpuGraph.TYPE_KEY] = CpuGraph
COMPONENT_REGISTRY[CpuFreq.TYPE_KEY] = CpuFreq
COMPONENT_REGISTRY[LoadAvg.TYPE_KEY] = LoadAvg

# --- System: Memory ---
COMPONENT_REGISTRY[RamUsage.TYPE_KEY] = RamUsage
COMPONENT_REGISTRY[RamBar.TYPE_KEY] = RamBar
COMPONENT_REGISTRY[RamGraph.TYPE_KEY] = RamGraph
COMPONENT_REGISTRY[SwapUsage.TYPE_KEY] = SwapUsage

# --- System: Disk ---
COMPONENT_REGISTRY[DiskUsage.TYPE_KEY] = DiskUsage
COMPONENT_REGISTRY[DiskBar.TYPE_KEY] = DiskBar
COMPONENT_REGISTRY[DiskIO.TYPE_KEY] = DiskIO
COMPONENT_REGISTRY[DiskIOGraph.TYPE_KEY] = DiskIOGraph

# --- System: Network ---
COMPONENT_REGISTRY[NetUpload.TYPE_KEY] = NetUpload
COMPONENT_REGISTRY[NetDownload.TYPE_KEY] = NetDownload
COMPONENT_REGISTRY[NetUploadGraph.TYPE_KEY] = NetUploadGraph
COMPONENT_REGISTRY[NetDownloadGraph.TYPE_KEY] = NetDownloadGraph
COMPONENT_REGISTRY[NetIp.TYPE_KEY] = NetIp

# --- System: Battery ---
COMPONENT_REGISTRY[BatteryPercent.TYPE_KEY] = BatteryPercent
COMPONENT_REGISTRY[BatteryBar.TYPE_KEY] = BatteryBar
COMPONENT_REGISTRY[BatteryTime.TYPE_KEY] = BatteryTime

# --- System: Temperature ---
COMPONENT_REGISTRY[Temperature.TYPE_KEY] = Temperature

# --- System: Processes ---
COMPONENT_REGISTRY[Processes.TYPE_KEY] = Processes
COMPONENT_REGISTRY[ProcessCount.TYPE_KEY] = ProcessCount

# --- Display ---
COMPONENT_REGISTRY[Clock.TYPE_KEY] = Clock
COMPONENT_REGISTRY[Date.TYPE_KEY] = Date
COMPONENT_REGISTRY[Uptime.TYPE_KEY] = Uptime
COMPONENT_REGISTRY[CustomText.TYPE_KEY] = CustomText
COMPONENT_REGISTRY[Spacer.TYPE_KEY] = Spacer
COMPONENT_REGISTRY[Separator.TYPE_KEY] = Separator
COMPONENT_REGISTRY[GenericBar.TYPE_KEY] = GenericBar
COMPONENT_REGISTRY[GenericGraph.TYPE_KEY] = GenericGraph

# --- Advanced ---
COMPONENT_REGISTRY[ExecCommand.TYPE_KEY] = ExecCommand
COMPONENT_REGISTRY[LuaSnippet.TYPE_KEY] = LuaSnippet
