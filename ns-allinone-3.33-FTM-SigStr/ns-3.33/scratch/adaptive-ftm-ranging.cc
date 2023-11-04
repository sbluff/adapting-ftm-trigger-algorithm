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


using namespace ns3;

NS_LOG_COMPONENT_DEFINE ("FtmAdaptiveAlgorithm");

Ptr<WirelessFtmErrorModel::FtmMap> map;
Ptr<WifiNetDevice> _ap;
Ptr<WifiNetDevice> _sta;
Address recvAddr;
double t1;
double t2; 
int session_counter = 0;
int measurements = 1000;
double intial_distance = 10.0;

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

static void GenerateTraffic ()
{
	Ptr<RegularWifiMac> _sta_mac = _sta->GetMac()->GetObject<RegularWifiMac>();

	Mac48Address to = Mac48Address::ConvertFrom (recvAddr);

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
		// 	initial_position = _ap->GetNode()->GetObject<MobilityModel>()->GetPosition();
		

	t1 = Simulator::Now().GetSeconds();
}

void SessionOver(FtmSession session){
    std::cout << "end session" << std::endl;
    std::string file_path = "./ftm_ranging/simulations/data/adaptive-algorithm-test/";
    std::string file_name =  file_path + "adaptive-algorithm";
    t2 =  Simulator::Now().GetSeconds();
    
    //expected distance & actual distance
    double expected_distance;
    final_position = _ap->GetNode()->GetObject<MobilityModel>()->GetPosition();
    std::cout << final_position.x << " " << final_position.y << " " << final_position.z << std::endl;
    std::cout << t2 << std::endl;
    std::cout << "-------------------------------" << std::endl;
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

    output << expected_distance << " " << double(total_rtt / count) << " " << mean_sig_str << " " << t2 - t1 << " " << double(total_rtt/(pow(10,9))) << " 2.5"  << "\n";
    
    output.close();

	if (session_counter < measurements)
    	Simulator::Schedule(Seconds (0.001), &GenerateTraffic);
    else{
        std::cout << "configuration finished!" << std::endl;
        std::cout << "Stopping simulator..." << std::endl;
        Simulator::Stop();  
    }

    session_counter++;
}

void loadFtmMap(){
  map = CreateObject<WirelessFtmErrorModel::FtmMap> ();

  map->LoadMap ("src/wifi/ftm_map/FTM_Wireless_Error.map");

  std::cout << "Multipath Map loaded!" << std::endl;
}

void initialSetUp(){
  	//set time resolution to pico seconds for the time stamps, as default is in nano seconds. IMPORTANT
	Time::SetResolution(Time::PS);

	Config::SetDefault ("ns3::RegularWifiMac::FTM_Enabled", BooleanValue(true));

    //create nodes
    NodeContainer initiatingNodesContainer;
    NodeContainer receivingNodesContainer;
    initiatingNodesContainer.Create (1);
    receivingNodesContainer.Create (1);

    // assign mobility model
	MobilityHelper mobility;
	std::string _speed = "ns3::ConstantRandomVariable[Constant=" + std::to_string(0.5) + "]";
	mobility.SetMobilityModel ("ns3::RandomDirection2dMobilityModel",
		"Speed", StringValue (_speed),
		"Bounds", StringValue ("0|" + std::to_string(10) + "|0|" + std::to_string(10))
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


}

void runSimulation(){
    Simulator::ScheduleNow (&GenerateTraffic);

    Simulator::Stop (Seconds (500000.0));
    Simulator::Run ();
    Simulator::Destroy ();
}

int main (int argc, char *argv[]){
	loadFtmMap();
	initialSetUp();
	runSimulation();
	return 0;
}