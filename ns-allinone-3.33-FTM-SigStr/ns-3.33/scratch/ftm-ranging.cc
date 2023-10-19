/* -*-  Mode: C++; c-file-style: "gnu"; indent-tabs-mode:nil; -*- */
/*
 * Copyright (c) 2009 The Boeing Company
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 2 as
 * published by the Free Software Foundation;
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 *
 */
/*
 * Based on the "wifi-simple-infra.cc" example.
 * Modified by Christos Laskos.
 * 2022
 */

#include <typeinfo>
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
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <vector>
#include <cmath>
#include <string>

using namespace ns3;

NS_LOG_COMPONENT_DEFINE ("FtmRanging");

int session_counter = 0;
int measurements_per_distance = 2000;
int max_sampling_distance = 10;
int step = 5;
double velocity = 0;
double distance = 10;
std::string file_name;
int min_delta_ftm, burst_duration, burst_exponent, burst_period, ftm_per_burst;
Ptr<WirelessFtmErrorModel::FtmMap> map;
Ptr<WifiNetDevice> _ap;
Ptr<WifiNetDevice> _sta;
Address recvAddr;
std::string mobility_model;
double t1;
double t2; //meassure session lenght in time
bool configuration_finished = false;

Vector initial_position = Vector(0, 0, 0); //this positions will be used for the mean 
Vector final_position = Vector(0, 0, 0);	//position in the markov meassurements

void SessionOver (FtmSession session);


//configures the parameters of the ftm protocol
void configureFtm(FtmParams &ftm_params){
  ftm_params.SetStatusIndication(FtmParams::RESERVED);
  ftm_params.SetStatusIndicationValue(0);

  //protocol parameters
  ftm_params.SetMinDeltaFtm(min_delta_ftm); //100 us between frames
  ftm_params.SetBurstDuration(burst_duration); //32 ms burst duration, this needs to be larger due to long processing delay until transmission
  ftm_params.SetNumberOfBurstsExponent(burst_exponent); //4 bursts
  ftm_params.SetBurstPeriod(burst_period); //1000 ms between burst periods
  ftm_params.SetFtmsPerBurst(ftm_per_burst);

  ftm_params.SetPartialTsfNoPref(true);
  ftm_params.SetAsap(true);

}

//only for circle mean
void changePosition (Ptr<Node> sta) {
    if (mobility_model == "circle_mean" || mobility_model == "test"){
        Ptr<MobilityModel> mobility = sta->GetObject<MobilityModel>();
        double x = cos(2 * M_PI / 360 * (session_counter%360)) * distance;
        double y = sin(2 * M_PI / 360 * (session_counter%360)) * distance;

        mobility->SetPosition(Vector(x, y, 0));
    }
}


void changeRadius(Ptr<Node> sta, double radius){
    if (mobility_model == "fix_position"){
      Ptr<MobilityModel> mobility_ap = _ap->GetNode()->GetObject<MobilityModel>();
      Ptr<MobilityModel> mobility = sta->GetObject<MobilityModel>();

      std::cout << "----------------------------" << std::endl;
      std::cout << mobility->GetPosition().x << mobility->GetPosition().y << std::endl; 
      std::cout << mobility_ap->GetPosition().x << " " << mobility_ap->GetPosition().y << std::endl;
      std::cout << "----------------------------" << std::endl;

      mobility->SetPosition(Vector(distance, 0, 0));
    }

    else if (mobility_model == "circle_velocity"){
        Ptr<CircleMobilityModel> mobility = _ap->GetNode()->GetObject<CircleMobilityModel>();
        std::cout << mobility << std::endl;
        mobility->ChangeRadius(double(radius));
    }

    std::cout << "Radius changed, new radius " << distance << std::endl;


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
	if (mobility_model == "brownian")
		initial_position = _ap->GetNode()->GetObject<MobilityModel>()->GetPosition();
	

  t1 = Simulator::Now().GetSeconds();
}


