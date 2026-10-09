"""Unit tests for all component render_conky_text() outputs (Sub-Task 3)."""

import pytest

import gonky.components  # noqa: F401 — side-effect: populates COMPONENT_REGISTRY

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


# ---------------------------------------------------------------------------
# Registry completeness
# ---------------------------------------------------------------------------

class TestComponentRegistry:
    EXPECTED_KEYS = {
        "cpu_usage", "cpu_bar", "cpu_graph", "cpu_freq", "load_avg",
        "ram_usage", "ram_bar", "ram_graph", "swap_usage",
        "disk_usage", "disk_bar", "disk_io", "disk_io_graph",
        "net_upload", "net_download", "net_upload_graph", "net_download_graph", "net_ip",
        "battery_percent", "battery_bar", "battery_time",
        "temperature",
        "processes", "process_count",
        "clock", "date", "uptime", "text", "spacer", "separator", "bar", "graph",
        "exec", "lua_snippet",
    }

    def test_all_expected_keys_present(self):
        for key in self.EXPECTED_KEYS:
            assert key in COMPONENT_REGISTRY, f"Missing key in COMPONENT_REGISTRY: {key}"

    def test_registry_values_are_classes(self):
        for key, cls in COMPONENT_REGISTRY.items():
            assert isinstance(cls, type), f"COMPONENT_REGISTRY[{key!r}] is not a class"

    def test_type_key_matches_registry_key(self):
        for key, cls in COMPONENT_REGISTRY.items():
            assert cls.TYPE_KEY == key, (
                f"TYPE_KEY mismatch: registry key={key!r}, TYPE_KEY={cls.TYPE_KEY!r}"
            )


# ---------------------------------------------------------------------------
# CPU components
# ---------------------------------------------------------------------------

class TestCpuUsage:
    def setup_method(self):
        self.c = CpuUsage()

    def test_defaults_all_cores(self):
        assert self.c.render_conky_text({"core": 0}) == "${cpu}"

    def test_specific_core(self):
        assert self.c.render_conky_text({"core": 2}) == "${cpu cpu2}"

    def test_with_color(self):
        assert self.c.render_conky_text({"core": 0, "color": "red"}) == "${color red}${cpu}${color}"

    def test_with_core_and_color(self):
        assert self.c.render_conky_text({"core": 1, "color": "ff0000"}) == "${color ff0000}${cpu cpu1}${color}"

    def test_no_color_wrapping_when_empty(self):
        result = self.c.render_conky_text({"core": 1, "color": ""})
        assert "${color}" not in result


class TestCpuBar:
    def setup_method(self):
        self.c = CpuBar()

    def test_defaults(self):
        assert self.c.render_conky_text({}) == "${cpubar}"

    def test_specific_core(self):
        assert self.c.render_conky_text({"core": 1}) == "${cpubar cpu1}"

    def test_height_only(self):
        assert self.c.render_conky_text({"height": 6}) == "${cpubar 6}"

    def test_height_and_width(self):
        assert self.c.render_conky_text({"height": 6, "width": 200}) == "${cpubar 6,200}"

    def test_width_ignored_without_height(self):
        # Conky requires height before width; width alone is meaningless
        assert self.c.render_conky_text({"width": 200}) == "${cpubar}"

    def test_with_color(self):
        result = self.c.render_conky_text({"color": "blue"})
        assert result == "${color blue}${cpubar}${color}"

    def test_core_height_width_color(self):
        result = self.c.render_conky_text({"core": 2, "height": 8, "width": 150, "color": "green"})
        assert result == "${color green}${cpubar cpu2 8,150}${color}"


