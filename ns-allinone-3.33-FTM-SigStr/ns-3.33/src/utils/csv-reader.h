#ifndef CSV_READER_H    // To make sure you don't declare the function more than once by including the header multiple times.
#define CSV_READER_H

#include <iostream>
#include <string>
#include <vector>
#include <fstream>
#include <utility> // std::pair
#include <stdexcept> // std::runtime_error
#include <sstream> // std::stringstream

std::vector<std::pair<std::string, std::vector<int>>> read_csv(std::string filename);


#endif