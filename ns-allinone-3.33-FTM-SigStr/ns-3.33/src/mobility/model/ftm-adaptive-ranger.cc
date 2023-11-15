#include "ftm-adaptive-ranger.h"

//constructor of the class
FtmAdaptiveRanger::FtmAdaptiveRanger(){
    version = 1.1;
    state = "brownian";
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
    //minutes
    simulation_time = ns3::Minutes(10);
}

// returns the version of the algorithm
// v0: static algorithm
// v1: two static configurations
// v1.1: smoothness in burst_exponent between static configs
double
FtmAdaptiveRanger::GetVersion(){
    return version;
}

//returns the time passed to the ns3 simulator
ns3::Time
FtmAdaptiveRanger::GetSimulationTime(){
    return simulation_time;
}

//returns the current value FTM parameters of the algorithm
ns3::FtmParams
FtmAdaptiveRanger::GetParameters(){
    return parameters;
}

//returns all the RTT measured during the execution of the algorithm
std::vector<std::pair<std::string, double>> 
FtmAdaptiveRanger::GetHistRtt(){
    return hist_rtt;
}

//returns the last RTT obtaines in the execution of the algorithm
std::pair<std::string, double> 
FtmAdaptiveRanger::GetLastRtt(){
    if (hist_rtt.size() > 0)
        return hist_rtt[0];
    else 
        return std::make_pair("empty", 0);    
}

//returns the counter on how many sessions the algorithm has perceived the same state
int 
FtmAdaptiveRanger::GetSameStateCounter(){
    return same_state_counter;
}

//adds an entry to the hist_rtt attribute
void
FtmAdaptiveRanger::AddRtt(double rtt){
    hist_rtt.insert(hist_rtt.begin(), std::make_pair(state, rtt));
    std::cout << "Rtt entry added: " << state << " " << rtt << std::endl;
}

// Reads a CSV file into a std::vector of <string, std::vector<int>> pairs where
// each pair represents <column name, column values>
std::vector<std::pair<std::string, std::vector<double>>> 
FtmAdaptiveRanger::ReadCsv(std::string filename){
    std::cout << filename << std::endl;
    // Create a std::vector of <string, int std::vector> pairs to store the result
    std::vector<std::pair<std::string, std::vector<double>>> result;

    // Create an input filestream
    std::ifstream myFile(filename);

    // Make sure the file is open
    if(!myFile.is_open()) throw std::runtime_error("Could not open file");

    // Helper vars
    std::string line, colname;
    double val;


    int colIdx = 0;
    // Read the column names
    if(myFile.good())
    {
        // Extract the first line in the file
        std::getline(myFile, line);

        // Create a stringstream from line
        std::stringstream ss(line);

        // Extract each column name
        while(std::getline(ss, colname, ',')){
            // Initialize and add <colname, double std::vector> pairs to result
            result.push_back({colname, std::vector<double> {}});

            colIdx++;    
        }
    }

    // Read data, line by line
    while(std::getline(myFile, line))
    {
        // Create a stringstream of the current line
        std::stringstream ss(line);
        // Keep track of the current column index
        colIdx = 0;        
        // Extract each integer
        while(ss >> val){
            // Add the current integer to the 'colIdx' column's values std::vector
            result.at(colIdx).second.push_back(val);
            // If the next token is a comma, ignore it and move on
            
            if(ss.peek() == ',') ss.ignore();
            
            // Increment the column index
            colIdx++;
        }
    }

    // Close file
    myFile.close();
    return result;
}

