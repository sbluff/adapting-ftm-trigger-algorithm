#include "ns3/command-line.h"
#include "ns3/config.h"
#include "ns3/double.h"
#include "ns3/string.h"
#include "ns3/log.h"
#include "ns3/yans-wifi-helper.h"
#include "ns3/ssid.h"
#include "ns3/mobility-helper.h"
#include "ns3/ipv4-address-helper.h"
#include "ns3/yans-wifi-channel.h"
#include "ns3/mobility-model.h"
#include "ns3/mobility-module.h"
#include "ns3/internet-stack-helper.h"
#include "ns3/wifi-net-device.h"
#include "ns3/ap-wifi-mac.h"
#include "ns3/sta-wifi-mac.h"
#include "ns3/ftm-header.h"
#include "ns3/mgt-headers.h"
#include "ns3/ftm-error-model.h"
#include "ns3/pointer.h"
#include <vector>

using namespace ns3;

NS_LOG_COMPONENT_DEFINE ("FtmAdaptiveAlgorithm");

Ptr<WirelessFtmErrorModel::FtmMap> map;
Ptr<WifiNetDevice> _ap;
Ptr<WifiNetDevice> _sta;
Address recvAddr;
double t1;
double t2; 
int session_counter = 0;
int measurements = 20000;
int analysis_window = 10;
int same_state_counter = 0;
std::vector<double> hist_rtt;
std::string state = "fix_position";
double intial_distance = 10.0;

bool dynamic_mode = false;
double simulation_time = 4;

Vector initial_position = Vector(0, 0, 0); //this positions will be used for the mean 
Vector final_position = Vector(0, 0, 0);	//position in the markov meassurements

struct {             
	int min_delta_ftm = 15;         
	int burst_period = 10;         
	int burst_exponent = 2;         
	int burst_duration = 10;         
	int ftm_per_burst = 2;         
} FtmParameters; 

void SessionOver (FtmSession session);

//configures the parameters of the ftm protocol
void configureFtm(FtmParams &ftm_params){
  ftm_params.SetStatusIndication(FtmParams::RESERVED);
  ftm_params.SetStatusIndicationValue(0);

  //protocol parameters
  ftm_params.SetMinDeltaFtm(FtmParameters.min_delta_ftm); //100 us between frames
  ftm_params.SetBurstDuration(FtmParameters.burst_duration); //32 ms burst duration, this needs to be larger due to long processing delay until transmission
  ftm_params.SetNumberOfBurstsExponent(FtmParameters.burst_exponent); //4 bursts
  ftm_params.SetBurstPeriod(FtmParameters.burst_period); //1000 ms between burst periods
  ftm_params.SetFtmsPerBurst(FtmParameters.ftm_per_burst);

  ftm_params.SetPartialTsfNoPref(true);
  ftm_params.SetAsap(true);
}

void analysis(){
    if (abs(hist_rtt[0]-hist_rtt[1])/hist_rtt[1] > 0.05){
        if (state == "fix_position"){
            state="transition";
        } 
        else if (state == "transition"){
            state="brownian";
            same_state_counter = 0;
            FtmParameters.burst_exponent = 2;
            FtmParameters.ftm_per_burst = 2;
            FtmParameters.burst_duration = 10;
            FtmParameters.burst_period = 10;
        } 
        else if (state == "brownian") same_state_counter++;
    }

    //not moving and last state was brownian
    else if (state == "brownian"){
        same_state_counter = 0;
        state = "transition";
    }

    //not moving and last state was fix_position
    else if (state == "fix_position"){
        FtmParameters.burst_exponent = (FtmParameters.burst_exponent < 4) ? (2 + (same_state_counter / 5)) : 4;
        FtmParameters.ftm_per_burst = (FtmParameters.ftm_per_burst < 5 ) ? (2 + (same_state_counter/2)) : 5;
        FtmParameters.burst_duration = (FtmParameters.burst_duration < 11) ? (7 + (same_state_counter / 2)) : 11;
        FtmParameters.burst_period = (FtmParameters.burst_period < 12) ? (8 + (same_state_counter / 2)) : 12;
        same_state_counter++;
    }

    //not moving and last state was fix_position
    else if (state == "transition"){
        state = "fix_position";
        same_state_counter = 0;
        FtmParameters.burst_exponent = 2;
        FtmParameters.ftm_per_burst = 2;
        FtmParameters.burst_duration = 10;
        FtmParameters.burst_period = 10;
    }

}