class TestCpuGraph:
    def setup_method(self):
        self.c = CpuGraph()

    def test_defaults(self):
        assert self.c.render_conky_text({}) == "${cpugraph}"

    def test_specific_core(self):
        assert self.c.render_conky_text({"core": 3}) == "${cpugraph cpu3}"

    def test_height_and_width(self):
        assert self.c.render_conky_text({"height": 40, "width": 200}) == "${cpugraph 40,200}"

    def test_colors(self):
        result = self.c.render_conky_text({"color_lo": "00ff00", "color_hi": "ff0000"})
        assert result == "${cpugraph 00ff00 ff0000}"

    def test_partial_colors_ignored(self):
        # Conky needs both or neither
        assert "00ff00" not in self.c.render_conky_text({"color_lo": "00ff00"})

    def test_all_options(self):
        result = self.c.render_conky_text({"core": 1, "height": 40, "width": 200, "color_lo": "0f0", "color_hi": "f00"})
        assert result == "${cpugraph cpu1 40,200 0f0 f00}"


class TestCpuFreq:
    def setup_method(self):
        self.c = CpuFreq()

    def test_default_all_cores(self):
        assert self.c.render_conky_text({}) == "${freq_g}"

    def test_specific_core(self):
        assert self.c.render_conky_text({"core": 1}) == "${freq_g 1}"


class TestLoadAvg:
    def setup_method(self):
        self.c = LoadAvg()

    def test_default_all(self):
        assert self.c.render_conky_text({}) == "${loadavg}"

    def test_period_1(self):
        assert self.c.render_conky_text({"period": 1}) == "${loadavg 1}"

    def test_period_3(self):
        assert self.c.render_conky_text({"period": 3}) == "${loadavg 3}"


# ---------------------------------------------------------------------------
# Memory components
# ---------------------------------------------------------------------------

class TestRamUsage:
    def setup_method(self):
        self.c = RamUsage()

    def test_default_percent(self):
        assert self.c.render_conky_text({}) == "${memperc}"

    def test_percent_explicit(self):
        assert self.c.render_conky_text({"format": "%"}) == "${memperc}"

    def test_human(self):
        assert self.c.render_conky_text({"format": "human"}) == "${mem}"

    def test_bytes(self):
        assert self.c.render_conky_text({"format": "bytes"}) == "${memraw}"


class TestRamBar:
    def setup_method(self):
        self.c = RamBar()

    def test_defaults(self):
        assert self.c.render_conky_text({}) == "${membar}"

    def test_height_only(self):
        assert self.c.render_conky_text({"height": 6}) == "${membar 6}"

    def test_height_and_width(self):
        assert self.c.render_conky_text({"height": 6, "width": 200}) == "${membar 6,200}"

    def test_with_color(self):
        assert self.c.render_conky_text({"color": "cyan"}) == "${color cyan}${membar}${color}"


class TestRamGraph:
    def setup_method(self):
        self.c = RamGraph()

    def test_defaults(self):
        assert self.c.render_conky_text({}) == "${memgraph}"

    def test_height_and_width(self):
        assert self.c.render_conky_text({"height": 40, "width": 200}) == "${memgraph 40,200}"

    def test_colors(self):
        result = self.c.render_conky_text({"color_lo": "0f0", "color_hi": "f00"})
        assert result == "${memgraph 0f0 f00}"


class TestSwapUsage:
    def setup_method(self):
        self.c = SwapUsage()

    def test_default_percent(self):
        assert self.c.render_conky_text({}) == "${swapperc}"

    def test_human(self):
        assert self.c.render_conky_text({"format": "human"}) == "${swap}"

    def test_bytes(self):
        assert self.c.render_conky_text({"format": "bytes"}) == "${swapraw}"


# ---------------------------------------------------------------------------
# Disk components
# ---------------------------------------------------------------------------

class TestDiskUsage:
    def setup_method(self):
        self.c = DiskUsage()

    def test_default_percent(self):
        assert self.c.render_conky_text({}) == "${fs_used_perc /}"

    def test_human(self):
        assert self.c.render_conky_text({"format": "human", "mount_point": "/"}) == "${fs_used /}"

    def test_custom_mount(self):
        assert self.c.render_conky_text({"mount_point": "/home", "format": "%"}) == "${fs_used_perc /home}"


