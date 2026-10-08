"""Components package — imports all component types and builds the registry."""

from gonky.components.system.cpu import CpuBar, CpuFreq, CpuGraph, CpuUsage, LoadAvg
from gonky.models.component import COMPONENT_REGISTRY

COMPONENT_REGISTRY[CpuUsage.TYPE_KEY] = CpuUsage
COMPONENT_REGISTRY[CpuBar.TYPE_KEY] = CpuBar
COMPONENT_REGISTRY[CpuGraph.TYPE_KEY] = CpuGraph
COMPONENT_REGISTRY[CpuFreq.TYPE_KEY] = CpuFreq
COMPONENT_REGISTRY[LoadAvg.TYPE_KEY] = LoadAvg
