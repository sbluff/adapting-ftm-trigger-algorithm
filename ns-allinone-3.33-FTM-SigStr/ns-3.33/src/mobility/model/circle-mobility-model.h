#include "ns3/simulator.h"
#include "mobility-model.h"
// #include "ns3/netsimulyzer-module.h"

#ifndef CIRCLE_MOBILITY_MODEL_H
#define CIRCLE_MOBILITY_MODEL_H

namespace ns3 {

/**
 * \ingroup mobility
 *
 * \brief Mobility model for which the current speed does not change once it has been set and until it is set again explicitly to a new value.
 */
class CircleMobilityModel : public MobilityModel 
{
public:
    /**
     * Create position located at coordinates (0,0,0) with
     * speed (0,0,0).
     */
    CircleMobilityModel ();
    virtual ~CircleMobilityModel ();
    static TypeId GetTypeId (void);

    /**
     * \param speed the new speed to set.
     *
     * Set the current speed now to (dx,dy,dz)
     * Unit is meters/s
     */
    void SetParameters(const Vector &Origin, const double Radius, const double StartAngle, const double Speed);
    void ChangeRadius(const double Radius);
    virtual Vector DoGetPosition (void) const;
    virtual Vector DoGetVelocity (void) const;

private:
    virtual void DoSetPosition (const Vector &position);
    Vector m_position; //!< the constant position
    Vector m_Origin;
    double m_Radius;
    double m_StartAngle;
    double m_Speed;
    Time m_lastUpdate;
};

} // namespace ns3

#endif /* CONSTANT_POSITION_MOBILITY_MODEL_H */

