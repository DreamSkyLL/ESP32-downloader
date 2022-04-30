# 水泵液位自动控制设备对 ESP32 固件自动烧录程序 (Windows) #

本程序是 Windows 环境下自动产生 EEPROM 配置区固件并能向 ESP32 自动写入固件的程序。需要 ```esptool.py```。

使用方法非常简单，工作人员只需连续按下 ```Enter``` 键并按照提示操作即可完成批量固件烧录，以及按下 ```Ctrl-C``` 结束程序，即可完成最基本的设备对烧录操作。

本程序的配置文件 ```config.json``` 内容讲解如下。

| 键 | 类型 | 描述 | 示例 |
| - | - | - | - |
| serial_port | string | 待烧录设备与 PC 通讯的 UART 端口号 (COMx)。 | COM6 |
| serial_speed | uint32 | UART 的通讯速率 (bps)，如非必要请保持默认值。 | 1500000 |
| gen_ppid | boolean | 是否自动产生递增 PPID。未用。 | true |
| ppid_start | uint8 array[4] | 递增 PPID 的起始值，数组中每个值的范围是 1-254。 | [1, 1, 1, 1] |
| server_addr | string | 服务器地址，域名或者 IPv4。 | 47.104.141.250 |
| server_port | uint16 | 服务程序端口号。 | 9991 |