class TestDiskBar:
    def setup_method(self):
        self.c = DiskBar()

    def test_defaults(self):
        assert self.c.render_conky_text({}) == "${diskbar /}"

    def test_height_and_width(self):
        result = self.c.render_conky_text({"mount_point": "/", "height": 6, "width": 100})
        assert result == "${diskbar 6,100 /}"

    def test_custom_mount(self):
        assert self.c.render_conky_text({"mount_point": "/data"}) == "${diskbar /data}"


class TestDiskIO:
    def setup_method(self):
        self.c = DiskIO()

    def test_default_read(self):
        assert self.c.render_conky_text({}) == "${diskio_read}"

    def test_write(self):
        assert self.c.render_conky_text({"direction": "write"}) == "${diskio_write}"

    def test_total(self):
        assert self.c.render_conky_text({"direction": "total"}) == "${diskio}"

    def test_with_device(self):
        assert self.c.render_conky_text({"device": "sda", "direction": "read"}) == "${diskio_read sda}"

    def test_write_with_device(self):
        assert self.c.render_conky_text({"device": "nvme0n1", "direction": "write"}) == "${diskio_write nvme0n1}"


class TestDiskIOGraph:
    def setup_method(self):
        self.c = DiskIOGraph()

    def test_default_read(self):
        assert self.c.render_conky_text({}) == "${diskiograph_read}"

    def test_write(self):
        assert self.c.render_conky_text({"direction": "write"}) == "${diskiograph_write}"

    def test_total(self):
        assert self.c.render_conky_text({"direction": "total"}) == "${diskiograph}"

    def test_with_device(self):
        assert self.c.render_conky_text({"device": "sda"}) == "${diskiograph_read sda}"

    def test_height_and_width(self):
        result = self.c.render_conky_text({"device": "sda", "height": 40, "width": 200})
        assert result == "${diskiograph_read sda 40,200}"


# ---------------------------------------------------------------------------
# Network components
# ---------------------------------------------------------------------------

class TestNetUpload:
    def setup_method(self):
        self.c = NetUpload()

    def test_default_interface(self):
        assert self.c.render_conky_text({}) == "${upspeed eth0}"

    def test_custom_interface(self):
        assert self.c.render_conky_text({"interface": "wlan0"}) == "${upspeed wlan0}"


class TestNetDownload:
    def setup_method(self):
        self.c = NetDownload()

    def test_default_interface(self):
        assert self.c.render_conky_text({}) == "${downspeed eth0}"

    def test_custom_interface(self):
        assert self.c.render_conky_text({"interface": "wlan0"}) == "${downspeed wlan0}"


class TestNetUploadGraph:
    def setup_method(self):
        self.c = NetUploadGraph()

    def test_default(self):
        assert self.c.render_conky_text({}) == "${upspeedgraph eth0}"

    def test_height_and_width(self):
        result = self.c.render_conky_text({"interface": "eth0", "height": 40, "width": 200})
        assert result == "${upspeedgraph eth0 40,200}"

    def test_colors(self):
        result = self.c.render_conky_text({"interface": "eth0", "color_lo": "0f0", "color_hi": "f00"})
        assert result == "${upspeedgraph eth0 0f0 f00}"

    def test_partial_colors_ignored(self):
        result = self.c.render_conky_text({"interface": "eth0", "color_lo": "0f0"})
        assert "0f0" not in result


class TestNetDownloadGraph:
    def setup_method(self):
        self.c = NetDownloadGraph()

    def test_default(self):
        assert self.c.render_conky_text({}) == "${downspeedgraph eth0}"

    def test_height_and_width(self):
        result = self.c.render_conky_text({"interface": "eth0", "height": 40, "width": 200})
        assert result == "${downspeedgraph eth0 40,200}"

    def test_colors(self):
        result = self.c.render_conky_text({"interface": "eth0", "color_lo": "0f0", "color_hi": "f00"})
        assert result == "${downspeedgraph eth0 0f0 f00}"