//based on the "parameters" and "state" (filter ), updates the value of the following global variables:
//    -distribution_mean
//    -standard_deviation
void 
FtmAdaptiveRanger::LoadStatisticalVariables(){
    double total_mean_percentage = 0;
    double total_mean = 0;
    double mean_distance = 0;
    int count = 0;
    bool same_configuration = false;
    std::vector<std::pair<std::string, std::vector<double>>>* data = (state == "brownian") ? &brownian_data : &fix_position_data;

    for (unsigned i = 0; i < (*data)[3].second.size(); i++){
        same_configuration = (*data)[3].second[i] == double(parameters.GetMinDeltaFtm()) && (*data)[4].second[i] == double(parameters.GetBurstPeriod()) && (*data)[5].second[i] == double(parameters.GetNumberOfBurstsExponent()) && (*data)[6].second[i] == double(parameters.GetBurstDuration()) && (*data)[7].second[i] == double(parameters.GetFtmsPerBurst()) ;
        if (same_configuration){
            total_mean_percentage += ((*data)[8].second[i]/(*data)[1].second[i]); 
            total_mean += (*data)[8].second[i]; 
            mean_distance += (*data)[1].second[i];
            count++;
        }
    }
    total_mean_percentage = double(total_mean_percentage/count) * 100;
    total_mean = double(total_mean/count);
    mean_distance = double(mean_distance / count);
    std::cout << total_mean  << "m mean error" << std::endl;
    std::cout << mean_distance  << "m mean distance between nodes" << std::endl;
    std::cout << total_mean_percentage << "% mean error" << std::endl;

    std_deviation = 0;
    for (unsigned i = 0; i < (*data)[3].second.size(); i++){
        // same_configuration = (*data)[3].second[i] == double(parameters.GetMinDeltaFtm()) && (*data)[4].second[i] == double(parameters.GetBurstPeriod()) && (*data)[5].second[i] == double(parameters.GetNumberOfBurstsExponent()) && (*data)[6].second[i] == double(parameters.GetBurstDuration()) && (*data)[7].second[i] == double(parameters.GetFtmsPerBurst()) ;
        // same_configuration = (*data)[3].second[i] == double(parameters.GetMinDeltaFtm()) && (*data)[4].second[i] == double(parameters.GetBurstPeriod()) && (*data)[5].second[i] == double(parameters.GetNumberOfBurstsExponent()) && (*data)[6].second[i] == double(parameters.GetBurstDuration()) && (*data)[7].second[i] == double(parameters.GetFtmsPerBurst()) ;
        same_configuration = (*data)[3].second[i] == double(parameters.GetMinDeltaFtm()) && (*data)[4].second[i] == double(parameters.GetBurstPeriod()) && (*data)[5].second[i] == double(parameters.GetNumberOfBurstsExponent()) && (*data)[6].second[i] == double(parameters.GetBurstDuration()) && (*data)[7].second[i] == double(parameters.GetFtmsPerBurst()) ;        
        if (same_configuration){
            std_deviation += std::pow((*data)[8].second[i] - total_mean, 2); 
        }


    }
    std_deviation = std::sqrt(double(std_deviation/count))/mean_distance;
    std::cout << std_deviation  << "% std deviation" << std::endl;
}

//based on the last RTT measurements, the current state and some statistical variables; update the state and set new values to ftm parameters
void 
FtmAdaptiveRanger::Analysis(){
    bool config_change = false;
    std::string _state = state;
    //there has been a change in the expected RTT
    if (hist_rtt.size() > 2){
        if ((abs(hist_rtt[0].second - hist_rtt[1].second)/hist_rtt[1].second) > std_deviation){
            std::cout << "Change detected: " << (abs(hist_rtt[0].second - hist_rtt[1].second)/hist_rtt[1].second) << "% (std_dev(%):" << std_deviation << std::endl;
            if (state == "fix_position"){
                _state="transition";
            } 
            else if (state == "transition"){
                _state="brownian";
                if (hist_rtt[2].first != "brownian")
                    same_state_counter = 0;
                else    
                    same_state_counter++;
                parameters.SetNumberOfBurstsExponent(1);
                parameters.SetFtmsPerBurst(4);
                parameters.SetBurstDuration(7);
                parameters.SetBurstPeriod(7);
                config_change = true;
            } 
            else if (state == "brownian"){
                same_state_counter++;
            } 
        }

        //not moving and last state was brownian
        else if (state == "brownian"){
            _state = "transition";
        }

        //not moving and last state was fix_position
        else if (state == "fix_position"){
            parameters.SetMinDeltaFtm(15);
            parameters.SetBurstDuration(10);
            parameters.SetNumberOfBurstsExponent(parameters.GetNumberOfBurstsExponent() < 4 ? (1 + same_state_counter/2) : 4);
            parameters.SetBurstPeriod(10);
            parameters.SetFtmsPerBurst(5);
            same_state_counter++;
            config_change = true;
        }

        //not moving and last state was fix_position
        else if (state == "transition"){
            _state = "fix_position";
            if (hist_rtt[2].first != "fix_position")
                same_state_counter = 0;
            else    
                same_state_counter++;
            same_state_counter = 0;
            parameters.SetMinDeltaFtm(15);
            parameters.SetBurstDuration(10);
            parameters.SetNumberOfBurstsExponent(parameters.GetNumberOfBurstsExponent() < 4 ? (1 + same_state_counter/2) : 4);
            parameters.SetBurstPeriod(10);
            parameters.SetFtmsPerBurst(5);
            config_change = true;
        }
    }

    if (config_change){
        LoadStatisticalVariables();
        std::cout << "-------------" << std::endl;
    }
    state = _state;
}