"""Components package — imports all component types and builds the registry."""

from gonky.components.system.cpu import CpuBar, CpuFrequency, CpuGraph, CpuUsage
from gonky.models.component import COMPONENT_REGISTRY

COMPONENT_REGISTRY[CpuUsage.TYPE_KEY] = CpuUsage
COMPONENT_REGISTRY[CpuBar.TYPE_KEY] = CpuBar
COMPONENT_REGISTRY[CpuGraph.TYPE_KEY] = CpuGraph
COMPONENT_REGISTRY[CpuFrequency.TYPE_KEY] = CpuFrequency