class TestNetIp:
    def setup_method(self):
        self.c = NetIp()

    def test_default_interface(self):
        assert self.c.render_conky_text({}) == "${addr eth0}"

    def test_custom_interface(self):
        assert self.c.render_conky_text({"interface": "wlan0"}) == "${addr wlan0}"


# ---------------------------------------------------------------------------
# Battery components
# ---------------------------------------------------------------------------

class TestBatteryPercent:
    def setup_method(self):
        self.c = BatteryPercent()

    def test_default(self):
        assert self.c.render_conky_text({}) == "${battery_percent BAT0}"

    def test_custom_id(self):
        assert self.c.render_conky_text({"battery_id": "BAT1"}) == "${battery_percent BAT1}"


class TestBatteryBar:
    def setup_method(self):
        self.c = BatteryBar()

    def test_default(self):
        assert self.c.render_conky_text({}) == "${battery_bar BAT0}"

    def test_height_only(self):
        assert self.c.render_conky_text({"height": 6}) == "${battery_bar 6 BAT0}"

    def test_height_and_width(self):
        assert self.c.render_conky_text({"height": 6, "width": 100}) == "${battery_bar 6,100 BAT0}"

    def test_custom_battery_id(self):
        assert self.c.render_conky_text({"battery_id": "BAT1"}) == "${battery_bar BAT1}"


class TestBatteryTime:
    def setup_method(self):
        self.c = BatteryTime()

    def test_default(self):
        assert self.c.render_conky_text({}) == "${battery_time BAT0}"

    def test_custom_id(self):
        assert self.c.render_conky_text({"battery_id": "BAT1"}) == "${battery_time BAT1}"


# ---------------------------------------------------------------------------
# Temperature component
# ---------------------------------------------------------------------------

class TestTemperature:
    def setup_method(self):
        self.c = Temperature()

    def test_hwmon_default(self):
        result = self.c.render_conky_text({})
        assert result == "${hwmon 0 temp 1}"

    def test_hwmon_custom(self):
        result = self.c.render_conky_text({"source": "hwmon", "hwmon_n": 1, "hwmon_num": 2})
        assert result == "${hwmon 1 temp 2}"

    def test_thermal_zone_default(self):
        result = self.c.render_conky_text({"source": "thermal_zone", "thermal_zone": 0})
        assert result == "${exec cat /sys/class/thermal/thermal_zone0/temp}"

    def test_thermal_zone_custom(self):
        result = self.c.render_conky_text({"source": "thermal_zone", "thermal_zone": 2})
        assert result == "${exec cat /sys/class/thermal/thermal_zone2/temp}"

    def test_unit_celsius_unchanged(self):
        result = self.c.render_conky_text({"unit": "C"})
        assert result == "${hwmon 0 temp 1}"

    def test_unit_fahrenheit_wraps(self):
        result = self.c.render_conky_text({"unit": "F"})
        assert "awk" in result
        assert "9/5" in result


# ---------------------------------------------------------------------------
# Process components
# ---------------------------------------------------------------------------

class TestProcesses:
    def setup_method(self):
        self.c = Processes()

    def test_cpu_sort_default(self):
        result = self.c.render_conky_text({"count": 3, "sort_by": "cpu"})
        lines = result.split("\n")
        assert len(lines) == 3
        assert lines[0] == "${top name 1} ${top cpu 1}"
        assert lines[2] == "${top name 3} ${top cpu 3}"

    def test_mem_sort(self):
        result = self.c.render_conky_text({"count": 2, "sort_by": "mem"})
        lines = result.split("\n")
        assert len(lines) == 2
        assert lines[0] == "${top_mem name 1} ${top_mem mem 1}"

    def test_count_floor_at_1(self):
        result = self.c.render_conky_text({"count": 0, "sort_by": "cpu"})
        assert result == "${top name 1} ${top cpu 1}"


