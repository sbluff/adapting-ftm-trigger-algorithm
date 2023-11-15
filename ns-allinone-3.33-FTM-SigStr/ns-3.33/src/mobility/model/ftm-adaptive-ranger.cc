#include "ftm-adaptive-ranger.h"

// constructor of the class
FtmAdaptiveRanger::FtmAdaptiveRanger()
{
    version = 1.1;
    state = "brownian";
    transition = false;
    same_state_counter = 0;
    std_deviation = 0;

    brownian_data = ReadCsv("ftm_ranging/simulations/data/data-brownian.csv");
    fix_position_data = ReadCsv("ftm_ranging/simulations/data/data-fix_position.csv");

    parameters.SetMinDeltaFtm(15);
    parameters.SetBurstDuration(7);
    parameters.SetNumberOfBurstsExponent(1);
    parameters.SetBurstPeriod(7);
    parameters.SetFtmsPerBurst(4);

    LoadStatisticalVariables();
    // minutes
    simulation_time = ns3::Minutes(2);
}

// returns the version of the algorithm
// v0: static algorithm
// v1: two static configurations
// v1.1: smoothness in burst_exponent between static configs
double
FtmAdaptiveRanger::GetVersion()
{
    return version;
}

// returns the time passed to the ns3 simulator
ns3::Time
FtmAdaptiveRanger::GetSimulationTime()
{
    return simulation_time;
}

// returns the current value FTM parameters of the algorithm
ns3::FtmParams
FtmAdaptiveRanger::GetParameters()
{
    return parameters;
}

// returns all the RTT measured during the execution of the algorithm
std::vector<std::pair<std::string, double>>
FtmAdaptiveRanger::GetHistRtt()
{
    return hist_rtt;
}

// returns the last RTT obtaines in the execution of the algorithm
std::pair<std::string, double>
FtmAdaptiveRanger::GetLastRtt()
{
    if (hist_rtt.size() > 0)
        return hist_rtt[0];
    else
        return std::make_pair("empty", 0);
}

// returns the counter on how many sessions the algorithm has perceived the same
// state
int FtmAdaptiveRanger::GetSameStateCounter()
{
    return same_state_counter;
}

// adds an entry to the hist_rtt attribute
void FtmAdaptiveRanger::AddRtt(double rtt)
{
    hist_rtt.insert(hist_rtt.begin(), std::make_pair(state, rtt));
}

// generates a string with the format
// MinDeltaFtm-BurstPeriod-BurstExponent-BurstDuration-FtmPerBurst
std::string
FtmAdaptiveRanger::GenerateParameterKey()
{
    return std::to_string(parameters.GetMinDeltaFtm()) + "-" +
           std::to_string(parameters.GetBurstPeriod()) + "-" +
           std::to_string(parameters.GetNumberOfBurstsExponent()) + "-" +
           std::to_string(parameters.GetBurstDuration()) + "-" +
           std::to_string(parameters.GetFtmsPerBurst());
}

// shows in screen the values of brownian_statistical_data &
// fix_position_statistical_data
void FtmAdaptiveRanger::DisplayStats()
{
    std::map<std::string, std::map<std::string, double>> *statistical_data =
        (state == "brownian")
            ? &brownian_statistical_data
            : &fix_position_statistical_data; // update the pointer to the current data structure

    std::cout << state << std::endl;
    for (std::map<std::string, std::map<std::string, double>>::const_iterator it = (*statistical_data).begin(); it != (*statistical_data).end(); ++it)
    {
        std::cout << it->first << "\n";
    }
}