static void GenerateTraffic ()
{
	Ptr<RegularWifiMac> _sta_mac = _sta->GetMac()->GetObject<RegularWifiMac>();

	Mac48Address to = Mac48Address::ConvertFrom (recvAddr);


    // std::cout << _sta_mac << std::endl;
    // std::cout << to << std::endl;

	Ptr<FtmSession> session = _sta_mac->NewFtmSession(to);

	if (session == 0)
		NS_FATAL_ERROR ("ftm not enabled");
		
	Ptr<FtmErrorModel> error_model;

	//create wireless error model
	//m_ap has to be created prior
	Ptr<WirelessFtmErrorModel> wireless_error = CreateObject<WirelessFtmErrorModel> ();
	wireless_error->SetFtmMap(map);
	wireless_error->SetNode(_sta->GetNode());
	wireless_error->SetChannelBandwidth(WiredFtmErrorModel::Channel_20_MHz);
	error_model = wireless_error;


	//using wired error model in this case
	session->SetFtmErrorModel(error_model);

	//create the parameter for this session and set them
	FtmParams ftm_params;
	configureFtm(ftm_params);
	session->SetFtmParams(ftm_params);

	session->SetSessionOverCallback(MakeCallback(&SessionOver));
	session->SessionBegin();
		// if (mobility_model == "brownian")
	initial_position = _ap->GetNode()->GetObject<MobilityModel>()->GetPosition();
		

	t1 = Simulator::Now().GetSeconds();
}

void SessionOver(FtmSession session){
    // std::cout << "FtmParameters.burst_exponent:" << FtmParameters.burst_exponent <<  std::endl;
    // std::cout << "FtmParameters.burst_duration:" << FtmParameters.burst_duration <<  std::endl;
    // std::cout << "FtmParameters.burst_period:" << FtmParameters.burst_period <<  std::endl;
    // std::cout << "FtmParameters.ftm_per_burst:" << FtmParameters.ftm_per_burst <<  std::endl;
    // std::cout << "FtmParameters.min_delta_ftm:" << FtmParameters.min_delta_ftm <<  std::endl;
    // std::cout << "---------------------" <<  std::endl;


    std::string file_path = "./ftm_ranging/simulations/data/adaptive-algorithm-test/";
    std::string file_name =  file_path + (dynamic_mode ? "adaptive-algorithm" : "static-algorithm");
    t2 =  Simulator::Now().GetSeconds();
    
    //expected distance & actual distance
    double expected_distance;
    final_position = _ap->GetNode()->GetObject<MobilityModel>()->GetPosition();
    Vector middle_position = Vector ((final_position.x+initial_position.x)/2, (final_position.y+initial_position.y)/2, (final_position.z+initial_position.z)/2);
    expected_distance = CalculateDistance(middle_position, Vector(0,0,0));

    std::list<int64_t> rtts = session.GetIndividualRTT();
    std::list<double> sig_strs = session.GetIndividualSignalStrength();
    std::ofstream output (file_name, std::ofstream::out | std::ofstream::app);
    int64_t total_rtt = 0;
    double mean_sig_str = 0;
    int count = 0;
    while (!rtts.empty()){
        total_rtt += rtts.front();
        mean_sig_str += sig_strs.front();
        sig_strs.pop_front();
        rtts.pop_front();
        count++;
    }

    mean_sig_str = double(mean_sig_str / count);

    output << FtmParameters.min_delta_ftm << " " << FtmParameters.burst_period << " " << FtmParameters.burst_exponent << " " << FtmParameters.burst_duration << " " << FtmParameters.ftm_per_burst << " "  << expected_distance << " " << double(total_rtt / count) << " " << mean_sig_str << " " << t2 - t1 << " " << double(total_rtt/(pow(10,9))) << " 2.5 " << final_position.x << " " << final_position.y <<"\n";
    output.close();

    //for algorithm analysis purposes
    hist_rtt.insert(hist_rtt.begin(), double(total_rtt / count));
    if (dynamic_mode && hist_rtt.size() > 2){
        analysis();
    }

    Simulator::Schedule(Seconds (0.001), &GenerateTraffic);
}

void loadConfigurations(std::vector<std::vector<int>>& configurations){
    if (!dynamic_mode){
        std::ifstream file("./scratch/ftm-configurations.txt");
        if (file.is_open()){
            std::string line;
            while (std::getline(file, line, '\n')) {
                // vector<double> configuration;
                // using printf() in all tests for consistency
                std::stringstream configuration(line);
                std::string segment;
                std::vector<int> seglist;
                while(std::getline(configuration, segment, ' '))
                    seglist.push_back(stoi(segment));
                
                configurations.push_back(seglist);
            
            }
            file.close();
        }
    }else{
        configurations.push_back({15,7,1,7,1});
    }
}

void updateParameters(std::vector<int>& configuration){
    FtmParameters.min_delta_ftm = configuration[0]; 
    FtmParameters.burst_period = configuration[1];
    FtmParameters.burst_exponent = configuration[2];
    FtmParameters.burst_duration = configuration[3];
    FtmParameters.ftm_per_burst = configuration[4];

    std::cout << "Parameters uploaded" << std::endl;
}

