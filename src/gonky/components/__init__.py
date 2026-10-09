"""Components package — imports all component types and builds the registry."""

from gonky.components.system.cpu import CpuBar, CpuFreq, CpuGraph, CpuUsage, LoadAvg
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