// Reads a CSV file into a std::vector of <string, std::vector<int>> pairs where
// each pair represents <column name, column values>
std::vector<std::pair<std::string, std::vector<double>>>
FtmAdaptiveRanger::ReadCsv(std::string filename)
{
    std::cout << filename << std::endl;
    // Create a std::vector of <string, int std::vector> pairs to store the result
    std::vector<std::pair<std::string, std::vector<double>>> result;

    // Create an input filestream
    std::ifstream myFile(filename);

    // Make sure the file is open
    if (!myFile.is_open())
        throw std::runtime_error("Could not open file");

    // Helper vars
    std::string line, colname;
    double val;

    int colIdx = 0;
    // Read the column names
    if (myFile.good())
    {
        // Extract the first line in the file
        std::getline(myFile, line);

        // Create a stringstream from line
        std::stringstream ss(line);

        // Extract each column name
        while (std::getline(ss, colname, ','))
        {
            // Initialize and add <colname, double std::vector> pairs to result
            result.push_back({colname, std::vector<double>{}});

            colIdx++;
        }
    }

    // Read data, line by line
    while (std::getline(myFile, line))
    {
        // Create a stringstream of the current line
        std::stringstream ss(line);
        // Keep track of the current column index
        colIdx = 0;
        // Extract each integer
        while (ss >> val)
        {
            // Add the current integer to the 'colIdx' column's values std::vector
            result.at(colIdx).second.push_back(val);
            // If the next token is a comma, ignore it and move on

            if (ss.peek() == ',')
                ss.ignore();

            // Increment the column index
            colIdx++;
        }
    }

    // Close file
    myFile.close();
    return result;
}

// handle the transition when an rtt increase is NOT detected
void FtmAdaptiveRanger::HandleTransitionFixPosition(std::string &new_state, bool &config_change)
{
    transition = false;
    new_state = "fix_position";
    config_change = true;
    if (state == "brownian")
    {
        same_state_counter = 0;
    }
    else if (state == "fix_position")
    {
        same_state_counter++;
    }
    std::cout << same_state_counter << std::endl;
    SetFixPositionParameters();
}

// handle the transition when an rtt increase is detected
void FtmAdaptiveRanger::HandleTransitionBrownian(std::string &new_state, bool &config_change)
{
    transition = false;
    new_state = "brownian";
    if (state == "brownian")
    {
        same_state_counter++;
    }
    else if (state == "fix_position")
    {
        config_change = true;
        same_state_counter = 0;
    }
    SetBrownianParameters();
}

// based on the "parameters" and "state" (filter ), updates the value of the
// following global variables:
//     -distribution_mean
//     -standard_deviation
void FtmAdaptiveRanger::LoadStatisticalVariables()
{

    std::string map_key = GenerateParameterKey();
    std::map<std::string, std::map<std::string, double>> *statistical_data =
        (state == "brownian")
            ? &brownian_statistical_data
            : &fix_position_statistical_data; // update the pointer to the current data structure

    if ((*statistical_data).find(map_key) == (*statistical_data).end())
    { // its the first time this configuration is used, lets calculate the statistical values an store them
        double mean_error = 0;
        double mean_distance = 0;
        int count = 0;
        bool same_configuration = false;
        std::vector<std::pair<std::string, std::vector<double>>> *data =
            (state == "brownian") ? &brownian_data
                                  : &fix_position_data; // update the pointer to the
                                                        // current data structure

        for (unsigned i = 0; i < (*data)[3].second.size(); i++)
        {
            same_configuration =
                (*data)[3].second[i] == double(parameters.GetMinDeltaFtm()) &&
                (*data)[4].second[i] == double(parameters.GetBurstPeriod()) &&
                (*data)[5].second[i] == double(parameters.GetNumberOfBurstsExponent()) &&
                (*data)[6].second[i] == double(parameters.GetBurstDuration()) &&
                (*data)[7].second[i] == double(parameters.GetFtmsPerBurst());
            if (same_configuration)
            {
                mean_error += (*data)[8].second[i];
                mean_distance += (*data)[1].second[i];
                count++;
            }
        }
        mean_error = double(mean_error / count);
        mean_distance = double(mean_distance / count);

        std_deviation = 0;
        for (unsigned i = 0; i < (*data)[3].second.size(); i++)
        {
            // same_configuration = (*data)[3].second[i] ==
            // double(parameters.GetMinDeltaFtm()) && (*data)[4].second[i] ==
            // double(parameters.GetBurstPeriod()) && (*data)[5].second[i] ==
            // double(parameters.GetNumberOfBurstsExponent()) && (*data)[6].second[i] ==
            // double(parameters.GetBurstDuration()) && (*data)[7].second[i] ==
            // double(parameters.GetFtmsPerBurst()) ; same_configuration =
            // (*data)[3].second[i] == double(parameters.GetMinDeltaFtm()) &&
            // (*data)[4].second[i] == double(parameters.GetBurstPeriod()) &&
            // (*data)[5].second[i] == double(parameters.GetNumberOfBurstsExponent()) &&
            // (*data)[6].second[i] == double(parameters.GetBurstDuration()) &&
            // (*data)[7].second[i] == double(parameters.GetFtmsPerBurst()) ;
            same_configuration =
                (*data)[3].second[i] == double(parameters.GetMinDeltaFtm()) &&
                (*data)[4].second[i] == double(parameters.GetBurstPeriod()) &&
                (*data)[5].second[i] == double(parameters.GetNumberOfBurstsExponent()) &&
                (*data)[6].second[i] == double(parameters.GetBurstDuration()) &&
                (*data)[7].second[i] == double(parameters.GetFtmsPerBurst());
            if (same_configuration)
            {
                std_deviation += std::pow((*data)[8].second[i] - mean_error, 2);
            }
        }
        std_deviation = std::sqrt(double(std_deviation / count));

        (*statistical_data)[map_key]["count"] = count;
        (*statistical_data)[map_key]["mean_distance"] = mean_distance;
        (*statistical_data)[map_key]["mean_error"] = mean_error;
        (*statistical_data)[map_key]["mean_error_p"] =
            double(mean_error / mean_distance);
        (*statistical_data)[map_key]["std_deviation"] = std_deviation;
        (*statistical_data)[map_key]["std_deviation_p"] =
            double(std_deviation / mean_distance);
    }

    else
    {
        std::cout << "I red the value from memory!" << std::endl;
    }

    std_deviation = (*statistical_data)[map_key]["std_deviation_p"];
}

