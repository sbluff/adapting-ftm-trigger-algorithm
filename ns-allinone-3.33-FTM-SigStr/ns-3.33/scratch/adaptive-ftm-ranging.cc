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
#include "../src/mobility/model/ftm-adaptive-ranger.cc"
#include <vector>

NS_LOG_COMPONENT_DEFINE ("FtmAdaptiveAlgorithm");


using namespace ns3;

void configureFtm(FtmParams &ftm_params);
void runSimulation();
static void GenerateTraffic ();
void SessionOver(FtmSession session);

Ptr<WirelessFtmErrorModel::FtmMap> map;
Ptr<WifiNetDevice> _ap;
Ptr<WifiNetDevice> _sta;
Address recvAddr;
double t1;
double t2; 



FtmAdaptiveRanger myRanger;
Vector initial_position = Vector(0, 0, 0); //this positions will be used for the mean 
Vector final_position = Vector(0, 0, 0);	//position in the markov meassurements

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
	session->SetFtmParams(myRanger.GetParameters());

	session->SetSessionOverCallback(MakeCallback(&SessionOver));
	session->SessionBegin();
		// if (mobility_model == "brownian")
	initial_position = _ap->GetNode()->GetObject<MobilityModel>()->GetPosition();
		

	t1 = Simulator::Now().GetSeconds();
}

void SessionOver(FtmSession session){
    std::string file_path = "./ftm_ranging/simulations/data/adaptive-algorithm-test/";
    std::string file_name =  file_path + "adaptive-algorithm";
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

    FtmParams parameters = myRanger.GetParameters();

    output << std::to_string(parameters.GetMinDeltaFtm()) << " " << std::to_string(parameters.GetBurstPeriod()) << " " << std::to_string(parameters.GetNumberOfBurstsExponent()) << " " << std::to_string(parameters.GetBurstDuration()) << " " << std::to_string(parameters.GetFtmsPerBurst()) << " "  << expected_distance << " " << double(total_rtt / count) << " " << mean_sig_str << " " << t2 - t1 << " " << double(total_rtt/(pow(10,9))) << " 2.5 " << final_position.x << " " << final_position.y << " " <<  myRanger.GetSameStateCounter() << "\n";
    output.close();

    //for algorithm analysis purposes
    myRanger.AddRtt((total_rtt / count));
    myRanger.Analysis();

    Simulator::Schedule(Seconds (0.1), &GenerateTraffic);
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

    Simulator::Schedule(Seconds(0.001), &GenerateTraffic);
    Simulator::Stop (myRanger.GetSimulationTime());
    Simulator::Run ();
    Simulator::Destroy();
}

int main (int argc, char *argv[]){
    map = CreateObject<WirelessFtmErrorModel::FtmMap> ();
    map->LoadMap ("src/wifi/ftm_map/FTM_Wireless_Error.map");
	
    Time::SetResolution(Time::PS);

    runSimulation();
    
	return 0;
}