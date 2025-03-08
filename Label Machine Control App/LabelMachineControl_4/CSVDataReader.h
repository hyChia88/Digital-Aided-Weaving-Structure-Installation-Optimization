#ifndef CSVDATAREADER_H
#define CSVDATAREADER_H

#include <vector>
#include <string>

class CSVDataReader {
public:
    CSVDataReader(const std::string& filename);

    const std::vector<double>& getCsvLocation() const;
    const std::vector<std::string>& getCsvID() const;
    const std::vector<int>& getCsvColour() const;

private:
    void readCSV(const std::string& filename);
    std::vector<int> before_csv_Location;
    std::vector<std::string> csv_ID;
    std::vector<int> csv_Colour;
    mutable std::vector<double> csv_Location; // for storing
};

#endif
