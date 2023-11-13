#include <vector>

class FtmAdaptiveRanger{
    public:
        FtmAdaptiveRanger();
        ns3::FtmParams GetParameters();
        ns3::Time GetSimulationTime();
        std::vector<std::pair<std::string, double>> GetHistRtt();
        std::pair<std::string, double> GetLastRtt();
        int GetSameStateCounter();
        void AddRtt(double rtt);
        void Analysis();

    private:
        ns3::FtmParams parameters; 

        double std_deviation;
        int same_state_counter;
        ns3::Time simulation_time;


        std::vector<std::pair<std::string, std::vector<int>>> brownian_data;
        std::vector<std::pair<std::string, std::vector<int>>> fix_position_data;
        std::vector<std::pair<std::string, double>> hist_rtt;
        std::string state;

        double LoadStatisticalVariables();
        static std::vector<std::pair<std::string, std::vector<int>>> ReadCsv(std::string filename);
        
};

