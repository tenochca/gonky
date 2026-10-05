# Conky Variables Reference

Supported Conky variables and their configuration syntax for use in Gonky-generated config files.

> **Note:** This document is a stub. Full variable documentation will be added in Sub-Task 3
> (Component System).

## Categories

- System: CPU, memory, disk, network, battery, temperature
- Display: clock, date, uptime, text, spacer, separator, graph, bar
- Advanced: raw Lua snippets, exec commands

## Variable Syntax

Conky variables are written as `${variable_name arg1 arg2}` inside the `conky.text` block.

Examples:

```
${cpu cpu0}          -- CPU usage percentage for core 0
${mem}               -- Used RAM
${memperc}           -- RAM usage percentage
${fs_used_perc /}    -- Root filesystem usage percentage
${upspeed eth0}      -- Upload speed on eth0
${battery_percent}   -- Battery percentage
${time %H:%M:%S}     -- Current time
```