// sets the values for the ftm parameters running under the brownian state
void FtmAdaptiveRanger::SetBrownianParameters()
{
    parameters.SetMinDeltaFtm(15);
    parameters.SetNumberOfBurstsExponent(1);
    parameters.SetFtmsPerBurst(4);
    parameters.SetBurstDuration(7);
    parameters.SetBurstPeriod(7);
}

// sets the values for the ftm parameters running under the fix_position state
void FtmAdaptiveRanger::SetFixPositionParameters()
{
    parameters.SetMinDeltaFtm(15);
    parameters.SetBurstDuration(10);
    parameters.SetNumberOfBurstsExponent((parameters.GetNumberOfBurstsExponent() < 4 && same_state_counter < 8) ? (1 + same_state_counter / 2) : 4);
    parameters.SetBurstPeriod(10);
    parameters.SetFtmsPerBurst(5);
}

// based on the last RTT measurements, the current state and some statistical
// variables; update the state and set new values to ftm parameters
void FtmAdaptiveRanger::Analysis()
{
    bool config_change = false;
    std::string new_state = state;
    // there has been a change in the expected RTT
    if (hist_rtt.size() > 2)
    {
        double rtt_change_percentage = abs(hist_rtt[0].second - hist_rtt[1].second) / hist_rtt[1].second;
        std::cout << "rtt_change_percentage: " << rtt_change_percentage << " std_deviation: " << std_deviation << std::endl;
        if (rtt_change_percentage > std_deviation)
        { // movement perceived
            if (!transition)
                HandleTransitionBrownian(new_state, config_change);
            else if (state == "fix_position")
                transition = !transition;
        }

        else
        { // movement was not perceived
            if (!transition && state == "brownian")
                transition = !transition;

            HandleTransitionFixPosition(new_state, config_change);
        }
    }

    state = new_state;
    LoadStatisticalVariables();
    if (config_change)
    {
        DisplayStats();
    }
    std::string aux = (transition) ? " transition" : " NO transition";
    std::cout << "new_state: " << new_state << aux << std::endl;
    std::cout << "-------------" << std::endl;
}