void SessionOver (FtmSession session)
{
  if (distance <= max_sampling_distance){
		if (mobility_model == "brownian")
			final_position = _ap->GetNode()->GetObject<MobilityModel>()->GetPosition();

    t2 =  Simulator::Now().GetSeconds();
    std::string file_path = "./ftm_ranging/simulations/" + mobility_model + "/" + std::to_string(int(min_delta_ftm)) + '-' + std::to_string(int(burst_duration)) + '-' + std::to_string(int(burst_exponent)) + '-' + std::to_string(int(burst_period)) + '-' + std::to_string(int(ftm_per_burst)) + '/';
    file_name =  file_path + std::to_string(int(distance)) + 'm';
    //create folder for files
    const char* str = file_path.c_str();
    mkdir(str ,0777);

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
    if (distance <= max_sampling_distance){
        mean_sig_str = double(mean_sig_str / count);
				double expected_distance;
				if (mobility_model == "brownian"){
					Vector middle_position = Vector ((final_position.x+initial_position.x)/2, (final_position.y+initial_position.y)/2, (final_position.z+initial_position.z)/2);
					expected_distance = CalculateDistance(middle_position, Vector(0,0,0));
					// std::cout << "----------------------------" << std::endl;
					// std::cout << "intial_position: " << initial_position.x << " " << initial_position.y << " " << initial_position.z << std::endl;
					// std::cout << "final_position: " << final_position.x << " " << final_position.y << " " << final_position.z << std::endl;
					// std::cout << "middle_position: " << middle_position.x << " " << middle_position.y << " " << middle_position.z << std::endl;
					// std::cout << "distance: " << expected_distance << std::endl;
				}
				else
					expected_distance = distance;

        output << expected_distance << " " << double(total_rtt / count) << " " << mean_sig_str << " " << t2 - t1 << " " << double(total_rtt/(pow(10,9))) << " " << velocity  << "\n";
    }
    output.close();

    session_counter++;
    changePosition(_sta->GetNode());
    if (session_counter >= measurements_per_distance){
        session_counter = 0;
        if (distance < max_sampling_distance){
            distance += step;
            changeRadius(_ap->GetNode(), double(distance));
        }
        else {
          configuration_finished = true;
          std::cout << "configuration finished!" << std::endl;
          std::cout << "Stopping simulator..." << std::endl;
          Simulator::Stop();
        }
    }

    if (int(distance) <= max_sampling_distance && !configuration_finished){
      Simulator::Schedule(Seconds (0.001), &GenerateTraffic);
    }

  }

  else{

  }
}

//loads into configurations the set of parameters that will be used during each one of the mobility_model simulations
void loadConfigurations(std::vector<std::vector<int>>& configurations){
  configurations.push_back({15,10,1,10,2});
  configurations.push_back({15,10,1,10,3});
  configurations.push_back({15,10,1,10,4});
  configurations.push_back({15,10,1,10,5});
  configurations.push_back({15,10,2,10,2});
  configurations.push_back({15,10,2,10,3});
  configurations.push_back({15,10,2,10,4});
  configurations.push_back({15,10,2,10,5});  
  configurations.push_back({15,10,3,10,2});
  configurations.push_back({15,10,3,10,3});
  configurations.push_back({15,10,3,10,4});
  configurations.push_back({15,10,3,10,5});
  configurations.push_back({15,10,4,10,2});
  configurations.push_back({15,10,4,10,3});
  configurations.push_back({15,10,4,10,4});
  configurations.push_back({15,10,4,10,5});
}

//loads in models the type of simulations that will take place
void loadModels(std::vector<std::string>& models){
  // models.push_back("test");
  models.push_back("brownian");
  // models.push_back("circle_mean");
  // models.push_back("circle_velocity");
  // models.push_back("fix_position");
}

