/*
Author: huiyenchia
update: 13/05/2024
function:
- Initializes serial communication with multiple devices, including encoders and printers.
- Reads positional data from an encoder to track the real-time position of the system.
- Matches the position to pre-defined print locations and triggers the corresponding print action.
- Processes print commands using specific IDs and colors based on CSV input.
- Implements error handling and ensures synchronized communication between devices.
*/

#include <iostream>
#include <sstream>
#include <string>
#include <Windows.h>
#include <iomanip>
#include <stdexcept>
#include <chrono>
#include <thread>
#include <vector>
#include <cmath>
#include "CSVDataReader.h"

// Define the constant based on hardware connections
const LPCWSTR ENCODER_SERIAL_PORT = L"COM6";//Rotate encoder
const LPCWSTR COLOUR0_SERIAL_PORT = L"COM16";//printhead 1
const LPCWSTR COLOUR1_SERIAL_PORT = L"COM8";//printhead 2
const LPCWSTR COLOUR2_SERIAL_PORT = L"COM8";//printhead 3
const LPCWSTR COLOUR3_SERIAL_PORT = L"COM9";//printhead 4
const LPCWSTR COLOUR4_SERIAL_PORT = L"COM10";//printhead 5
const double radius = 30; //radius of measuring wheel
const int BAUD_RATE = CBR_115200; //Baud rate
const int TIMEOUT_MS = 10; 
const std::string filename = "csvtoRead.csv"; //csv file name to read
const std::string PREFIXCOMMAND = "FA1B00527400080002000A000A000000000043"; //fixed due to the setting of hardware 

// ReadCSVData
CSVDataReader csvReader(filename);
const std::vector<double>& csv_Location = csvReader.getCsvLocation();//Printing location
const std::vector<std::string>& csv_ID = csvReader.getCsvID();//Printing content
const std::vector<int>& csv_Colour = csvReader.getCsvColour();//Printing color
int matchingIndex = 0; //the index of data to print

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

std::string convertToHex(const std::string& input) {
    // Check data format
    if (input.length() != 8 || input[0] != 'C' || input[4] != 'P') {
        return "Input incorrect should be CxxxPxxx";
    }

    std::ostringstream oss;
    oss << PREFIXCOMMAND;

    for (int i = 1; i < 8; ++i) {
        if (i != 4) {
            int num = input[i] - '0';
            oss << (30 + num); //num convert to code
        }
        else {
            oss << "50"; //P
        }

        oss << "AAAA"; //end of the number
        return oss.str();
    }
}

void formatData(const std::string& input, char* output) {
    for (size_t i = 0, j = 0; i < input.length(); i += 2, j++) {
        std::string byteStr = input.substr(i, 2);
        output[j] = static_cast<char>(std::stoi(byteStr, nullptr, 16));
    }
}

void sendClearCommand(SerialPort& printerSerialPort) {
    const char printData[] = "\xFA\x06\x00\x51\x01\xAA\xAA";
    printerSerialPort.sendData(printData, sizeof(printData) - 1);
    std::this_thread::sleep_for(std::chrono::milliseconds(10));
}
void sendDataCommand(SerialPort& printerSerialPort, std::string id) {
    std::string data1 = convertToHex(id);
    const size_t formattedDataSize = data1.length() / 2;
    char* formattedData = new char[formattedDataSize];
    formatData(data1, formattedData);
    printerSerialPort.sendData(formattedData, formattedDataSize);
    std::this_thread::sleep_for(std::chrono::milliseconds(10));
}
void sendPrintCommand(SerialPort& printerSerialPort) {
    const char printData[] = "\xFA\x05\x00\x5F\xAA\xAA";
    printerSerialPort.sendData(printData, sizeof(printData) - 1);
    std::this_thread::sleep_for(std::chrono::milliseconds(10));
}


/*
Update matching index
*/
void updateMatchingIndex() {
    matchingIndex++;
    if (matchingIndex >= csv_ID.size()) {
        std::cerr << "Error: matchingIndex out of range." << std::endl;
        throw std::out_of_range("matchingIndex out of range");
    }
}

/*
Get the printhead portName based on colorNumber
*/
LPCWSTR getPortName(int colournumber) {
    switch (colournumber) {
    case 0: return COLOUR0_SERIAL_PORT;
    case 1: return COLOUR1_SERIAL_PORT;
    case 2: return COLOUR2_SERIAL_PORT;
    case 3: return COLOUR3_SERIAL_PORT;
    case 4: return COLOUR4_SERIAL_PORT;
    default: return L"Invalid COM Port"; // Handle invalid color number
    }
}

int main() {
    try {
        //Read data from csv
        const std::string filename = "csvtoRead.csv";
        CSVDataReader csvReader(filename);
        const std::vector<double>& csv_Location = csvReader.getCsvLocation();
        const std::vector<std::string>& csv_ID = csvReader.getCsvID();
        const std::vector<int>& csv_Colour = csvReader.getCsvColour();

        // Initialize serial port
        SerialPort ENCODERSerialPort(ENCODER_SERIAL_PORT, BAUD_RATE);

        int matchingIndex = 0;
        int counterValue = 0;

        while (true) {
            std::string receivedData = ENCODERSerialPort.receiveData();
            if (!receivedData.empty()) {
                // Process the incomming signal
                int counter = std::stoi(receivedData);
                counterValue++;

                //Get real-time length
                double length = 2 * 3.1415 * radius * (counterValue / 360.0); 
                int length_round = static_cast<int>(std::round(length)); 
                std::cout << "Received_counterValue: " << counterValue << "Received_length_round: " << length_round;
                std::cout << "\nDATA" << matchingIndex << " Printdata: " << csv_Location[matchingIndex] << " Colour: " << csv_Colour[matchingIndex];

                // check match states
                if (matchingIndex < csv_Location.size() && length_round == csv_Location[matchingIndex]) {
                    // Initialize printer serial port
                    LPCWSTR PRINTER_SERIAL_PORT = getPortName(csv_Colour[matchingIndex]);
                    SerialPort printerSerialPort(PRINTER_SERIAL_PORT, BAUD_RATE);

                    // Send clear command
                    sendClearCommand(printerSerialPort);
                    std::cout << "\nCLEAR";

                    // Send to-print-data
                    std::string input = csv_ID[matchingIndex];
                    sendDataCommand(printerSerialPort, input);
                    std::cout << "\nDATA" << matchingIndex << " Printdata: " << input << " Colour: " << csv_Colour[matchingIndex];

                    // Send print command to print
                    sendPrintCommand(printerSerialPort);
                    std::cout << "\nPRINT";

                    // Matched, update index
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