class TestProcessCount:
    def setup_method(self):
        self.c = ProcessCount()

    def test_default_running(self):
        assert self.c.render_conky_text({}) == "${running_processes}"

    def test_total(self):
        assert self.c.render_conky_text({"count_type": "total"}) == "${processes}"

    def test_running_explicit(self):
        assert self.c.render_conky_text({"count_type": "running"}) == "${running_processes}"


# ---------------------------------------------------------------------------
# Display: Clock / Date / Uptime
# ---------------------------------------------------------------------------

class TestClock:
    def setup_method(self):
        self.c = Clock()

    def test_default_format(self):
        assert self.c.render_conky_text({}) == "${time %H:%M:%S}"

    def test_custom_format(self):
        assert self.c.render_conky_text({"format": "%I:%M %p"}) == "${time %I:%M %p}"


class TestDate:
    def setup_method(self):
        self.c = Date()

    def test_default_format(self):
        assert self.c.render_conky_text({}) == "${time %Y-%m-%d}"

    def test_custom_format(self):
        assert self.c.render_conky_text({"format": "%d/%m/%Y"}) == "${time %d/%m/%Y}"


class TestUptime:
    def setup_method(self):
        self.c = Uptime()

    def test_output(self):
        assert self.c.render_conky_text({}) == "${uptime}"


# ---------------------------------------------------------------------------
# Display: CustomText
# ---------------------------------------------------------------------------

class TestCustomText:
    def setup_method(self):
        self.c = CustomText()

    def test_basic(self):
        result = self.c.render_conky_text({"content": "Hello", "color": "", "font": "Mono", "size": 10})
        assert result == "${font Mono:size=10}Hello${font}"

    def test_with_color(self):
        result = self.c.render_conky_text({"content": "Hi", "color": "red", "font": "Mono", "size": 10})
        assert result == "${color red}${font Mono:size=10}Hi${font}${color}"

    def test_empty_content(self):
        result = self.c.render_conky_text({"content": "", "color": "", "font": "Mono", "size": 10})
        assert result == "${font Mono:size=10}${font}"


# ---------------------------------------------------------------------------
# Display: Spacer
# ---------------------------------------------------------------------------

class TestSpacer:
    def setup_method(self):
        self.c = Spacer()

    def test_default_one_newline(self):
        assert self.c.render_conky_text({}) == "\n"

    def test_three_newlines(self):
        assert self.c.render_conky_text({"line_count": 3}) == "\n\n\n"

    def test_floor_at_one(self):
        assert self.c.render_conky_text({"line_count": 0}) == "\n"


# ---------------------------------------------------------------------------
# Display: Separator
# ---------------------------------------------------------------------------

class TestSeparator:
    def setup_method(self):
        self.c = Separator()

    def test_defaults(self):
        assert self.c.render_conky_text({}) == "${hr}"

    def test_with_width(self):
        assert self.c.render_conky_text({"width": 2}) == "${hr 2}"

    def test_with_color(self):
        assert self.c.render_conky_text({"color": "gray"}) == "${color gray}${hr}${color}"

    def test_width_and_color(self):
        assert self.c.render_conky_text({"width": 1, "color": "white"}) == "${color white}${hr 1}${color}"


# ---------------------------------------------------------------------------
# Display: GenericBar
# ---------------------------------------------------------------------------

class TestGenericBar:
    def setup_method(self):
        self.c = GenericBar()

    def test_defaults(self):
        assert self.c.render_conky_text({}) == "${bar}"

    def test_with_variable(self):
        assert self.c.render_conky_text({"variable_expr": "cpu"}) == "${bar cpu}"

    def test_height_and_width(self):
        assert self.c.render_conky_text({"height": 6, "width": 200}) == "${bar 6,200}"

    def test_all_options(self):
        assert self.c.render_conky_text({"variable_expr": "memperc", "height": 8, "width": 100}) == "${bar 8,100 memperc}"


# ---------------------------------------------------------------------------
# Display: GenericGraph
# ---------------------------------------------------------------------------

