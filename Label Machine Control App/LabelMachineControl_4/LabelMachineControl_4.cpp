/*
Author: huiyenchia
update: 27/03/2024
function:
- 达到了readcsv, 获取realtimelocation，并在isMatch进行对应号码的Print喷印,获取颜色
*/

#include <iostream>
#include <string>
#include <Windows.h> // 串口通信库
#include <iomanip>
#include <stdexcept>
#include <chrono>
#include <thread>
#include <vector>
#include "CSVDataReader.h"

// 定义常量
const LPCWSTR ARDUINO_SERIAL_PORT = L"COM5";
const int BAUD_RATE = CBR_115200;
const int TIMEOUT_MS = 10;
const double radius = 25; //测距轮子半径(mm)

// ReadCSVData，获取Print内容
const std::string filename = "csvtoread.csv";
CSVDataReader csvReader(filename);
const std::vector<int>& data_LoactiontoPrint = csvReader.getSequenceData();
const std::vector<std::string>& sequenceDataID = csvReader.getSequenceDataID();
const std::vector<int>& sequenceDataColour = csvReader.getSequenceDataColour();
int matchingIndex = 0; // 当前匹配的索引,

// 串口通信类
class SerialPort {
public:
    SerialPort(LPCWSTR portName, int baudRate) : portName(portName), baudRate(baudRate) {
        serialPort = CreateFile(portName, GENERIC_READ | GENERIC_WRITE, 0, NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
        if (serialPort == INVALID_HANDLE_VALUE) {
            throw std::runtime_error("Error opening serial port.");
        }

        DCB dcbSerialParams = { 0 };
        dcbSerialParams.DCBlength = sizeof(dcbSerialParams);
        if (!GetCommState(serialPort, &dcbSerialParams) || !SetupComm(serialPort, 1024, 0)) {
            CloseHandle(serialPort);
            throw std::runtime_error("Error setting up serial port.");
        }

        dcbSerialParams.BaudRate = baudRate;
        dcbSerialParams.ByteSize = 8;
        dcbSerialParams.StopBits = ONESTOPBIT;
        dcbSerialParams.Parity = NOPARITY;
        if (!SetCommState(serialPort, &dcbSerialParams)) {
            CloseHandle(serialPort);
            throw std::runtime_error("Error setting serial port parameters.");
        }

        COMMTIMEOUTS timeouts = { 0 };
        timeouts.ReadIntervalTimeout = TIMEOUT_MS;
        timeouts.ReadTotalTimeoutConstant = TIMEOUT_MS;
        timeouts.ReadTotalTimeoutMultiplier = 10;
        timeouts.WriteTotalTimeoutConstant = TIMEOUT_MS;
        timeouts.WriteTotalTimeoutMultiplier = 10;
        if (!SetCommTimeouts(serialPort, &timeouts)) {
            CloseHandle(serialPort);
            throw std::runtime_error("Error setting serial port timeouts.");
        }
    }

    ~SerialPort() {
        if (serialPort != INVALID_HANDLE_VALUE) {
            CloseHandle(serialPort);
        }
    }

    void sendData(const char* data, int dataSize) {
        DWORD bytesWritten;
        if (!WriteFile(serialPort, data, dataSize, &bytesWritten, NULL)) {
            throw std::runtime_error("Error writing data to serial port.");
        }
    }

    std::string receiveData() {
        char dataReceived[100];
        DWORD bytesRead;
        if (!ReadFile(serialPort, dataReceived, sizeof(dataReceived), &bytesRead, NULL)) {
            throw std::runtime_error("Error reading data from serial port.");
        }
        return std::string(dataReceived, bytesRead);
    }

private:
    LPCWSTR portName;
    int baudRate;
    HANDLE serialPort;
};

// 打印指令类
std::string convertToHex(const std::string& input) {
    // 检查输入是否符合格式要求
    if (input.length() != 8 || input[0] != 'C' || input[4] != 'P') {
        return "Input incorrect should be CxxxPxxx";
    }

    // 将输入字符串拆分为数组
    char arr[8];
    for (int i = 0; i < 8; ++i) {
        arr[i] = input[i];
    }

    // 将数组中的数字部分转换为规定的数字
    std::string convertedStr = "43"; // 添加 '43'
    for (int i = 1; i < 8; ++i) {
        char ch = arr[i];
        if (i != 4) {
            int num = ch - '0';
            convertedStr += std::to_string(30 + num);
        }
        else {
            convertedStr += "50"; // 添加 '50' 表示 'P'
        }
    }

    return  "FA1B00527400080002000A000A0000000000" + convertedStr + "AAAA";
}
void formatData(const std::string& input, char* output) {
    for (size_t i = 0, j = 0; i < input.length(); i += 2, j++) {
        std::string byteStr = input.substr(i, 2);
        output[j] = static_cast<char>(std::stoi(byteStr, nullptr, 16));
    }
}

// 打印指令发送函数
void sendClearCommand(SerialPort& printerSerialPort) {
    const char printData[] = "\xFA\x06\x00\x51\x01\xAA\xAA";
    printerSerialPort.sendData(printData, sizeof(printData) - 1);
    std::this_thread::sleep_for(std::chrono::milliseconds(10)); // 等待响应
}
void sendDataCommand(SerialPort& printerSerialPort, std::string id) {
    std::string data1 = convertToHex(id);
    const size_t formattedDataSize = data1.length() / 2;
    char* formattedData = new char[formattedDataSize];
    formatData(data1, formattedData);
    printerSerialPort.sendData(formattedData, formattedDataSize);
    std::this_thread::sleep_for(std::chrono::milliseconds(10)); // 等待响应
}
void sendPrintCommand(SerialPort& printerSerialPort) {
    const char printData[] = "\xFA\x05\x00\x5F\xAA\xAA";
    printerSerialPort.sendData(printData, sizeof(printData) - 1);
    std::this_thread::sleep_for(std::chrono::milliseconds(10)); // 等待响应
}

//// 判断程序：判断数字是否匹配顺序数据
bool isMatch(double length) {
    if (matchingIndex < data_LoactiontoPrint.size() && length == data_LoactiontoPrint[matchingIndex]) {
        return true;
    }
    return false;
}

void increasematchingIndex() {
    matchingIndex++; // 增加 matchingIndex
    if (matchingIndex >= sequenceDataID.size()) {
        std::cerr << "Error: matchingIndex out of range." << std::endl;
        throw std::out_of_range("matchingIndex out of range");
    }
}

// 判断颜色墨盒
LPCWSTR getPortName(int colournumber) {
    switch (colournumber) {
    case 0: return L"COM9";
    case 1: return L"COM10";
    case 2: return L"COM11";
    case 3: return L"COM12";
    case 4: return L"COM13";
    default: return L"Invalid COM Port"; // Handle invalid color number
    }
}

int main() {
    try {
        // 从 CSV 文件中读取数据
        const std::string filename = "csvtoread.csv";
        CSVDataReader csvReader(filename);
        const std::vector<int>& data_LoactiontoPrint = csvReader.getSequenceData();
        const std::vector<std::string>& sequenceDataID = csvReader.getSequenceDataID();
        const std::vector<int>& sequenceDataColour = csvReader.getSequenceDataColour();

        // 初始化串口通信
        SerialPort arduinoSerialPort(ARDUINO_SERIAL_PORT, BAUD_RATE);

        int matchingIndex = 0;

        while (true) {
            std::string receivedData = arduinoSerialPort.receiveData();
            if (!receivedData.empty()) {
                // 处理接收到的数据
                int counterValue = std::stoi(receivedData);
                double length = 2 * 3.14 * radius * (counterValue / 720.0);
                std::cout << "Received: " << counterValue << " " << length;

                // 检查匹配
                if (matchingIndex < data_LoactiontoPrint.size() && counterValue == sequenceData[matchingIndex]) {
                    // 初始化串口通信
                    LPCWSTR PRINTER_SERIAL_PORT = getPortName(sequenceDataColour[matchingIndex]);
                    SerialPort printerSerialPort(PRINTER_SERIAL_PORT, BAUD_RATE);

                    // 发送打印指令
                    sendClearCommand(printerSerialPort);
                    std::cout << "\nCLEAR";

                    // 发送数据
                    std::string input = sequenceDataID[matchingIndex];
                    sendDataCommand(printerSerialPort, input);
                    std::cout << "\nDATA" << matchingIndex << " Printdata: " << input << " Colour: " << sequenceDataColour[matchingIndex];

                    // 发送打印指令
                    sendPrintCommand(printerSerialPort);
                    std::cout << "\nPRINT";

                    // 匹配成功，更新索引
                    matchingIndex++;
                }
                else {
                    std::cout << " Pass" << std::endl;
                }
                std::cout << std::endl;
            }
        }
    }
    catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        std::cerr << "Terminating program." << std::endl;
        return 1;
    }
    std::cout << "Program terminated." << std::endl;
    return 0;
}