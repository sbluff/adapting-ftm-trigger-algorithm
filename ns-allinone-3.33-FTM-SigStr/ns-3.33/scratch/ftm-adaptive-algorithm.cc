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
int measurements = 1000;
double intial_distance = 10.0;

struct {             
	int min_delta_ftm = 15;         
	int burst_period = 7;         
	int burst_exponent = 1;         
	int burst_duration = 5;         
	int ftm_per_burst = 1;         
} FtmParameters;       

FtmParameters expectedParameters;

void loadFtmMap(){
  map = CreateObject<WirelessFtmErrorModel::FtmMap> ();

  map->LoadMap ("src/wifi/ftm_map/FTM_Wireless_Error.map");

  std::cout << "Multipath Map loaded!" << std::endl;
}

void configure(){
  	//set time resolution to pico seconds for the time stamps, as default is in nano seconds. IMPORTANT
	Time::SetResolution(Time::PS);

	Config::SetDefault ("ns3::RegularWifiMac::FTM_Enabled", BooleanValue(true));

    //create nodes
    NodeContainer initiatingNodesContainer;
    NodeContainer receivingNodesContainer;
    initiatingNodesContainer.Create (1);
    receivingNodesContainer.Create (1);

    // assignMobilityModel(initiatingNodesContainer, receivingNodesContainer, mobility_model, velocity);
	

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

    Simulator::Stop (Seconds (500000.0));
    Simulator::Run ();
    Simulator::Destroy ();
}


int main (int argc, char *argv[]){
	loadFtmMap();
	configure();



	return 0;
}