class TestGenericGraph:
    def setup_method(self):
        self.c = GenericGraph()

    def test_defaults(self):
        assert self.c.render_conky_text({}) == "${graph}"

    def test_with_variable(self):
        assert self.c.render_conky_text({"variable_expr": "cpu"}) == "${graph cpu}"

    def test_height_and_width(self):
        assert self.c.render_conky_text({"height": 40, "width": 200}) == "${graph 40,200}"

    def test_colors(self):
        result = self.c.render_conky_text({"color_lo": "0f0", "color_hi": "f00"})
        assert result == "${graph 0f0 f00}"

    def test_all_options(self):
        result = self.c.render_conky_text({"variable_expr": "memperc", "height": 40, "width": 200, "color_lo": "0f0", "color_hi": "f00"})
        assert result == "${graph memperc 40,200 0f0 f00}"


# ---------------------------------------------------------------------------
# Advanced: ExecCommand
# ---------------------------------------------------------------------------

class TestExecCommand:
    def setup_method(self):
        self.c = ExecCommand()

    def test_default_exec_no_command(self):
        assert self.c.render_conky_text({}) == "${exec}"

    def test_exec_with_command(self):
        assert self.c.render_conky_text({"command": "date", "exec_type": "exec"}) == "${exec date}"

    def test_execbar(self):
        assert self.c.render_conky_text({"command": "mycmd", "exec_type": "execbar"}) == "${execbar mycmd}"

    def test_execgraph(self):
        assert self.c.render_conky_text({"command": "mycmd", "exec_type": "execgraph"}) == "${execgraph mycmd}"

    def test_invalid_exec_type_defaults_to_exec(self):
        result = self.c.render_conky_text({"command": "ls", "exec_type": "invalid"})
        assert result == "${exec ls}"


# ---------------------------------------------------------------------------
# Advanced: LuaSnippet
# ---------------------------------------------------------------------------

class TestLuaSnippet:
    def setup_method(self):
        self.c = LuaSnippet()

    def test_empty_raw_text(self):
        assert self.c.render_conky_text({}) == ""

    def test_passthrough(self):
        raw = "${lua my_func arg1}"
        assert self.c.render_conky_text({"raw_text": raw}) == raw

    def test_multiline(self):
        raw = "line1\nline2"
        assert self.c.render_conky_text({"raw_text": raw}) == raw


# ---------------------------------------------------------------------------
# Property schema smoke tests — every class must return a list
# ---------------------------------------------------------------------------

class TestPropertySchemas:
    ALL_CLASSES = [
        CpuUsage, CpuBar, CpuGraph, CpuFreq, LoadAvg,
        RamUsage, RamBar, RamGraph, SwapUsage,
        DiskUsage, DiskBar, DiskIO, DiskIOGraph,
        NetUpload, NetDownload, NetUploadGraph, NetDownloadGraph, NetIp,
        BatteryPercent, BatteryBar, BatteryTime,
        Temperature,
        Processes, ProcessCount,
        Clock, Date, Uptime,
        CustomText, Spacer, Separator, GenericBar, GenericGraph,
        ExecCommand, LuaSnippet,
    ]

    @pytest.mark.parametrize("cls", ALL_CLASSES)
    def test_property_schema_returns_list(self, cls):
        schema = cls.property_schema()
        assert isinstance(schema, list), f"{cls.__name__}.property_schema() did not return a list"

    @pytest.mark.parametrize("cls", ALL_CLASSES)
    def test_property_schema_keys_match_defaults(self, cls):
        """Every key in property_schema must also be present in DEFAULT_PROPERTIES
        (Uptime and LuaSnippet are expected exceptions with empty schemas)."""
        schema = cls.property_schema()
        defaults = cls.DEFAULT_PROPERTIES
        for field in schema:
            assert field.key in defaults, (
                f"{cls.__name__}: property_schema key {field.key!r} not in DEFAULT_PROPERTIES"
            )
