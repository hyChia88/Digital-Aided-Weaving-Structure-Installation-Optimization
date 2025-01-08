/*
Author: huiyenchia
update: 13/05/2024
*/

1. CSV文件确认
- filename = "csvtoRead.csv"
- 格式：位置(mm),编号(CXXXPXXX), 颜色(0~4),

2.硬件设置
	1.将旋转编码器以及5个墨盒接到USB扩接板，再接至计算机
	2.最后电源连接至中枢板，为墨盒供电

3. 程序设置
	1.打开计算机上的device manager，检查墨盒和编码器的串口
	2.于main.cpp更改定义
	// 定义常量
const LPCWSTR ENCODER_SERIAL_PORT = L"COM6";//旋转编码器串口
const LPCWSTR COLOUR1_SERIAL_PORT = L"COM5";//颜色0串口
const LPCWSTR COLOUR2_SERIAL_PORT = L"COM7";//颜色1串口
const LPCWSTR COLOUR3_SERIAL_PORT = L"COM8";//颜色2串口
const LPCWSTR COLOUR4_SERIAL_PORT = L"COM9";//颜色3串口
const LPCWSTR COLOUR5_SERIAL_PORT = L"COM10";//颜色4串口
const double radius = 30; //测距轮子半径(mm)
const int BAUD_RATE = CBR_115200; //波特率，一般默认
const int TIMEOUT_MS = 10; //串口通信率，一般默认
const std::string filename = "csvtoRead.csv"; //文件读取名字，一般默认
