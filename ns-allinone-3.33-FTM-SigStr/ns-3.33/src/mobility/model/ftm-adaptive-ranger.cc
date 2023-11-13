#include "ftm-adaptive-ranger.h"

//constructor of the class
FtmAdaptiveRanger::FtmAdaptiveRanger(){
    parameters.SetMinDeltaFtm(15);
    parameters.SetBurstDuration(8);
    parameters.SetNumberOfBurstsExponent(1);
    parameters.SetBurstPeriod(8);
    parameters.SetFtmsPerBurst(5);

    //minutes
    simulation_time = ns3::Minutes(1);

    same_state_counter = 0;
    state = "fix_position";
    std_deviation = 0;


    brownian_data = ReadCsv("ftm_ranging/simulations/data/data-brownian.csv");
    fix_position_data = ReadCsv("ftm_ranging/simulations/data/data-fix_position.csv");
}

ns3::Time
FtmAdaptiveRanger::GetSimulationTime(){
    return simulation_time;
}

ns3::FtmParams
FtmAdaptiveRanger::GetParameters(){
    return parameters;
}

std::vector<std::pair<std::string, double>> 
FtmAdaptiveRanger::GetHistRtt(){
    return hist_rtt;
}

std::pair<std::string, double> 
FtmAdaptiveRanger::GetLastRtt(){
    if (hist_rtt.size() > 0)
        return hist_rtt[0];
    else 
        return std::make_pair("empty", 0);    
}

int 
FtmAdaptiveRanger::GetSameStateCounter(){
    return same_state_counter;
}

void
FtmAdaptiveRanger::AddRtt(double rtt){
    hist_rtt.insert(hist_rtt.begin(), std::make_pair(state, rtt));
    std::cout << "Rtt entry added: " << state << " " << rtt << std::endl;
}

    // Reads a CSV file into a std::vector of <string, std::vector<int>> pairs where
// each pair represents <column name, column values>
std::vector<std::pair<std::string, std::vector<int>>> 
FtmAdaptiveRanger::ReadCsv(std::string filename){
    // Create a std::vector of <string, int std::vector> pairs to store the result
    std::vector<std::pair<std::string, std::vector<int>>> result;

    // Create an input filestream
    std::ifstream myFile(filename);

    // Make sure the file is open
    if(!myFile.is_open()) throw std::runtime_error("Could not open file");

    // Helper vars
    std::string line, colname;
    int val;

    // Read the column names
    if(myFile.good())
    {
        // Extract the first line in the file
        std::getline(myFile, line);

        // Create a stringstream from line
        std::stringstream ss(line);

        // Extract each column name
        while(std::getline(ss, colname, ',')){
            
            // Initialize and add <colname, int std::vector> pairs to result
            result.push_back({colname, std::vector<int> {}});
        }
    }

    // Read data, line by line
    while(std::getline(myFile, line))
    {
        // Create a stringstream of the current line
        std::stringstream ss(line);
        
        // Keep track of the current column index
        int colIdx = 0;
        
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
double 
FtmAdaptiveRanger::LoadStatisticalVariables(){
    return 0.0;
}

void 
FtmAdaptiveRanger::Analysis(){
    //there has been a change in the expected RTT
    if (hist_rtt.size() > 1 && abs(hist_rtt[0].second-hist_rtt[1].second)/hist_rtt[1].second > 0.05){
        if (state == "fix_position"){
            state="transition";
        } 
        else if (state == "transition"){
            state="brownian";
            if (hist_rtt[2].first != "brownian")
                same_state_counter = 0;
            else    
                same_state_counter++;
            parameters.SetNumberOfBurstsExponent(1);
            parameters.SetFtmsPerBurst(4);
            parameters.SetBurstDuration(7);
            parameters.SetBurstPeriod(7);
        } 
        else if (state == "brownian"){
            same_state_counter++;
        } 
    }

    //not moving and last state was brownian
    else if (state == "brownian"){
        state = "transition";
    }

    //not moving and last state was fix_position
    else if (state == "fix_position"){
        parameters.SetNumberOfBurstsExponent((parameters.GetNumberOfBurstsExponent() < 4) ? (1 + (same_state_counter / 5)) : 4);
        parameters.SetFtmsPerBurst((parameters.GetFtmsPerBurst() < 5 ) ? (5 + (same_state_counter/2)) : 5);
        parameters.SetBurstDuration((parameters.GetBurstDuration() < 11) ? (8 + (same_state_counter / 2)) : 11);
        parameters.SetBurstPeriod((parameters.GetBurstPeriod() < 12) ? (8 + (same_state_counter / 2)) : 12);
        same_state_counter++;

    }

    //not moving and last state was fix_position
    else if (state == "transition"){
        state = "fix_position";
        if (hist_rtt[2].first != "fix_position")
            same_state_counter = 0;
        else    
            same_state_counter++;
        same_state_counter = 0;
        parameters.SetNumberOfBurstsExponent(1);
        parameters.SetFtmsPerBurst(5);
        parameters.SetBurstDuration(8);
        parameters.SetBurstPeriod(8);
    }

}