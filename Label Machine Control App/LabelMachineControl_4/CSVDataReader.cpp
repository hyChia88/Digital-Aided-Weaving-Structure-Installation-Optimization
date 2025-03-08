#include "CSVDataReader.h"
#include <fstream>
#include <sstream>

CSVDataReader::CSVDataReader(const std::string& filename) {
    readCSV(filename);
}

void CSVDataReader::readCSV(const std::string& filename) {
    std::ifstream file(filename);
    std::string line;

    while (std::getline(file, line)) {
        std::stringstream ss(line);
        std::string item;
        std::vector<std::string> tokens;

        while (std::getline(ss, item, ',')) {
            tokens.push_back(item);
        }

        if (tokens.size() == 3) {
            before_csv_Location.push_back(std::stoi(tokens[0]));
            csv_ID.push_back(tokens[1]);
            csv_Colour.push_back(std::stoi(tokens[2]));
        }
    }
}

const std::vector<double>& CSVDataReader::getCsvLocation() const {
    csv_Location.clear();
    for (size_t i = 0; i < before_csv_Location.size(); ++i) {
        csv_Location.push_back(before_csv_Location[i] + csv_Colour[i] * 31);
    }
    return csv_Location;
}

const std::vector<std::string>& CSVDataReader::getCsvID() const {
    return csv_ID;
}

const std::vector<int>& CSVDataReader::getCsvColour() const {
    return csv_Colour;
}