//based on mobility_mode variable this function assigns the container different mobility modes and sets its parameters
void assignMobilityModel(NodeContainer& initiatingNodes, NodeContainer& receivingNodes, std::string mobility_model){
    if (mobility_model == "circle_velocity"){
				velocity = 3.5;
        MobilityHelper circularMobility;
        circularMobility.SetMobilityModel ("ns3::CircleMobilityModel");
        circularMobility.Install (receivingNodes);
        Ptr<CircleMobilityModel> m0 = receivingNodes.Get(0)->GetObject<CircleMobilityModel>();
        m0->SetParameters(Vector (0, 0, 0), double(distance), double(90), double(10));

        MobilityHelper constantPositionMobility;
        constantPositionMobility.SetMobilityModel ("ns3::ConstantPositionMobilityModel");
        constantPositionMobility.Install (initiatingNodes);
        Ptr<ConstantPositionMobilityModel> m1 = initiatingNodes.Get(0)->GetObject<ConstantPositionMobilityModel>();
        m1->DoSetPosition(Vector (0, 0, 0));
    }

    else if (mobility_model == "circle_mean" || mobility_model == "test"){
				velocity = 0;
        MobilityHelper constantPositionMobility;
        constantPositionMobility.SetMobilityModel ("ns3::ConstantPositionMobilityModel");
        constantPositionMobility.Install (initiatingNodes);
        constantPositionMobility.Install (receivingNodes);
        Ptr<ConstantPositionMobilityModel> m1 = initiatingNodes.Get(0)->GetObject<ConstantPositionMobilityModel>();
        Ptr<ConstantPositionMobilityModel> m2 = receivingNodes.Get(0)->GetObject<ConstantPositionMobilityModel>();
        m1->DoSetPosition(Vector (distance, 0, 0));
        m2->DoSetPosition(Vector (0, 0, 0));
    }

    else if (mobility_model == "fix_position"){
        velocity = 0;
        MobilityHelper constantPositionMobility;
        constantPositionMobility.SetMobilityModel ("ns3::ConstantPositionMobilityModel");
        constantPositionMobility.Install (initiatingNodes);
        constantPositionMobility.Install (receivingNodes);
        Ptr<ConstantPositionMobilityModel> m1 = initiatingNodes.Get(0)->GetObject<ConstantPositionMobilityModel>();
        Ptr<ConstantPositionMobilityModel> m2 = receivingNodes.Get(0)->GetObject<ConstantPositionMobilityModel>();
        m1->DoSetPosition(Vector (distance, 0, 0));
        m2->DoSetPosition(Vector (0, 0, 0));
    }

    else if (mobility_model == "brownian"){
        velocity = 2.223;
        MobilityHelper mobility;
        std::string _speed = "ns3::ConstantRandomVariable[Constant=" + std::to_string(velocity) + "]";
        mobility.SetMobilityModel (
            "ns3::RandomWalk2dMobilityModel",
            "Mode", StringValue ("Time"),
            "Time", StringValue ("10s"),
            "Speed", StringValue (_speed),
            "Bounds", StringValue ("0|" + std::to_string(distance) + "|0|" + std::to_string(distance))
        );
          
        mobility.SetPositionAllocator ("ns3::RandomBoxPositionAllocator",
            "X", StringValue ("ns3::UniformRandomVariable[Min="+std::to_string(distance)+"|Max=0]"),
            "Y", StringValue ("ns3::UniformRandomVariable[Min=0|Max=0]"),
            "Z", StringValue ("ns3::UniformRandomVariable[Min=0|Max=0]")
        );

        mobility.Install (receivingNodes);


        MobilityHelper constantPositionMobility;
        constantPositionMobility.SetMobilityModel ("ns3::ConstantPositionMobilityModel");
        constantPositionMobility.Install (initiatingNodes);
        Ptr<ConstantPositionMobilityModel> m1 = initiatingNodes.Get(0)->GetObject<ConstantPositionMobilityModel>();
        m1->DoSetPosition(Vector (0, 0, 0));
  }

      else {
          std::cout << "invalid mobility model, can't configure it!" << std::endl;
          return;
      }
}

// Creates the nodes infrastructure, configures them according to configuration param, assigns mobility models according to mobility_mode param
// then runs simulator
void runSimulation(const std::vector<int>& configuration){
    ///////// PARAMETERS
    configuration_finished = false;
    std::cout << "New config" << std::endl;
    min_delta_ftm = configuration[0];
    burst_duration = configuration[1];
    burst_exponent = configuration[2];
    burst_period = configuration[3];
    ftm_per_burst = configuration[4];

    //enable FTM through attribute system
    Config::SetDefault ("ns3::RegularWifiMac::FTM_Enabled", BooleanValue(true));

    //create nodes
    NodeContainer initiatingNodesContainer;
    NodeContainer receivingNodesContainer;
    initiatingNodesContainer.Create (1);
    receivingNodesContainer.Create (1);

    assignMobilityModel(initiatingNodesContainer, receivingNodesContainer, mobility_model);

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


int main (int argc, char *argv[])
{
  map = CreateObject<WirelessFtmErrorModel::FtmMap> ();

  map->LoadMap ("src/wifi/ftm_map/FTM_Wireless_Error.map");

  std::cout << "Multipath Map loaded!" << std::endl;
  //set time resolution to pico seconds for the time stamps, as default is in nano seconds. IMPORTANT
  Time::SetResolution(Time::PS);

  std::vector<std::vector<int>> configurations;
  loadConfigurations(configurations);

  std::vector<std::string> models;
  loadModels(models);
  for (unsigned i = 0; i < models.size(); i++)
    for (unsigned j = 0; j < configurations.size(); j++){
        distance = 10;
        mobility_model = models[i];
        runSimulation(configurations[j]);
    }
  return 0;
}