
#include "circle-mobility-model.h"
#include <ns3/double.h>
#include <ns3/boolean.h>

namespace ns3 {
  NS_OBJECT_ENSURE_REGISTERED (CircleMobilityModel);

  void
  CircleMobilityModel::SetParameters(const Vector &Origin, const double Radius, const double StartAngle, const double Speed)
  {
      DoSetPosition(Origin);
      m_Origin=Origin;
      m_Radius=Radius;
      m_StartAngle=StartAngle;
      m_Speed=Speed;
      NotifyCourseChange ();
  }

  TypeId CircleMobilityModel::GetTypeId (void)
  {
    static TypeId tid = TypeId ("ns3::CircleMobilityModel")
      .SetParent<MobilityModel> ()
      .SetGroupName ("Mobility")
      .AddConstructor<CircleMobilityModel> ();
    return tid;
  }

  CircleMobilityModel::CircleMobilityModel ()
  {
  }

  CircleMobilityModel::~CircleMobilityModel ()
  {
  }

  Vector CircleMobilityModel::DoGetPosition (void) const
  {
    Time now = Simulator::Now ();
    NS_ASSERT (m_lastUpdate <= now);
    //m_lastUpdate = now;
    double angle = m_StartAngle + ((m_Speed/m_Radius) * now.GetSeconds());
    double cosAngle = cos(angle);
    double sinAngle = sin(angle);    
    return Vector ( m_Origin.x + cosAngle * m_Radius, m_Origin.y + sinAngle * m_Radius, m_Origin.z);
  }

  void CircleMobilityModel::DoSetPosition (const Vector &position)
  {
    m_position = position;
    m_lastUpdate = Simulator::Now(); 
    NotifyCourseChange ();
  }

  Vector CircleMobilityModel::DoGetVelocity (void) const
  {
    Time now = Simulator::Now ();
    NS_ASSERT (m_lastUpdate <= now);
    //m_lastUpdate = now;
    double angle = m_StartAngle + ((m_Speed/m_Radius) * now.GetSeconds());
    double cosAngle = cos(angle);
    double sinAngle = sin(angle);
    
    return Vector ( -sinAngle * m_Speed, cosAngle * m_Speed, 0.0);
  }

} // namespace ns3
