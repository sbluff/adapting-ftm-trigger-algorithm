#include <vector>
#include <algorithm>
#include <math.h>

class FtmAdaptiveRanger{
    public:
        FtmAdaptiveRanger();
        ns3::FtmParams GetParameters();
        ns3::Time GetSimulationTime();
        std::vector<std::pair<std::string, double>> GetHistRtt();
        std::pair<std::string, double> GetLastRtt();
        double GetVersion();
        int GetSameStateCounter();
        void AddRtt(double rtt);
        void Analysis();

    private:
        ns3::FtmParams parameters; 

        double std_deviation;
        int same_state_counter;
        ns3::Time simulation_time;
        double version;


        std::vector<std::pair<std::string, std::vector<double>>> brownian_data;
        std::vector<std::pair<std::string, std::vector<double>>> fix_position_data;
        std::vector<std::pair<std::string, double>> hist_rtt;
        std::string state;

        void LoadStatisticalVariables();
        static std::vector<std::pair<std::string, std::vector<double>>> ReadCsv(std::string filename);
        
};