void runSimulation(){
    //set time resolution to pico seconds for the time stamps, as default is in nano seconds. IMPORTANT
	Config::SetDefault ("ns3::RegularWifiMac::FTM_Enabled", BooleanValue(true));

    //create nodes
    NodeContainer initiatingNodesContainer;
    NodeContainer receivingNodesContainer;
    initiatingNodesContainer.Create (1);
    receivingNodesContainer.Create (1);

    // assign mobility model
	MobilityHelper mobility;
	std::string _speed = "ns3::ConstantRandomVariable[Constant=" + std::to_string(2.5) + "]";
	mobility.SetMobilityModel ("ns3::RandomDirection2dMobilityModel",
		"Speed", StringValue (_speed),
		"Bounds", StringValue ("0|" + std::to_string(15) + "|0|" + std::to_string(15))
	);
		
	mobility.SetPositionAllocator ("ns3::RandomBoxPositionAllocator",
		"X", StringValue ("ns3::UniformRandomVariable[Min="+std::to_string(10)+"|Max=0]"),
		"Y", StringValue ("ns3::UniformRandomVariable[Min=0|Max=0]"),
		"Z", StringValue ("ns3::UniformRandomVariable[Min=0|Max=0]")
	);

	mobility.Install (receivingNodesContainer);

	MobilityHelper constantPositionMobility;
	constantPositionMobility.SetMobilityModel ("ns3::ConstantPositionMobilityModel");
	constantPositionMobility.Install (initiatingNodesContainer);
	Ptr<ConstantPositionMobilityModel> m1 = initiatingNodesContainer.Get(0)->GetObject<ConstantPositionMobilityModel>();
	m1->DoSetPosition(Vector (0, 0, 0));

	// end assign mobility model

    

    WifiHelper wifi;
    wifi.SetStandard (WIFI_STANDARD_80211n_2_4GHZ);

    // This is one parameter that matters when using FixedRssLossModel
    // set it to zero; otherwise, gain will be added
    YansWifiPhyHelper wifiPhy;
    wifiPhy.Set ("RxGain", DoubleValue (0) );
    wifiPhy.Set ("TxPowerStart", DoubleValue(14));
    wifiPhy.Set ("TxPowerEnd", DoubleValue(14));
    wifiPhy.Set ("RxSensitivity", DoubleValue(-150));
    wifiPhy.Set ("CcaEdThreshold", DoubleValue(-150));
    // ns-3 supports RadioTap and Prism tracing extensions for 802.11b
    wifiPhy.SetPcapDataLinkType (WifiPhyHelper::DLT_IEEE802_11_RADIO);

    YansWifiChannelHelper wifiChannel;
    wifiChannel.SetPropagationDelay ("ns3::ConstantSpeedPropagationDelayModel");

	//  wifiChannel.AddPropagationLoss ("ns3::ThreeGppIndoorOfficePropagationLossModel");


	// The below FixedRssLossModel will cause the rss to be fixed regardless
	// of the distance between the two stations, and the transmit power
	wifiChannel.AddPropagationLoss ("ns3::FixedRssLossModel","Rss",DoubleValue (-40));
    
    wifiPhy.SetChannel (wifiChannel.Create ());
    WifiMacHelper wifiMac;
    wifi.SetRemoteStationManager ("ns3::ConstantRateWifiManager");

    // Setup the rest of the mac
    Ssid ssid = Ssid ("wifi-default");
    // setup sta.
    wifiMac.SetType ("ns3::StaWifiMac",
                    "Ssid", SsidValue (ssid));
    //  wifiMac.SetType ("ns3::StaWifiMac");
    NetDeviceContainer staDevice = wifi.Install (wifiPhy, wifiMac, initiatingNodesContainer.Get(0));
    NetDeviceContainer devices = staDevice;

    // setup ap.
    wifiMac.SetType ("ns3::ApWifiMac",
                    "Ssid", SsidValue (ssid));
    NetDeviceContainer apDevice = wifi.Install (wifiPhy, wifiMac, receivingNodesContainer.Get(0));
    devices.Add (apDevice);


    //this have been made global to handle them from sessionOver for scheduling
    Ptr<NetDevice> ap = apDevice.Get(0);
    Ptr<NetDevice> sta = staDevice.Get(0);
    recvAddr = ap->GetAddress();

    //convert net device to wifi net device
    _ap = ap->GetObject<WifiNetDevice>();
    _sta = sta->GetObject<WifiNetDevice>();

    // Tracing
    wifiPhy.EnablePcap ("ftm-ranging", devices);

    Simulator::ScheduleNow (&GenerateTraffic);
    Simulator::Stop (Hours (simulation_time));
    Simulator::Run ();
    Simulator::Destroy();
}

int main (int argc, char *argv[]){
    //Load FTM map
    map = CreateObject<WirelessFtmErrorModel::FtmMap> ();
    map->LoadMap ("src/wifi/ftm_map/FTM_Wireless_Error.map");
	
    Time::SetResolution(Time::PS);

    std::vector<std::vector<int>> configurations;
    loadConfigurations(configurations);
    for (unsigned i = 0; configurations.size(); i++){
        for (unsigned j = 0; j < configurations[i].size(); j++){
            std::cout << configurations[i][j] << " ";
        }
        std::cout << std::endl;
        updateParameters(configurations[i]);
        runSimulation();
    }
	return 0;
}